from Utility import df_ops, music_ops, vmd_ops
import pandas as pd

VMD_TO_LOAD = 'data/PV311_LIVE_MIK_00.vmd'
SAVE_FILENAME = 'saved.vmd'

if __name__ == "__main__":
  df = vmd_ops.getDfFromVMD(VMD_TO_LOAD)
  df = df_ops.parseFramesFromDf(df, 500, 1000)
  newDf = pd.DataFrame()
  newDf = df_ops.appendFrames(newDf, df)
  vmd_ops.saveDfToVmdFile(newDf, SAVE_FILENAME)
  
  # originalVMD = vmd_ops.loadVMD(VMD_TO_LOAD)
  # df = vmd_ops.convertVMDToDataFrame(originalVMD)
  # vmd_ops.convertDataFrameToVMD(vmd_ops.initEmptyVmd(), df)
  # vmd_ops.saveToVMD(SAVE_FILENAME, originalVMD)