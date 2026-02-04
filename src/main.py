import json
from pathlib import Path
import os
from datetime import date

from src.email_reader import (
    email_reader
)

from src.content_filter import extract_content_from_html, filter_news

from src.audio_generator import generate_audio

audio_folder_path = Path("data\\audio_files")
os.makedirs(audio_folder_path, exist_ok=True)

text_folder_path = Path("data\\text_files")
os.makedirs(text_folder_path, exist_ok=True)

with open("config/credentials/api_keys.json","r") as f:
    credentials_file = json.load(f)

news_list = email_reader()

filtered_content = extract_content_from_html(news_list)

cleaned_content = [filter_news(content,credentials_file) for content in filtered_content]


for content in cleaned_content:
    source = content["source"]
    file_name = f"{source}_{date.today().strftime('%Y_%m_%d')}.txt"
    with open(file_name, 'w', encoding='utf-8') as file:
            file.write(content["content"])
    generate_audio(content,credentials_file)