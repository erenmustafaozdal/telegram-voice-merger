from telethon.sync import TelegramClient
from moviepy.editor import AudioFileClip, VideoFileClip
from config import api_id, api_hash, session_name, downloads_dir, exports_dir
from download_manager import DownloadManager
from media_processor import MediaProcessor
from utils import format_date, path_is_exists


async def main():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()

    # Sohbetleri al
    chats = await client.get_dialogs()
    for i, chat in enumerate(chats, start=1):
        print(f"{i}. {chat.title}")

    # Sohbet seçimi
    selected_chat_index = int(input("Bir sohbet seçin (sayı): "))
    selected_chat = chats[selected_chat_index - 1]

    print(f"Seçilen sohbet: {selected_chat.title}")

    new_downloads_dir = f"{downloads_dir}/{selected_chat.title}"
    new_exports_dir = f"{exports_dir}/{selected_chat.title}"

    download_manager = DownloadManager(client, downloads_dir=new_downloads_dir)
    media = MediaProcessor(exports_dir=new_exports_dir)

    daily_date = None
    voices, videos = [], []

    async for message in client.iter_messages(selected_chat.id, reverse=False):
        if not message.video_note and not message.voice:
            continue

        # eğer videolu mesajsa
        if message.video_note:
            video_path = f"{new_downloads_dir}/video_{message.id}.mp4"
            voice_path = f"{new_downloads_dir}/video_{message.id}.wav"

            # eğer video yoksa indir
            if not path_is_exists(video_path):
                await download_manager.download_media(message, video_path)

            # eğer yoksa videoyu sese dönüştür
            if not path_is_exists(voice_path):
                media.extract_audio_from_video(video_path, voice_path)

        # eğer sesli mesajsa
        if message.voice:
            video_path = f"{new_downloads_dir}/voice_{message.id}.mp4"
            voice_path = f"{new_downloads_dir}/voice_{message.id}.wav"

            # eğer ses dosyası yoksa indir
            if not path_is_exists(voice_path):
                await download_manager.download_media(message, voice_path)

            # eğer yoksa sesten siyah video üret
            if not path_is_exists(video_path):
                media.create_temp_clip(voice_path, video_path)

        # eğer gün değişti ise günlük dosyaları oluştur
        if daily_date and daily_date.date() != message.date.date():
            # son tarihten başladığı için videoları ve sesleri tersine çevir
            videos.reverse()
            voices.reverse()

            daily_name = format_date(daily_date)

            e_video_path = f"{new_exports_dir}/{daily_name}.mp4"
            e_voice_path = f"{new_exports_dir}/{daily_name}.wav"
            # eğer daha önce oluşturulmadıysa işlemleri yap
            if voices and not path_is_exists(e_voice_path):
                media.concatenate_clips(voices, e_voice_path, is_audio=True)

            if videos and not path_is_exists(e_video_path):
                media.concatenate_clips(videos, e_video_path, is_audio=False)

            voices.clear()
            videos.clear()

        voices.append(AudioFileClip(voice_path))
        videos.append(video_path)

        daily_date = message.date

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
