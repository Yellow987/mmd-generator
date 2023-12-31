import pymeshio.common
from Utility import df_ops, vmd_ops, interpolate
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
  
def updateBoneListsForNextOccurenceOfBone(boneName, currentFrameNumber, lastFrame, lastBoneList, nextBoneList, df):
  lastBoneList[boneName] = nextBoneList[boneName]
  nextBoneOccurenceValues = getNextBoneOccurence(df, boneName, currentFrameNumber)
  if nextBoneOccurenceValues is not None:
    nextBoneList[boneName] = nextBoneOccurenceValues
  else:
    nextBoneList[boneName] = {"frameNumber": lastFrame, "position": lastBoneList[boneName]['position'], "rotation": lastBoneList[boneName]['rotation']}
  return lastBoneList, nextBoneList

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
        lastBoneList, nextBoneList = updateBoneListsForNextOccurenceOfBone(missingBone, currentFrameNumber, lastFrame, lastBoneList, nextBoneList, df)
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

def rotate_point_around_wy_axis(point, centerRotation):
  vec3 = point.values[0]
  xyzpoint = (vec3.x, vec3.y, vec3.z)
  quaternion = (centerRotation.w, centerRotation.x, centerRotation.y, centerRotation.z)

  def quaternion_multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return (w, x, y, z)

  def quaternion_conjugate(q):
    w, x, y, z = q
    return (w, -x, -y, -z)

  def rotate_point_by_quaternion(point, quaternion):
    # Represent the point as a quaternion
    point_quaternion = (0, point[0], point[1], point[2])
    
    # Calculate the rotated point
    q_conjugate = quaternion_conjugate(quaternion)
    new_point_quaternion = quaternion_multiply(quaternion_multiply(quaternion, point_quaternion), q_conjugate)
    
    # Extract the x, y, z coordinates from the resulting quaternion
    _, x, y, z = new_point_quaternion
    return (x, y, z)
  
  rotated_point = rotate_point_by_quaternion(xyzpoint, quaternion)
  
  return pymeshio.common.Vector3(rotated_point[0], rotated_point[1], rotated_point[2])

def normalizePositionsToCenter(df):
  df = df_ops.sortDf(df)
  df_position_bones = df[df['name'].isin(['センター', '左足ＩＫ', '右足ＩＫ'])]
  complement = vmd_ops.getComplement(df)
  lastFrame = df_ops.getLastFrame(df_position_bones)
  centerBone = 'センター'
  footIKBones = ['左足ＩＫ', '右足ＩＫ']
  boneList = [centerBone] + footIKBones

  lastBoneList = {boneName: {"frameNumber": None, "position": None, "rotation": None} for boneName in boneList}
  for boneName in lastBoneList.keys(): #init lastbonelist
    lastBoneList[boneName] = interpolate.getNextBoneOccurence(df_position_bones, boneName, 0)
  nextBoneList = {boneName: {"frameNumber": -1, "position": lastBoneList[boneName]['position'], "rotation": lastBoneList[boneName]['rotation']} for boneName in boneList}

  newFrames = []
  for currentFrameNumber in range(0, lastFrame + 1):
    frameDf = df_position_bones[df_position_bones['frame'] == currentFrameNumber]
    presentBonesOfBoneList = [boneName for boneName in boneList if boneName in frameDf['name'].values]
    for boneName in presentBonesOfBoneList:
      if currentFrameNumber > nextBoneList[boneName]['frameNumber']:
        lastBoneList, nextBoneList = interpolate.updateBoneListsForNextOccurenceOfBone(boneName, currentFrameNumber, lastFrame, lastBoneList, nextBoneList, df_position_bones)
      if boneName == centerBone:
        for footIKBone in [footIKBone for footIKBone in footIKBones if footIKBone not in presentBonesOfBoneList]:
          interpolatedFootBonePosition = interpolate.calculateVector3Porportion(currentFrameNumber, lastBoneList[footIKBone], nextBoneList[footIKBone])
          newFrames.append([
            currentFrameNumber,
            footIKBone,
            interpolate.rotate_point_around_wy_axis(interpolatedFootBonePosition - nextBoneList[centerBone]['position'], nextBoneList[centerBone]['rotation']),
            interpolate.calculateVector4Porportion(currentFrameNumber, lastBoneList[footIKBone], nextBoneList[footIKBone])
          ])
        for footIKBone in [footIKBone for footIKBone in footIKBones if footIKBone in presentBonesOfBoneList]:
          df_position_bones.loc[(df_position_bones['frame'] == currentFrameNumber) & (df_position_bones['name'] == footIKBone), 'position'] -= nextBoneList[centerBone]['position']
          df_position_bones.loc[(df_position_bones['frame'] == currentFrameNumber) & (df_position_bones['name'] == footIKBone), 'position'].values[0] = interpolate.rotate_point_around_wy_axis(df_position_bones.loc[(df_position_bones['frame'] == currentFrameNumber) & (df_position_bones['name'] == footIKBone), 'position'], nextBoneList[centerBone]['rotation'])
        break
      else:
        interpolatedCenterBonePosition = interpolate.calculateVector3Porportion(currentFrameNumber, lastBoneList[centerBone], nextBoneList[centerBone])
        interpolatedCenterBoneRotation = interpolate.calculateVector4Porportion(currentFrameNumber, lastBoneList[centerBone], nextBoneList[centerBone])
        df_position_bones.loc[(df_position_bones['frame'] == currentFrameNumber) & (df_position_bones['name'] == boneName), 'position'] -= interpolatedCenterBonePosition
        df_position_bones.loc[(df_position_bones['frame'] == currentFrameNumber) & (df_position_bones['name'] == boneName), 'position'].values[0] = interpolate.rotate_point_around_wy_axis(df_position_bones.loc[(df_position_bones['frame'] == currentFrameNumber) & (df_position_bones['name'] == boneName), 'position'], interpolatedCenterBoneRotation)
  newFramesDf = pd.DataFrame(newFrames, columns=['frame', 'name', 'position', 'rotation'])
  normalized_to_center_df = df.copy()
  normalized_to_center_df.update(df_position_bones, overwrite=True)
  normalized_to_center_df = pd.concat([normalized_to_center_df, newFramesDf])
  normalized_to_center_df = df_ops.sortDf(normalized_to_center_df)
  normalized_to_center_df['complement'] = complement
  normalized_to_center_df = normalized_to_center_df[normalized_to_center_df['name'] != centerBone]
  normalized_to_center_df = df_ops.sortDf(normalized_to_center_df)
  return normalized_to_center_df