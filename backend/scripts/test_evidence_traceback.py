import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import traceback
from pathlib import Path

os.environ['GITHUB_TOKEN'] = os.environ.get('GITHUB_TOKEN', '')

from app.platform.runtime import PlatformRuntime
from scripts.platform_showcase.context import PlatformContext
from app.platform.canonical_pipeline import CanonicalPlatformPipeline
from app.platform.api.contracts import RuntimePipelineInput

p = PlatformRuntime.create()
p.register_default_modules()
built = p.build()
built.initialize()
built.start()

input_req = RuntimePipelineInput(
    repository='facebook/react',
    branch='main',
    commits=2,
    github_token=os.environ['GITHUB_TOKEN'],
    tenant_id='default',
)

context = PlatformContext(
    repository=input_req.repository,
    branch=input_req.branch,
    commit_limit=input_req.commits,
    github_token=input_req.github_token,
    tenant_id=input_req.tenant_id,
    output_directory=Path('outputs/showcase'),
    runtime=built.runtime,
    service_provider=built.provider,
)

bindings = CanonicalPlatformPipeline(built)._bindings_by_runtime_order()
for binding in bindings:
    print(f"Running {binding.stage.name}...", flush=True)
    try:
        binding.stage.run(context)
    except Exception as e:
        print(f"FAILED in {binding.stage.name}:", flush=True)
        traceback.print_exc()
        break
