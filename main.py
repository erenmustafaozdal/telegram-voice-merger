from moviepy.editor import concatenate_audioclips, AudioFileClip, concatenate_videoclips, VideoFileClip
from telethon.sync import TelegramClient
from tqdm import tqdm
import os
from config import *


# Geçici ses dosyası adı
TEMP_AUDIO_FILE = 'temp_audio.wav'

# Telegram istemcisini oluştur
client = TelegramClient('telegram-voice-merger', api_id, api_hash)

downloads_dir = "./downloads"
if not os.path.exists(downloads_dir):
    os.mkdir(downloads_dir)

exports_dir = "./exports"
if not os.path.exists(exports_dir):
    os.mkdir(exports_dir)


# Printing download progress
def callback(current, total):
    global pbar
    global prev_curr
    pbar.update(current-prev_curr)
    prev_curr = current


async def get_chats():
    chats = await client.get_dialogs()
    for i, chat in enumerate(chats, start=1):
        print(f"{i}. {chat.title}")
    return chats


async def main():
    global pbar
    global prev_curr

    await client.start()

    # Kullanıcıya sohbet listesini göster
    print("Sohbet listesi:")
    chats = await get_chats()

    # Kullanıcıdan bir sohbet seçmesini iste
    selected_chat_index = int(input("Bir sohbet seçin (sayı): "))
    selected_chat = chats[selected_chat_index - 1]

    print(f"Seçilen sohbet: {selected_chat.title}")

    # Seçilen sohbetin tüm sesli ve videolu mesajlarını birleştir
    daily_date = None
    voices = []
    videos = []
    async for message in client.iter_messages(selected_chat.id, reverse=True):
        # eğer mesaj videolu mesaj veya sesli mesaj değilse geç
        if not message.video_note and not message.voice:
            continue

        # videolu mesajsa
        if message.video_note:
            video_path = f"{downloads_dir}/video_{message.id}.mp4"
            voice_path = f"{downloads_dir}/video_{message.id}.wav"

            prev_curr = 0
            pbar = tqdm(total=message.document.size, unit='B', unit_scale=True)
            await message.download_media(video_path, progress_callback=callback)
            pbar.close()
            os.system(f'ffmpeg -i {video_path} -q:a 0 -map a {voice_path}')

        # sesli mesaj varsa
        if message.voice:
            voice_path = f"{downloads_dir}/voice_{message.id}.wav"

            prev_curr = 0
            pbar = tqdm(total=message.document.size, unit='B', unit_scale=True)
            await message.download_media(voice_path, progress_callback=callback)
            pbar.close()

        # mesaj tarihi None değilse ve yeni mesaj tarihi ile aynı değilse dosyayı oluştur
        if daily_date and daily_date.date() != message.date.date():
            daily_name = daily_date.strftime("%Y-%m-%d")

            # eğer sesler varsa
            if voices:
                daily_voice_clip = concatenate_audioclips(voices)
                daily_voice_clip.write_audiofile(
                    f"{exports_dir}/{daily_name}.wav")

            # eğer videolar varsa
            if videos:
                daily_video_clip = concatenate_videoclips(videos)
                daily_video_clip.write_videofile(
                    f"{exports_dir}/{daily_name}.mp4")

            # verileri boşalt
            voices.clear()
            videos.clear()

        # videolu mesajsa
        if message.video_note:
            voices.append(AudioFileClip(voice_path))
            videos.append(VideoFileClip(video_path))

        # sesli mesaj varsa
        if message.voice:
            voices.append(AudioFileClip(voice_path))

        # tarihi yenile
        daily_date = message.date

if __name__ == "__main__":
    client.loop.run_until_complete(main())
    client.disconnect()
