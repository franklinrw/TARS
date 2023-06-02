import gradio as gr
import discourse as d

# set a custom theme
theme = gr.themes.Default().set(
    body_background_fill="#000000",
)

with gr.Blocks(theme=theme) as ui:
    # advisor image input and microphone input
    # advisor = gr.Image(value=config.TARS_LOGO).style(width=config.LOGO_IMAGE_WIDTH, height=config.LOGO_IMAGE_HEIGHT)
    message = gr.Audio(source="microphone", type="filepath")
    audio_response = gr.Audio()

    # text transcript output and audio 
    # text_output = gr.Textbox(label="Transcript")

    btn1 = gr.Button("Respond")
    btn1.click(fn=d.respond, inputs=message, outputs=[audio_response])

    btn2 = gr.Button("Save Conversation")
    btn2.click(fn=d.memory)

ui.launch()
