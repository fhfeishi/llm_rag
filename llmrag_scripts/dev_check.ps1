$ErrorActionPreference = "Stop"

python -B -m compileall llmrag
$code = @"
from llmrag import LlmRagClient
from llmrag.cli import main

client = LlmRagClient()
index = client.index_file('README.md', summarize=False)
answer = client.ask('What is PageIndex?', index, top_k=2)
print(index.title)
print(len(index.root.children))
print(answer.query)
"@
$code | python -B -
python -B -m llmrag.cli ask --file README.md --query "What is PageIndex?" --no-summarize --output json | Out-Null
