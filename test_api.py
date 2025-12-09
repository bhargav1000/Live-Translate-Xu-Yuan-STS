#!/usr/bin/env python3
import requests
import soundfile as sf
import numpy as np
import io

# Create a simple test audio (1 second of silence at 16kHz)
test_audio = np.zeros(16000, dtype=np.float32)

# Write to WAV bytes
buffer = io.BytesIO()
sf.write(buffer, test_audio, 16000, format='WAV')
buffer.seek(0)

# Send to API
files = {"audio": ("test.wav", buffer, "audio/wav")}
data = {"src_lang": "eng", "tgt_lang": "fra"}

print("Sending test request to API...")
response = requests.post("http://localhost:8000/translate", files=files, data=data)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
print(f"Response size: {len(response.content)} bytes")

if response.status_code == 200 and 'audio' in response.headers.get('content-type', ''):
    print("SUCCESS! Got audio back")
    # Save it
    with open('/tmp/test_output.wav', 'wb') as f:
        f.write(response.content)
    print("Saved to /tmp/test_output.wav")
else:
    print(f"ERROR: {response.text}")
