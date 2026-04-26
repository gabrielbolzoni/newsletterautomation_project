# dags/news_audio_pipeline.py

import json
from pathlib import Path
import os
from airflow.sdk import DAG, task
from datetime import datetime
from airflow.models import Variable

# Na DAG ou na task
audio_model_config = Variable.get("audio_model_config")
audio__model_config_json = json.loads(audio_model_config)
bucket_name = Variable.get("s3_bucket_name")

# ── DAG definition ──────────────────────────────────────────────────────────
with DAG(
    dag_id="news_audio_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["news", "audio"],
) as dag:

    @task()
    def read_emails():
        from utils.email_reader import email_reader
        news_list = email_reader()
        return news_list 

    @task()
    def extract_content(news_list: list):
        from utils.content_filter import extract_content_from_html
        filtered_content = extract_content_from_html(news_list)
        return filtered_content

    @task()
    def filter_content(filtered_content: list):
        from utils.content_filter import filter_news
        with open("/opt/airflow/config/credentials/api_keys.json", "r") as f:
            credentials_file = json.load(f)
        cleaned_content = [filter_news(content, credentials_file) for content in filtered_content]
        return cleaned_content

    @task()
    def generate_audios(cleaned_content: list, audio__model_config_json: dict):
        from utils.audio_generator import generate_audio
        with open("/opt/airflow/config/credentials/api_keys.json", "r") as f:
            credentials_file = json.load(f)

        audio_folder_path = Path("/opt/airflow/data/audio_files")
        text_folder_path = Path("/opt/airflow/data/text_files")
        os.makedirs(audio_folder_path, exist_ok=True)
        os.makedirs(text_folder_path, exist_ok=True)

        paths = [generate_audio(content, credentials_file, audio__model_config_json) for content in cleaned_content]
        return paths    
    @task
    def send_audio(paths: list, bucket_name: str):
        from utils.audio_sender import upload_file
        with open("/opt/airflow/config/credentials/api_keys.json", "r") as f:
            credentials_file = json.load(f)

        for path in paths:
            object_name = os.path.basename(path)
            upload_file(credentials_file,path,bucket_name,object_name)
    @task
    def teste(audio_config_json):
        print(audio_config_json)
        print(type(audio_config_json))
        
        

    # ── Sequenciamento ───────────────────────────────────────────────────────
    news         = read_emails()
    extracted    = extract_content(news)
    cleaned      = filter_content(extracted)
    audio_files  = generate_audios(cleaned,audio__model_config_json)
    send_audio(audio_files,bucket_name)
    