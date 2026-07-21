import { ShieldCheck } from 'lucide-react';
export default function ValidationPage() {
  return (
    <div className="page">
      <div className="page-header"><div className="page-header__title"><ShieldCheck size={24} /><div><h1>Validation</h1><div className="page-header__subtitle">Frozen validation suite results and migration readiness</div></div></div></div>
      <div className="stat-row">
        <div className="stat-card"><div className="stat-card__label">Replay</div><div className="stat-card__value accent-green">100%</div></div>
        <div className="stat-card"><div className="stat-card__label">Regression</div><div className="stat-card__value accent-green">100%</div></div>
        <div className="stat-card"><div className="stat-card__label">Hash Mismatches</div><div className="stat-card__value accent-green">0</div></div>
        <div className="stat-card"><div className="stat-card__label">Decision</div><div className="stat-card__value accent-green">GO</div></div>
      </div>
      <div className="card" style={{ padding: 24 }}>
        <h3 style={{ marginBottom: 16, fontSize: 15 }}>Validated Repositories</h3>
        <table className="data-table">
          <thead><tr><th>Repository</th><th>Replay</th><th>Regression</th><th>Lineage</th><th>Status</th></tr></thead>
          <tbody>
            <tr><td className="mono">facebook/react</td><td><span className="badge badge--success">100%</span></td><td><span className="badge badge--success">100%</span></td><td><span className="badge badge--success">Complete</span></td><td><span className="badge badge--success">PASS</span></td></tr>
            <tr><td className="mono">fastapi/fastapi</td><td><span className="badge badge--success">100%</span></td><td><span className="badge badge--success">100%</span></td><td><span className="badge badge--success">Complete</span></td><td><span className="badge badge--success">PASS</span></td></tr>
            <tr><td className="mono">encode/starlette</td><td><span className="badge badge--success">100%</span></td><td><span className="badge badge--success">100%</span></td><td><span className="badge badge--success">Complete</span></td><td><span className="badge badge--success">PASS</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
