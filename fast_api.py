"""
FastAPI backend for faster translation inference.
Run with: uvicorn fast_api:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import torch
import numpy as np
from transformers import SeamlessM4TModel, AutoProcessor
import io
import soundfile as sf
import torchaudio
from functools import lru_cache
import os

app = FastAPI(title="Live Translate API")

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model cache
MODEL_CACHE = {}

@lru_cache(maxsize=1)
def get_model():
    """Load and cache the model."""
    if 'model' not in MODEL_CACHE:
        print("Loading model...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model = SeamlessM4TModel.from_pretrained(
            "facebook/seamless-m4t-v2-large",
            cache_dir="./models",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            low_cpu_mem_usage=True
        )
        processor = AutoProcessor.from_pretrained(
            "facebook/seamless-m4t-v2-large",
            cache_dir="./models",
            use_fast=False
        )
        
        model = model.to(device)
        model.eval()
        
        # Compile model for faster inference (PyTorch 2.0+)
        if hasattr(torch, 'compile'):
            try:
                model = torch.compile(model, mode="reduce-overhead")
            except Exception as e:
                print(f"Could not compile model: {e}")
        
        MODEL_CACHE['model'] = model
        MODEL_CACHE['processor'] = processor
        MODEL_CACHE['device'] = device
        print(f"Model loaded on {device}")
    
    return MODEL_CACHE['model'], MODEL_CACHE['processor'], MODEL_CACHE['device']

def process_audio(audio_data, sample_rate):
    """Process audio to required format."""
    if len(audio_data.shape) > 1:
        audio_data = audio_data.mean(axis=1)
    
    if sample_rate != 16000:
        audio_tensor = torch.tensor(audio_data).unsqueeze(0)
        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
        audio_tensor = resampler(audio_tensor)
        audio_data = audio_tensor.squeeze().numpy()
    
    return audio_data

@app.get("/")
async def root():
    """Serve the main HTML interface."""
    return FileResponse("index.html")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": 'model' in MODEL_CACHE,
        "device": MODEL_CACHE.get('device', 'not loaded')
    }

@app.post("/translate")
async def translate(
    audio: UploadFile = File(...),
    src_lang: str = Form(...),
    tgt_lang: str = Form(...)
):
    """Translate audio file from source to target language."""
    try:
        # Load model
        model, processor, device = get_model()
        
        # Read audio file
        audio_bytes = await audio.read()
        audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
        
        # Process audio
        processed_audio = process_audio(audio_data, sample_rate)
        
        # Prepare inputs
        inputs = processor(audio=processed_audio, src_lang=src_lang, sampling_rate=16000, return_tensors="pt")
        inputs = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}
        
        # Generate translation - SeamlessM4T returns tuple: (text_output, audio_output)
        with torch.inference_mode():
            output = model.generate(
                **inputs,
                tgt_lang=tgt_lang,
                generate_speech=True,
                num_beams=1,
                max_new_tokens=256
            )
        
        # Output is tuple: (text_sequences, audio_waveform)
        # We want the audio waveform (second element)
        if isinstance(output, tuple) and len(output) >= 2:
            audio_output = output[1].cpu().numpy().squeeze()
            print(f"Extracted audio from tuple[1], shape: {audio_output.shape}")
        elif isinstance(output, dict) and 'waveform' in output:
            audio_output = output['waveform'].cpu().numpy().squeeze()
            print(f"Extracted audio from dict['waveform'], shape: {audio_output.shape}")
        else:
            print(f"ERROR: Unexpected output type: {type(output)}")
            return {"error": f"Unexpected output format: {type(output)}"}
        
        print(f"Audio output shape: {audio_output.shape}, dtype: {audio_output.dtype}, length: {len(audio_output)}")
        
        # Ensure audio is 1D and has data
        if len(audio_output.shape) > 1:
            audio_output = audio_output.flatten()
        
        if len(audio_output) == 0:
            print("ERROR: Generated audio is empty!")
            return {"error": "Generated audio is empty"}
        
        # Normalize audio if needed
        if audio_output.dtype != np.float32:
            audio_output = audio_output.astype(np.float32)
        
        # Convert to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, audio_output, 16000, format='WAV', subtype='PCM_16')
        buffer.seek(0)
        
        # Read back to verify
        wav_bytes = buffer.read()
        print(f"WAV file size: {len(wav_bytes)} bytes")
        
        if len(wav_bytes) == 0:
            print("ERROR: Failed to create WAV file!")
            return {"error": "Failed to create WAV file"}
        
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="audio/wav")
    
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health():
    """Health check endpoint."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return {
        "status": "healthy",
        "device": device,
        "model_loaded": 'model' in MODEL_CACHE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8600)
