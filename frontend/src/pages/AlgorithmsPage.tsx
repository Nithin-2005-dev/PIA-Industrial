import { useState, useEffect } from 'react';
import { Cpu, ChevronRight, ChevronDown, Zap, Clock, AlertCircle } from 'lucide-react';

interface AlgorithmData {
  algorithm_id: string;
  name: string;
  version: string;
  description: string;
  formula: string;
  inputs: { name: string; type: string; description: string; required?: boolean }[];
  outputs: { name: string; type: string; description: string }[];
  normalization: any;
  thresholds: any;
  consumers: string[];
  tags: string[];
  deprecated: boolean;
  superseded_by: string | null;
  diagnostics: { avg_latency_ms: number; avg_memory_mb: number; execution_count: number; failure_count: number };
}

export default function AlgorithmsPage() {
  const [algorithms, setAlgorithms] = useState<AlgorithmData[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/registry/algorithms')
      .then(r => r.json())
      .then(data => {
        setAlgorithms(data.algorithms || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const toggle = (id: string) => setExpandedId(expandedId === id ? null : id);

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-header__title">
          <Cpu size={24} />
          <div>
            <h1>Algorithms</h1>
            <div className="page-header__subtitle">Registered measurement, evidence, and reasoning algorithms</div>
          </div>
        </div>
      </div>

      <div className="stat-row">
        <div className="stat-card">
          <div className="stat-card__label">Total Algorithms</div>
          <div className="stat-card__value accent-blue">{algorithms.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Total Executions</div>
          <div className="stat-card__value accent-green">{algorithms.reduce((sum, a) => sum + (a.diagnostics?.execution_count || 0), 0)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Failures</div>
          <div className="stat-card__value accent-red">{algorithms.reduce((sum, a) => sum + (a.diagnostics?.failure_count || 0), 0)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Deprecated</div>
          <div className="stat-card__value accent-yellow">{algorithms.filter(a => a.deprecated).length}</div>
        </div>
      </div>

      {loading ? (
        <div className="empty-state"><div style={{ animation: 'pulse 1.5s infinite' }}>Loading algorithms...</div></div>
      ) : algorithms.length === 0 ? (
        <div className="empty-state">
          <Cpu size={48} />
          <div className="empty-state__title">No algorithms registered</div>
          <div className="empty-state__desc">Algorithm registrations happen during platform initialization.</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {algorithms.map(algo => (
            <div key={algo.algorithm_id} className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <div
                onClick={() => toggle(algo.algorithm_id)}
                style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', cursor: 'pointer', transition: 'background 150ms' }}
              >
                {expandedId === algo.algorithm_id ? <ChevronDown size={14} style={{ color: 'var(--text-tertiary)' }} /> : <ChevronRight size={14} style={{ color: 'var(--text-tertiary)' }} />}
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontWeight: 600, fontSize: 13 }}>{algo.name}</span>
                    <span className="badge badge--neutral">v{algo.version}</span>
                    {algo.deprecated && <span className="badge badge--warning">Deprecated</span>}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-tertiary)', marginTop: 2 }}>{algo.description}</div>
                </div>
                <div style={{ display: 'flex', gap: 16, fontSize: 11, color: 'var(--text-tertiary)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Zap size={12} /> {algo.diagnostics?.execution_count || 0} runs</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Clock size={12} /> {algo.diagnostics?.avg_latency_ms?.toFixed(1) || '—'}ms</span>
                  {(algo.diagnostics?.failure_count || 0) > 0 && (
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--accent-red)' }}><AlertCircle size={12} /> {algo.diagnostics.failure_count} failures</span>
                  )}
                </div>
              </div>

              {expandedId === algo.algorithm_id && (
                <div style={{ padding: '0 16px 16px', borderTop: '1px solid var(--panel-border)' }}>
                  {algo.formula && (
                    <div style={{ marginTop: 12 }}>
                      <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 4, fontWeight: 600 }}>Formula</div>
                      <div className="mono" style={{ fontSize: 12, color: 'var(--accent-cyan)', background: 'var(--bg-tertiary)', padding: '8px 12px', borderRadius: 'var(--radius-md)' }}>{algo.formula}</div>
                    </div>
                  )}

                  {algo.inputs && algo.inputs.length > 0 && (
                    <div style={{ marginTop: 12 }}>
                      <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 6, fontWeight: 600 }}>Inputs</div>
                      <table className="data-table">
                        <thead><tr><th>Name</th><th>Type</th><th>Description</th><th>Required</th></tr></thead>
                        <tbody>
                          {algo.inputs.map((inp, j) => (
                            <tr key={j}>
                              <td className="mono" style={{ fontSize: 12 }}>{inp.name}</td>
                              <td><span className="badge badge--neutral">{inp.type}</span></td>
                              <td style={{ fontSize: 12 }}>{inp.description}</td>
                              <td>{inp.required ? <span className="badge badge--success">Yes</span> : <span className="badge badge--neutral">No</span>}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {algo.outputs && algo.outputs.length > 0 && (
                    <div style={{ marginTop: 12 }}>
                      <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 6, fontWeight: 600 }}>Outputs</div>
                      <table className="data-table">
                        <thead><tr><th>Name</th><th>Type</th><th>Description</th></tr></thead>
                        <tbody>
                          {algo.outputs.map((out, j) => (
                            <tr key={j}>
                              <td className="mono" style={{ fontSize: 12 }}>{out.name}</td>
                              <td><span className="badge badge--neutral">{out.type}</span></td>
                              <td style={{ fontSize: 12 }}>{out.description}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: 24, marginTop: 12 }}>
                    {algo.tags && algo.tags.length > 0 && (
                      <div>
                        <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 4, fontWeight: 600 }}>Tags</div>
                        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                          {algo.tags.map(tag => <span key={tag} className="badge badge--info">{tag}</span>)}
                        </div>
                      </div>
                    )}
                    {algo.consumers && algo.consumers.length > 0 && (
                      <div>
                        <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 4, fontWeight: 600 }}>Consumers</div>
                        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                          {algo.consumers.map(c => <span key={c} className="badge badge--neutral">{c}</span>)}
                        </div>
                      </div>
                    )}
                  </div>

                  <div style={{ marginTop: 12 }}>
                    <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 4, fontWeight: 600 }}>ID</div>
                    <div className="mono" style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>{algo.algorithm_id}</div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
