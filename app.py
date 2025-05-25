from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from db import init_db, get_db
from utils import hash_password, check_password, create_token

app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this for production use
jwt = JWTManager(app)

# Initialize database tables
init_db()

# Register user
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (
            data['username'],
            data['email'],
            hash_password(data['password'])
        ))
        conn.commit()
        return jsonify(msg="User registered successfully"), 201
    except Exception as e:
        return jsonify(error="Username or email already exists", details=str(e)), 400

# Login user
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username=?", (data['username'],))
    user = cur.fetchone()
    if user and check_password(data['password'], user[1]):
        token = create_token(user[0])
        return jsonify(access_token=token), 200
    return jsonify(error="Invalid credentials"), 401

# Add a video (authenticated)
@app.route('/videos', methods=['POST'])
@jwt_required()
def add_video():
    user_id = get_jwt_identity()
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO series (name) VALUES (?)", (data['series_name'],))
    conn.commit()
    cur.execute("SELECT id FROM series WHERE name=?", (data['series_name'],))
    series_id = cur.fetchone()[0]
    cur.execute("""INSERT INTO videos (category, script, series_id, series_number, video_url)
                   VALUES (?, ?, ?, ?, ?)""",
                (data['category'], data['script'], series_id, data['series_number'], data['video_url']))
    conn.commit()
    return jsonify(msg="Video added"), 201

# List all videos (public)
@app.route('/videos', methods=['GET'])
def list_videos():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.id, v.category, v.script, s.name as series_name, v.series_number, v.video_url
        FROM videos v LEFT JOIN series s ON v.series_id = s.id
    """)
    rows = cur.fetchall()
    return jsonify([{
        "id": row[0],
        "category": row[1],
        "script": row[2],
        "series_name": row[3],
        "series_number": row[4],
        "video_url": row[5]
    } for row in rows])

# Save video to user's collection
@app.route('/save-video', methods=['POST'])
@jwt_required()
def save_video():
    user_id = get_jwt_identity()
    video_id = request.json.get('video_id')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO user_saved_videos (user_id, video_id) VALUES (?, ?)", (user_id, video_id))
    conn.commit()
    return jsonify(msg="Video saved"), 200

# Get user's saved videos
@app.route('/my-videos', methods=['GET'])
@jwt_required()
def my_videos():
    user_id = get_jwt_identity()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.id, v.category, v.script, s.name, v.series_number, v.video_url
        FROM user_saved_videos uv
        JOIN videos v ON uv.video_id = v.id
        LEFT JOIN series s ON v.series_id = s.id
        WHERE uv.user_id = ?
    """, (user_id,))
    rows = cur.fetchall()
    return jsonify([{
        "id": row[0],
        "category": row[1],
        "script": row[2],
        "series_name": row[3],
        "series_number": row[4],
        "video_url": row[5]
    } for row in rows])


import random

@app.route('/videos-random', methods=['GET'])
def videos_random():
    category = request.args.get("category")
    series_name = request.args.get("series_name")

    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT v.id, v.category, v.script, s.name as series_name, v.series_number, v.video_url
        FROM videos v
        LEFT JOIN series s ON v.series_id = s.id
    """
    conditions = []
    params = []

    if category:
        conditions.append("v.category = ?")
        params.append(category)

    if series_name:
        conditions.append("s.name = ?")
        params.append(series_name)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cur.execute(query, params)
    videos = cur.fetchall()

    if not videos:
        return jsonify(error="No matching videos found"), 404

    import random
    random.shuffle(videos)

    return jsonify([{
        "id": v[0],
        "category": v[1],
        "script": v[2],
        "series_name": v[3],
        "series_number": v[4],
        "video_url": v[5]
    } for v in videos])



from chatbot import chat_with_gpt

@app.route('/chat-with-script', methods=['POST'])
def chat_with_script():
    data = request.json
    video_id = data.get("video_id")
    user_input = data.get("user_input")

    if not video_id or not user_input:
        return jsonify(error="Missing video_id or user_input"), 400

    # Check if conversation already started
    from chatbot import conversation_context
    if video_id in conversation_context:
        reply = chat_with_gpt(video_id, user_input)
    else:
        # Fetch script from DB
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT script FROM videos WHERE id = ?", (video_id,))
        row = cur.fetchone()
        if not row:
            return jsonify(error="Video not found"), 404
        video_script = row[0]

        # Start new conversation with script
        reply = chat_with_gpt(video_id, user_input, script=video_script)

    return jsonify({"reply": reply})

@app.route('/videos', methods=['DELETE'])
def delete_all_videos():
    conn = get_db()
    cur = conn.cursor()

    # Delete user-saved records first to prevent foreign key constraint errors
    cur.execute("DELETE FROM user_saved_videos")
    cur.execute("DELETE FROM videos")
    conn.commit()

    return jsonify(msg="All videos deleted"), 200


# Run the server
if __name__ == "__main__":
    app.run(debug=True)