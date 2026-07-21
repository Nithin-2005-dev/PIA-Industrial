import requests, time

import os
TOKEN = os.environ.get('GITHUB_TOKEN', '')
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github+json'}

print('Fetching commits list...', flush=True)
t = time.time()
r = requests.get(
    'https://api.github.com/repos/facebook/react/commits',
    headers=headers,
    params={'per_page': 3},
    timeout=(10, 30),
)
print(f'Commits list: {r.status_code} in {time.time()-t:.1f}s', flush=True)
sha = r.json()[0]['sha']
print(f'SHA: {sha[:12]}', flush=True)

print('Fetching commit details...', flush=True)
t = time.time()
r2 = requests.get(
    f'https://api.github.com/repos/facebook/react/commits/{sha}',
    headers=headers,
    timeout=(10, 30),
)
elapsed = time.time() - t
print(f'Commit details: {r2.status_code} in {elapsed:.1f}s', flush=True)
data = r2.json()
files = data.get('files', [])
print(f'Files changed: {len(files)}', flush=True)
print('Direct API test PASSED', flush=True)
