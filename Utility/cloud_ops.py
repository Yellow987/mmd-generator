import pinecone      
from dotenv import load_dotenv
import os
load_dotenv()

def initPinecone():
  pinecone.init(      
    api_key=os.getenv('PINECONE_API_KEY'),
    environment='gcp-starter'      
  )
  return pinecone

def getPineconeIndexStats(pinecone, index):
  print(pinecone.describe_index(index))