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
    unique_count = df['name'].nunique()
    last_folder = os.path.basename(os.path.dirname(vmd))
    print(f"folder {last_folder} has {unique_count} boneNames")

    # Count the occurrences of each name
    name_counts = df['name'].value_counts()

    # Get names that appear only once
    names_only_once = name_counts[name_counts == 1].index.tolist()

    # Filter the DataFrame to only include rows with names that appear once
    df_names_only_once = df[df['name'].isin(names_only_once)]

    # Extract the 'frame' column for these names
    frame_numbers = df_names_only_once['frame']

    print("Names that appear only once:", names_only_once)
    print("Frame numbers for names that appear only once:", frame_numbers.tolist())

  #io_ops.apply_func_to_inputData(print_file_name, INPUT_DATA_FOLDER)
  df = vmd_ops.convertVMDToDataFrame(vmd_ops.loadVmdFromFile(VMD_TO_LOAD))
  print(vmd_ops.findInvalidDuplicateNames(df))
  df = vmd_ops.filterDataframeForValidBoneNames(df)
  vmd_ops.saveDfToVmdFile(df, SAVE_FOLDER + SAVE_FILENAME + '.vmd')