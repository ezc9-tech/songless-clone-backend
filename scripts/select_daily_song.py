#!/usr/bin/env python3
"""Select a daily song from the Supabase database and update its last_picked_date."""

from __future__ import annotations

import datetime
import os
import random
import sys

import requests
from dotenv import load_dotenv


def require_env(name: str) -> str:
    """Require an environment variable to be set."""
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def fetch_all_songs(supabase_url: str, supabase_key: str) -> list[dict[str, str | None]]:
    """Fetch all songs from Supabase with their last_picked_date."""
    url = f"{supabase_url.rstrip('/')}/rest/v1/spotify_playlist_songs"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
    }
    # We fetch song, artist, and last_picked_date
    params = {
        "select": "song,artist,last_picked_date"
    }
    response = requests.get(url, headers=headers, params=params, timeout=30)
    if not response.ok:
        print(f"Error fetching from Supabase: {response.status_code} - {response.text}")
    response.raise_for_status()
    return response.json()


def update_song_date(song: str, artist: str, date_str: str, supabase_url: str, supabase_key: str):
    """Update the last_picked_date of a song in Supabase."""
    url = f"{supabase_url.rstrip('/')}/rest/v1/spotify_playlist_songs"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    # Using on_conflict to ensure we update the specific song/artist pair
    params = {"on_conflict": "song,artist"}
    payload = {
        "song": song,
        "artist": artist,
        "last_picked_date": date_str
    }
    response = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
    if not response.ok:
        print(f"Error updating Supabase: {response.status_code} - {response.text}")
    response.raise_for_status()


def parse_date(d_str: str | None) -> datetime.date:
    """Parse YYYY-MM-DD date string, returning a very old date if None or invalid."""
    if not d_str:
        return datetime.date(1900, 1, 1)
    try:
        return datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
    except ValueError:
        return datetime.date(1900, 1, 1)


def main() -> int:
    load_dotenv()

    try:
        supabase_url = require_env("SUPABASE_URL")
        supabase_key = require_env("SUPABASE_ANON_KEY")
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    try:
        songs = fetch_all_songs(supabase_url, supabase_key)
    except Exception as e:
        print(f"Failed to fetch songs: {e}")
        return 1

    if not songs:
        print("No songs found in the database.")
        return 1

    # Get today's date in YYYY-MM-DD format (standard for SQL and Supabase DATE type)
    today_date = datetime.date.today()
    today_str = today_date.isoformat()

    # 1. Check if a song already has today's date
    for s in songs:
        if s.get("last_picked_date") == today_str:
            print(f"{s['song']} - {s['artist']}")
            return 0

    # 2. Filter eligible songs
    # The requirement is: "Exclude songs that were picked within the last n days, where n is the total number of songs"
    # This effectively means we pick from songs that haven't been picked in the current cycle.
    # We'll pick from the songs with the oldest last_picked_date (including NULL).
    
    sorted_songs = sorted(songs, key=lambda x: parse_date(x.get("last_picked_date")))
    
    # The first element has the oldest date
    oldest_date = parse_date(sorted_songs[0].get("last_picked_date"))
    
    # All songs that have this same oldest date are equally eligible
    eligible_songs = [s for s in songs if parse_date(s.get("last_picked_date")) == oldest_date]
    
    if not eligible_songs:
        print("No eligible songs found.")
        return 1

    # 3. Randomly select one
    selected_song = random.choice(eligible_songs)
    
    # 4. Update the database
    try:
        update_song_date(
            selected_song["song"], 
            selected_song["artist"], 
            today_str, 
            supabase_url, 
            supabase_key
        )
    except Exception as e:
        print(f"Failed to update selected song: {e}")
        return 1

    # 5. Return the daily song
    print(f"{selected_song['song']} - {selected_song['artist']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
