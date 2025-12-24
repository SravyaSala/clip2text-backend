import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)
CORS(app)   # ✅ THIS IS THE MISSING PIECE

@app.route('/')
def home():
    return "Clip2Text Backend Running!"

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    video_url = data.get('url', '')

    if "youtube.com" not in video_url and "youtu.be" not in video_url:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        # Extract video ID
        if "youtu.be" in video_url:
            video_id = video_url.split('/')[-1]
        else:
            video_id = video_url.split('v=')[-1].split('&')[0]

        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join(item['text'] for item in transcript_list)

        return jsonify({"transcript": transcript_text})

    except Exception as e:
        error_msg = str(e)
        if "No transcript found" in error_msg:
            return jsonify({"error": "Transcript not available for this video"}), 404
        elif "Video unavailable" in error_msg:
            return jsonify({"error": "The YouTube video is unavailable"}), 404
        else:
            return jsonify({"error": f"Failed to fetch transcript: {error_msg}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
