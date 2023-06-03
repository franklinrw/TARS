import gradio as gr
import discourse as d
import memory as m

# set a custom theme
theme = gr.themes.Default().set(
    body_background_fill="#000000",
)

with gr.Blocks(theme=theme) as ui:
    with gr.Row():
        with gr.Column(scale=1):
            message = gr.Audio(source="microphone", type="filepath")
    with gr.Row():
        btn1 = gr.Button("Generate Reponse")
    with gr.Row():
        with gr.Column(scale=1):
            audio_response = gr.Audio()
    with gr.Row():
        text_response = gr.Textbox(label="Transcript", max_lines=10)
    with gr.Row():
        btn3 = gr.Button("Show Transcript")
    with gr.Row():
        btn2 = gr.Button("Save Transcript")

    btn1.click(fn=d.respond, inputs=message, outputs=audio_response)
    btn2.click(fn=m.save_as_hf_dataset)
    btn3.click(fn=d.transcript, output=text_response)

ui.launch()
