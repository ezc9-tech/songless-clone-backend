#!/usr/bin/env python3
"""Fetch YouTube lyric video URLs for songs in the Supabase database."""

from __future__ import annotations

import os
import subprocess
import json
import requests
from dotenv import load_dotenv

from fetch_spotify_token import require_env


def fetch_songs_from_supabase(supabase_url: str, supabase_key: str) -> list[dict[str, str]]:
    """Fetch songs that haven't been searched yet."""
    url = f"{supabase_url.rstrip('/')}/rest/v1/spotify_playlist_songs"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
    }
    # Fetch songs where searched is false or null
    params = {
        "or": "(searched.is.null,searched.eq.false)",
        "select": "song,artist"
    }
    response = requests.get(url, headers=headers, params=params, timeout=30)
    if not response.ok:
        print(f"Error fetching from Supabase: {response.status_code} - {response.text}")
    response.raise_for_status()
    return response.json()


def update_supabase_status(song: str, artist: str, youtube_url: str | None, supabase_url: str, supabase_key: str):
    """Update the youtube_url and set searched=true for a specific song and artist."""
    url = f"{supabase_url.rstrip('/')}/rest/v1/spotify_playlist_songs"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    params = {
        "song": f"eq.{song}",
        "artist": f"eq.{artist}"
    }
    
    data = {"searched": True}
    if youtube_url:
        data["youtube_url"] = youtube_url
    
    response = requests.patch(url, headers=headers, params=params, json=data, timeout=30)
    response.raise_for_status()


def search_youtube(song_name: str, artist_name: str) -> str | None:
    """Search YouTube for a lyric video and return the URL of the most viewed result."""
    # We search for the top 10 results to increase the chance of finding a match that meets the strict criteria.
    try:
        # We still use the artist in the query to find the CORRECT song, but we don't require it in the title.
        query = f"{song_name} {artist_name}"
        search_query = f"ytsearch10:{query} lyric"
        # We use --flat-playlist and --dump-json to get metadata for all 10 results without downloading
        command = [
            "yt-dlp",
            "--flat-playlist",
            "--dump-json",
            search_query
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        results = [json.loads(line) for line in result.stdout.strip().split("\n") if line]
        
        if not results:
            return None
        
        # Strict filter: Both song name AND 'lyric' must be in the title (case-insensitive)
        song_name_lower = song_name.lower()
        matching_results = [
            r for r in results 
            if "lyric" in r.get("title", "").lower() and song_name_lower in r.get("title", "").lower()
        ]
        
        if not matching_results:
            return None
        
        # Sort the matches by view count descending to get the most popular one
        sorted_results = sorted(
            matching_results, 
            key=lambda x: x.get("view_count") or 0, 
            reverse=True
        )
        
        return sorted_results[0].get("webpage_url")
        
    except Exception as e:
        # Check if it was a subprocess error to see stderr
        if hasattr(e, 'stderr') and e.stderr:
            print(f"yt-dlp error for '{song_name}': {e.stderr}")
        else:
            print(f"Error searching YouTube for '{song_name}': {e}")
        return None


def main() -> int:
    load_dotenv()

    supabase_url = require_env("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip() or require_env("SUPABASE_ANON_KEY")

    print("Fetching songs from Supabase...")
    songs = fetch_songs_from_supabase(supabase_url, supabase_key)
    
    if not songs:
        print("No songs found needing a YouTube URL.")
        return 0

    print(f"Found {len(songs)} songs to process.")
    
    updated_count = 0
    for item in songs:
        song = item["song"]
        artist = item["artist"]
        
        print(f"Searching YouTube for: {song} by {artist}...")
        url = search_youtube(song, artist)
        
        if url:
            print(f"Found: {url}. Updating database...")
        else:
            print(f"No results found for '{song} by {artist}' that met the strict criteria. Skipping...")
        
        try:
            # Always update, even if url is None, to mark 'searched' = True
            update_supabase_status(song, artist, url, supabase_url, supabase_key)
            if url:
                updated_count += 1
        except Exception as e:
            print(f"Failed to update database for '{song}': {e}")

    print(f"Finished. Updated {updated_count} songs with YouTube URLs.")
    return 0


if __name__ == "__main__":
    # Ensure yt-dlp is installed
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: 'yt-dlp' is not installed. Please install it with: pip install yt-dlp")
        raise SystemExit(1)

    raise SystemExit(main())
