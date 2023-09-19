import pandas as pd

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