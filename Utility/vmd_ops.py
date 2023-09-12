import pymeshio.vmd.reader
import pymeshio.vmd.writer
import pandas as pd

def loadVmdFromFile(filename):
  vmd = pymeshio.vmd.reader.read_from_file(filename)
  return vmd

def saveVmdToFile(filename, vmd):
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
  boneFrames = [{'frame': motion.frame, 'name': motion.name.decode("shift-jis"), 'position': motion.pos, 'rotation': motion.q, 'complement': motion.complement} for motion in vmd.motions]
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