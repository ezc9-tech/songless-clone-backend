#!/usr/bin/env python3
"""Fetch and print Spotify playlist items from SPOTIFY_PLAYLIST_ID."""

from __future__ import annotations

import json
import os

import requests
from dotenv import load_dotenv

from fetch_spotify_token import fetch_spotify_token


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def fetch_playlist_songs() -> list[dict[str, str]]:
    token = fetch_spotify_token()
    playlist_id = require_env("SPOTIFY_PLAYLIST_ID")

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/items"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    payload = response.json()
    songs: list[dict[str, str]] = []
    for row in payload.get("items", []):
        track = row.get("item") or {}
        name = str(track.get("name", "")).strip()
        artists = ", ".join(str(a.get("name", "")).strip() for a in track.get("artists", []))
        if name:
            songs.append({"song": name, "artist": artists})
    return songs


def main() -> int:
    load_dotenv()
    songs = fetch_playlist_songs()
    print(json.dumps(songs, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
