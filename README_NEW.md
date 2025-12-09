# Live Translate - Real-Time Speech-to-Speech Translator

🎙️ An **offline**, **real-time** speech-to-speech translator using Meta's SeamlessM4T model. Translate your voice from one language to another instantly with a modern web interface - completely offline on your local machine.

## ✨ Features

- 🎙️ **Walkie-Talkie Mode**: Press and hold to record, release to auto-translate
- ⚡ **Real-Time**: Fast inference with optimized FastAPI backend  
- 🌐 **Modern Web UI**: Beautiful HTML/JS interface with instant playback
- 🔒 **100% Offline**: No internet connection required after model download
- 🎯 **12 Languages**: English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Arabic, Hindi
- 📱 **Mobile Friendly**: Works on desktop and mobile browsers

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/bhargav1000/Live-Translate-Xu-Yuan-STS.git
cd Live-Translate-Xu-Yuan-STS

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note**: First run will download the SeamlessM4T model (~2GB) to `./models` folder.

### 2. Start the Application

**Easy way (one command):**
```bash
./start.sh
```

**Manual way:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Start the FastAPI server
uvicorn fast_api:app --host 0.0.0.0 --port 8000
```

Then open your browser to: **http://localhost:8000**

## 📖 How to Use

1. **Allow microphone access** when prompted by your browser
2. **Select languages**: Choose your source language (what you speak) and target language (translation)
3. **Enable Walkie-Talkie mode** (default) for instant translation
4. **Press and HOLD** the record button while speaking
5. **Release** to automatically translate
6. **Listen** - the translation plays immediately!

### Walkie-Talkie Mode

- **ON** (default): Press and hold to record, release to auto-translate
- **OFF**: Click once to start recording, click again to stop and translate

## 🌍 Supported Languages

| Language | Code | Language | Code |
|----------|------|----------|------|
| English | eng | Portuguese | por |
| Spanish | spa | Russian | rus |
| French | fra | Mandarin Chinese | cmn |
| German | deu | Japanese | jpn |
| Italian | ita | Korean | kor |
| Arabic | arb | Hindi | hin |

## ⚙️ Technical Details

### Architecture

```
Browser (HTML/JS)
    ↓ WebRTC Audio Capture
    ↓ HTTP POST /translate
FastAPI Server (Python)
    ↓ Audio Processing
SeamlessM4T Model (PyTorch)
    ↓ Speech-to-Speech Translation
    ↓ Return WAV Audio
Browser Auto-plays Translation
```

### Performance Optimizations

- **Model Caching**: Model stays loaded in memory between requests
- **Torch Inference Mode**: Disables gradient computation for 2x speedup
- **Greedy Decoding**: Uses `num_beams=1` for faster generation
- **Float16 Precision**: On GPU, reduces memory and increases speed
- **Audio Streaming**: Direct audio buffer processing without temp files

### Model Information

- **Model**: `facebook/seamless-m4t-v2-large`
- **Task**: Direct speech-to-speech translation (no intermediate text)
- **Cache Location**: `./models/`
- **Model Size**: ~2GB downloaded
- **License**: CC-BY-NC 4.0 (research/non-commercial use)

## 🔧 Troubleshooting

### "Cannot connect to translation API"
- Make sure FastAPI server is running: `uvicorn fast_api:app --host 0.0.0.0 --port 8000`
- Check if port 8000 is available: `lsof -i :8000`

### "Microphone access denied"
- Click the lock icon in your browser's address bar
- Allow microphone permissions
- Refresh the page

### Translation is slow
- **First translation is always slower** (model loading)
- Subsequent translations should be 2-3x faster
- GPU recommended for best performance
- Close other heavy applications

### Audio doesn't play
- Check browser console (F12) for errors
- Ensure your browser supports Web Audio API (Chrome, Firefox, Safari, Edge)
- Check system audio settings and volume

### "Address already in use" error
- Server is already running! Just open http://localhost:8000
- Or kill existing process: `lsof -ti:8000 | xargs kill -9`

## 📁 Project Structure

```
Live-Translate-Xu-Yuan-STS/
├── fast_api.py          # FastAPI backend server
├── index.html           # Modern web interface
├── start.sh             # Easy startup script
├── requirements.txt     # Python dependencies
├── app.py              # Legacy Streamlit app
├── app_fast.py         # Streamlit FastAPI client
├── main.py             # Console version
└── models/             # Model cache directory
```

## 🎯 Use Cases

- **Language Learning**: Practice pronunciation and get instant translations
- **Travel Preparation**: Test conversations before trips (works offline!)
- **Accessibility**: Help bridge language barriers in real-time
- **Research**: Experiment with speech-to-speech translation
- **Privacy**: All processing happens locally, no data sent to cloud

## 🛠️ Development

### Running in Development Mode

```bash
# FastAPI with auto-reload
uvicorn fast_api:app --reload --host 0.0.0.0 --port 8000

# View logs
tail -f nohup.out
```

### Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Test translation (requires audio file)
curl -X POST http://localhost:8000/translate \
  -F "audio=@test.wav" \
  -F "src_lang=eng" \
  -F "tgt_lang=spa" \
  --output translated.wav
```

## 📝 Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: ~5GB (model + dependencies)
- **Microphone**: Required for voice input
- **Browser**: Modern browser with Web Audio API support

## 🙏 Credits

- **Model**: Meta's [SeamlessM4T](https://ai.meta.com/research/seamless-communication/)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ML Library**: [Transformers](https://huggingface.co/transformers/) by Hugging Face

## 📄 License

This project uses Meta's SeamlessM4T model under the CC-BY-NC 4.0 license (research and non-commercial use only).

## 🐛 Issues & Contributions

Found a bug or want to contribute? Open an issue or submit a pull request on GitHub!

---

**Made with ❤️ for real-time offline translation**
