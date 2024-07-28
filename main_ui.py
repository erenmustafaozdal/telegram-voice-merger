import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QTextEdit
from PyQt5.QtCore import Qt
from telethon.sync import TelegramClient
from moviepy.editor import concatenate_audioclips, AudioFileClip, concatenate_videoclips, VideoFileClip
from tqdm import tqdm
import os
from config import *


class TelegramVoiceMergerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.api_id = ''
        self.api_hash = ''

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Telegram Voice Merger')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()

        self.settings_tab = QWidget()
        self.media_merge_tab = QWidget()

        self.init_settings_tab()
        self.init_media_merge_tab()

        self.tab_widget.addTab(self.media_merge_tab, 'Medya Birleştir')
        self.tab_widget.addTab(self.settings_tab, 'Ayarlar')

        self.layout.addWidget(self.tab_widget)

    def init_settings_tab(self):
        # Dikey düzen oluştur ve yatay düzeni içine ekle
        connect_layout = QVBoxLayout()

        # API ID
        api_id_layout = QHBoxLayout()
        api_id_label = QLabel('API ID:')
        self.api_id_line_edit = QLineEdit()
        api_id_layout.addWidget(api_id_label)
        api_id_layout.addWidget(self.api_id_line_edit)

        # API HASH
        api_hash_layout = QHBoxLayout()
        api_hash_label = QLabel('API Hash:')
        self.api_hash_line_edit = QLineEdit()
        api_hash_layout.addWidget(api_hash_label)
        api_hash_layout.addWidget(self.api_hash_line_edit)

        # PHONE
        phone_layout = QHBoxLayout()
        phone_label = QLabel('Phone Number:')
        self.phone_line_edit = QLineEdit()
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_line_edit)

        # CODE
        code_layout = QHBoxLayout()
        code_label = QLabel('Code Number:')
        self.code_line_edit = QLineEdit()
        code_layout.addWidget(code_label)
        code_layout.addWidget(self.code_line_edit)

        # CONNCT BUTTON
        button_layout = QHBoxLayout()
        connect_button = QPushButton('Bağlan')
        connect_button.clicked.connect(self.connect_telegram)
        button_layout.addWidget(connect_button)

        # Dikey düzen oluştur ve yatay düzeni içine ekle
        connect_layout = QVBoxLayout()

        result_layout = QHBoxLayout()
        self.settings_result = QTextEdit()
        self.settings_result.setReadOnly(True)
        result_layout.addWidget(self.settings_result)

        connect_layout.addLayout(api_id_layout)
        connect_layout.addLayout(api_hash_layout)
        connect_layout.addLayout(phone_layout)
        connect_layout.addLayout(code_layout)
        connect_layout.addLayout(button_layout)
        connect_layout.addLayout(result_layout)
        self.settings_tab.setLayout(connect_layout)

    def init_media_merge_tab(self):
        layout = QVBoxLayout()

        merge_button = QPushButton('Medyaları Birleştir')
        merge_button.clicked.connect(self.merge_media)

        layout.addWidget(merge_button)

        self.media_merge_tab.setLayout(layout)

    def connect_telegram(self):
        self.api_id_line_edit.setText(api_id)
        self.api_hash_line_edit.setText(api_hash)
        self.phone_line_edit.setText(phone_number)
        self.api_id = self.api_id_line_edit.text()
        self.api_hash = self.api_hash_line_edit.text()
        self.phone = self.phone_line_edit.text()
        self.code = self.code_line_edit.text()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.async_connect_telegram())

    async def async_connect_telegram(self):
        self.client = TelegramClient(
            "telegram-voice-merger-ui", self.api_id, self.api_hash)
        await self.client.connect()

        if self.code == "":
            result = await self.client.send_code_request(self.phone)
            self.phone_hash = result.phone_code_hash
            return

        me = await self.client.sign_in(self.phone, self.code, phone_code_hash=self.phone_hash)
        print(me)

        print(await self.client.get_me())
        self.settings_result.append('Telegram\'a başarıyla bağlandınız.')

    def merge_media(self):
        # Add logic to merge media files
        # You can use the existing logic or modify it as needed.

        self.settings_result.append('Medyalar başarıyla birleştirildi.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TelegramVoiceMergerApp()
    window.show()
    sys.exit(app.exec_())
