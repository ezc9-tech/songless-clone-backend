# songless-clone-backend

Backend + scripts for Songless.

## Prerequisites

- Node.js 20+
- npm
- Python 3.10+
- PostgreSQL (for Prisma)
- A Spotify app (client ID/secret + redirect URI)
- Supabase project (for `spotify_playlist_songs` uploads)

## 1. Install dependencies

```bash
# Node dependencies
npm install

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
# optional, recommended for Docker/CI (non-interactive):
SPOTIFY_REFRESH_TOKEN=your_spotify_refresh_token

SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
# optional, preferred for inserts:
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DB_NAME
```

## 3. Prepare the database (Prisma)

```bash
npx prisma migrate dev
```

## 4. Run the backend server

```bash
node src/server.js
```

Server starts on `http://localhost:3000`.

## 5. Run Spotify scripts

From repo root (with your venv activated):

```bash
# Fetch and print playlist songs
python scripts/fetch_spotify_playlist_items.py

# Fetch songs and upload to Supabase table `spotify_playlist_songs`
python scripts/upload_spotify_playlist_songs.py
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

`make run` will:
- run `scripts/upload_spotify_playlist_songs.py` in the container
- exit when the upload script finishes

### Docker env notes

- Docker flow does not start a local database container.
- Upload goes directly to Supabase using `SUPABASE_URL` and key values from `.env`.
- For Spotify scripts in Docker, set `SPOTIFY_REFRESH_TOKEN` to avoid browser OAuth.
