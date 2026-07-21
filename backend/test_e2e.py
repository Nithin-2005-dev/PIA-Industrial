import os
import asyncio
from app.industrial.workspace_runtime import IndustrialWorkspaceRuntime

async def main():
    if os.path.exists('data/knowledge/demo-p101-knowledge.json'):
        os.remove('data/knowledge/demo-p101-knowledge.json')

    runtime = IndustrialWorkspaceRuntime()
    # It will automatically reload the demo dataset
    
    queries = [
        "Summarize the key findings.",
        "What failures were reported for P-204?",
        "What maintenance actions are recommended?",
        "What evidence supports the findings?",
        "Which assets are discussed?"
    ]
    
    for q in queries:
        print(f"\nQ: {q}")
        result = runtime.answer_query('demo-p101', q)
        print(f"A: {result.get('answer')}")

asyncio.run(main())
