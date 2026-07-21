import { useState, useEffect } from 'react';
import { Gauge, ChevronRight } from 'lucide-react';

export default function MeasurementsPage() {
  const [measurements, setMeasurements] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedMeasurement, setSelectedMeasurement] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/store/measurements')
      .then(r => r.json())
      .then(data => {
        setMeasurements(data.items || []);
        setTotal(data.total || 0);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const openDetail = async (objectId: string) => {
    setDetailLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/store/measurements/${objectId}`);
      if (res.ok) setSelectedMeasurement(await res.json());
    } catch {}
    setDetailLoading(false);
  };

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-header__title">
          <Gauge size={24} />
          <div>
            <h1>Measurements</h1>
            <div className="page-header__subtitle">Quantitative signals extracted from repository data</div>
          </div>
        </div>
      </div>

      <div className="stat-row">
        <div className="stat-card">
          <div className="stat-card__label">Total Measurements</div>
          <div className="stat-card__value accent-blue">{total}</div>
        </div>
      </div>

      {detailLoading && (
        <div className="card mb-4" style={{ color: 'var(--text-tertiary)' }}>
          Loading measurement detail...
        </div>
      )}

      {selectedMeasurement && (
        <div className="card mb-4" style={{ borderColor: 'var(--accent-blue)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600 }}>Measurement Detail</h3>
            <button onClick={() => setSelectedMeasurement(null)} style={{ background: 'transparent', border: '1px solid var(--panel-border)', color: 'var(--text-secondary)', fontSize: 11 }}>Close</button>
          </div>

          <div className="stat-row">
            <div className="stat-card">
              <div className="stat-card__label">Metric</div>
              <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--accent-blue)' }}>{selectedMeasurement.metric_name || '—'}</div>
            </div>
            <div className="stat-card">
              <div className="stat-card__label">Value</div>
              <div className="stat-card__value accent-green" style={{ fontSize: 20 }}>{typeof selectedMeasurement.metric_value === 'number' ? selectedMeasurement.metric_value.toFixed(4) : '—'}</div>
            </div>
            <div className="stat-card">
              <div className="stat-card__label">Confidence</div>
              <div className="stat-card__value accent-yellow" style={{ fontSize: 20 }}>{selectedMeasurement.confidence != null ? (selectedMeasurement.confidence * 100).toFixed(1) + '%' : '—'}</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 6 }}>Formula</div>
              <div className="mono" style={{ fontSize: 12, color: 'var(--accent-cyan)', background: 'var(--bg-tertiary)', padding: 10, borderRadius: 'var(--radius-md)' }}>{selectedMeasurement.formula || '—'}</div>
            </div>
            <div>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 6 }}>Subject</div>
              <div className="mono" style={{ fontSize: 12 }}>{selectedMeasurement.subject_type}: {selectedMeasurement.subject_id?.substring(0, 12) || '—'}</div>
            </div>
          </div>

          {selectedMeasurement.inputs && (
            <div style={{ marginTop: 12 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 6 }}>Inputs</div>
              <pre className="mono" style={{ fontSize: 11, color: 'var(--text-secondary)', background: 'var(--bg-tertiary)', padding: 10, borderRadius: 'var(--radius-md)', whiteSpace: 'pre-wrap' }}>{JSON.stringify(selectedMeasurement.inputs, null, 2)}</pre>
            </div>
          )}

          {selectedMeasurement.algorithm && (
            <div style={{ marginTop: 12 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', marginBottom: 6 }}>Algorithm</div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                <strong>{selectedMeasurement.algorithm.name}</strong> v{selectedMeasurement.algorithm.version}
                {selectedMeasurement.algorithm.description && <span style={{ color: 'var(--text-tertiary)' }}> — {selectedMeasurement.algorithm.description}</span>}
              </div>
            </div>
          )}
        </div>
      )}

      {loading ? (
        <div className="empty-state"><div style={{ animation: 'pulse 1.5s infinite' }}>Loading measurements...</div></div>
      ) : measurements.length === 0 ? (
        <div className="empty-state">
          <Gauge size={48} />
          <div className="empty-state__title">No measurements</div>
          <div className="empty-state__desc">Measurements are generated automatically during repository sync.</div>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead><tr><th>ID</th><th>Label</th><th>Type</th><th>Created</th><th></th></tr></thead>
            <tbody>
              {measurements.slice(0, 100).map((m: any, i: number) => (
                <tr key={i} onClick={() => openDetail(m.object_id)} style={{ cursor: 'pointer' }}>
                  <td className="mono" style={{ fontSize: 11 }}>{m.object_id?.substring(0, 12) || '—'}</td>
                  <td className="truncate" style={{ maxWidth: 300 }}>{m.label || '—'}</td>
                  <td><span className="badge badge--info">{m.object_type || 'measurement'}</span></td>
                  <td className="mono" style={{ fontSize: 11 }}>{m.created_at || '—'}</td>
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
