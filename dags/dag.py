# dags/news_audio_pipeline.py

import json
from pathlib import Path
import os
from datetime import date
from airflow.sdk import DAG, task
from datetime import datetime
from pendulum import timezone

# ── DAG definition ──────────────────────────────────────────────────────────
with DAG(
    dag_id="news_audio_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="30 6 * * *",
    catchup=False,
    timezone=timezone("America/Sao_Paulo"),  # Airflow respects local time
    tags=["news", "audio"],
) as dag:

    @task()
    def read_emails():
        from src.email_reader import email_reader
        news_list = email_reader()
        return news_list  # retorno será serializado como XCom

    @task()
    def extract_content(news_list: list):
        from src.content_filter import extract_content_from_html
        filtered_content = extract_content_from_html(news_list)
        return filtered_content

    @task()
    def filter_content(filtered_content: list):
        from src.content_filter import filter_news
        with open("/opt/airflow/config/credentials/api_keys.json", "r") as f:
            credentials_file = json.load(f)
        cleaned_content = [filter_news(content, credentials_file) for content in filtered_content]
        return cleaned_content

    @task()
    def generate_audios(cleaned_content: list):
        from src.audio_generator import generate_audio
        with open("/opt/airflow/config/credentials/api_keys.json", "r") as f:
            credentials_file = json.load(f)

        audio_folder_path = Path("/opt/airflow/data/audio_files")
        text_folder_path = Path("/opt/airflow/data/text_files")
        os.makedirs(audio_folder_path, exist_ok=True)
        os.makedirs(text_folder_path, exist_ok=True)

        for content in cleaned_content:
            generate_audio(content, credentials_file)

    # ── Sequenciamento ───────────────────────────────────────────────────────
    news         = read_emails()
    extracted    = extract_content(news)
    cleaned      = filter_content(extracted)
    generate_audios(cleaned)