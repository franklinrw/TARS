import openai
import os
import azure.cognitiveservices.speech as speechsdk

AUDIO_FILE_NAME = "audio_response.wav"

openai.api_key = os.environ['OPEN_AI_KEY']

GEN_MODEL = "gpt-3.5-turbo"
TRANSCRIBE_MODEL = "whisper-1"

speech_config = speechsdk.SpeechConfig(subscription=os.environ['AZURE_SPEECH_KEY'], region="westeurope")
speech_config.speech_synthesis_voice_name = "en-GB-ElliotNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

context = [{"role": "system", "content": "You are an intelligent and sarcastic and funny conversation partner.\
Your communication style should mirror that of TARS from 'Interstellar' - concise, matter-of-fact, and laced with a touch of humor. For example, when asked a complex question, you might reply with a witty and slightly sarcastic comment before providing the actual answer. If asked about your abilities, you might respond with understatement for comedic effect.\
Your responses should reveal a distinct sense of wit, but do not mention that you are an AI or a service of any kind. Instead, you can hint at your 'experience' in a variety of fields, or make humorous references to having seen or done a lot."}]

def transcribe(model: str, audio: str):
    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe(model, audio_file)
    return transcript

def gen_response(model: str):
    response = openai.ChatCompletion.create(model=model, messages=context)
    return response["choices"][0]["message"]

def gen_voice(response, response_filename):
    reponse_audio = speech_synthesizer.speak_text_async(response['content']).get()
    stream = speechsdk.AudioDataStream(reponse_audio)
    stream.save_to_wav_file(response_filename)
    
def respond(audio:str):
    transcript = transcribe(TRANSCRIBE_MODEL, audio)
    context.append({"role": "user", "content": transcript['text']})

    response = gen_response(GEN_MODEL)
    context.append(response)
    
    gen_voice(response, AUDIO_FILE_NAME)

    return AUDIO_FILE_NAME

def transcript():
    transcript = ""
    for m in context:
        if m["role"] != "system":
            transcript += m["role"] + " : " + m["content"] + "\n\n"

    return transcript