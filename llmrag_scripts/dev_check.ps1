$ErrorActionPreference = "Stop"

python -B -m compileall llmrag
$code = @"
from llmrag import LlmRagClient

client = LlmRagClient()
index = client.index_file('README.md', summarize=False)
answer = client.ask('What is PageIndex?', index, top_k=2)
print(index.title)
print(len(index.root.children))
print(answer.query)
"@
$code | python -B -
