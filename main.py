import streamlit as st
from gradio_client import Client, file

# Replace 'your_hf_token' with your actual Hugging Face token
hf_token = "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"

# Initialize Gradio clients with the Hugging Face token
sd_client = Client("stabilityai/stable-diffusion-3-5-large", hf_token=hf_token)
vto_client = Client("AI-Platform/Virtual-Try-On", hf_token=hf_token)

# Streamlit app
st.title("Image Generation and Virtual Try-On")

# Stable Diffusion section
st.header("Stable Diffusion")
prompt = st.text_input("Enter your prompt:", "Hello!!")
negative_prompt = st.text_input("Enter negative prompt:", "Hello!!")
seed = st.number_input("Seed:", min_value=0, value=0)
width = st.number_input("Width:", min_value=256, value=1024)
height = st.number_input("Height:", min_value=256, value=1024)
guidance_scale = st.number_input("Guidance Scale:", min_value=1.0, value=4.5)
num_inference_steps = st.number_input("Inference Steps:", min_value=1, value=40)

if st.button("Generate Image"):
    with st.spinner("Generating image..."):
        try:
            result = sd_client.predict(
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                randomize_seed=True,
                width=width,
                height=height,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                api_name="/infer"
            )
            st.image(result, caption="Generated Image", use_column_width=True)
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Virtual Try-On section
st.header("Virtual Try-On")
garment_des = st.text_input("Garment Description:", "Hello!!")
is_checked = st.checkbox("Use check for fitting?", value=True)
is_checked_crop = st.checkbox("Use cropping?", value=False)
denoise_steps = st.number_input("Denoise Steps:", min_value=1, value=30)
seed_vto = st.number_input("Seed for Try-On:", min_value=0, value=42)

# Upload background and garment images
background = st.file_uploader("Upload Background Image", type=["png", "jpg"])
garment_img = st.file_uploader("Upload Garment Image", type=["png", "jpg"])

if st.button("Try On"):
    if background and garment_img:
        with st.spinner("Processing Virtual Try-On..."):
            try:
                result_vto = vto_client.predict(
                    dict={
                        "background": file(background),
                        "layers": [],
                        "composite": None
                    },
                    garm_img=file(garment_img),
                    garment_des=garment_des,
                    is_checked=is_checked,
                    is_checked_crop=is_checked_crop,
                    denoise_steps=denoise_steps,
                    seed=seed_vto,
                    api_name="/tryon"
                )
                st.image(result_vto, caption="Virtual Try-On Result", use_column_width=True)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.error("Please upload both background and garment images.")
