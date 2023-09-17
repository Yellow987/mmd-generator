from Utility import df_ops, music_ops, vmd_ops, io_ops
import pandas as pd
import os

VMD_TO_LOAD = 'inputDataVariety/Last Christmas/motion.vmd'
SAVE_FOLDER = 'data/'
SAVE_FILENAME= 'LastChristmas'
SONG_TO_LOAD = 'data/SuperDuper/song3_sduper [1].wav'
INPUT_DATA_FOLDER = 'inputDataVariety'

if __name__ == "__main__":
  io_ops.apply_func_to_inputData

  def print_file_name(wav, vmd):
    df = vmd_ops.convertVMDToDataFrame(vmd_ops.loadVmdFromFile(vmd))
    print(vmd_ops.findMissingBoneNames(df))

  #io_ops.apply_func_to_inputData(print_file_name, INPUT_DATA_FOLDER)
  df = vmd_ops.convertVMDToDataFrame(vmd_ops.loadVmdFromFile(VMD_TO_LOAD))
  df = vmd_ops.filterDataframeForCoreBoneNames(df)
  vmd_ops.saveDfToVmdFile(df, SAVE_FOLDER + SAVE_FILENAME + '.vmd')