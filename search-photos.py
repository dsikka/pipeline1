import json
import boto3

from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection

print('This is another random update 2')
# TODO: Put everything in try/except
def lambda_handler(event, context):
    current_data = event['currentIntent']['slots']
    kwA = current_data['KeywordA']
    kwB = current_data['KeywordB']
    
    
    if kwA is None and kwB is None:
        response = {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                  "contentType": "SSML",
                  "content": "Invalid query. Please try again"
                }
            }
        }
        return response
    else:
        host = 'vpc-photos-rr7lchatfncvoutiu2htehfqjq.us-east-1.es.amazonaws.com'
        region = 'us-east-1'
        service = 'es'
        
        credentials = boto3.Session().get_credentials()
        access_key = credentials.access_key
        secret_key = credentials.secret_key
        token = credentials.token
     
        auth = AWSRequestsAuth(aws_access_key=access_key,
                               aws_secret_access_key=secret_key,
                               aws_token=token,
                               aws_host=host,
                               aws_region=region,
                               aws_service=service)
    
        es = Elasticsearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection 
        )
        if kwA[-1] == 's':
            kwA = kwA[:-1]

        kwA_query = es.search(index = 'photos', body = {"from" : 0, "size" : 100, "query": { "match": { "labels":  kwA}}})
        all_hits  = kwA_query['hits']['hits']
        image_names = []
        for hit in all_hits:
            image_names.append(hit['_source']['objectKey'])

        if len(image_names) == 0:
            kwA = kwA + 's'
            kwA_query = es.search(index = 'photos', body = {"from" : 0, "size" : 100, "query": { "match": { "labels":  kwA}}})
            all_hits  = kwA_query['hits']['hits']
            for hit in all_hits:
                image_names.append(hit['_source']['objectKey'])
            
        if kwB is not None:
            if kwB[-1] == 's':
                kwB = kwB[:-1]
            kwB_query = es.search(index = 'photos', body = {"from" : 0, "size" : 100, "query": { "match": { "labels":  kwB}}})
            qB_hits = kwB_query['hits']['hits']
            for hit in qB_hits:
                image_names.append(hit['_source']['objectKey'])

            if len(qB_hits) == 0:
                kwB = kwB + 's'
                kwB_query = es.search(index = 'photos', body = {"from" : 0, "size" : 100, "query": { "match": { "labels":  kwB}}})
                qB_hits = kwB_query['hits']['hits']
                for hit in qB_hits:
                    image_names.append(hit['_source']['objectKey'])

        
        image_names = list(set(image_names))
        print(image_names)
    response = {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
              "contentType": "SSML",
              "content": str(image_names)
            }
        }
    
    }
    return response