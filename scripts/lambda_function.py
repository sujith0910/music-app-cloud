import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

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

    email = data.get("email", "")
    password = data.get("password", "")

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

    email = data.get("email", "")
    user_name = data.get("user_name", "")
    password = data.get("password", "")

    existing_user = login_table.get_item(Key={"email": email})

    if "Item" in existing_user:
        return response(409, {"message": "The email already exists"})

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

    title = params.get("title", "")
    artist = params.get("artist", "")
    year = params.get("year", "")
    album = params.get("album", "")

    # Artist + Album → Use LSI
    if artist and album:

        result = music_table.query(
            IndexName="album-index",
            KeyConditionExpression=
                Key("artist").eq(artist) &
                Key("album").eq(album)
        )

    # Title only → Use GSI
    elif title and not artist and not year and not album:

        result = music_table.query(
            IndexName="title-index",
            KeyConditionExpression=Key("title").eq(title)
        )

    # Artist only → Main table query
    elif artist and not title and not year and not album:

        result = music_table.query(
            KeyConditionExpression=Key("artist").eq(artist)
        )

    # Artist + Year → Query + Filter
    elif artist and year:

        result = music_table.query(
            KeyConditionExpression=Key("artist").eq(artist),
            FilterExpression=Attr("year").eq(year)
        )

    # Other searches → Scan
    else:

        filter_expression = None

        if title:
            filter_expression = Attr("title").eq(title)

        if year:
            if filter_expression:
                filter_expression = filter_expression & Attr("year").eq(year)
            else:
                filter_expression = Attr("year").eq(year)

        if album:
            if filter_expression:
                filter_expression = filter_expression & Attr("album").eq(album)
            else:
                filter_expression = Attr("album").eq(album)

        if artist:
            if filter_expression:
                filter_expression = filter_expression & Attr("artist").eq(artist)
            else:
                filter_expression = Attr("artist").eq(artist)

        if not filter_expression:
            return response(400, {
                "message": "At least one field must be completed"
            })

        result = music_table.scan(
            FilterExpression=filter_expression
        )

    items = result.get("Items", [])

    if len(items) == 0:
        return response(404, {
            "message": "No result is retrieved. Please query again"
        })

    return response(200, items)


def get_subscriptions(event):
    params = event.get("queryStringParameters") or {}
    email = params.get("email", "")

    result = subscription_table.query(
        KeyConditionExpression=Key("email").eq(email)
    )

    return response(200, result.get("Items", []))


def add_subscription(event):
    data = json.loads(event.get("body", "{}"))

    subscription_table.put_item(Item=data)

    return response(201, {"message": "Subscription added"})


def remove_subscription(event):
    data = json.loads(event.get("body", "{}"))

    email = data.get("email", "")
    song_id = data.get("song_id", "")

    subscription_table.delete_item(
        Key={
            "email": email,
            "song_id": song_id
        }
    )

    return response(200, {"message": "Subscription removed"})