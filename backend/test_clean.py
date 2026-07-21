import os
import asyncio
from app.industrial.workspace_runtime import IndustrialWorkspaceRuntime

async def main():
    runtime = IndustrialWorkspaceRuntime()
    workspace_id = 'test-clean'
    runtime.create_workspace(workspace_id, 'Clean Workspace')
    
    # Create a dummy text file
    content = """
    This is a long report regarding P-204 pump failure.
    We found a significant maintenance activity on the primary pump P-204 so that we can ensure operations continue.
    The bearing temperature reached 80C. This is highly problematic and warrants immediate replacement.
    A post-maintenance verification is recommended after replacement and lubrication restoration.
    """
    
    with open('dummy.txt', 'wb') as f:
        f.write(content.encode('utf-8'))
        
    runtime.ingest_file(workspace_id, os.path.abspath('dummy.txt'), 'dummy.txt')
    
    queries = [
        "What failures were reported for P-204?",
        "What maintenance actions are recommended?",
        "What evidence supports the findings?"
    ]
    
    for q in queries:
        print(f"\nQ: {q}")
        result = runtime.answer_query(workspace_id, q)
        print(f"A: {result.get('answer')}")

asyncio.run(main())
