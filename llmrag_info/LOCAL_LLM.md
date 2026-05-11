# Local LLM

`llmrag` supports local models through an OpenAI-compatible HTTP endpoint.

This keeps inference engines decoupled from the RAG workflow:

```text
llmrag -> /v1/chat/completions -> llama.cpp / vLLM / other local server
```

## llama.cpp

Download or build `llama.cpp`, then run `llama-server` with a local GGUF model:

```powershell
.\llmrag_scripts\start_llamacpp_server.ps1 `
  -LlamaServerExe D:\tools\llama.cpp\llama-server.exe `
  -ModelPath D:\models\qwen2.5-7b-instruct-q4_k_m.gguf `
  -ContextSize 8192 `
  -Threads 8
```

Then call `llmrag`:

```powershell
.\llmrag_scripts\quickstart.ps1 `
  -File .\README.md `
  -Query "What is PageIndex?" `
  -Model "local-model" `
  -LocalBaseUrl "http://127.0.0.1:8080/v1" `
  -NoSummarize
```

`llama-server` ignores the exact model name in many setups, but `llmrag` still sends one because the OpenAI-compatible schema requires it.

## vLLM

On a GPU machine, start vLLM's OpenAI-compatible server:

```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct \
  --served-model-name qwen-local \
  --host 127.0.0.1 \
  --port 8000
```

Then call:

```powershell
python -m llmrag.cli ask `
  --file README.md `
  --query "What is PageIndex?" `
  --model qwen-local `
  --local-base-url http://127.0.0.1:8000/v1 `
  --no-summarize
```

## Python API

```python
from llmrag import LlmRagClient

client = LlmRagClient(
    model="local-model",
    local_base_url="http://127.0.0.1:8080/v1",
)

index = client.index_file("README.md", summarize=False)
answer = client.ask("What is PageIndex?", index)
print(answer.answer)
```

## Design Rule

Local runtime management belongs in scripts. `llmrag` only owns:

- request/response protocol
- retries and timeouts
- RAG workflow
- rendering and persistence

This avoids tying the package to one inference engine.
