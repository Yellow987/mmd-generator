import os

def apply_func_to_inputData(func, foldername: str):
  """
  Apply a given function to all .wav and .vmd files in each subfolder of a given folder.

  Parameters:
      func (function): The function to apply to the files.
      foldername (str): The name of the folder to search in.

  Returns:
      None
  """
  print(foldername)
  for root, dirs, files in os.walk(foldername):
    wav, vmd = "", ""
    for file in files:
      if file.endswith(".wav"):
        filepath = os.path.join(root, file)
        wav = filepath
      if file.endswith(".vmd"):
        filepath = os.path.join(root, file)
        vmd = filepath
    if wav == "" and vmd == "":
      print("MISSING FILE FOR " + root)

    func(wav, vmd)