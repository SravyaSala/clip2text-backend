import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

app = Flask(__name__)
CORS(app)  # ✅ THIS fixes frontend popup

@app.route("/")
def home():
    return "Clip2Text Backend Running!"

@app.route("/get_transcript", methods=["POST"])
def get_transcript():
    data = request.get_json()
    video_url = data.get("url")

    if not video_url:
        return jsonify({"error": "URL missing"}), 400

    try:
        # Extract video ID
        if "youtu.be" in video_url:
            video_id = video_url.split("/")[-1]
        else:
            video_id = video_url.split("v=")[1].split("&")[0]

        # ✅ Correct API usage
        transcript = (
            YouTubeTranscriptApi
            .list_transcripts(video_id)
            .find_transcript(["en"])
            .fetch()
        )

        transcript_text = " ".join(item["text"] for item in transcript)

        return jsonify({"transcript": transcript_text})

    except TranscriptsDisabled:
        return jsonify({"error": "Transcripts are disabled for this video"}), 404
    except NoTranscriptFound:
        return jsonify({"error": "No English transcript found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
