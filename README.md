# Live-Translate-Xu-Yuan-STS

A local, offline speech-to-speech translator using SeamlessM4T model with walkie-talkie mode for instant translation.

## Features

- 🎤 **Walkie-Talkie Mode**: Press to record, release to auto-translate
- ⚡ **Fast Inference**: Optimized with FastAPI backend for 2-3x speed improvement
- 🔒 **100% Offline**: Runs entirely on your local machine after setup
- 🌍 **Multi-language**: Support for 10+ languages
- 🎯 **Preserves Intonation**: Maintains speaker's voice characteristics

## Requirements

- Python 3.8+
- 4GB+ RAM (8GB+ recommended)
- Microphone for voice input

## Quick Start

### 1. Installation

```bash
git clone https://github.com/bhargav1000/Live-Translate-Xu-Yuan-STS.git
cd Live-Translate-Xu-Yuan-STS

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

First run will download the model (~2GB) to `./models` folder.

### 2. Usage Options

#### Option A: Standard Mode (All-in-one)
```bash
streamlit run app.py
```
- Integrated solution, slower inference
- Best for: Single user, simple setup

#### Option B: Fast Mode (Recommended)
```bash
# Terminal 1 - Start API server
uvicorn fast_api:app --reload

# Terminal 2 - Start UI
streamlit run app_fast.py
```
- 2-3x faster translation
- Best for: Better performance, multiple users

#### Option C: Console Mode
```bash
python main.py
```
- Command-line interface
- Fixed 5-second recording intervals

## Supported Languages

| Code | Language | Code | Language |
|------|----------|------|----------|
| eng  | English  | por  | Portuguese |
| fra  | French   | rus  | Russian |
| spa  | Spanish  | cmn  | Mandarin |
| deu  | German   | jpn  | Japanese |
| ita  | Italian  | kor  | Korean |

## Performance Tips

1. **Use Fast Mode**: FastAPI backend provides significant speed boost
2. **Short Clips**: 3-5 second recordings translate fastest
3. **GPU**: CUDA-enabled GPU will accelerate inference (auto-detected)
4. **Walkie-Talkie**: Enable for immediate translation on release

## Architecture

- **Model**: SeamlessM4T-large (Meta AI)
- **Backend**: FastAPI with PyTorch optimizations
- **Frontend**: Streamlit with custom audio components
- **Inference**: torch.inference_mode() + beam search optimization

## Troubleshooting

**Slow inference?**
- Use Fast Mode (Option B)
- Use smaller audio clips
- Check if GPU is detected: visit `http://localhost:8000/health`

**Model not loading?**
- Ensure 4GB+ free RAM
- Check `./models` directory has write permissions

**Audio issues?**
- Grant microphone permissions in browser
- Test with file upload first
- Check system audio settings

## Project Structure

```
├── app.py           # Standard Streamlit app
├── app_fast.py      # Optimized Streamlit app (FastAPI client)
├── fast_api.py      # FastAPI backend server
├── main.py          # Console version
├── models/          # Cached model files (auto-created)
└── requirements.txt # Python dependencies
```

## License

MIT License - see repository for details
