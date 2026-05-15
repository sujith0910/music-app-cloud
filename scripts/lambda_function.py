import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

login_table = dynamodb.Table("login")
music_table = dynamodb.Table("music")
subscription_table = dynamodb.Table("subscriptions")


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    method = event.get("httpMethod", "")
    path = event.get("path", "")

    if method == "OPTIONS":
        return response(200, {"message": "CORS OK"})

    if path == "/login" and method == "POST":
        return login_user(event)

    if path == "/register" and method == "POST":
        return register_user(event)

    if path == "/music" and method == "GET":
        return query_music(event)

    if path == "/subscriptions" and method == "GET":
        return get_subscriptions(event)

    if path == "/subscriptions" and method == "POST":
        return add_subscription(event)

    if path == "/subscriptions" and method == "DELETE":
        return remove_subscription(event)

    return response(404, {"message": "Route not found"})


def login_user(event):
    data = json.loads(event.get("body", "{}"))

    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    result = login_table.get_item(Key={"email": email})
    user = result.get("Item")

    if user and user.get("password") == password:
        return response(200, {
            "message": "Login successful",
            "email": user["email"],
            "user_name": user["user_name"]
        })

    return response(401, {"message": "email or password is invalid"})


def register_user(event):
    data = json.loads(event.get("body", "{}"))

    email = data.get("email", "").strip()
    user_name = data.get("user_name", "").strip()
    password = data.get("password", "").strip()

    if not email or not user_name or not password:
        return response(400, {"message": "All fields are required"})

    if "@" not in email:
        return response(400, {"message": "Please enter a valid email address"})

    existing_email = login_table.get_item(Key={"email": email})

    if "Item" in existing_email:
        return response(409, {"message": "Email already exists. Please use another email"})

    users = login_table.scan()
    for user in users.get("Items", []):
        if user.get("user_name", "").lower().strip() == user_name.lower():
            return response(409, {"message": "Username already exists. Please try another username"})

    login_table.put_item(
        Item={
            "email": email,
            "user_name": user_name,
            "password": password
        }
    )

    return response(201, {"message": "Registration successful"})


def query_music(event):
    params = event.get("queryStringParameters") or {}

    title = params.get("title", "").strip().lower()
    artist = params.get("artist", "").strip().lower()
    year = params.get("year", "").strip()
    album = params.get("album", "").strip().lower()

    if not title and not artist and not year and not album:
        return response(400, {"message": "At least one field must be completed"})

    result = music_table.scan()
    songs = result.get("Items", [])

    matched_songs = []

    for song in songs:
        song_title = song.get("title", "").lower().strip()
        song_artist = song.get("artist", "").lower().strip()
        song_album = song.get("album", "").lower().strip()
        song_year = str(song.get("year", "")).strip()

        title_match = True
        artist_match = True
        album_match = True
        year_match = True

        if title:
            title_match = title in song_title

        if artist:
            artist_match = artist in song_artist

        if album:
            album_match = album in song_album

        if year:
            year_match = year == song_year

        if title_match and artist_match and album_match and year_match:
            matched_songs.append(song)

    if len(matched_songs) == 0:
        return response(404, {"message": "No result is retrieved. Please query again"})

    return response(200, matched_songs)


def get_subscriptions(event):
    params = event.get("queryStringParameters") or {}
    email = params.get("email", "").strip()

    result = subscription_table.query(
        KeyConditionExpression=Key("email").eq(email)
    )

    return response(200, result.get("Items", []))


def add_subscription(event):
    data = json.loads(event.get("body", "{}"))

    email = data.get("email", "").strip()
    song_id = data.get("song_id", "").strip()

    existing_subscription = subscription_table.get_item(
        Key={
            "email": email,
            "song_id": song_id
        }
    )

    if "Item" in existing_subscription:
        return response(409, {"message": "Song already subscribed"})

    subscription_table.put_item(Item=data)

    return response(201, {"message": "Subscription added"})


def remove_subscription(event):
    data = json.loads(event.get("body", "{}"))

    email = data.get("email", "").strip()
    song_id = data.get("song_id", "").strip()

    subscription_table.delete_item(
        Key={
            "email": email,
            "song_id": song_id
        }
    )

    return response(200, {"message": "Subscription removed"})