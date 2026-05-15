Music Subscription Web Application - AWS Deployment Guide

Project: COSC2626 Cloud Computing Assignment 2
Group: Group 18

1. Project Overview
This project is a cloud-based music subscription web application deployed using AWS services. The application allows users to register, log in, search music, subscribe to songs, view subscriptions, and remove subscribed songs.

The application has been implemented using three backend deployment models:
1. Amazon EC2 backend
2. Amazon ECS/Fargate backend
3. AWS Lambda with API Gateway backend

The frontend is hosted separately using Amazon S3 static website hosting.

2. Main AWS Services Used
- Amazon S3: Frontend hosting and artist image storage
- Amazon DynamoDB: login, music, and subscriptions tables
- Amazon EC2: Flask backend deployment
- Amazon ECS/Fargate: Containerised Flask backend deployment
- Amazon ECR: Docker image storage for ECS
- AWS Lambda: Serverless backend logic
- Amazon API Gateway: REST API routing for Lambda
- IAM LabRole: AWS service permissions
- CloudWatch: Logs and monitoring

3. Frontend
Frontend files are located in the frontend folder:
- index.html
- register.html
- main.html
- app.js
- styles.css

The frontend is hosted in the S3 bucket:
music-app-images-group18

To access the frontend, open the S3 static website endpoint:
http://music-app-images-group18.s3-website-us-east-1.amazonaws.com

4. Backend Option 1 - EC2
EC2 backend files are located in:
ec2-backend/

Files:
- app.py
- requirements.txt

To run the EC2 backend:

1. Start the EC2 instance from the AWS console.
2. Connect using EC2 Instance Connect.
3. Run:

cd ~/music-backend
sudo python3 app.py

4. Open the EC2 public IPv4 address in browser:

http://EC2_PUBLIC_IP

Expected output:
{"message":"EC2 Flask backend is running"}

If using EC2 with the frontend, update app.js:

const API_BASE_URL = "http://EC2_PUBLIC_IP";

Then upload app.js to S3.

5. Backend Option 2 - ECS/Fargate
ECS backend files are located in:
ecs-backend/

Files:
- app.py
- Dockerfile
- requirements.txt

To rebuild and push the ECS backend image:

cd ~/ecs-backend

docker build -t music-app-ecs-backend:v5 .

docker tag music-app-ecs-backend:v5 908414500515.dkr.ecr.us-east-1.amazonaws.com/music-app-ecs-backend:v5

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 908414500515.dkr.ecr.us-east-1.amazonaws.com

docker push 908414500515.dkr.ecr.us-east-1.amazonaws.com/music-app-ecs-backend:v5

Then update the ECS service to use image tag v5.

ECS application URL example:
https://mu-5cd4137b7ef64bddaa570a12c9c2ac25.ecs.us-east-1.on.aws

Expected output:
{"message":"ECS Flask backend is running"}

If using ECS with frontend, update app.js:

const API_BASE_URL = "https://mu-5cd4137b7ef64bddaa570a12c9c2ac25.ecs.us-east-1.on.aws";

Then upload app.js to S3.

6. Backend Option 3 - Lambda and API Gateway
Lambda backend files are located in:
lambda-backend/

File:
- lambda_function.py

API Gateway exposes the following REST endpoints:
- POST /login
- POST /register
- GET /music
- GET /subscriptions
- POST /subscriptions
- DELETE /subscriptions

To use the serverless backend, copy the API Gateway invoke URL from:

API Gateway → Stages → prod → Invoke URL

Then update app.js:

const API_BASE_URL = "https://API_ID.execute-api.us-east-1.amazonaws.com/prod";

Upload app.js to S3 and refresh the frontend.

This is the recommended final backend because the API Gateway URL is stable and does not depend on EC2 or ECS public IP changes.

7. DynamoDB Tables
The application uses three DynamoDB tables:

1. login
- Partition key: email
- Stores user email, username, and password

2. music
- Partition key: artist
- Sort key: song_id
- Stores title, artist, album, year, and image reference
- Includes title-index GSI
- Includes album-index LSI

3. subscriptions
- Partition key: email
- Sort key: song_id
- Stores songs subscribed by each user

8. S3 Storage
The S3 bucket stores:
- frontend files
- artist images

Bucket:
music-app-images-group18

Frontend files:
- index.html
- register.html
- main.html
- app.js
- styles.css

9. Main Application Features
- User registration
- Duplicate email validation
- Duplicate username validation
- Login validation
- Music search
- Partial and case-insensitive search
- Subscribe to song
- Prevent duplicate subscription
- Remove subscribed song
- Logout
- RESTful backend API using GET, POST, and DELETE

10. Testing Instructions
To test the application:

1. Open the S3 frontend URL.
2. Register a new user.
3. Log in using the registered account.
4. Search music by artist/title/album/year.
5. Subscribe to a song.
6. Try subscribing to the same song again.
   Expected message:
   Song already subscribed
7. Go to My Subscriptions.
8. Remove a subscribed song.
9. Log out.

11. Backend Switching
The frontend uses the API_BASE_URL variable inside app.js.

To test EC2:
const API_BASE_URL = "http://EC2_PUBLIC_IP";

To test ECS:
const API_BASE_URL = "https://ECS_APPLICATION_URL";

To test Lambda/API Gateway:
const API_BASE_URL = "https://API_ID.execute-api.us-east-1.amazonaws.com/prod";

After changing app.js, upload it to S3 and hard refresh the browser using:
CTRL + SHIFT + R

12. Notes
- EC2 public IP changes after stopping and starting the instance.
- ECS Application URL is more stable than EC2 public IP.
- API Gateway invoke URL is the most stable backend endpoint.
- The final recommended architecture is:
  S3 Frontend → API Gateway → Lambda → DynamoDB and S3

13. Submission Contents
The zip submission contains:
- frontend/
- ec2-backend/
- ecs-backend/
- lambda-backend/
- scripts/
- report/
- screenshots/
- README.txt
