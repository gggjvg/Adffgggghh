# Highrise Music Radio (starter)

A separate Highrise chat bot + browser-based radio queue. This is **not** a Highrise in-room audio transmitter. Highrise's documented Python bot interface does not expose a supported live audio injection method; listeners open the `/radio` page to hear tracks.

## Features
- `!play https://...` adds a direct audio URL to the queue
- `!queue`, `!now`, `!radio`
- Admin-only `!skip`, `!pause`, `!resume`, `!clear`
- Minimal browser player and health endpoint
- Railway deployment files

## Important limitations
- The starter accepts direct HTTP(S) audio URLs only. It does not rip music from YouTube, Spotify, SoundCloud, or other services.
- A URL must point to an audio file or a playback-compatible stream and its host must allow browser playback (CORS / redirects / authentication can prevent playback).
- The queue is stored in SQLite and shared by the bot and web player because `run_all.py` starts both in one Railway service. It is stored in the container filesystem, so it may reset when Railway replaces the container. Use a Railway Volume mounted at `/data` and set `RADIO_DB_PATH=/data/radio.sqlite3` for persistence.
- Search by song title, automatic track duration/advance, and a true relayed stream are not implemented yet. The player switches to the next track when an admin skips; automatic end-of-track detection is not included in this starter.
- This project does not send audio into Highrise voice. The `!radio` command shares the external listening page.

## Railway setup
Create a Railway project from this GitHub repository. Add variables:
- `HIGHRISE_ROOM_ID` — your Highrise room ID
- `HIGHRISE_API_TOKEN` — bot API token (keep secret)
- `OWNER_IDS` — comma-separated Highrise user IDs allowed to use admin commands
- `RADIO_ADMIN_KEY` — long random secret for future web admin controls
- `PUBLIC_BASE_URL` — your deployed public Railway domain, e.g. `https://your-app.up.railway.app`

Deploy as one Railway service. `run_all.py` starts the web player and Highrise bot together; they share the same SQLite queue. Do not create a second service for the bot.

## Local run
```bash
pip install -r requirements.txt
uvicorn webapp:app --host 0.0.0.0 --port 8000
```

## Security
Never commit bot tokens or admin keys. If a token was ever uploaded publicly, revoke it and generate a new one. Use Railway Variables.
