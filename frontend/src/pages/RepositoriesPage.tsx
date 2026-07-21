import React, { useState, useEffect, useCallback } from 'react';
import { GitBranch, RefreshCw, Plus, Loader2, Clock, CheckCircle2, XCircle, AlertCircle, HardDrive, Wifi, Activity } from 'lucide-react';
import { useTelemetryStore } from '../api/useLiveTelemetry';
import './RepositoriesPage.css';
interface SyncJob {
  job_id: string;
  repository: string;
  repository_session_id?: string | null;
  workspace_id: string | null;
  sync_mode: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  error: string | null;
  progress: Record<string, number>;
  current_operation?: string;
}

export default function RepositoriesPage() {
  const [repos, setRepos] = useState<any[]>([]);
  const [totalRepos, setTotalRepos] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showSyncForm, setShowSyncForm] = useState(false);
  const [syncRepo, setSyncRepo] = useState('');
  const [syncBranch, setSyncBranch] = useState('main');
  const [syncMode, setSyncMode] = useState('incremental');
  const [syncLimit, setSyncLimit] = useState(100);
  const [syncToken, setSyncToken] = useState('');
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState('');
  const [activeJobs, setActiveJobs] = useState<SyncJob[]>([]);
  const [history, setHistory] = useState<SyncJob[]>([]);
  
  const { events } = useTelemetryStore();

  const normalizeRepo = (repo: string) =>
    repo.trim().replace(/^https:\/\/github\.com\//, '').replace(/\.git$/, '').replace(/^\/+|\/+$/g, '').toLowerCase();

  const fetchRepos = useCallback(() => {
    setLoading(true);
    fetch('http://localhost:8000/api/v1/store/repositories')
      .then(r => r.json())
      .then(data => {
        setRepos(data.items || []);
        setTotalRepos(data.total || 0);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const fetchJobs = useCallback(() => {
    fetch('http://localhost:8000/api/v1/sync/active')
      .then(r => r.json())
      .then(data => setActiveJobs(data.jobs || []))
      .catch(() => {});

    fetch('http://localhost:8000/api/v1/sync/history?limit=10')
      .then(r => r.json())
      .then(data => setHistory(data.jobs || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchRepos();
    fetchJobs();
  }, [fetchRepos, fetchJobs]);

  // Live WebSocket updates
  useEffect(() => {
    if (events.length === 0) return;
    const lastEvent = events[events.length - 1];
    
    if (lastEvent.event_type === 'sync.started' || lastEvent.event_type === 'sync.progress') {
      setActiveJobs(prev => {
        const idx = prev.findIndex(j => j.job_id === lastEvent.job_id);
        const nextJob: SyncJob = {
          job_id: lastEvent.job_id,
          repository: lastEvent.repository,
          repository_session_id: lastEvent.repository_session_id,
          workspace_id: null,
          sync_mode: lastEvent.sync_mode || 'incremental',
          status: lastEvent.status || 'running',
          started_at: lastEvent.occurred_at,
          completed_at: null,
          error: null,
          progress: {
            commits: lastEvent.commits_processed || 0,
            total: lastEvent.commits_total || 0,
            developers: lastEvent.developers_found || 0,
            files: lastEvent.files_processed || 0,
            objects: lastEvent.objects_added || 0,
          },
          current_operation: lastEvent.current_operation || 'Syncing...'
        };
        if (idx >= 0) {
          const updated = [...prev];
          updated[idx] = { 
            ...updated[idx], 
            status: lastEvent.status || updated[idx].status,
            progress: {
              commits: lastEvent.commits_processed,
              total: lastEvent.commits_total,
              developers: lastEvent.developers_found,
              files: lastEvent.files_processed,
              objects: lastEvent.objects_added,
            },
            current_operation: lastEvent.current_operation || updated[idx].current_operation
          };
          return updated;
        }
        return [nextJob, ...prev];
      });
    } else if (lastEvent.event_type === 'sync.completed' || lastEvent.event_type === 'sync.failed') {
      setActiveJobs(prev => prev.filter(job => job.job_id !== lastEvent.job_id));
      fetchJobs();
      fetchRepos();
    }
  }, [events, fetchJobs, fetchRepos]);

  const handleSync = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!syncRepo) return;
    const repository = normalizeRepo(syncRepo);
    const alreadyRunning = activeJobs.some(job =>
      normalizeRepo(job.repository) === repository && ['pending', 'running', 'paused'].includes(job.status)
    );
    if (alreadyRunning) {
      setError('A sync is already running for this repository.');
      return;
    }
    setSyncing(true);
    setError('');
    try {
      const res = await fetch('http://localhost:8000/api/v1/sync/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository,
          branch: syncBranch,
          commit_limit: syncLimit,
          mode: syncMode,
          github_token: syncToken || undefined,
        })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to start sync');
      }
      const data = await res.json();
      setActiveJobs(prev => [{
        job_id: data.job_id,
        repository: data.repository,
        repository_session_id: data.repository_session_id,
        workspace_id: data.workspace_id || null,
        sync_mode: data.sync_mode,
        status: data.status,
        started_at: data.started_at,
        completed_at: null,
        error: null,
        progress: { commits: 0, total: 0, developers: 0, files: 0, objects: 0 }
      }, ...prev.filter(job => job.job_id !== data.job_id)]);
      setShowSyncForm(false);
      setSyncRepo('');
      // Refresh immediately
      setTimeout(() => { fetchJobs(); fetchRepos(); }, 500);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSyncing(false);
    }
  };

  const statusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 size={14} style={{ color: 'var(--accent-green)' }} />;
      case 'failed': return <XCircle size={14} style={{ color: 'var(--accent-red)' }} />;
      case 'running': return <Loader2 size={14} style={{ color: 'var(--accent-blue)', animation: 'spin 1s linear infinite' }} />;
      default: return <Clock size={14} style={{ color: 'var(--text-tertiary)' }} />;
    }
  };

  const statusBadge = (status: string) => {
    switch (status) {
      case 'completed': return 'badge--success';
      case 'failed': return 'badge--error';
      case 'running': return 'badge--info';
      default: return 'badge--neutral';
    }
  };

  const parseGitProgress = (operation: string) => {
    let phase = operation;
    let percent = null;
    let speed = null;
    let dataSize = null;
    let subCounts = null;

    const phaseMatch = operation.match(/^([^:]+):\s+(\d+)%/);
    if (phaseMatch) {
      phase = phaseMatch[1].trim();
      percent = parseInt(phaseMatch[2]);
    } else {
      const altPhaseMatch = operation.match(/^([^:]+):/);
      if (altPhaseMatch) {
        phase = altPhaseMatch[1].trim();
      }
    }

    const speedMatch = operation.match(/\|\s+([\d.]+\s+[KMG]iB\/s)/);
    if (speedMatch) {
      speed = speedMatch[1];
    }

    const dataMatch = operation.match(/,\s+([\d.]+\s+[KMG]iB)/);
    if (dataMatch) {
      dataSize = dataMatch[1];
    }

    const countsMatch = operation.match(/\(([\d]+)\/([\d]+)\)/);
    if (countsMatch) {
      subCounts = `${countsMatch[1]} / ${countsMatch[2]}`;
    }

    return { phase, percent, speed, dataSize, subCounts };
  };

  const renderJobTerminal = (job: SyncJob, styleProps: React.CSSProperties = {}) => {
    const progress = job.progress || {};
    const commits = progress.commits ?? 0;
    const total = progress.total ?? 0;
    const isCompleted = job.status === 'completed' || job.status === 'failed';
    const percent = total > 0 ? Math.min(100, Math.round((commits / total) * 100)) : (isCompleted ? 100 : 0);
    
    // Display logic for totals
    const displayTotal = total > 0 ? total : (isCompleted ? commits : '?');
    const displayRemaining = total > 0 ? Math.max(0, total - commits) : (isCompleted ? 0 : '?');

    // Calculate sync time
    let durationStr = '0s';
    if (job.started_at) {
      const start = new Date(job.started_at);
      const end = job.completed_at ? new Date(job.completed_at) : new Date();
      const durationSec = Math.floor((end.getTime() - start.getTime()) / 1000);
      if (!isNaN(durationSec) && durationSec >= 0) {
        const mins = Math.floor(durationSec / 60);
        const secs = durationSec % 60;
        durationStr = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
      }
    }

    const parsedOp = job.current_operation ? parseGitProgress(job.current_operation) : null;

    return (
      <div key={job.job_id} className="card" style={{ padding: 0, overflow: 'hidden', border: '1px solid var(--panel-border)', ...styleProps }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--panel-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-secondary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {job.status === 'running' ? (
              <Loader2 size={18} style={{ color: 'var(--accent-blue)', animation: 'spin 1s linear infinite' }} />
            ) : job.status === 'completed' ? (
              <CheckCircle2 size={18} style={{ color: 'var(--accent-green)' }} />
            ) : job.status === 'failed' ? (
              <XCircle size={18} style={{ color: 'var(--accent-red)' }} />
            ) : (
              <Clock size={18} style={{ color: 'var(--text-tertiary)' }} />
            )}
            <div>
              <h3 style={{ margin: 0, fontSize: 14, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
                {job.repository}
                <span className="badge badge--neutral" style={{ fontSize: 10 }}>{job.sync_mode}</span>
              </h3>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
                {commits} of {displayTotal} commits synced ({displayRemaining} remaining)
              </div>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div className="mono" style={{ fontSize: 12, color: 'var(--text-primary)' }}>{percent}% Overall</div>
            <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginTop: 4 }}>{job.job_id.substring(0, 8)}</div>
          </div>
        </div>
        
        {/* Overall Progress Bar */}
        <div style={{ height: 3, width: '100%', background: 'var(--bg-tertiary)' }}>
          <div style={{ 
            height: '100%', 
            width: `${percent}%`, 
            background: job.status === 'failed' ? 'var(--accent-red)' : job.status === 'completed' ? 'var(--accent-green)' : 'var(--accent-blue)',
            transition: 'width 0.3s ease-in-out'
          }} />
        </div>

        {/* Real-time Dashboard */}
        <div style={{ padding: '16px 20px', background: '#0a0a0a' }}>
          {job.status === 'running' && parsedOp ? (
            <div className="active-job-dashboard">
              <div className="dashboard-header">
                <div className="pulsing-dot"></div>
                <span style={{ color: '#fff' }}>{parsedOp.phase}</span>
              </div>
              
              {parsedOp.percent !== null && (
                <div className="sub-progress-container">
                  <div className="sub-progress-bar">
                    <div className="sub-progress-fill" style={{ width: `${parsedOp.percent}%` }}></div>
                  </div>
                  <div className="sub-progress-stats mono">
                    <span>{parsedOp.percent}%</span>
                    {parsedOp.subCounts && <span>{parsedOp.subCounts}</span>}
                  </div>
                </div>
              )}
              
              <div className="metrics-grid">
                <div className={`metric-card ${parsedOp.speed ? 'active-network' : ''}`}>
                  <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Wifi size={12} /> Network Speed
                  </div>
                  <div className="metric-value mono">
                    {parsedOp.speed ? parsedOp.speed : <span style={{ color: 'var(--text-tertiary)' }}>--</span>}
                  </div>
                </div>
                <div className="metric-card">
                  <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <HardDrive size={12} /> Downloaded
                  </div>
                  <div className="metric-value mono">
                    {parsedOp.dataSize ? parsedOp.dataSize : <span style={{ color: 'var(--text-tertiary)' }}>--</span>}
                  </div>
                </div>
                <div className="metric-card">
                  <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Activity size={12} /> Elapsed Time
                  </div>
                  <div className="metric-value mono">
                    {durationStr}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ color: '#888', fontFamily: 'monospace', fontSize: 12, padding: '8px 0' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <div>$ latent-engine sync {job.repository} --mode={job.sync_mode}</div>
                <div><span style={{color: '#888'}}>{'>'}</span> Status: {job.status.toUpperCase()}</div>
                {job.progress && Object.entries(job.progress).map(([k, v]) => (
                  <div key={k}><span style={{color: '#888'}}>{'>'}</span> {k}: {v}</div>
                ))}
                {job.current_operation && (
                  <div style={{ color: '#00AAFF', marginTop: 4, display: 'flex', gap: 8 }}>
                    <span style={{color: '#888'}}>{'>'}</span> 
                    <span>{job.current_operation}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-header__title">
          <GitBranch size={24} />
          <div>
            <h1>Repositories</h1>
            <div className="page-header__subtitle">Synced repositories and their ingestion status</div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => { fetchRepos(); fetchJobs(); }} style={{ background: 'var(--bg-tertiary)', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <RefreshCw size={14} /> Refresh
          </button>
          <button onClick={() => setShowSyncForm(true)} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <Plus size={14} /> Sync Repository
          </button>
        </div>
      </div>

      {/* Sync Form */}
      {showSyncForm && (
        <div className="card" style={{ marginBottom: 16, borderColor: 'var(--accent-blue)' }}>
          <h3 style={{ marginBottom: 16, fontSize: 14, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
            <GitBranch size={16} style={{ color: 'var(--accent-blue)' }} /> Start New Sync
          </h3>
          <form onSubmit={handleSync}>
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: 12, marginBottom: 12 }}>
              <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                <span style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', fontWeight: 600 }}>GitHub Repository</span>
                <input value={syncRepo} onChange={e => setSyncRepo(e.target.value)} placeholder="owner/repo (e.g. facebook/react)" required />
              </label>
              <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                <span style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', fontWeight: 600 }}>GitHub Token (Optional)</span>
                <input type="password" value={syncToken} onChange={e => setSyncToken(e.target.value)} placeholder="ghp_..." />
              </label>
              <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                <span style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', fontWeight: 600 }}>Branch</span>
                <input value={syncBranch} onChange={e => setSyncBranch(e.target.value)} required />
              </label>
              <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                <span style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', fontWeight: 600 }}>Mode</span>
                <select value={syncMode} onChange={e => setSyncMode(e.target.value)}>
                  <option value="incremental">Incremental</option>
                  <option value="full">Full</option>
                </select>
              </label>
              <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', fontWeight: 600 }}>Commit Limit</span>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 10, color: 'var(--text-secondary)' }}>
                    <input type="checkbox" checked={syncLimit === -1} onChange={e => setSyncLimit(e.target.checked ? -1 : 100)} />
                    All
                  </label>
                </div>
                <input type="number" value={syncLimit === -1 ? '' : syncLimit} onChange={e => setSyncLimit(parseInt(e.target.value) || 100)} min={1} disabled={syncLimit === -1} required={syncLimit !== -1} placeholder={syncLimit === -1 ? 'Unlimited' : ''} />
              </label>
            </div>
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
              <button type="button" onClick={() => setShowSyncForm(false)} style={{ background: 'transparent', border: '1px solid var(--panel-border)', color: 'var(--text-secondary)' }}>Cancel</button>
              <button type="submit" disabled={syncing} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                {syncing ? <><Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> Starting...</> : 'Start Sync'}
              </button>
            </div>
          </form>
          {error && (
            <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px', background: 'var(--accent-red-dim)', borderRadius: 'var(--radius-md)', fontSize: 12, color: 'var(--accent-red)' }}>
              <AlertCircle size={14} /> {error}
            </div>
          )}
        </div>
      )}

      {/* Active Jobs (Vercel-like Live Terminal) */}
      {activeJobs.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 24 }}>
          {activeJobs.map(job => renderJobTerminal(job))}
        </div>
      )}

      <div className="stat-row">
        <div className="stat-card">
          <div className="stat-card__label">Total Repositories</div>
          <div className="stat-card__value accent-blue">{totalRepos}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Active Syncs</div>
          <div className="stat-card__value accent-yellow">{activeJobs.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">History</div>
          <div className="stat-card__value accent-purple">{history.length}</div>
        </div>
      </div>

      {/* Repository List */}
      {loading ? (
        <div className="empty-state"><div style={{ animation: 'pulse 1.5s infinite' }}>Loading repositories...</div></div>
      ) : repos.length === 0 ? (
        <div className="empty-state">
          <GitBranch size={48} />
          <div className="empty-state__title">No repositories synced</div>
          <div className="empty-state__desc">Click "Sync Repository" to ingest a GitHub repository and begin pipeline execution.</div>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 16 }}>
          <table className="data-table">
            <thead><tr><th>Repository</th><th>Object ID</th><th>Type</th><th>Created</th><th>Live Watch</th></tr></thead>
            <tbody>
              {repos.map((r: any, i: number) => {
                const isWatching = r.metadata?.watch_mode === true;
                
                const handleToggleWatch = async () => {
                  try {
                    const res = await fetch(`http://localhost:8000/api/v1/sync/watch/${r.object_id}`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ enabled: !isWatching })
                    });
                    if (res.ok) {
                      fetchRepos();
                    }
                  } catch (e) {
                    console.error("Failed to toggle watch mode", e);
                  }
                };

                const latestJob = activeJobs.find(j => j.repository_session_id === r.object_id) || history.find(j => j.repository_session_id === r.object_id);

                return (
                  <React.Fragment key={i}>
                    <tr>
                      <td style={{ fontWeight: 500 }}>
                        <div>{r.label || r.object_id?.substring(0, 12) || '—'}</div>
                      </td>
                      <td className="mono" style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>{r.object_id?.substring(0, 16) || '—'}</td>
                      <td><span className="badge badge--success">{r.object_type || 'repository_session'}</span></td>
                      <td className="mono" style={{ fontSize: 11 }}>{r.created_at || '—'}</td>
                      <td>
                        <button 
                          onClick={handleToggleWatch}
                          className={`px-2 py-1 rounded text-xs transition-colors ${isWatching ? 'bg-blue-600/20 text-blue-400 border border-blue-500/50' : 'bg-slate-800 text-slate-400 border border-slate-700'}`}
                        >
                          {isWatching ? 'Live On' : 'Live Off'}
                        </button>
                      </td>
                    </tr>
                    {isWatching && latestJob && (
                      <tr>
                        <td colSpan={5} style={{ padding: '0 16px 16px 16px', borderBottom: '1px solid var(--panel-border)' }}>
                          {renderJobTerminal(latestJob, { border: 'none', background: 'var(--bg-primary)', boxShadow: '0 4px 20px rgba(0,0,0,0.5)', marginTop: 8 })}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Sync History */}
      {history.length > 0 && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--panel-border)' }}>
            <h3 style={{ fontSize: 13, fontWeight: 600 }}>Sync History</h3>
          </div>
          <table className="data-table">
            <thead><tr><th>Job ID</th><th>Repository</th><th>Mode</th><th>Status</th><th>Started</th><th>Completed</th></tr></thead>
            <tbody>
              {history.map(job => (
                <tr key={job.job_id}>
                  <td className="mono" style={{ fontSize: 11 }}>{job.job_id.substring(0, 12)}</td>
                  <td className="mono" style={{ fontWeight: 500 }}>{job.repository}</td>
                  <td><span className="badge badge--neutral">{job.sync_mode}</span></td>
                  <td>
                    <span className={`badge ${statusBadge(job.status)}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                      {statusIcon(job.status)} {job.status}
                    </span>
                  </td>
                  <td className="mono" style={{ fontSize: 11 }}>{job.started_at || '—'}</td>
                  <td className="mono" style={{ fontSize: 11 }}>{job.completed_at || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
