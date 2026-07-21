import asyncio
from app.industrial.workspace_runtime import IndustrialWorkspaceRuntime

async def main():
    runtime = IndustrialWorkspaceRuntime()
    workspace_id = 'industrial-workspace-2'
    
    print(f"Reprocessing {workspace_id}...")
    runtime.reprocess_workspace(workspace_id)
    docs = runtime.documents(workspace_id)
    print(f"Done reprocessing. Documents: {len(docs)}")
    if docs:
        print(f"First doc chunks: {len(docs[0].get('chunks', []))}")
    
    queries = [
        "Summarize the key findings from the uploaded document.",
        "What failures were reported for P-204?",
    ]
    
    for q in queries:
        print(f"\nQ: {q}")
        result = runtime.answer_query(workspace_id, q)
        print(f"A: {result.get('answer')}")

asyncio.run(main())
