import torch
import numpy as np
import sounddevice as sd
from transformers import SeamlessM4TModel, AutoProcessor

def main():
    # Load the model and processor
    print("Loading model... This may take a while on first run.")
    model = SeamlessM4TModel.from_pretrained("facebook/seamless-m4t-v2-large", cache_dir="./models")
    processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large", cache_dir="./models", use_fast=False)

    while True:
        # Get user input for languages
        src_lang = input("Enter source language code (e.g., 'eng' for English, or 'quit' to exit): ").strip()
        if src_lang.lower() == 'quit':
            break
        tgt_lang = input("Enter target language code (e.g., 'fra' for French): ").strip()

        # Audio recording parameters
        fs = 16000  # Sample rate
        duration = 5  # Duration in seconds

        print("Recording for 5 seconds... Speak now!")
        # Record audio
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()
        audio = audio.flatten()

        # Process the audio
        inputs = processor(audios=audio, src_lang=src_lang, return_tensors="pt")

        # Generate translated speech
        print("Translating...")
        output = model.generate(**inputs, tgt_lang=tgt_lang, generate_speech=True)

        # Extract the audio output
        audio_output = output[0].cpu().numpy()

        # Play the translated audio
        print("Playing translated speech...")
        sd.play(audio_output, samplerate=fs)
        sd.wait()
        print("Done. Ready for next translation.")

if __name__ == "__main__":
    main()