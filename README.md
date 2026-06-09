# MOSS-TTS-Nano-API

[中文文档](README_zh.md)

OpenAI-compatible TTS API powered by [MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano) (Fudan OpenMOSS / MOSI.AI).

100M parameters. 48kHz stereo. 20 languages. Runs on CPU or GPU. Ultra-lightweight — can coexist with other GPU services.

## Features

- OpenAI-compatible `/v1/audio/speech` endpoint (JSON body)
- 100M parameters — smallest high-quality TTS model
- 48kHz stereo output (superior audio quality)
- 20 languages including Chinese, English, Japanese, Korean
- Voice cloning from reference audio
- **CPU inference** — no GPU required (set DEVICE=cpu)
- Built-in voice presets (zh_1-zh_6, en_1-en_5, jp_1-jp_5, etc.)
- Apache-2.0 license

## Quick Start

```bash
docker run -d --gpus all \
  -p 8080:8080 \
  -v /mnt/user/appdata/moss-tts-nano-api/models:/root/.cache/huggingface \
  --shm-size=2g \
  --name moss-tts-nano-api \
  ghcr.io/hsiang-han/moss-tts-nano-api:latest
```

CPU-only (no GPU needed):
```bash
docker run -d \
  -p 8080:8080 \
  -v /mnt/user/appdata/moss-tts-nano-api/models:/root/.cache/huggingface \
  -e DEVICE=cpu \
  --name moss-tts-nano-api \
  ghcr.io/hsiang-han/moss-tts-nano-api:latest
```

First start downloads model from HuggingFace. China users: set `HF_ENDPOINT=https://hf-mirror.com`.

## Usage Examples

```bash
# Default Chinese voice
curl -X POST http://localhost:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "你好世界", "voice": "zh_1"}' \
  --output output.wav

# English voice
curl -X POST http://localhost:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world!", "voice": "en_1"}' \
  --output english.wav

# Voice cloning
curl -X POST http://localhost:8080/v1/audio/speech/clone \
  -F "input=这是克隆的声音" \
  -F "ref_audio=@reference.wav" \
  --output cloned.wav

# List available voices
curl http://localhost:8080/v1/voices
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/audio/speech` | POST | Text-to-speech (JSON, OpenAI-compatible) |
| `/v1/audio/speech/clone` | POST | Voice cloning (Form + file upload) |
| `/v1/voices` | GET | List available voice presets |
| `/v1/models` | GET | List models |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger documentation |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| MODEL_ID | OpenMOSS-Team/MOSS-TTS-Nano-100M | HuggingFace model ID |
| DEVICE | auto | Compute device (auto, cuda:0, cpu) |
| DTYPE | auto | Model precision |
| DEFAULT_VOICE | zh_1 | Default voice preset |
| PORT | 8080 | API server port |
| HF_ENDPOINT | https://huggingface.co | HuggingFace mirror |

## Hardware Requirements

- **GPU mode**: Any NVIDIA GPU with 1GB+ VRAM
- **CPU mode**: 4+ cores recommended, 2GB+ RAM
- Docker (with NVIDIA Container Toolkit for GPU mode)

## Credits

- [MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano) by OpenMOSS (Fudan University NLP Lab / MOSI.AI)

## License

Apache-2.0
