import pymeshio.common
import df_ops, vmd_ops
import pandas as pd


def getMissingBones(df, boneList):
  df_bone_names_set = set(df['name'])
  boneList_set = set(boneList)
  return list(boneList_set - df_bone_names_set)

def getNextBoneOccurence(df, boneName, startFrame):
  boneDf = df[df['name'] == boneName]
  boneDf = boneDf[boneDf['frame'] >= startFrame]
  if boneDf.empty:
    return None
  else:
    return {"frameNumber": boneDf.iloc[0]['frame'], "position": boneDf.iloc[0]['position'], "rotation": boneDf.iloc[0]['rotation']}
  
def calculateVector3Porportion(currentFrame, lastBoneOccurence, nextBoneOccurence):
  if lastBoneOccurence['frameNumber'] == nextBoneOccurence['frameNumber']:
    return lastBoneOccurence['position']
  else:
    porportion = (currentFrame - lastBoneOccurence['frameNumber']) / (nextBoneOccurence['frameNumber'] - lastBoneOccurence['frameNumber'])
    return pymeshio.common.Vector3(
      lastBoneOccurence['position'].x + (nextBoneOccurence['position'].x - lastBoneOccurence['position'].x) * porportion,
      lastBoneOccurence['position'].y + (nextBoneOccurence['position'].y - lastBoneOccurence['position'].y) * porportion,
      lastBoneOccurence['position'].z + (nextBoneOccurence['position'].z - lastBoneOccurence['position'].z) * porportion
    )

def calculateVector4Porportion(currentFrame, lastBoneOccurence, nextBoneOccurence):
  if lastBoneOccurence['frameNumber'] == nextBoneOccurence['frameNumber']:
    return lastBoneOccurence['rotation']
  else:
    porportion = (currentFrame - lastBoneOccurence['frameNumber']) / (nextBoneOccurence['frameNumber'] - lastBoneOccurence['frameNumber'])
    return pymeshio.common.Vector4(
      lastBoneOccurence['rotation'].x + (nextBoneOccurence['rotation'].x - lastBoneOccurence['rotation'].x) * porportion,
      lastBoneOccurence['rotation'].y + (nextBoneOccurence['rotation'].y - lastBoneOccurence['rotation'].y) * porportion,
      lastBoneOccurence['rotation'].z + (nextBoneOccurence['rotation'].z - lastBoneOccurence['rotation'].z) * porportion,
      lastBoneOccurence['rotation'].w + (nextBoneOccurence['rotation'].w - lastBoneOccurence['rotation'].w) * porportion
    )

import pymeshio.common
def addInterpolationsToEachFrame(df):
  df = df_ops.sortDf(df)
  complement = vmd_ops.getComplement(df)
  boneNames = df['name'].unique().tolist()

  lastBoneList = {boneName: {"frameNumber": None, "position": None, "rotation": None} for boneName in boneNames}
  for boneName in lastBoneList.keys(): #init lastbonelist
    lastBoneList[boneName] = getNextBoneOccurence(df, boneName, 0)
  nextBoneList = {boneName: {"frameNumber": -1, "position": lastBoneList[boneName]['position'], "rotation": lastBoneList[boneName]['rotation']} for boneName in boneNames}

  newFrames = []
  lastFrame = df['frame'].max()
  for currentFrameNumber in range(0, lastFrame + 1):
    frameDf = df[df['frame'] == currentFrameNumber]
    missingBonesOfCurrentFrame = getMissingBones(frameDf, boneNames)
    for missingBone in missingBonesOfCurrentFrame:
      if currentFrameNumber > nextBoneList[missingBone]['frameNumber']:
        lastBoneList[missingBone] = nextBoneList[missingBone]
        nextBoneOccurenceValues = getNextBoneOccurence(df, missingBone, currentFrameNumber)
        nextBoneList[missingBone] = nextBoneOccurenceValues if nextBoneOccurenceValues is not None else nextBoneList[missingBone]
      newFrames.append([
        currentFrameNumber,
        missingBone,
        lastBoneList[missingBone]['position'] if missingBone not in vmd_ops.getBonesWherePositionIsUsed() else calculateVector3Porportion(currentFrameNumber, lastBoneList[missingBone], nextBoneList[missingBone]),
        calculateVector4Porportion(currentFrameNumber, lastBoneList[missingBone], nextBoneList[missingBone])
      ])
      #print(currentFrameNumber, missingBone, nextBoneList[missingBone]['position'], lastBoneList[missingBone]['position'])
  newFramesDf = pd.DataFrame(newFrames, columns=['frame', 'name', 'position', 'rotation'])
  interpolated_df = df.copy()
  interpolated_df = pd.concat([df, newFramesDf])
  interpolated_df = df_ops.sortDf(interpolated_df)
  interpolated_df['complement'] = complement
  return interpolated_df
  