FROM pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git sox libsox-dev ffmpeg curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone --depth 1 https://github.com/OpenMOSS/MOSS-TTS-Nano.git /app/moss-tts-nano && \
    cd /app/moss-tts-nano && \
    pip install --no-cache-dir --no-deps -e . && \
    pip install --no-cache-dir \
        "numpy>=1.24" "sentencepiece>=0.1.99" "transformers==4.57.1" "onnxruntime>=1.20.0" \
        fastapi uvicorn[standard] python-multipart soundfile

COPY api/ ./api/
COPY docker/scripts/entrypoint.sh .
RUN chmod +x entrypoint.sh

ENV MODEL_ID=OpenMOSS-Team/MOSS-TTS-Nano-100M \
    DEVICE=auto \
    DTYPE=auto \
    DEFAULT_VOICE=zh_1 \
    PORT=8080 \
    HF_HOME=/root/.cache/huggingface \
    HF_ENDPOINT=https://huggingface.co \
    PYTHONUNBUFFERED=1

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -sf http://localhost:${PORT}/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
