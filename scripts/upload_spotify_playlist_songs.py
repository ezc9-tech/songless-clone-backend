#!/usr/bin/env python3
"""Fetch Spotify playlist songs and upload them to Supabase."""

from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

from fetch_spotify_playlist_items import fetch_playlist_songs
from fetch_spotify_token import require_env


def upload_to_supabase(rows: list[dict[str, str]], supabase_url: str, supabase_key: str) -> int:
    url = f"{supabase_url.rstrip('/')}/rest/v1/spotify_playlist_songs"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation,resolution=ignore-duplicates",
    }
    params = {"on_conflict": "song,artist"}
    response = requests.post(url, headers=headers, params=params, json=rows, timeout=30)
    response.raise_for_status()

    inserted_rows = response.json()
    return len(inserted_rows)


def main() -> int:
    load_dotenv()

    supabase_url = require_env("SUPABASE_URL")
    supabase_key = require_env("SUPABASE_ANON_KEY")

    rows = fetch_playlist_songs()

    if not rows:
        print("No songs found to upload.")
        return 0

    inserted = upload_to_supabase(rows=rows, supabase_url=supabase_url, supabase_key=supabase_key)
    print(f"Inserted {inserted} new row(s) into spotify_playlist_songs. Existing rows were kept.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
