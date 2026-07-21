import { Fragment, useState, useEffect } from 'react';
import { Play, ChevronRight, Clock, Layers } from 'lucide-react';

interface ExecutionDetail {
  object_id: string;
  created_at: string;
  query: string;
  intent: string;
  status: string;
  capabilities_used: string[];
  measurement_ids: string[];
  evidence_ids: string[];
  reasoning_ids: string[];
  answer: string;
  confidence: number;
  total_latency_ms: number;
  stage_latencies: Record<string, number>;
  completed_at: string;
  reasoning: any[];
}

export default function ExecutionsPage() {
  const [execs, setExecs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [selectedExec, setSelectedExec] = useState<ExecutionDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/store/executions')
      .then(r => r.json())
      .then(data => {
        setExecs(data.items || []);
        setTotal(data.total || 0);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const openDetail = async (objectId: string) => {
    setDetailLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/store/executions/${objectId}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedExec(data);
      }
    } catch {}
    setDetailLoading(false);
  };

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-header__title">
          <Play size={24} />
          <div>
            <h1>Executions</h1>
            <div className="page-header__subtitle">Pipeline execution history and traces</div>
          </div>
        </div>
      </div>

      <div className="stat-row">
        <div className="stat-card">
          <div className="stat-card__label">Total Executions</div>
          <div className="stat-card__value accent-blue">{total}</div>
        </div>
      </div>

      {detailLoading && (
        <div className="card mb-4" style={{ color: 'var(--text-tertiary)' }}>
          Loading execution detail...
        </div>
      )}

      {selectedExec && (
        <div className="card mb-4" style={{ borderColor: 'var(--accent-blue)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Layers size={16} style={{ color: 'var(--accent-blue)' }} />
              Execution Detail
            </h3>
            <button onClick={() => setSelectedExec(null)} style={{ background: 'transparent', border: '1px solid var(--panel-border)', color: 'var(--text-secondary)', fontSize: 11 }}>Close</button>
          </div>

          <div className="stat-row">
            <div className="stat-card">
              <div className="stat-card__label">Status</div>
              <div className="stat-card__value accent-green" style={{ fontSize: 18 }}>{selectedExec.status || '—'}</div>
            </div>
            <div className="stat-card">
              <div className="stat-card__label">Confidence</div>
              <div className="stat-card__value accent-blue" style={{ fontSize: 18 }}>{selectedExec.confidence != null ? (selectedExec.confidence * 100).toFixed(1) + '%' : '—'}</div>
            </div>
            <div className="stat-card">
              <div className="stat-card__label">Latency</div>
              <div className="stat-card__value accent-yellow" style={{ fontSize: 18 }}>{selectedExec.total_latency_ms != null ? selectedExec.total_latency_ms + 'ms' : '—'}</div>
            </div>
            <div className="stat-card">
              <div className="stat-card__label">Measurements</div>
              <div className="stat-card__value accent-purple" style={{ fontSize: 18 }}>{selectedExec.measurement_ids?.length || 0}</div>
            </div>
          </div>

          {selectedExec.query && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 4 }}>Query</div>
              <div className="mono" style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{selectedExec.query}</div>
            </div>
          )}

          {selectedExec.answer && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 4 }}>Answer</div>
              <div style={{ fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.6 }}>{selectedExec.answer}</div>
            </div>
          )}

          {selectedExec.stage_latencies && Object.keys(selectedExec.stage_latencies).length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 8 }}>Stage Timeline</div>
              <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                {Object.entries(selectedExec.stage_latencies).map(([stage, latency], i) => (
                  <Fragment key={stage}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'var(--bg-tertiary)', padding: '4px 10px', borderRadius: 'var(--radius-md)', fontSize: 11 }}>
                      <Clock size={12} style={{ color: 'var(--accent-cyan)' }} />
                      <span style={{ color: 'var(--text-secondary)' }}>{stage}</span>
                      <span className="mono" style={{ color: 'var(--accent-yellow)' }}>{latency}ms</span>
                    </div>
                    {i < Object.entries(selectedExec.stage_latencies).length - 1 && (
                      <ChevronRight size={14} style={{ color: 'var(--text-tertiary)', alignSelf: 'center' }} />
                    )}
                  </Fragment>
                ))}
              </div>
            </div>
          )}

          {selectedExec.reasoning && selectedExec.reasoning.length > 0 && (
            <div>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 8 }}>Reasoning</div>
              <table className="data-table">
                <thead><tr><th>ID</th><th>Type</th><th>Conclusion</th><th>Confidence</th><th>Rules Fired</th></tr></thead>
                <tbody>
                  {selectedExec.reasoning.map((r: any, i: number) => (
                    <tr key={i}>
                      <td className="mono" style={{ fontSize: 11 }}>{r.reasoning_id?.substring(0, 12) || '—'}</td>
                      <td><span className="badge badge--info">{r.reasoning_type || '—'}</span></td>
                      <td style={{ maxWidth: 300 }} className="truncate">{r.conclusion || '—'}</td>
                      <td>{r.confidence != null ? (r.confidence * 100).toFixed(1) + '%' : '—'}</td>
                      <td className="mono" style={{ fontSize: 11 }}>{r.rules_fired?.join(', ') || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {loading ? (
        <div className="empty-state"><div style={{ animation: 'pulse 1.5s infinite' }}>Loading executions...</div></div>
      ) : execs.length === 0 ? (
        <div className="empty-state">
          <Play size={48} />
          <div className="empty-state__title">No executions recorded</div>
          <div className="empty-state__desc">Sync a repository to generate pipeline executions.</div>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead><tr><th>Execution</th><th>Label</th><th>Type</th><th>Created</th><th></th></tr></thead>
            <tbody>
              {execs.map((e: any, i: number) => (
                <tr key={i} onClick={() => openDetail(e.object_id)} style={{ cursor: 'pointer' }}>
                  <td className="mono" style={{ fontSize: 11 }}>{e.object_id?.substring(0, 12) || '—'}</td>
                  <td className="truncate" style={{ maxWidth: 300 }}>{e.label || '—'}</td>
                  <td><span className="badge badge--info">{e.object_type || 'execution'}</span></td>
                  <td className="mono" style={{ fontSize: 11 }}>{e.created_at || '—'}</td>
                  <td><ChevronRight size={14} style={{ color: 'var(--text-tertiary)' }} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
