import base64
import requests
import os
from flask import Flask, request, redirect

app = Flask(__name__)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:5000/callback"

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

access_token = None
refresh_token = None


@app.route("/")
def home():
    return "Server running."


@app.route("/login")
def login():
    scope = "user-modify-playback-state user-read-playback-state"
    auth_url = (
        f"{SPOTIFY_AUTH_URL}"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={scope}"
    )
    return redirect(auth_url)


@app.route("/callback")
def callback():
    global access_token, refresh_token

    code = request.args.get("code")

    auth_header = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
    tokens = response.json()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    return "Authorization successful. You can close this tab."


def refresh_access_token():
    global access_token

    auth_header = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
    tokens = response.json()
    access_token = tokens.get("access_token")


def spotify_put(endpoint):
    global access_token

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.put(f"{SPOTIFY_API_BASE}{endpoint}", headers=headers)

    if response.status_code == 401:
        refresh_access_token()
        headers["Authorization"] = f"Bearer {access_token}"
        requests.put(f"{SPOTIFY_API_BASE}{endpoint}", headers=headers)


@app.route("/pause")
def pause():
    spotify_put("/me/player/pause")
    return "Paused"


@app.route("/play")
def play():
    spotify_put("/me/player/play")
    return "Playing"

@app.route("/state")
def state():
    global access_token

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        f"{SPOTIFY_API_BASE}/me/player",
        headers=headers
    )

    if response.status_code == 401:
        refresh_access_token()
        headers["Authorization"] = f"Bearer {access_token}"
        response = requests.get(
            f"{SPOTIFY_API_BASE}/me/player",
            headers=headers
        )

    if response.status_code != 200:
        return {"is_playing": False}

    data = response.json()

    return {"is_playing": data.get("is_playing", False)}


if __name__ == "__main__":
    app.run(port=5000)