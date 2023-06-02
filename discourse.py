import openai
import os
import azure.cognitiveservices.speech as speechsdk

import csv
from huggingface_hub import Repository

DATASET_REPO_URL = "https://huggingface.co/datasets/FranklinWillemen/persistent-space-dataset"
DATA_FILENAME = "data.txt"
DATA_FILE = os.path.join("data", DATA_FILENAME)
HF_TOKEN = os.environ.get("HF_TOKEN")

repo = Repository(
    local_dir="data", clone_from=DATASET_REPO_URL, use_auth_token=HF_TOKEN
)

openai.api_key = os.environ['OPEN_AI_KEY']

speech_config = speechsdk.SpeechConfig(subscription=os.environ['AZURE_SPEECH_KEY'], region="westeurope")
speech_config.speech_synthesis_voice_name = "nl-NL-ColetteNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

context = [{"role": "system", "content": 'You are a clever and helpfull conversationalist. \
                                        Respond concise and to the point. \
                                        Do not mention that you are an AI or service of any kind.'}]

def transcribe(model: str, audio: str):
    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe(model, audio_file)
    return transcript

def gen_response(model: str, context: list):
    response = openai.ChatCompletion.create(model=model, messages=context)
    return response["choices"][0]["message"]

def gen_voice(response, response_filename):
    reponse_audio = speech_synthesizer.speak_text_async(response['content']).get()
    stream = speechsdk.AudioDataStream(reponse_audio)
    stream.save_to_wav_file(response_filename)

def memory():
    with open(DATA_FILE, "a") as csvfile:
        for message in context:
            writer = csv.DictWriter(csvfile, fieldnames=["name", "message"])
            writer.writerow(
                {"name": message['role'], "message": message['content']}
            )
        commit_url = repo.push_to_hub()
        print(commit_url)
    
def respond(audio:str):
    transcript = transcribe("whisper-1", audio)
    context.append({"role": "user", "content": transcript['text']})

    response = gen_response("gpt-3.5-turbo", context)
    context.append(response)
    
    gen_voice(response, "audio_response.wav")

    return "audio_response.wav"