from Utility import df_ops, music_ops, vmd_ops, io_ops
import pandas as pd

VMD_TO_LOAD = 'data/PV311_LIVE_MIK_00.vmd'
SAVE_FOLDER = 'data/generated/SuperDuper/'
SAVE_FILENAME= 'motion'
SONG_TO_LOAD = 'data/SuperDuper/song3_sduper [1].wav'

INPUT_DATA_FOLDER = 'inputData'

if __name__ == "__main__":
  io_ops.apply_func_to_inputData

  # Example usage
  def print_file_name(wav, vmd):
      print(f"vmd: {vmd}, wav: {wav}")

  io_ops.apply_func_to_inputData(print_file_name, INPUT_DATA_FOLDER)
