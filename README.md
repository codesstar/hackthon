# Video Chatbot Backend

This is a Flask-based backend for a video chatbot platform. It supports user registration/login, video storage, video script-based conversation using GPT-4, and the ability to save and retrieve user-specific video collections.

## Features

* User registration & login with JWT authentication
* Video management: add, list, delete
* Chat interface using GPT-4, scoped per video
* Save videos to user collections
* Support for random video fetching & filtering

## Tech Stack

* Python 3
* Flask
* SQLite (local dev)
* JWT Authentication (flask-jwt-extended)
* GPT Integration (openai)

## Folder Structure

project/
├── app.py                Main API routes
├── db.py                 DB init and helper functions
├── utils.py              Password + token helpers
├── chatbot.py            GPT interaction logic with per-video memory
├── chatbot\_app.db        SQLite database file
└── static/               Local video files (served with Python HTTP server)

## How to Run

Install dependencies:

pip install flask flask-jwt-extended flask-cors bcrypt openai

Start backend:

python app.py

(Optional) Serve video files:

cd static/
python3 -m http.server 8000

## Testing with curl or Apifox

Use /register, /login, and then authenticated routes like /videos, /my-videos, etc.

# API Endpoints

## Authentication

POST /register
Register a new user.

{
"username": "john",
"email": "[john@example.com](mailto:john@example.com)",
"password": "securepass"
}

POST /login
Log in and get a JWT token.

{
"username": "john",
"password": "securepass"
}

Response:
{
"access\_token": "..."
}

## Videos

POST /videos
Add a new video.

{
"category": "language learning",
"script": "This is a script...",
"series\_name": "English 101",
"series\_number": 1,
"video\_url": "[http://localhost:8000/video1.mp4](http://localhost:8000/video1.mp4)"
}

GET /videos
List all videos (public).

DELETE /videos
Delete all videos (no auth required).

GET /videos-random
List videos in random order.
Query params: category, series\_name

GET /random-video
Get one random video.
Query params: category, series\_name

## Saved Videos

POST /save-video
Save a video to user's collection.

{
"video\_id": 3
}

GET /my-videos
Return the current user's saved videos.

## GPT Chat

POST /chat-with-script
Start or continue a chat for a given video (context scoped by video).

{
"video\_id": 1,
"user\_input": "Can you summarize this video?"
}

Response:
{
"reply": "The video explains..."
}

## Status Codes

* 200 OK - success
* 201 Created - resource added
* 400 Bad Request - input error
* 401 Unauthorized - login needed
* 403 Forbidden - access denied
* 404 Not Found - not found

## Credits

Created by Callum with assistance from ChatGPT. Built for learning, showcasing full-stack AI integration with video content.
