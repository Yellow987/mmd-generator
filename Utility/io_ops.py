import os
from concurrent.futures import ProcessPoolExecutor

def apply_func_to_inputData(func, foldername: str):
  """
  Apply a given function to all .wav and .vmd files in each subfolder of a given folder.

  Parameters:
      func (function): The function to apply to the files.
      foldername (str): The name of the folder to search in.

  Returns:
      None
  """
  for root, dirs, files in os.walk(foldername):
    if root == foldername:
      continue
    wav, vmd, feather = "", "", None
    for file in files:
      if file.endswith(".wav"):
        filepath = os.path.join(root, file)
        wav = filepath
      if file.endswith(".vmd"):
        filepath = os.path.join(root, file)
        vmd = filepath
      if file.endswith(".feather"):
        filepath = os.path.join(root, file)
        feather = filepath
    if wav == "" and vmd == "":
      print("MISSING FILE FOR " + root)

    folderName = root.split("\\")[-1]
    func(wav=wav, vmd=vmd, folderName=folderName, feather=feather)


def worker(root, files, func):
  wav, vmd, feather = "", "", None
  for file in files:
    if file.endswith(".wav"):
      filepath = os.path.join(root, file)
      wav = filepath
    if file.endswith(".vmd"):
      filepath = os.path.join(root, file)
      vmd = filepath
    if file.endswith(".feather"):
      filepath = os.path.join(root, file)
      feather = filepath
  if wav == "" and vmd == "":
    print(f"MISSING FILE FOR {root}")

  folderName = root.split("\\")[-1]
  func(wav=wav, vmd=vmd, folderName=folderName, feather=feather)

def apply_func_to_inputData_multiThreaded(func, foldername: str, num_threads: int):
  """
  Apply a given function to all .wav and .vmd files in each subfolder of a given folder.

  Parameters:
      func (function): The function to apply to the files.
      foldername (str): The name of the folder to search in.
      num_threads (int): The number of processes to use for parallel processing.

  Returns:
      None
  """
  tasks = []
  with ProcessPoolExecutor(max_workers=num_threads) as executor:
    for root, dirs, files in os.walk(foldername):
      if root == foldername:
        continue
      tasks.append(executor.submit(worker, root, files, func))

  for future in tasks:
    future.result()