#!/bin/bash
set -e

echo "=== MOSS-TTS-Nano-API ==="
echo "Model:  ${MODEL_ID}"
echo "Device: ${DEVICE}"
echo "Voice:  ${DEFAULT_VOICE}"
echo "Port:   ${PORT}"
echo "========================="

exec python -m uvicorn api.main:app \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --log-level info \
    --timeout-keep-alive 65
