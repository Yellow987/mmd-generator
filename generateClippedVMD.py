from Utility import df_ops, music_ops, vmd_ops, io_ops, cloud_ops, interpolate
import pandas as pd
import time 

INPUT_DATA_FOLDER = 'inputData'

def featherizeAll(wav, vmd, folderName, feather):
  print('working on: ' + folderName)
  start_time = time.time()

  #if feather == None:
  df = vmd_ops.getDfFromVmdFileName(vmd)
  df = vmd_ops.filterDataframeForCoreBoneNames(df)
  centered_df = interpolate.normalizePositionsToCenter(df)
  print('centered')
  interpolated_centered_df = interpolate.addInterpolationsToEachFrame(centered_df)
  print('interpolated')
  df_ops.saveDfToFeather(interpolated_centered_df, INPUT_DATA_FOLDER + "\\" + folderName + '\\interpolatedMotion.feather')
  # else:
  #   print('found feather file, skipping interpolation for ' + folderName)
  #   return
    # interpolated_centered_df = df_ops.loadDfFromFeather(feather)
  cloud_ops.upsertDfAnimation(cloud_ops.initPinecone(), interpolated_centered_df, folderName)
  print('completed in ' + str(time.time() - start_time) + ' seconds')

def printFeather(wav, vmd, folderName, feather):
  print(feather)

if __name__ == "__main__":
  io_ops.apply_func_to_inputData(featherizeAll, INPUT_DATA_FOLDER)