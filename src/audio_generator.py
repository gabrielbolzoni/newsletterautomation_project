from pathlib import Path
import openai
from datetime import date
from pathlib import Path
import os
from src.content_filter import filter_news
import json
from openai import OpenAI

audio_folder_path = Path("data\\audio_files")
os.makedirs(audio_folder_path, exist_ok=True)
with open("config/credentials/api_keys.json","r") as f:
    credentials_file = json.load(f)

client = OpenAI(
    api_key=credentials_file["openAI"],
)

def generate_audio(newsletter_content: str, folder_path: str):
    source = newsletter_content["source"]
    file_name = f"{source}_{date.today().strftime('%Y_%m_%d')}.mp3"
    file_path = folder_path.joinpath(file_name)

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        instructions = """
                Você vai narrar as notícias abaixo em áudio, como se estivesse conversando com um amigo próximo.

                TOM:
                - Conversa informal, natural e envolvente.
                - Linguagem simples, como alguém contando algo interessante que acabou de ler.
                - Evite tom de locutor, telejornal ou publicidade.
                - Não soe robótico nem monótono.

                ESTILO DE FALA:
                - Varie levemente o ritmo e a entonação entre as notícias.
                - Use pausas naturais entre os blocos, como em uma conversa.
                - Demonstre curiosidade ou leve surpresa quando fizer sentido.
                - Não seja exagerado, nem teatral.

                REGRAS:
                - Não use chamadas comerciais ou frases promocionais.
                - Não adicione opiniões pessoais fortes.
                - Não invente fatos.

                FORMATO:
                - Conte cada notícia como uma história curta.
                - Separe as notícias com uma pausa perceptível, não verbal.
                - Não anuncie início ou fim do áudio.""",
        speed = 1.25,
        voice="alloy",
        input=f"""
                News Letter: {source}
                {newsletter_content["content"]}
                """
        ) as response:
                response.stream_to_file(file_path)


texto_final = filter_news(formatted_text,credentials_file)
sender = "Deschamps"

newsletter_content = {
    "source": sender,
    "content": texto_final
}

generate_audio(newsletter_content,audio_folder_path)

