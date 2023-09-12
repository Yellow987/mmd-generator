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