import json
import boto3
import requests

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

login_table = dynamodb.Table('login')

users = [
    {
        "email": "s4151134@student.rmit.edu.au",
        "user_name": "SujithSubramanian0",
        "password": "012345"
    },
    {
        "email": "s4162176@student.rmit.edu.au",
        "user_name": "SasidharanRaveendiran1",
        "password": "123456"
    },
    {
        "email": "s4152859@student.rmit.edu.au",
        "user_name": "TamilSattai2",
        "password": "234567"
    },
    {
        "email": "s3987653@student.rmit.edu.au",
        "user_name": "RahulVerma3",
        "password": "345678"
    },
    {
        "email": "s3987654@student.rmit.edu.au",
        "user_name": "AnanyaReddy4",
        "password": "456789"
    },
    {
        "email": "s3987655@student.rmit.edu.au",
        "user_name": "KaranPatel5",
        "password": "567890"
    },
    {
        "email": "s3987656@student.rmit.edu.au",
        "user_name": "MeeraIyer6",
        "password": "678901"
    },
    {
        "email": "s3987657@student.rmit.edu.au",
        "user_name": "ArjunNair7",
        "password": "789012"
    },
    {
        "email": "s3987658@student.rmit.edu.au",
        "user_name": "NehaKapoor8",
        "password": "890123"
    },
    {
        "email": "s3987659@student.rmit.edu.au",
        "user_name": "VikramDas9",
        "password": "901234"
    }
]

for user in users:
    login_table.put_item(Item=user)

print("Login table users inserted successfully.")