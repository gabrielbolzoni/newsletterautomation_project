from pathlib import Path
from datetime import date
from openai import OpenAI
from elevenlabs.client import ElevenLabs


def openAI_model(newsletter_content: dict, credentials_file, audio_parameters, audio_file_path: Path):
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
            - Não anuncie início ou fim do áudio."""

    client = OpenAI(api_key=credentials_file["openAI"])

    speed = audio_parameters["speed"]
    voice = audio_parameters["voice"]

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        instructions=instructions,
        speed=speed,
        voice=voice,
        input=newsletter_content["content"]
    ) as response:
        response.stream_to_file(audio_file_path)


def elevenLabs_model(newsletter_content: dict, credentials_file, audio_parameters, audio_file_path: Path):
    client = ElevenLabs(api_key=credentials_file["elevenLabs"])

    speed = audio_parameters["speed"]
    voice = audio_parameters["voice"]
    

    audio_stream = client.text_to_speech.convert(
        text=newsletter_content["content"],
        voice_id=voice,
        model_id="eleven_flash_v2_5",
        voice_settings={
            "stability": "0.5",
            "speed": speed,
        },
        output_format="mp3_44100_128",
    )

    with open(audio_file_path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)


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
        str: path of the generated audio, passed to the S3 upload function.
    """

    source = newsletter_content["source"]
    file_name = f"{source}_{date.today().strftime('%Y_%m_%d')}.mp3"
    audio_folder_path = Path("/opt/airflow/data/audio_files")
    audio_file_path = audio_folder_path.joinpath(file_name)


    if audio_model_config_json["model"] == "openAI":
        openAI_model(newsletter_content, credentials_file, audio_model_config_json, audio_file_path)
    elif audio_model_config_json["model"] == "elevenLabs":
        elevenLabs_model(newsletter_content, credentials_file, audio_model_config_json, audio_file_path)
    else:
        raise ValueError(f"Unsupported model: {audio_model_config_json['model']}")

    return str(audio_file_path)