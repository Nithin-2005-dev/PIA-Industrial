"""
Isolation test: run only the GitHub collection stage and time each commit fetch.
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TOKEN = os.environ.get('GITHUB_TOKEN', '')

from app.platform.core_modules import GitHubAdapterFactory
from app.observation.ingestion import ObservationIngestionEngine
from app.platform.runtime import PlatformRuntime

factory = GitHubAdapterFactory()
adapter = factory.create(TOKEN)

from dataclasses import dataclass
from typing import Any, Mapping

@dataclass
class SimpleQuery:
    identifier: str
    filters: Mapping[str, Any]

query = SimpleQuery(identifier='facebook/react', filters={'per_page': 10, 'sha': 'main'})

print('Starting collection...', flush=True)
t_total = time.time()

observations = []
for i, obs in enumerate(adapter.collect(query)):
    elapsed = time.time() - t_total
    print(f'  Commit {i+1}: {obs.observation_id[:12] if obs.observation_id else "?"} at {elapsed:.1f}s', flush=True)
    observations.append(obs)
    if i >= 9:
        break

print(f'\nTotal: {len(observations)} observations in {time.time()-t_total:.1f}s', flush=True)
print('Collection test PASSED', flush=True)
