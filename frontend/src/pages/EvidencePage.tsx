import { useState, useEffect } from 'react';
import { FileSearch, ChevronRight } from 'lucide-react';

export default function EvidencePage() {
  const [evidence, setEvidence] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedEvidence, setSelectedEvidence] = useState<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/store/evidence')
      .then(r => r.json())
      .then(data => {
        setEvidence(data.items || []);
        setTotal(data.total || 0);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const openDetail = async (objectId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/store/evidence/${objectId}`);
      if (res.ok) setSelectedEvidence(await res.json());
    } catch {}
  };

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-header__title">
          <FileSearch size={24} />
          <div>
            <h1>Evidence</h1>
            <div className="page-header__subtitle">Interpreted signals that support reasoning</div>
          </div>
        </div>
      </div>

      <div className="stat-row">
        <div className="stat-card">
          <div className="stat-card__label">Total Evidence</div>
          <div className="stat-card__value accent-green">{total}</div>
        </div>
      </div>

      {selectedEvidence && (
        <div className="card mb-4" style={{ borderColor: 'var(--accent-green)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600 }}>Evidence Detail</h3>
            <button onClick={() => setSelectedEvidence(null)} style={{ background: 'transparent', border: '1px solid var(--panel-border)', color: 'var(--text-secondary)', fontSize: 11 }}>Close</button>
          </div>

          <div className="stat-row">
            <div className="stat-card">
              <div className="stat-card__label">Type</div>
              <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--accent-green)' }}>{selectedEvidence.evidence_type || '—'}</div>
            </div>
            <div className="stat-card">
              <div className="stat-card__label">Confidence</div>
              <div className="stat-card__value accent-yellow" style={{ fontSize: 20 }}>{selectedEvidence.confidence != null ? (selectedEvidence.confidence * 100).toFixed(1) + '%' : '—'}</div>
            </div>
            <div className="stat-card">
              <div className="stat-card__label">Measurements</div>
              <div className="stat-card__value accent-blue" style={{ fontSize: 20 }}>{selectedEvidence.measurement_ids?.length || 0}</div>
            </div>
            <div className="stat-card">
              <div className="stat-card__label">Commits</div>
              <div className="stat-card__value accent-purple" style={{ fontSize: 20 }}>{selectedEvidence.commit_ids?.length || 0}</div>
            </div>
          </div>

          {selectedEvidence.summary && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 4 }}>Summary</div>
              <div style={{ fontSize: 13, lineHeight: 1.6, color: 'var(--text-primary)' }}>{selectedEvidence.summary}</div>
            </div>
          )}

          {selectedEvidence.content && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 4 }}>Content</div>
              <pre className="mono" style={{ fontSize: 11, color: 'var(--text-secondary)', background: 'var(--bg-tertiary)', padding: 10, borderRadius: 'var(--radius-md)', whiteSpace: 'pre-wrap', maxHeight: 300, overflowY: 'auto' }}>{typeof selectedEvidence.content === 'string' ? selectedEvidence.content : JSON.stringify(selectedEvidence.content, null, 2)}</pre>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 4 }}>Subject</div>
              <div className="mono" style={{ fontSize: 12 }}>{selectedEvidence.subject_type}: {selectedEvidence.subject_id?.substring(0, 12) || '—'}</div>
            </div>
            <div>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 4 }}>Object ID</div>
              <div className="mono" style={{ fontSize: 11 }}>{selectedEvidence.object_id || '—'}</div>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="empty-state"><div style={{ animation: 'pulse 1.5s infinite' }}>Loading evidence...</div></div>
      ) : evidence.length === 0 ? (
        <div className="empty-state">
          <FileSearch size={48} />
          <div className="empty-state__title">No evidence</div>
          <div className="empty-state__desc">Evidence is derived from measurements during pipeline execution.</div>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead><tr><th>ID</th><th>Label</th><th>Type</th><th>Created</th><th></th></tr></thead>
            <tbody>
              {evidence.slice(0, 100).map((e: any, i: number) => (
                <tr key={i} onClick={() => openDetail(e.object_id)} style={{ cursor: 'pointer' }}>
                  <td className="mono" style={{ fontSize: 11 }}>{e.object_id?.substring(0, 12) || '—'}</td>
                  <td className="truncate" style={{ maxWidth: 300 }}>{e.label || '—'}</td>
                  <td><span className="badge badge--success">{e.object_type || 'evidence'}</span></td>
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
