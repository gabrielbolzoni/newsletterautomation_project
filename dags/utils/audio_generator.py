from pathlib import Path
from datetime import date
from pathlib import Path
from openai import OpenAI


def generate_audio(newsletter_content: dict, credentials_file, audio_model_config_json: dict):
    """
    Converts newsletter content into an MP3 audio file using
    text-to-speech API, streaming the result directly to disk.

    Builds the output filename from the newsletter source and today's date,
    then streams the synthesized speech to the Airflow audio files directory.
    Model, voice, and speed are fully configurable via the config argument.

    Args:
        newsletter_content (dict):
            newsletter content after being formatted by the AI model
        credentials_file:
            json file containing the necessary API keys
        audio_model_config_json (dict):
            dictionary with the TTS model configuration (model, voice, speed)

    Returns:
        file_path: path of the generated audio.It is passed to the function responsible for sending the audio to the S3 bucket.
    """
    client = OpenAI(
    api_key=credentials_file["openAI"],
        )    
    model = audio_model_config_json["model"]
    speed = audio_model_config_json["speed"]
    voice = audio_model_config_json["voice"]

    source = newsletter_content["source"]
    file_name = f"{source}_{date.today().strftime('%Y_%m_%d')}.mp3"
    audio_folder_path = Path("/opt/airflow/data/audio_files")
    file_path = audio_folder_path.joinpath(file_name)
    with client.audio.speech.with_streaming_response.create(
        model = model ,
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
        speed = speed,
        voice= voice,
        input=f"""
                News Letter: {source}
                {newsletter_content["content"]}
                """
        ) as response:
                response.stream_to_file(file_path)
                
    return str(file_path)


