import json
import boto3
from datetime import datetime
import os
import requests

from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection

bucket = 'index-photos'
#photo_name = 'dog.jpg'

def lambda_handler(event, context):
    # TODO implement)
    print(event)
    photo_name = event['Records'][0]['s3']['object']['key']
    client=boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object':
        {'Bucket':bucket,'Name':photo_name}},
        MaxLabels=10,
        MinConfidence= 75)
    
    labels = []
    
    for label in response['Labels']:
        labels.append(label['Name'])
    
    print('Labels found', labels)
    payload = {
        "objectKey": photo_name,
        "bucket": bucket,
        "createdTimestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "labels": labels
    }
    
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
    #out = es.search(index = 'photos', body = {"from" : 0, "size" : 100, "query": { "match_all": {}}})
    #es.indices.delete(index='photos', ignore=[400, 404])
    es.index(index="photos", doc_type="_doc", body=payload)
    # print('RESPONSE', out)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }