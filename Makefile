.PHONY: build run

build:
	docker compose build app

run:
	docker compose run --rm app python scripts/upload_spotify_playlist_songs.py
