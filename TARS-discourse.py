import gradio as gr
import openai
import config
import os
import pyttsx3
import azure.cognitiveservices.speech as speechsdk

openai.api_key = config.OPENAI_API_KEY

speech_config = speechsdk.SpeechConfig(subscription=config.AZURE_VOICE_KEY, region=config.AZURE_VOICE_LOCATION)
speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

messages = [{"role": "system", "content": 'You are a clever and helpfull conversationalist. Respond to all input in 25 words or less. Do not mention that you are an AI or service of any kind.'}]

def transcribe(audio: str):
    global messages

    audio_filename_with_extension = audio + '.wav'
    os.rename(audio, audio_filename_with_extension)
    
    audio_file = open(audio_filename_with_extension, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    messages.append({"role": "user", "content": transcript["text"]})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    system_message = response["choices"][0]["message"]
    messages.append(system_message)

    # engine = pyttsx3.init()
    # engine.say(system_message['content'])
    # engine.runAndWait()

    result = speech_synthesizer.speak_text_async(system_message['content']).get()

    # Checks result.
    # if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    #     print("Speech synthesized to speaker for text [{}]".format(text))
    # elif result.reason == speechsdk.ResultReason.Canceled:
    #     cancellation_details = result.cancellation_details
    #     print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    #     if cancellation_details.reason == speechsdk.CancellationReason.Error:
    #         if cancellation_details.error_details:
    #             print("Error details: {}".format(cancellation_details.error_details))
    #     print("Did you update the subscription info?")

    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    return chat_transcript

# set a custom theme
theme = gr.themes.Default().set(
    body_background_fill="#000000",
)

with gr.Blocks(theme=theme) as ui:
    # advisor image input and microphone input
    advisor = gr.Image(value=config.ADVISOR_IMAGE).style(width=config.ADVISOR_IMAGE_WIDTH, height=config.ADVISOR_IMAGE_HEIGHT)
    audio_input = gr.Audio(source="microphone", type="filepath")

    # text transcript output and audio 
    text_output = gr.Textbox(label="Conversation Transcript")
    audio_output = gr.Audio()

    btn = gr.Button("Run")
    btn.click(fn=transcribe, inputs=audio_input, outputs=[text_output, audio_output])

ui.launch(debug=True, share=True)
