import openai
import os
import azure.cognitiveservices.speech as speechsdk

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

def save_context(context):
    chat_transcript = ""
    file_name = "context.txt"
    
    with open(file_name, 'w') as file:
        for message in context:
            if message['role'] != 'system':
                chat_transcript = message['role'] + ": " + message['content'] + "\n\n"
                file.write(chat_transcript)


def respond(audio:str):
    transcript = transcribe("whisper-1", audio)
    context.append({"role": "user", "content": transcript['text']})

    response = gen_response("gpt-3.5-turbo", context)
    context.append(response)
    
    gen_voice(response, "audio_response.wav")

    return "audio_response.wav"