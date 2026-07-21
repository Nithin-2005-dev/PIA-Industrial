const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface WorkspaceSummary {
  id: string;
  name: string;
  description: string;
  status: string;
  source_kind: string;
  document_count: number;
  asset_count: number;
  graph: { nodes: number; edges: number };
  ingestion_status: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, init);
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

function withWorkspace(path: string, workspaceId: string): string {
  const joiner = path.includes('?') ? '&' : '?';
  return `${path}${joiner}workspace_id=${encodeURIComponent(workspaceId)}`;
}

export const industrialApi = {
  listWorkspaces: () => request<{ workspaces: WorkspaceSummary[] }>('/api/v1/industrial/workspaces'),
  createWorkspace: (name: string, description = '') =>
    request<{ workspace: WorkspaceSummary }>('/api/v1/industrial/workspaces', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description }),
    }),
  loadDemo: (workspaceId: string) =>
    request(`/api/v1/industrial/workspaces/${encodeURIComponent(workspaceId)}/load-demo`, { method: 'POST' }),
  uploadDocument: (workspaceId: string, file: File) => {
    const body = new FormData();
    body.append('file', file);
    return request<{ job: any }>(`/api/v1/industrial/workspaces/${encodeURIComponent(workspaceId)}/documents`, {
      method: 'POST',
      body,
    });
  },
  overview: (workspaceId: string) => request<any>(withWorkspace('/api/v1/industrial/overview', workspaceId)),
  assets: (workspaceId: string) => request<any>(withWorkspace('/api/v1/industrial/assets', workspaceId)),
  asset: (workspaceId: string, assetId: string) =>
    request<any>(withWorkspace(`/api/v1/industrial/assets/${encodeURIComponent(assetId)}`, workspaceId)),
  rca: (workspaceId: string, assetId: string) =>
    request<any>(withWorkspace(`/api/v1/industrial/assets/${encodeURIComponent(assetId)}/rca`, workspaceId), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    }),
  simulation: (workspaceId: string, assetId: string) =>
    request<any>(withWorkspace(`/api/v1/industrial/assets/${encodeURIComponent(assetId)}/simulation?delay_days=30`, workspaceId), {
      method: 'POST',
    }),
  graph: (workspaceId: string) => request<any>(withWorkspace('/api/v1/industrial/graph', workspaceId)),
  documents: (workspaceId: string) => request<any>(withWorkspace('/api/v1/industrial/documents', workspaceId)),
  maintenance: (workspaceId: string) => request<any>(withWorkspace('/api/v1/industrial/maintenance', workspaceId)),
  failures: (workspaceId: string) => request<any>(withWorkspace('/api/v1/industrial/failures', workspaceId)),
  compliance: (workspaceId: string) => request<any>(withWorkspace('/api/v1/industrial/compliance', workspaceId)),
  decisions: (workspaceId: string) => request<any>(withWorkspace('/api/v1/industrial/decisions', workspaceId)),
  query: (workspaceId: string, query: string) =>
    request<any>('/api/v1/industrial/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, workspace_id: workspaceId }),
    }),
};
