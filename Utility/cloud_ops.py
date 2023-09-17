from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
import json


def create_client(useLocalhost=False):
  host = 'xlyaudsjhfthxpu0luf3.us-east-1.aoss.amazonaws.com'
  port = 443  # port for HTTPS
  if useLocalhost:
    host = 'localhost'
    port = 9200

  region = 'us-east-1'  # e.g. us-east-1

  service = 'aoss'
  credentials = boto3.Session().get_credentials()
  auth = AWSV4SignerAuth(credentials, region, service)

  # create an opensearch client and use the request-signer
  client = OpenSearch(
      hosts=[{'host': host, 'port': port}],
      http_auth=auth,
      use_ssl=True,
      verify_certs=True,
      connection_class=RequestsHttpConnection,
      pool_maxsize=20,
  )

  return client

settingsSettings = {
  "settings": {
    "index.knn": True
  }
}
settingsBody = {
  "mappings": {
    "properties": {
      "frame": {
        "type": "knn_vector",
        "dimension": 3
      },
      "animation-name": {
        "type": "text"
      },
      "frame-number": {
        "type": "int"
      }
    }
  }
}


def create_index(client, index_name, settings):
  create_response = client.indices.create(
    index='frames-index',
    body=settings
  )
  
  create_response = client.indices.create(
    index=index_name,
    body=settings
  )
  print('\nCreating index:')
  print(create_response)


def delete_index(client, index_name):
  # delete an index
  delete_response = client.indices.delete(index=index_name)
  print('\nDeleting index:')
  print(delete_response)

def get_indices(client):
  # get all indices
  indices = client.indices.get('*')
  print('\nIndices:')
  print(json.dumps(indices, indent=2))

def get_index_mappings(client, index_name):
  # get mappings for an index
  mappings = client.indices.get_mapping(index=index_name)
  print('\nMappings:')
  print(json.dumps(mappings, indent=2))

def update_index_mapping_body(client, index_name, settings):
  update_response = client.indices.put_mapping(
    index=index_name,
    body=settings
  )
  print('\nUpdating index mappings:')
  print(update_response)

#create_index(client, 'frames-index', settingsSettings.update(settingsBody))
#get_indices(client)
#delete_index(client, 'frame-index')