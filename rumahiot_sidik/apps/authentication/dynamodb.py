import boto3
import json
import decimal

# returning DynamoDB client
def dynamodb_client():
    client = boto3.resource('dynamodb', region_name='ap-southeast-1')
    return client

def user_check(email,password):
    client = dynamodb_client()
    table = client.Table(rumahiot_user)
