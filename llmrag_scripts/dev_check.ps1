$ErrorActionPreference = "Stop"

python -B -m compileall llmrag
$code = @"
from llmrag import LlmRagClient
from llmrag.cli import main
from llmrag.llm_local import LocalLLMClient

client = LlmRagClient()
local_client = LocalLLMClient(model='local-model', base_url='http://127.0.0.1:8080/v1')
index = client.index_file('README.md', summarize=False)
answer = client.ask('What is PageIndex?', index, top_k=2)
print(index.title)
print(len(index.root.children))
print(answer.query)
print(local_client.endpoint.chat_completions_url)
"@
$code | python -B -
python -B -m llmrag.cli ask --file README.md --query "What is PageIndex?" --no-summarize --output json | Out-Null
