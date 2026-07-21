import { Settings } from 'lucide-react';
import { useWorkspaceStore } from '../store/workspaceStore';

export default function SettingsPage() {
  const { workspace, updateWorkspace } = useWorkspaceStore();
  return (
    <div className="page">
      <div className="page-header"><div className="page-header__title"><Settings size={24} /><div><h1>Settings</h1><div className="page-header__subtitle">Workspace configuration and preferences</div></div></div></div>
      <div className="card" style={{ maxWidth: 600 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <label style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: 13 }}>
            <span style={{ fontWeight: 500 }}>Repository</span>
            <input value={workspace.repository} onChange={e => updateWorkspace({ repository: e.target.value })} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: 13 }}>
            <span style={{ fontWeight: 500 }}>Dataset Version</span>
            <input value={workspace.dataset} onChange={e => updateWorkspace({ dataset: e.target.value })} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: 13 }}>
            <span style={{ fontWeight: 500 }}>Branch</span>
            <input value={workspace.branch} onChange={e => updateWorkspace({ branch: e.target.value })} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: 13 }}>
            <span style={{ fontWeight: 500 }}>Commit Window</span>
            <input type="number" value={workspace.commitWindow} onChange={e => updateWorkspace({ commitWindow: parseInt(e.target.value) || 100 })} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: 13 }}>
            <span style={{ fontWeight: 500 }}>Provider</span>
            <select value={workspace.provider} onChange={e => updateWorkspace({ provider: e.target.value })}>
              <option value="sqlite">SQLite</option>
              <option value="postgres">PostgreSQL</option>
            </select>
          </label>
        </div>
      </div>
    </div>
  );
}
