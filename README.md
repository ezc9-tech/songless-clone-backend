# songless-clone-scripts

Scripts for Songless data synchronization.

## Prerequisites

- Python 3.10+
- A Spotify app (client ID/secret + redirect URI)
- Supabase project (for `spotify_playlist_songs` uploads)

## 1. Install dependencies

```bash
# Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Configure environment variables

Create `.env` in the repo root (or copy from `.env.example`) and set:

```env
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_PLAYLIST_ID=your_spotify_playlist_id
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
# optional, enables non-interactive auth for Docker/CI:
SPOTIFY_REFRESH_TOKEN=your_spotify_refresh_token

SUPABASE_URL=your_supabase_url
SUPABASE_PUBLISHABLE_KEY=your_supabase_publishable_key
SUPABASE_ANON_KEY=your_supabase_anon_key

SOUNDCLOUD_CLIENT_ID=your_soundcloud_client_id
SOUNDCLOUD_CLIENT_SECRET=your_soundcloud_client_secret
```

## 3. Run Spotify scripts

From repo root (with your venv activated):

```bash
# Fetch and print playlist songs
python scripts/fetch_spotify_playlist_items.py

# Fetch songs and upload to Supabase table `spotify_playlist_songs`
python scripts/upload_spotify_playlist_songs.py

# Fetch SoundCloud URLs for songs in Supabase
python scripts/fetch_soundcloud_urls.py
```

Notes:

- If `SPOTIFY_REFRESH_TOKEN` is set, scripts use it and skip browser OAuth.
- If `SPOTIFY_REFRESH_TOKEN` is not set, OAuth opens a browser window for login/consent.
- Token cache is saved to `.spotify_token_cache`.
- Upload uses `on_conflict=song,artist`, so duplicates are ignored.

## Docker note

For Docker/CI, set `SPOTIFY_REFRESH_TOKEN` in `.env` and use that inside the container.
This avoids interactive browser redirect handling in Docker.

## Docker + Makefile

### Run with Docker (step-by-step)

1. Create your env file:

```bash
cp .env.example .env
```

2. Edit `.env` and set at least:
- Spotify vars
- Supabase vars
- `SPOTIFY_REFRESH_TOKEN` (recommended for Docker)

3. Build:

```bash
make build
```

4. Run:

```bash
make sync-all
```

`make sync-all` will:
- run `scripts/upload_spotify_playlist_songs.py`
- run `scripts/fetch_soundcloud_urls.py`
- exit when finished

### Docker env notes

- Upload goes directly to Supabase using `SUPABASE_URL` and key values from `.env`.
- For Spotify scripts in Docker, set `SPOTIFY_REFRESH_TOKEN` to avoid browser OAuth.
