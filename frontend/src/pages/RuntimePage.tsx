import { useState, useEffect } from 'react';
import { Activity, Database, RefreshCw, Wifi } from 'lucide-react';
import RuntimeInspector from '../features/runtime/RuntimeInspector';
import ProjectionHealthConsole from '../features/runtime/ProjectionHealthConsole';

export default function RuntimePage() {
  const [stats, setStats] = useState<Record<string, number>>({});
  const [totalRecords, setTotalRecords] = useState(0);
  const [loading, setLoading] = useState(true);
  const [rateLimit, setRateLimit] = useState<any>(null);

  const fetchStats = () => {
    setLoading(true);
    fetch('http://localhost:8000/api/v1/store/stats')
      .then(r => r.json())
      .then(data => {
        setStats(data.tables || {});
        setTotalRecords(data.total_records || 0);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    fetch('http://localhost:8000/api/v1/sync/rate-limit')
      .then(r => r.json())
      .then(data => setRateLimit(data))
      .catch(() => {});
  };

  useEffect(() => { fetchStats(); }, []);

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-header__title">
          <Activity size={24} />
          <div>
            <h1>Runtime</h1>
            <div className="page-header__subtitle">Live telemetry, database stats, and system health</div>
          </div>
        </div>
        <button onClick={fetchStats} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'var(--bg-tertiary)', color: 'var(--text-primary)' }}>
          <RefreshCw size={14} style={{ animation: loading ? 'spin 1s linear infinite' : undefined }} /> {loading ? 'Refreshing' : 'Refresh'}
        </button>
      </div>

      {/* Top-level stats */}
      <div className="stat-row">
        <div className="stat-card">
          <div className="stat-card__label">Total Records</div>
          <div className="stat-card__value accent-blue">{totalRecords.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Tables</div>
          <div className="stat-card__value accent-purple">{Object.keys(stats).length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Provider</div>
          <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--accent-cyan)' }}>SQLite</div>
        </div>
        {rateLimit && (
          <div className="stat-card">
            <div className="stat-card__label">GitHub API Rate</div>
            <div className="stat-card__value" style={{ color: rateLimit.remaining > 100 ? 'var(--accent-green)' : 'var(--accent-red)', fontSize: 20 }}>
              {rateLimit.remaining}/{rateLimit.limit}
            </div>
          </div>
        )}
      </div>

      {/* Database table stats */}
      {Object.keys(stats).length > 0 && (
        <div className="card" style={{ marginBottom: 16, padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--panel-border)' }}>
            <h3 style={{ fontSize: 13, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Database size={14} style={{ color: 'var(--accent-blue)' }} /> Database Tables
            </h3>
          </div>
          <table className="data-table">
            <thead><tr><th>Table</th><th>Records</th><th>% of Total</th></tr></thead>
            <tbody>
              {Object.entries(stats)
                .sort(([, a], [, b]) => b - a)
                .map(([table, count]) => (
                <tr key={table}>
                  <td className="mono" style={{ fontWeight: 500 }}>{table}</td>
                  <td className="mono">{count.toLocaleString()}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ flex: 1, maxWidth: 120, height: 4, background: 'var(--bg-tertiary)', borderRadius: 2, overflow: 'hidden' }}>
                        <div style={{ width: `${totalRecords > 0 ? (count / totalRecords) * 100 : 0}%`, height: '100%', background: 'var(--accent-blue)', borderRadius: 2 }} />
                      </div>
                      <span className="mono" style={{ fontSize: 11 }}>{totalRecords > 0 ? ((count / totalRecords) * 100).toFixed(1) : 0}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Existing runtime panels */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div className="card">
          <h3 style={{ marginBottom: 12, fontSize: 13, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Wifi size={14} style={{ color: 'var(--accent-green)' }} /> Runtime Inspector
          </h3>
          <RuntimeInspector />
        </div>
        <div className="card">
          <h3 style={{ marginBottom: 12, fontSize: 13, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Activity size={14} style={{ color: 'var(--accent-cyan)' }} /> Projection Health
          </h3>
          <ProjectionHealthConsole />
        </div>
      </div>
    </div>
  );
}
