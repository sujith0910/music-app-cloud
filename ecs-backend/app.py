from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)
CORS(app)

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

login_table = dynamodb.Table("login")
music_table = dynamodb.Table("music")
subscription_table = dynamodb.Table("subscriptions")


@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()

    email = data.get("email", "")
    password = data.get("password", "")

    result = login_table.get_item(Key={"email": email})
    user = result.get("Item")

    if user and user.get("password") == password:
        return jsonify({
            "message": "Login successful",
            "email": user["email"],
            "user_name": user["user_name"]
        }), 200

    return jsonify({"message": "email or password is invalid"}), 401


@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()

    email = data.get("email", "").strip()
    user_name = data.get("user_name", "").strip()
    password = data.get("password", "").strip()

    if not email or not user_name or not password:
        return jsonify({"message": "All fields are required"}), 400

    if "@" not in email:
        return jsonify({"message": "Please enter a valid email address"}), 400

    existing_email = login_table.get_item(Key={"email": email})

    if "Item" in existing_email:
        return jsonify({"message": "Email already exists. Please use another email"}), 409

    username_check = login_table.scan(
        FilterExpression=Attr("user_name").eq(user_name)
    )

    if len(username_check.get("Items", [])) > 0:
        return jsonify({"message": "Username already exists. Please try another username"}), 409

    login_table.put_item(Item={
        "email": email,
        "user_name": user_name,
        "password": password
    })

    return jsonify({"message": "Registration successful"}), 201


@app.route("/music", methods=["GET"])
def query_music():
    title = request.args.get("title", "").strip().lower()
    artist = request.args.get("artist", "").strip().lower()
    year = request.args.get("year", "").strip()
    album = request.args.get("album", "").strip().lower()

    if not title and not artist and not year and not album:
        return jsonify({"message": "At least one field must be completed"}), 400

    result = music_table.scan()
    songs = result.get("Items", [])

    matched_songs = []

    for song in songs:
        song_title = song.get("title", "").lower().strip()
        song_artist = song.get("artist", "").lower().strip()
        song_album = song.get("album", "").lower().strip()
        song_year = song.get("year", "").strip()

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
        return jsonify({"message": "No result is retrieved. Please query again"}), 404

    return jsonify(matched_songs), 200


@app.route("/subscriptions", methods=["GET"])
def get_subscriptions():
    email = request.args.get("email", "")

    result = subscription_table.query(
        KeyConditionExpression=Key("email").eq(email)
    )

    return jsonify(result.get("Items", [])), 200


@app.route("/subscriptions", methods=["POST"])
def add_subscription():
    data = request.get_json()
    subscription_table.put_item(Item=data)

    return jsonify({"message": "Subscription added"}), 201


@app.route("/subscriptions", methods=["DELETE"])
def remove_subscription():
    data = request.get_json()

    email = data.get("email", "")
    song_id = data.get("song_id", "")

    subscription_table.delete_item(
        Key={
            "email": email,
            "song_id": song_id
        }
    )

    return jsonify({"message": "Subscription removed"}), 200


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "ECS Flask backend is running"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)