import asyncio
from telethon import TelegramClient
from telethon.tl.functions.account import UpdateProfileRequest
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from telethon.tl.functions.users import GetFullUserRequest

import config

# Settings for Spotify
SPOTIFY_CLIENT_ID = config.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = config.SPOTIFY_CLIENT_SECRET
SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback'
SPOTIFY_SCOPE = 'user-read-playback-state'

# Settings for Telegram
API_ID = config.TG_API_ID
API_HASH = config.TG_API_HASH
SESSION_NAME = 'session'  # Имя сессии Telethon

# Telethon init
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Spotify Client init
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope=SPOTIFY_SCOPE))

async def update_bio_with_track():
    async with client:
        me = await client.get_me()  # Получаем основную информацию о пользователе
        full_user = await client(GetFullUserRequest(me.id))  # Получаем полную информацию о пользователе
        user_description = full_user.full_user.about or ''  # Сохраняем текущее описание профиля пользователя

        while True:
            current_track = sp.current_playback()

            if current_track and current_track['is_playing']:
                track_name = current_track['item']['name']
                artist_name = current_track['item']['artists'][0]['name']
                progress_ms = current_track['progress_ms']
                duration_ms = current_track['item']['duration_ms']

                # Преобразование миллисекунд в минуты и секунды
                progress_time = f"{progress_ms // 60000}:{str((progress_ms // 1000) % 60).zfill(2)}"
                duration_time = f"{duration_ms // 60000}:{str((duration_ms // 1000) % 60).zfill(2)}"

                bio_text = f"Now playing: {artist_name} - {track_name} ({progress_time} of {duration_time})"

                # Если длина bio_text превышает 70 символов, обрезаем название трека
                max_track_name_length = 70 - len(f"Now playing: {artist_name} -  ({progress_time} of {duration_time})")
                if len(bio_text) > 70:
                    track_name = track_name[:max_track_name_length - 3] + "..."
                    bio_text = f"Now playing: {artist_name} - {track_name} ({progress_time} of {duration_time})"
            else:
                bio_text = user_description[:70]  # Обрезаем описание пользователя, если нужно


            # Update bio in Telegram
            await client(UpdateProfileRequest(about=bio_text))
            print(f'Spotify - Now playing: {artist_name} - {track_name} ({progress_time} из {duration_time})')

            # Await before update track
            await asyncio.sleep(30)

# Run bot
with client:
    client.loop.run_until_complete(update_bio_with_track())
