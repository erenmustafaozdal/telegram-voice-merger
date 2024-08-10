import os
import subprocess
from moviepy.editor import AudioFileClip, ColorClip, concatenate_audioclips, concatenate_videoclips
from utils import create_directory


class MediaProcessor:
    def __init__(self, exports_dir='./exports'):
        self.exports_dir = exports_dir
        create_directory(self.exports_dir)

    def extract_audio_from_video(self, video_path, voice_path):
        os.system(f'ffmpeg -i {video_path} -q:a 0 -map a {voice_path}')

    def create_temp_clip(self, voice_path, video_path):
        audio_clip = AudioFileClip(voice_path)
        black_clip = ColorClip(
            size=(384, 384),
            color=(255, 255, 255),
            duration=audio_clip.duration
        )
        black_clip = black_clip.set_audio(audio_clip).set_fps(24)
        black_clip.write_videofile(
            video_path, codec="libx264", audio_codec="aac")

    def concatenate_clips(self, clips, output_path, is_audio=True):
        if is_audio:
            final_clip = concatenate_audioclips(clips)
            final_clip.write_audiofile(output_path)
        else:
            # Video kliplerini FFmpeg kullanarak birleştir
            self.concatenate_videos_ffmpeg(clips, output_path)

    def concatenate_videos_ffmpeg(self, video_paths, output_path):
        if not video_paths:
            print("Birleştirilecek video yok.")
            return

        # FFmpeg concat komutunu oluştur
        input_cmds = []
        filter_cmds = []
        for i, video_path in enumerate(video_paths):
            input_cmds.append(f"-i {video_path}")
            filter_cmds.append(f"[{i}:v:0] [{i}:a:0]")

        filter_complex = f"{' '.join(filter_cmds)} concat=n={len(video_paths)}:v=1:a=1 [v] [a]"

        # FFmpeg komutunu oluştur
        ffmpeg_cmd = (
            f"ffmpeg {' '.join(input_cmds)} "
            f"-filter_complex \"{filter_complex}\" "
            f"-map \"[v]\" -map \"[a]\" "
            f"-c:v libx264 -crf 18 -preset slow "
            f"-c:a aac -b:a 192k "
            f"-r 30 "
            f"\"{output_path}\""
        )

        # Komutu çalıştır
        try:
            subprocess.run(ffmpeg_cmd, shell=True, check=True)
            print(f"Videolar birleştirildi: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg hata verdi: {str(e)}")
