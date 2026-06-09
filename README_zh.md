# MOSS-TTS-Nano-API

[English](README.md)

基于 [MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano)（复旦 OpenMOSS / MOSI.AI）的 OpenAI 兼容语音合成 API。

100M 参数。48kHz 立体声。20 种语言。支持 CPU 运行。超轻量——可与其他 GPU 服务共存。

## 功能特性

- OpenAI 兼容的 `/v1/audio/speech` 接口（JSON body）
- 100M 参数——最小的高质量 TTS 模型
- 48kHz 立体声输出（优质音频）
- 20 种语言（中文、英文、日语、韩语等）
- 声音克隆
- **CPU 推理**——无需 GPU（设置 DEVICE=cpu）
- 内置语音预设（zh_1-zh_6、en_1-en_5、jp_1-jp_5 等）
- Apache-2.0 许可

## 快速开始

```bash
docker run -d --gpus all \
  -p 8080:8080 \
  -v /mnt/user/appdata/moss-tts-nano-api/models:/root/.cache/huggingface \
  --shm-size=2g \
  --name moss-tts-nano-api \
  ghcr.io/hsiang-han/moss-tts-nano-api:latest
```

纯 CPU 运行（无需 GPU）：
```bash
docker run -d \
  -p 8080:8080 \
  -v /mnt/user/appdata/moss-tts-nano-api/models:/root/.cache/huggingface \
  -e DEVICE=cpu \
  --name moss-tts-nano-api \
  ghcr.io/hsiang-han/moss-tts-nano-api:latest
```

首次启动从 HuggingFace 下载模型。国内用户设置 `HF_ENDPOINT=https://hf-mirror.com` 加速下载。

## 使用示例

```bash
# 默认中文音色
curl -X POST http://localhost:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "你好世界", "voice": "zh_1"}' \
  --output output.wav

# 英文音色
curl -X POST http://localhost:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world!", "voice": "en_1"}' \
  --output english.wav

# 声音克隆
curl -X POST http://localhost:8080/v1/audio/speech/clone \
  -F "input=这是克隆的声音" \
  -F "ref_audio=@reference.wav" \
  --output cloned.wav

# 查看可用音色
curl http://localhost:8080/v1/voices
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/v1/audio/speech` | POST | 语音合成（JSON body，OpenAI 兼容） |
| `/v1/audio/speech/clone` | POST | 声音克隆（Form + 文件上传） |
| `/v1/voices` | GET | 列出可用语音预设 |
| `/v1/models` | GET | 列出模型 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | Swagger 文档 |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| MODEL_ID | OpenMOSS-Team/MOSS-TTS-Nano-100M | HuggingFace 模型 ID |
| DEVICE | auto | 计算设备（auto、cuda:0、cpu） |
| DTYPE | auto | 模型精度 |
| DEFAULT_VOICE | zh_1 | 默认语音预设 |
| PORT | 8080 | API 端口 |
| HF_ENDPOINT | https://huggingface.co | HuggingFace 镜像地址 |

## 硬件要求

- **GPU 模式**：任何 NVIDIA 显卡，1GB+ 显存
- **CPU 模式**：建议 4+ 核心，2GB+ 内存
- Docker（GPU 模式需 NVIDIA Container Toolkit）

## 致谢

- [MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano) — OpenMOSS（复旦大学 NLP 实验室 / MOSI.AI）

## 许可证

Apache-2.0
