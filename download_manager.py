from tqdm import tqdm
from utils import create_directory


class DownloadManager:
    def __init__(self, client, downloads_dir='./downloads'):
        self.client = client
        self.downloads_dir = downloads_dir
        self.pbar = None
        self.prev_curr = 0

        create_directory(self.downloads_dir)

    def progress_callback(self, current, total):
        self.pbar.update(current - self.prev_curr)
        self.prev_curr = current

    async def download_media(self, message, path):
        self.prev_curr = 0
        self.pbar = tqdm(total=message.document.size,
                         unit='B', unit_scale=True)
        await message.download_media(path, progress_callback=self.progress_callback)
        self.pbar.close()
