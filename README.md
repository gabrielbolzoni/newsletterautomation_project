# Newsletter-to-Audio Pipeline

## Project Objective

The goal of this project is to build a data pipeline that accesses an email inbox, extracts received newsletters, and converts their content into audio files. At the current stage, the generated audio files are stored locally. In future iterations, an additional step will be added to automatically send the audio files to a mobile device.

---

## Execution Steps

### 1. Create a Dedicated Gmail Account

Create a Gmail account that will be used exclusively to receive the desired newsletters.

### 2. Enable Gmail API Access

Follow the steps described in the official Google documentation to enable access to the Gmail API:

* Documentation: [https://developers.google.com/workspace/gmail/api/guides?hl=pt-br](https://developers.google.com/workspace/gmail/api/guides?hl=pt-br)

Make sure to generate the required credentials and save them in the following path:

```
config/credentials/credentials.json
```

This JSON file must contain the credentials necessary to authenticate and access the Gmail inbox.

### 3. Configure Newsletter Senders

Modify the `senders_query` variable in the code to include the email addresses of the senders that distribute the newsletters you want to process.

### 4. Configure API Keys

Create the file `config/credentials/api_keys.json` with the following structure:

```json
{
  "openAI": "your_api_key_here"
}
```

The API key must have sufficient credits available to run the models used in the pipeline.

The following models are currently used:

* **Text-to-Speech:** `gpt-4o-mini-tts`
* **Content Curation and Filtering:** `gpt-5-nano`

These models were selected primarily based on cost efficiency (price per token) rather than maximum performance.

### 5. Run the Pipeline

Execute the main script:

```bash
python main.py
```

---

## Outputs

For each processed newsletter, the pipeline generates two outputs:

1. **Filtered Text File**

```
data/text_files/{HH-MM-SS}.json
```

A JSON file containing the curated and filtered newsletter text that will be converted into audio.

2. **Audio File**

```
data/audio_files/{source}_{YYYY_MM_DD}.mp3
```

An MP3 file containing the newsletter content in audio format.

---

## Notes and Future Improvements

* Currently, all audio files are stored locally.
* A future enhancement will include automatically sending the generated audio files to a mobile device.
* The pipeline is designed to be modular, allowing easy extension or replacement of models and output destinations.
