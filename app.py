import gradio as gr
import openai
import config
import os
import azure.cognitiveservices.speech as speechsdk

openai.api_key = os.environ['OPEN_AI_KEY']

speech_config = speechsdk.SpeechConfig(subscription=os.environ['AZURE_SPEECH_KEY'], region="westeurope")
#audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_config.speech_synthesis_voice_name = "nl-NL-ColetteNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

context = [{"role": "system", "content": 'You are a clever and helpfull conversationalist. Respond to all input in 25 words or less. Do not mention that you are an AI or service of any kind.'}]

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

def conversation(audio:str):
    transcript = transcribe("whisper-1", audio)
    context.append({"role": "user", "content": transcript['text']})

    response = gen_response("gpt-3.5-turbo", context)
    context.append(response)
    
    gen_voice(response, "voice.wav")

    chat_transcript = ""
    for message in context:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    return chat_transcript, "voice.wav"

# set a custom theme
theme = gr.themes.Default().set(
    body_background_fill="#000000",
)

with gr.Blocks(theme=theme) as ui:
    # advisor image input and microphone input
    advisor = gr.Image(value=config.TARS_LOGO).style(width=config.LOGO_IMAGE_WIDTH, height=config.LOGO_IMAGE_HEIGHT)
    audio_input = gr.Audio(source="microphone", type="filepath")

    # text transcript output and audio 
    text_output = gr.Textbox(label="Conversation Transcript")
    audio_output = gr.Audio()

    btn = gr.Button("Run")
    btn.click(fn=conversation, inputs=audio_input, outputs=[text_output, audio_output])

ui.launch()
