import { useState, useEffect } from 'react';
import { FolderKanban, ChevronRight } from 'lucide-react';

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/store/datasets')
      .then(r => r.json())
      .then(data => {
        setDatasets(data.items || []);
        setTotal(data.total || 0);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-header__title">
          <FolderKanban size={24} />
          <div>
            <h1>Datasets</h1>
            <div className="page-header__subtitle">Managed datasets and snapshot versions</div>
          </div>
        </div>
      </div>

      <div className="stat-row">
        <div className="stat-card">
          <div className="stat-card__label">Total Datasets</div>
          <div className="stat-card__value accent-purple">{total}</div>
        </div>
      </div>

      {loading ? (
        <div className="empty-state"><div style={{ animation: 'pulse 1.5s infinite' }}>Loading datasets...</div></div>
      ) : datasets.length === 0 ? (
        <div className="empty-state">
          <FolderKanban size={48} />
          <div className="empty-state__title">No datasets</div>
          <div className="empty-state__desc">Datasets are created when repositories are synced. Each sync produces a frozen dataset snapshot.</div>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead><tr><th>ID</th><th>Label</th><th>Type</th><th>Created</th><th></th></tr></thead>
            <tbody>
              {datasets.map((d: any, i: number) => (
                <tr key={i}>
                  <td className="mono" style={{ fontSize: 11 }}>{d.object_id?.substring(0, 12) || '—'}</td>
                  <td className="truncate" style={{ maxWidth: 300, fontWeight: 500 }}>{d.label || '—'}</td>
                  <td><span className="badge badge--info">{d.object_type || 'dataset'}</span></td>
                  <td className="mono" style={{ fontSize: 11 }}>{d.created_at || '—'}</td>
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
