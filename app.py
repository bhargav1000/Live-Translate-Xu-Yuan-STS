import streamlit as st
import torch
import numpy as np
from transformers import SeamlessM4TModel, AutoProcessor
import io
import soundfile as sf
import streamlit.components.v1 as components

# Cache the model loading with optimizations
@st.cache_resource
def load_model():
    # Use smaller model for faster inference
    model = SeamlessM4TModel.from_pretrained(
        "facebook/seamless-m4t-large", 
        cache_dir="./models",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        low_cpu_mem_usage=True
    )
    processor = AutoProcessor.from_pretrained(
        "facebook/seamless-m4t-large", 
        cache_dir="./models", 
        use_fast=False
    )
    
    # Move to GPU if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()  # Set to evaluation mode
    
    return model, processor, device

def process_audio(audio_data, sample_rate):
    """Process audio to the required format."""
    # Convert to mono if stereo
    if len(audio_data.shape) > 1:
        audio_data = audio_data.mean(axis=1)
    
    # Resample to 16kHz if needed
    if sample_rate != 16000:
        import torchaudio
        audio_tensor = torch.tensor(audio_data).unsqueeze(0)
        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
        audio_tensor = resampler(audio_tensor)
        audio_data = audio_tensor.squeeze().numpy()
    
    return audio_data

def translate_audio(audio_data, model, processor, device, src_lang, tgt_lang):
    """Translate audio from source to target language with optimizations."""
    # Process audio input with sampling rate
    inputs = processor(audio=audio_data, src_lang=src_lang, sampling_rate=16000, return_tensors="pt")
    
    # Move inputs to device
    inputs = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}
    
    # Generate translated speech with optimizations
    with torch.inference_mode():  # Faster than torch.no_grad()
        output = model.generate(
            **inputs, 
            tgt_lang=tgt_lang, 
            generate_speech=True,
            num_beams=1,  # Greedy decoding for speed
            max_new_tokens=256  # Limit output length
        )
    
    # Extract audio from output - SeamlessM4T returns (waveform, sample_rate) tuple
    if isinstance(output, tuple):
        audio_output = output[0].cpu().numpy().squeeze()
    else:
        audio_output = output.cpu().numpy().squeeze()
    
    return audio_output

def main():
    st.set_page_config(page_title="Live Translate", page_icon="🎤", layout="centered")
    
    st.title("🎤 Walkie-Talkie Translator")
    st.caption("Press to speak, release to translate instantly")

    # Load model
    with st.spinner("Loading translation engine..."):
        model, processor, device = load_model()
    
    # Initialize session state
    if 'auto_translate' not in st.session_state:
        st.session_state.auto_translate = False
    if 'last_audio' not in st.session_state:
        st.session_state.last_audio = None

    # Language selection - compact layout
    col1, col2 = st.columns(2)
    with col1:
        src_lang = st.selectbox("🗣️ From", 
                                ["eng", "fra", "spa", "deu", "ita", "por", "rus", "cmn", "jpn", "kor"], 
                                index=0)
    with col2:
        tgt_lang = st.selectbox("🔊 To", 
                                ["eng", "fra", "spa", "deu", "ita", "por", "rus", "cmn", "jpn", "kor"], 
                                index=1)

    st.divider()

    # Walkie-talkie mode toggle
    walkie_mode = st.toggle("🚀 Walkie-Talkie Mode (Auto-translate on release)", value=True)
    
    if walkie_mode:
        st.info("🎙️ Press and hold to record, release to auto-translate!")
    else:
        st.info("🎙️ Record your voice and click translate when ready")

    # Audio input with auto-processing
    audio_bytes = st.audio_input("🎤 Press to Record")
    
    # Auto-translate logic for walkie-talkie mode
    should_translate = False
    
    if audio_bytes is not None:
        # Check if this is new audio
        current_audio_hash = hash(audio_bytes.getvalue())
        
        if st.session_state.last_audio != current_audio_hash:
            st.session_state.last_audio = current_audio_hash
            
            # Read the recorded audio
            audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes.getvalue()))
            
            # In walkie-talkie mode, translate immediately
            if walkie_mode:
                should_translate = True
                st.success("✅ Recording captured! Translating...")
            else:
                st.success("✅ Recording ready!")
                # Show original recording
                st.write("**📥 Your Recording:**")
                st.audio(audio_bytes, format='audio/wav')
                
                # Show translate button in manual mode
                if st.button("🔄 Translate Now", type="primary", use_container_width=True):
                    should_translate = True
            
            # Perform translation
            if should_translate:
                with st.spinner("⚡ Translating..."):
                    try:
                        # Process audio
                        processed_audio = process_audio(audio_data, sample_rate)
                        
                        # Translate with optimizations
                        translated_audio = translate_audio(
                            processed_audio, model, processor, device, src_lang, tgt_lang
                        )
                        
                        # Debug: Check audio shape and data
                        if len(translated_audio) == 0:
                            st.error("❌ Translation produced empty audio!")
                            st.stop()
                        
                        st.write(f"Debug: Audio shape: {translated_audio.shape}, Length: {len(translated_audio)}")
                        
                        # Convert to bytes for playback
                        buffer = io.BytesIO()
                        sf.write(buffer, translated_audio, 16000, format='WAV', subtype='PCM_16')
                        buffer.seek(0)
                        audio_bytes_out = buffer.read()
                        
                        if len(audio_bytes_out) == 0:
                            st.error("❌ Failed to create audio buffer!")
                            st.stop()

                        st.success("✅ Translation complete!")
                        st.caption(f"Translated from **{src_lang}** → **{tgt_lang}**")
                    
                    except Exception as e:
                        st.error(f"❌ Translation error: {str(e)}")
                        st.exception(e)
                        st.stop()
                    
                    # Dedicated translation playback section
                    st.divider()
                    st.write("**🔊 Translated Audio:**")
                    
                    # Translation playback and download - ALWAYS autoplay
                    col_play, col_dl = st.columns([4, 1])
                    with col_play:
                        st.audio(audio_bytes_out, format='audio/wav', autoplay=True)
                    with col_dl:
                        st.download_button(
                            label="💾 Save",
                            data=audio_bytes_out,
                            file_name=f"translated_{src_lang}_to_{tgt_lang}.wav",
                            mime="audio/wav",
                            use_container_width=True
                        )
    
    # Footer with tips
    st.divider()
    with st.expander("💡 Tips for best results"):
        st.markdown("""
        - **Speak clearly** and at a moderate pace
        - **Keep recordings short** (5-10 seconds) for faster processing
        - **Use walkie-talkie mode** for instant translation
        - **Good internet connection** helps with faster model loading
        - **Quiet environment** improves translation accuracy
        """)

if __name__ == "__main__":
    main()