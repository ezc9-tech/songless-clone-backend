#!/usr/bin/env python3
"""Spotify OAuth helper for fetching an access token with configured scopes."""

from __future__ import annotations

import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


DEFAULT_SCOPES = "playlist-read-private playlist-read-collaborative"


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def validate_redirect_uri(uri: str) -> None:
    parsed = urlparse(uri)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(
            "SPOTIPY_REDIRECT_URI must be a full URL, e.g. "
            "'http://127.0.0.1:8888/callback'"
        )


def fetch_spotify_token(scopes: str = DEFAULT_SCOPES) -> str:
    """Return a Spotify access token for the provided OAuth scopes."""
    load_dotenv()

    client_id = require_env("SPOTIFY_CLIENT_ID")
    client_secret = require_env("SPOTIFY_CLIENT_SECRET")
    redirect_uri = require_env("SPOTIPY_REDIRECT_URI")
    validate_redirect_uri(redirect_uri)

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scopes,
        cache_path=".spotify_token_cache",
        open_browser=True,
        show_dialog=False,
    )

    token_info = auth_manager.get_access_token(as_dict=True)
    access_token = str(token_info.get("access_token", "")).strip()
    if not access_token:
        raise RuntimeError("Spotify OAuth returned an empty access token")

    return access_token
