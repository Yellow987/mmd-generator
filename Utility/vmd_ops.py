import pymeshio.vmd.reader
import pymeshio.vmd.writer
import pandas as pd
import os 

def createFolderIfNotExists(folder_path):
  if not os.path.exists(folder_path):
    os.makedirs(folder_path)

def loadVmdFromFile(filename):
  vmd = pymeshio.vmd.reader.read_from_file(filename)
  return vmd

def saveVmdToFile(filename, vmd):
  createFolderIfNotExists(os.path.dirname(filename))
  with open(filename, 'wb') as file:
    pymeshio.vmd.writer.write(file, vmd)

def convertDataFrameToVMD(originalVMD, df):
    class Motion:
      __slots__=['name', 'frame', 'pos', 'q', 'complement']
      def __init__(self, frame, name, pos, q, complement):
          self.frame = frame
          self.name = name
          self.pos = pos
          self.q = q
          self.complement = complement

    motionArray = []
    for index, row in df.iterrows():
        frame = row['frame']
        name = row['name'].encode('shift-jis')
        position = row['position']
        rotation = row['rotation']
        complement = row['complement']

        motion = Motion(frame, name, position, rotation, complement)
        motionArray.append(motion)

    originalVMD.motions = motionArray
    return originalVMD

def convertVMDToDataFrame(vmd):
  boneFrames = [{'frame': motion.frame, 'name': motion.name.decode("shift-jis", errors="ignore"), 'position': motion.pos, 'rotation': motion.q, 'complement': motion.complement} for motion in vmd.motions]
  df = pd.DataFrame(boneFrames)
  return df

def initEmptyVmd():
  motion = pymeshio.vmd.Motion()
  return motion

def getDfFromVMD(VMD_FILENAME):
  return convertVMDToDataFrame(loadVmdFromFile(VMD_FILENAME))

def saveDfToVmdFile(df, SAVE_FILENAME):
  newVmd = convertDataFrameToVMD(initEmptyVmd(), df)
  saveVmdToFile(SAVE_FILENAME, newVmd)

def getValidBoneNames():
  return [
  "全ての親",
  "グルーブ",
  "センター",
  "上半身",
  "首",
  "頭",
  "左目",
  "下半身",
  "左肩",
  "左腕",
  "左ひじ",
  "左手首",
  "左親指１",
  "左親指２",
  "左人指１",
  "左人指２",
  "左人指３",
  "左中指１",
  "左中指２",
  "左中指３",
  "左薬指１",
  "左薬指２",
  "左薬指３",
  "左小指１",
  "左小指２",
  "左小指３",
  "左足",
  "左ひざ",
  "左足首",
  "両目",
    "左足ＩＫ",
  "左つま先ＩＫ",
  "右足ＩＫ",
  "右つま先ＩＫ",
  "右目",
  "右肩",
  "右腕",
  "右ひじ",
  "右手首",
  "右親指１",
  "右親指２",
  "右人指１",
  "右人指２",
  "右人指３",
  "右中指１",
  "右中指２",
  "右中指３",
  "右薬指１",
  "右薬指２",
  "右薬指３",
  "右小指１",
  "右小指２",
  "右小指３",
  "右足",
  "右ひざ",
  "右足首"
]

def filterDataframeForValidBoneNames(df):
  validBoneNames = getValidBoneNames()
  return df[df['name'].isin(validBoneNames)]

def findInvalidDuplicateNames(df):
  validBoneNames = getValidBoneNames()
  
  # Count the occurrences of each name
  name_counts = df['name'].value_counts()
  
  # Filter for names that occur more than once
  duplicate_names = name_counts[name_counts > 1].index.tolist()
  
  # Filter out valid bone names
  invalid_duplicate_names = [name for name in duplicate_names if name not in validBoneNames]
  
  return invalid_duplicate_names