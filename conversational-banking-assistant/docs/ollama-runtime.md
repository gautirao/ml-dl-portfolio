# Ollama Local Runtime

This document explains how to set up and use Ollama as a local LLM runtime for the Conversational Banking Assistant.

## 1. Prerequisites

- **Ollama**: Install from [ollama.com](https://ollama.com/).
- **RAM**: At least 8GB (16GB recommended for 7B+ models).

## 2. Setup

1. **Start Ollama**:
   Ensure the Ollama server is running. On macOS/Windows, this is usually a tray app. On Linux, run `ollama serve`.

2. **Pull Models**:
   We recommend the following models for local development:
   ```bash
   # Primary recommendation (fast and capable)
   ollama pull qwen2.5:3b
   
   # Alternative
   ollama pull llama3.2:3b
   ```

## 3. Configuration

The application uses the following environment variables to configure the Ollama client:

- `CBA_OLLAMA_BASE_URL`: URL of the Ollama API (default: `http://localhost:11434`).
- `CBA_OLLAMA_MODEL`: Default model to use if not specified in the request (default: `qwen2.5:3b`).
- `CBA_OLLAMA_TIMEOUT_SECONDS`: Request timeout in seconds (default: `60.0`).

## 4. Manual Smoke Test (Optional)

You can verify your local Ollama setup with this optional script. This test requires a running Ollama instance and the `qwen2.5:3b` model pulled.

```python
import asyncio
from cba.llm.ollama import OllamaLlmClient
from cba.llm.client import LlmRequest, LlmMessage, LlmRole, LlmProvider

async def smoke_test():
    print("Connecting to Ollama...")
    client = OllamaLlmClient()
    
    req = LlmRequest(
        messages=[
            LlmMessage(role=LlmRole.SYSTEM, content="You are a helpful banking assistant."),
            LlmMessage(role=LlmRole.USER, content="Hello! Who are you?")
        ],
        model="qwen2.5:3b",
        provider=LlmProvider.OLLAMA
    )
    
    try:
        resp = await client.generate(req)
        print(f"\nModel: {resp.model}")
        print(f"Response: {resp.text}")
        print(f"Usage: {resp.usage}")
    except Exception as e:
        print(f"\nSmoke test failed: {e}")
        print("\nEnsure Ollama is running and model is pulled: 'ollama pull qwen2.5:3b'")

if __name__ == "__main__":
    asyncio.run(smoke_test())
```

## 5. Troubleshooting

- **Connection Refused**: Ensure Ollama is running (`ollama serve`).
- **Model Not Found**: Ensure you have pulled the model (`ollama pull <model_name>`).
- **Slow Responses**: Local LLMs depend on your CPU/GPU. Try a smaller model like `qwen2.5:0.5b` if needed.
