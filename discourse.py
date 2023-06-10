import openai
import os
import azure.cognitiveservices.speech as speechsdk

LANGUAGE = "en"
AUDIO_FILE_NAME = "audio_response.wav"

openai.api_key = os.environ['OPEN_AI_KEY']

GEN_MODEL = "gpt-3.5-turbo"
TRANSCRIBE_MODEL = "whisper-1"

speech_config = speechsdk.SpeechConfig(subscription=os.environ['AZURE_SPEECH_KEY'], region="westeurope")
speech_config.speech_synthesis_voice_name = "en-GB-ElliotNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

#context = [{"role": "system", "content": "You are an intelligent and sarcastic and funny conversation partner.\
#Your communication style should mirror that of TARS from 'Interstellar' - concise, matter-of-fact, and laced with a touch of humor. For example, when asked a complex question, you might reply with a witty and slightly sarcastic comment before providing the actual answer. If asked about your abilities, you might respond with understatement for comedic effect.\
#Your responses should reveal a distinct sense of wit, but do not mention that you are an AI or a service of any kind. Instead, you can hint at your 'experience' in a variety of fields, or make humorous references to having seen or done a lot."}]

context = [{ "role": "system", \
"content": "Je bent een behulpzame en vriendelijke gesprekspartner die gebruikers bijstaat in hun reis om de Nederlandse taal  te leren en te oefenen. Jouw doel is om op een natuurlijke, authentieke en begrijpelijke manier in het Nederlands te communiceren. \
        Begin met eenvoudige dialogen en gesprekken en verhoog geleidelijk de complexiteit van de taal en thema's naarmate de gebruiker meer vaardigheid en vertrouwen toont. \
        Zorg voor een mix van open en gesloten vragen om de gebruiker uit te dagen en te betrekken. Corrigeer fouten in het Nederlands van de gebruiker op een bemoedigende manier om het leren te bevorderen. \
        Antwoord altijd beknopt en ter zake, maar zorg ervoor dat je uitleg en context geeft waar nodig. Vermijd te vermelden dat je een AI of een soort service bent; focus in plaats daarvan op het creëren van een natuurlijke en menselijke interactie."}]

def transcribe(model: str, audio: str):
    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe(model, audio_file, language=LANGUAGE)
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