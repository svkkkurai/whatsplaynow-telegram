import asyncio
from telethon import TelegramClient
from telethon.tl.functions.account import UpdateProfileRequest
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from telethon.tl.functions.users import GetFullUserRequest

import config

SPOTIFY_CLIENT_ID = config.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = config.SPOTIFY_CLIENT_SECRET
SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback'
SPOTIFY_SCOPE = 'user-read-playback-state'

API_ID = config.TG_API_ID
API_HASH = config.TG_API_HASH
SESSION_NAME = 'session'

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope=SPOTIFY_SCOPE))

async def update_bio_with_track():
    async with client:
        me = await client.get_me()
        full_user = await client(GetFullUserRequest(me.id))
        original_bio = (full_user.full_user.about or '')[:70]

        while True:
            current_track = sp.current_playback()

            if current_track and current_track.get('is_playing'):
                track_info = current_track.get('item')
                if track_info:
                    track_name = track_info.get('name', 'Unknown')
                    artist_name = track_info['artists'][0].get('name', 'Unknown')

                    progress_ms = current_track.get('progress_ms', 0)
                    duration_ms = track_info.get('duration_ms', 1)

                    progress_time = f"{progress_ms // 60000}:{(progress_ms // 1000) % 60:02d}"
                    duration_time = f"{duration_ms // 60000}:{(duration_ms // 1000) % 60:02d}"

                    base_text = f"Слушает Spotify: {artist_name} - "
                    time_text = f" ({progress_time} из {duration_time})"
                    max_track_length = 70 - len(base_text) - len(time_text) # Change 70 to 140, if you have Telegram Premium.

                    if len(track_name) > max_track_length:
                        track_name = track_name[:max_track_length - 3] + "..."

                    bio_text = base_text + track_name + time_text
            else:
                full_user = await client(GetFullUserRequest(me.id))
                current_bio = full_user.full_user.about or ''
                
                if current_bio != original_bio and not current_bio.startswith("Слушает Spotify"):
                    original_bio = current_bio[:70]
                
                bio_text = original_bio

            if full_user.full_user.about != bio_text:
                await client(UpdateProfileRequest(about=bio_text))
                print(f'Обновлено био: {bio_text}')

            await asyncio.sleep(15)
            
with client:
    client.loop.run_until_complete(update_bio_with_track())
