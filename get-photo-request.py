import json
import pprint
import boto3

def lambda_handler(event, context):
    print(event)
    client = boto3.client('lex-runtime')

    input = event["queryStringParameters"]["query_string"]
    print(input)
    response = client.post_text(
        botName = 'search_bot',
        botAlias = 'bot_version_one',
        userId = 'lchu',
        inputText = input
    )
    
    if response['message'] == "[]":
        msg = {
            'headers': { 'Access-Control-Allow-Origin': '*'}, 
            'message': {"pics": []} 
        
        }
    else:
        pics = list(map(lambda x: x.strip().strip("'").strip(), response['message'].strip("]").strip("[").split(",")))
        reply = list(f"https://index-photos.s3.amazonaws.com/{el}" for el in pics)
        msg = {
            'headers': { 'Access-Control-Allow-Origin': '*'}, 
            'message': {"pics": reply} 
        
    }
    print(msg)
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            "Access-Control-Allow-Credentials": "true"
        },
        'body': json.dumps(msg)
    }
