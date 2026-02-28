#!/usr/bin/env python3
"""Fetch SoundCloud URLs for songs in the Supabase database."""

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


def search_soundcloud(song_name: str, artist_name: str, soundcloud_client_id: str | None = None) -> str | None:
    """Search SoundCloud and return the URL of the most relevant result."""
    try:
        # Lowercase everything for better matching
        song_name_lower = song_name.lower()
        artist_name_lower = artist_name.lower()
        
        # Include both in the search query for better precision
        query = f"{song_name_lower} {artist_name_lower}"
        search_query = f"scsearch10:{query}"
        
        # We use --flat-playlist and --dump-json to get metadata for all 10 results without downloading
        command = [
            "yt-dlp",
            "--flat-playlist",
            "--dump-json",
        ]
        
        if soundcloud_client_id:
            command.extend(["--extractor-args", f"soundcloud:client_id={soundcloud_client_id}"])
            
        command.append(search_query)
        
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        results = [json.loads(line) for line in result.stdout.strip().split("\n") if line]
        
        if not results:
            return None
        
        matching_results = []
        for r in results:
            title = r.get("title", "").lower()
            uploader = r.get("uploader", "").lower()
            # Check if song name is in title, and artist name is in title or uploader
            if song_name_lower in title and (artist_name_lower in title or artist_name_lower in uploader):
                matching_results.append(r)
        
        if not matching_results:
            # Fallback: Just return the first result if it contains the song name
            for r in results:
                if song_name_lower in r.get("title", "").lower():
                    return r.get("webpage_url")
            return None
        
        # Sort by view count (play count on SoundCloud) if available
        sorted_results = sorted(
            matching_results, 
            key=lambda x: x.get("view_count") or 0, 
            reverse=True
        )
        
        return sorted_results[0].get("webpage_url")
        
    except Exception as e:
        if hasattr(e, 'stderr') and e.stderr:
            print(f"yt-dlp error for '{song_name}': {e.stderr}")
        else:
            print(f"Error searching SoundCloud for '{song_name}': {e}")
        return None


def batch_update_supabase(updates: list[dict[str, str | bool]], supabase_url: str, supabase_key: str):
    """Update multiple songs in Supabase using upsert (POST with on_conflict)."""
    if not updates:
        return

    url = f"{supabase_url.rstrip('/')}/rest/v1/spotify_playlist_songs"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    params = {"on_conflict": "song,artist"}
    
    response = requests.post(url, headers=headers, params=params, json=updates, timeout=30)
    if not response.ok:
        print(f"Supabase batch update error: {response.status_code} - {response.text}")
    response.raise_for_status()


def main() -> int:
    load_dotenv()

    supabase_url = require_env("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip() or require_env("SUPABASE_ANON_KEY")
    soundcloud_client_id = os.getenv("SOUNDCLOUD_CLIENT_ID")

    print("Fetching songs from Supabase...")
    songs = fetch_songs_from_supabase(supabase_url, supabase_key)
    
    if not songs:
        print("No songs found needing a SoundCloud URL.")
        return 0

    print(f"Found {len(songs)} songs to process.")
    
    all_updates = []
    found_count = 0
    
    for item in songs:
        song = item["song"]
        artist = item["artist"]
        
        print(f"Searching SoundCloud for: {song} by {artist}...")
        url = search_soundcloud(song, artist, soundcloud_client_id)
        
        update_data = {
            "song": song,
            "artist": artist,
            "searched": True,
            "soundcloud_url": url
        }
        if url:
            print(f"Found: {url}")
            found_count += 1
        else:
            print(f"No results found for '{song} by {artist}'.")
        
        all_updates.append(update_data)

    print(f"\nProcessing updates for {len(all_updates)} songs in batches of 100...")
    
    # Supabase has a limit of 1000 rows per request, so we batch the updates
    # Using 100 should be okay to avoid hitting any limits and still be efficient
    batch_size = 100
    for i in range(0, len(all_updates), batch_size):
        batch = all_updates[i:i + batch_size]
        try:
            batch_update_supabase(batch, supabase_url, supabase_key)
            print(f"Successfully updated batch {i // batch_size + 1} ({len(batch)} songs).")
        except Exception as e:
            print(f"Failed to update batch {i // batch_size + 1}: {e}")

    print(f"\nFinished. Updated {found_count} songs with SoundCloud URLs.")
    return 0


if __name__ == "__main__":
    # Ensure yt-dlp is installed
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: 'yt-dlp' is not installed. Please install it with: pip install yt-dlp")
        raise SystemExit(1)

    raise SystemExit(main())

