import pandas as pd
import pymeshio.common

def saveDfToFeather(df, filepath):
  df.loc[:, 'position'] = df['position'].apply(lambda v: (v.x, v.y, v.z))
  df.loc[:, 'rotation'] = df['rotation'].apply(lambda v: (v.x, v.y, v.z, v.w))
  df.to_feather(filepath)

def loadDfFromFeather(filepath):
  df = pd.read_feather(filepath)
  df['position'] = df['position'].apply(lambda t: pymeshio.common.Vector3(t[0], t[1], t[2]))
  df['rotation'] = df['rotation'].apply(lambda t: pymeshio.common.Quaternion(t[0], t[1], t[2], t[3]))
  return df

def appendFrames(df1, df2, buffer=0):
    last_frame_df1 = df1['frame'].max() if not df1.empty else 0
    first_frame_df2 = df2['frame'].min() if not df2.empty else 0
    frame_shift = first_frame_df2 - last_frame_df1 
    
    df2_copy = df2.copy()
    df2_copy['frame'] = df2_copy['frame'] - (frame_shift - buffer)
    
    result_df = pd.concat([df1, df2_copy], ignore_index=True)
    return result_df

def parseFramesFromDf(df, start, end):
  filtered_df = df[(df['frame'] >= start) & (df['frame'] <= end)]
  return filtered_df

def getLastFrame(df):
  return df['frame'].max() if not df.empty else 0

def sortDf(df):
  return df.sort_values(by=['frame', 'name'])

def processSongAndMotionIntoClips(wav, vmd):
  df = vmd_ops.getDfFromVMD(VMD_TO_LOAD)
  beatFrames = music_ops.get_beatFrames_from_filepath(SONG_TO_LOAD)

  tail = 0
  for i, beatFrame in enumerate(beatFrames):
    if i % 16 == 0:
      newDf = pd.DataFrame()
      newDf = df_ops.appendFrames(newDf, df_ops.parseFramesFromDf(df, tail, beatFrame))
      print(tail, beatFrame, beatFrame - tail)
      vmd_ops.saveDfToVmdFile(newDf, SAVE_FOLDER + SAVE_FILENAME + str(int(i / 16)) + '.vmd')
      tail = beatFrame

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
  
def addInterpolationsToEachFrame(df):
  df = df_ops.sortDf(df)
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
      if currentFrameNumber >= nextBoneList[missingBone]['frameNumber']:
        nextBoneOccurenceValues = getNextBoneOccurence(df, missingBone, currentFrameNumber)
        nextBoneList[missingBone] = nextBoneOccurenceValues if nextBoneOccurenceValues is not None else nextBoneList[missingBone]
      newFrames.append([
        currentFrameNumber,
        missingBone,
        nextBoneList[missingBone]['position'],
        nextBoneList[missingBone]['rotation']
      ])
      #print(currentFrameNumber, missingBone, nextBoneList[missingBone]['position'], lastBoneList[missingBone]['position'])
  newFramesDf = pd.DataFrame(newFrames, columns=['frame', 'name', 'position', 'rotation'])
  interpolated_df = df.copy()
  interpolated_df = pd.concat([df, newFramesDf])
  interpolated_df = df_ops.sortDf(interpolated_df)
  return interpolated_df