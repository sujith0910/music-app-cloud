import json
import boto3
import requests

# AWS setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')

# DynamoDB table
music_table = dynamodb.Table('music')

# S3 bucket
bucket_name = "music-app-images-group18"

# Open JSON dataset
with open('../data/2026a2_songs.json', 'r') as file:
    songs_data = json.load(file)

songs = songs_data['songs']

# Track uploaded images to avoid duplicate uploads
uploaded_images = set()

for song in songs:

    title = song['title']
    artist = song['artist']
    year = song['year']
    album = song['album']
    image_url = song['img_url']

    # Generate unique sort key
    song_id = f"{title}#{album}#{year}"

    # Extract image filename
    image_name = image_url.split("/")[-1]

    # Upload image only once
    if image_name not in uploaded_images:

        response = requests.get(image_url)

        s3.put_object(
            Bucket=bucket_name,
            Key=image_name,
            Body=response.content,
            ContentType='image/jpeg'
        )

        uploaded_images.add(image_name)

    # Insert item into DynamoDB
    music_table.put_item(
        Item={
            'artist': artist,
            'song_id': song_id,
            'title': title,
            'year': year,
            'album': album,
            'image_url': image_name
        }
    )

print("Music table and S3 image upload completed successfully.")