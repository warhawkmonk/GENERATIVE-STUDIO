import os
import urllib.request
from flask import Flask, jsonify, render_template_string

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STREAMLIT_HOST = os.environ.get("STREAMLIT_HOST", "127.0.0.1")
STREAMLIT_PORT = int(os.environ.get("STREAMLIT_PORT", "8051"))
FLASK_PORT = int(os.environ.get("FLASK_PORT", "8080"))
STREAMLIT_URL = f"http://{STREAMLIT_HOST}:{STREAMLIT_PORT}"

app = Flask(__name__)


@app.get("/")
def index():
    return render_template_string("""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Generative Studio</title>
        <meta http-equiv="refresh" content="0;url={{ streamlit_url }}" />
        <style>
          body { margin: 0; font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; display: grid; place-items: center; min-height: 100vh; }
          .card { background: #111827; padding: 24px; border-radius: 12px; text-align: center; }
          a { color: #93c5fd; }
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Opening Generative Studio</h1>
          <p>If you are not redirected automatically, <a href="{{ streamlit_url }}">open the Streamlit app here</a>.</p>
        </div>
      </body>
    </html>
    """, streamlit_url=STREAMLIT_URL)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "streamlit": STREAMLIT_URL})


@app.get("/health")
def health():
    return jsonify({"status": "ok", "streamlit": STREAMLIT_URL})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=False)
