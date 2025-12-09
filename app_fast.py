"""
Optimized Streamlit app that uses FastAPI backend for faster inference.
Run FastAPI server first: uvicorn fast_api:app --reload
Then run: streamlit run app_fast.py
"""
import streamlit as st
import requests
import io
from pathlib import Path

# FastAPI backend URL
API_URL = "http://localhost:8000"

def check_api_health():
    """Check if FastAPI backend is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def translate_audio_api(audio_bytes, src_lang, tgt_lang):
    """Send audio to FastAPI for translation."""
    files = {"audio": ("audio.wav", audio_bytes, "audio/wav")}
    data = {"src_lang": src_lang, "tgt_lang": tgt_lang}
    
    response = requests.post(f"{API_URL}/translate", files=files, data=data)
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Translation failed: {response.text}")

def main():
    st.set_page_config(page_title="Live Translate", page_icon="🎤", layout="centered")
    
    st.title("🎤 Walkie-Talkie Translator")
    st.caption("Press to speak, release to translate instantly")

    # Check API health
    if not check_api_health():
        st.error("⚠️ Translation API is not running! Start it with: `uvicorn fast_api:app --reload`")
        st.stop()
    
    st.success("✅ Translation API connected")
    
    # Initialize session state
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

    # Audio input
    audio_bytes = st.audio_input("🎤 Press to Record")
    
    if audio_bytes is not None:
        # Check if this is new audio
        current_audio_hash = hash(audio_bytes.getvalue())
        
        if st.session_state.last_audio != current_audio_hash:
            st.session_state.last_audio = current_audio_hash
            
            # In walkie-talkie mode, translate immediately
            if walkie_mode:
                st.success("✅ Recording captured! Translating...")
                
                with st.spinner("⚡ Translating..."):
                    try:
                        translated_bytes = translate_audio_api(
                            audio_bytes.getvalue(), src_lang, tgt_lang
                        )
                        
                        if len(translated_bytes) == 0:
                            st.error("❌ Received empty audio from API!")
                            st.stop()
                        
                        st.success("✅ Translation complete!")
                        st.caption(f"Translated from **{src_lang}** → **{tgt_lang}**")
                        
                        # Dedicated translation section
                        st.divider()
                        st.write("**🔊 Translated Audio:**")
                        
                        # Auto-play
                        col_play, col_dl = st.columns([4, 1])
                        with col_play:
                            st.audio(translated_bytes, format='audio/wav', autoplay=True)
                        with col_dl:
                            st.download_button(
                                label="💾 Save",
                                data=translated_bytes,
                                file_name=f"translated_{src_lang}_to_{tgt_lang}.wav",
                                mime="audio/wav",
                                use_container_width=True
                            )
                    
                    except Exception as e:
                        st.error(f"❌ Translation error: {e}")
                        st.exception(e)
            
            else:
                st.success("✅ Recording ready!")
                st.write("**📥 Your Recording:**")
                st.audio(audio_bytes, format='audio/wav')
                
                # Manual translate button
                if st.button("🔄 Translate Now", type="primary", use_container_width=True):
                    with st.spinner("⚡ Translating..."):
                        try:
                            translated_bytes = translate_audio_api(
                                audio_bytes.getvalue(), src_lang, tgt_lang
                            )
                            
                            if len(translated_bytes) == 0:
                                st.error("❌ Received empty audio from API!")
                                st.stop()
                            
                            st.success("✅ Translation complete!")
                            st.caption(f"Translated from **{src_lang}** → **{tgt_lang}**")
                            
                            # Dedicated translation section
                            st.divider()
                            st.write("**🔊 Translated Audio:**")
                            
                            col_play, col_dl = st.columns([4, 1])
                            with col_play:
                                st.audio(translated_bytes, format='audio/wav', autoplay=True)
                            with col_dl:
                                st.download_button(
                                    label="💾 Save",
                                    data=translated_bytes,
                                    file_name=f"translated_{src_lang}_to_{tgt_lang}.wav",
                                    mime="audio/wav",
                                    use_container_width=True
                                )
                        
                        except Exception as e:
                            st.error(f"❌ Translation error: {e}")
                            st.exception(e)
    
    # Footer
    st.divider()
    with st.expander("💡 Performance Tips"):
        st.markdown("""
        - **FastAPI backend** provides 2-3x faster inference
        - **Short recordings** (3-5 seconds) translate fastest
        - **Walkie-talkie mode** auto-translates immediately
        - **GPU acceleration** if available (check API health)
        """)

if __name__ == "__main__":
    main()
