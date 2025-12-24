from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from transformers import pipeline
import re

app = Flask(__name__)

# Lazy load summarizer to reduce startup time
summarizer = None
def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    return summarizer

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    youtube_url = data.get("url")

    if not youtube_url:
        return jsonify({"error": "No URL provided"}), 400

    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([t["text"] for t in transcript_data])
    except (TranscriptsDisabled, NoTranscriptFound):
        return jsonify({"error": "Transcript not available for this video."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    summary = get_summarizer()(
        transcript_text[:3000],
        max_length=150,
        min_length=60,
        do_sample=False
    )[0]["summary_text"]

    return jsonify({
        "transcript": transcript_text,
        "summary": summary
    })

if __name__ == "__main__":
    # Use 0.0.0.0 so Render can access the server externally
    app.run(host="0.0.0.0", port=5000)
