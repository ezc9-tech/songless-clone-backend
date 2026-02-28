.PHONY: build run sync-all fetch-urls

build:
	docker compose build app

run:
	docker compose run --rm app python scripts/upload_spotify_playlist_songs.py

fetch-urls:
	docker compose run --rm app python scripts/fetch_soundcloud_urls.py

sync-all: run fetch-urls
