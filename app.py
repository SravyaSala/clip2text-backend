from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from transformers import pipeline
import re

app = Flask(__name__)

# Load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    youtube_url = data.get("url")

    if not youtube_url:
        return jsonify({"error": "No URL provided"}), 400

    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    # TRY–EXCEPT MUST BE TOGETHER
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return jsonify({
            "error": "Transcript not available for this video. Try a video with captions."
        }), 400

    transcript_text = " ".join([item["text"] for item in transcript_data])

    summary = summarizer(
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
    app.run(debug=True)
