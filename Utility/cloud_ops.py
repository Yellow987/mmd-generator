import pinecone      
from dotenv import load_dotenv
import os
import itertools
from Utility import df_ops
load_dotenv()

def initPinecone():
  pinecone.init(      
    api_key=os.getenv('PINECONE_API_KEY'),
    environment='gcp-starter'      
  )
  return pinecone

def getPineconeIndexStats(pinecone, index):
  print(pinecone.describe_index(index))

class FrameForVectorization:
  def __init__(self, df):
    self.df = df
    self.core_bone_names = self.getCoreBoneNames()
    self.vector = []

    for bone_name, attributes in self.core_bone_names.items():
      position = self.df[self.df['name'] == bone_name]['position'].values[0]
      rotation = self.df[self.df['name'] == bone_name]['rotation'].values[0]
      if 'position_weight' in attributes:
        position_weight = attributes['position_weight']
        self.vector.append(position.x * position_weight) 
        self.vector.append(position.y * position_weight)
        self.vector.append(position.z * position_weight)
      rotation_weight = attributes['rotation_weight']
      self.vector.append(rotation.x * rotation_weight)
      self.vector.append(rotation.y * rotation_weight)
      self.vector.append(rotation.z * rotation_weight)
      self.vector.append(rotation.w * rotation_weight)

  @staticmethod
  def getCoreBoneNames():
    return {
      "センター": {'rotation_weight': 3, 'position_weight': 1},
      "上半身": {'rotation_weight': 3},
      "上半身2": {'rotation_weight': 3},
      "首": {'rotation_weight': 1},
      "頭": {'rotation_weight': 1},
      "下半身": {'rotation_weight': 3},
      "左肩": {'rotation_weight': 1},
      "左腕": {'rotation_weight': 1},
      "左ひじ": {'rotation_weight': 1},
      "左足": {'rotation_weight': 1},
      #"左ひざ": {'rotation_weight': 1},
      #"左足首": {'rotation_weight': 1},
      "左足ＩＫ": {'rotation_weight': 1, 'position_weight': 1},
      "右足ＩＫ": {'rotation_weight': 1, 'position_weight': 1},
      "右肩": {'rotation_weight': 1},
      "右腕": {'rotation_weight': 1},
      "右ひじ": {'rotation_weight': 1},
      "右足": {'rotation_weight': 1},
      #"右ひざ": {'rotation_weight': 1},
      #"右足首": {'rotation_weight': 1},
      "右腕捩": {'rotation_weight': 1},
      "左腕捩": {'rotation_weight': 1}
    }

def vectorizeFrame(df, frameNumber, animationName):
  df_frame = df[df['frame'] == frameNumber]

  vectorId = animationName + "-" + str(frameNumber)
  frameForVectorization = FrameForVectorization(df_frame)
  metaData = {
    'animationName': animationName,
    'frameNumber': frameNumber
  }
  vector = (vectorId, frameForVectorization.vector, metaData)
  return vector

def chunks(iterable, batch_size=100):
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))

def upsertDfAnimation(pinecone, df, animationName):
  lastFrame = df_ops.getLastFrame(df)

  vectorsOfFrames = []
  for currentFrameNumber in range(0, lastFrame + 1):
    vectorsOfFrames.append(vectorizeFrame(df, currentFrameNumber, animationName))
  index = pinecone.Index('')
  
  for ids_vectors_chunk in chunks(vectorsOfFrames, batch_size=100):
    index.upsert(vectors=ids_vectors_chunk)