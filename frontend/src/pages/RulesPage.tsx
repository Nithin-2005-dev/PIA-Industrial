import { BookOpen } from 'lucide-react';

const RULE_FAMILIES = [
  { family: 'Ownership', rules: ['ownership_concentration.knowledge_risk', 'knowledge_risk.forecast_risk', 'forecast_risk.executive_priority'], status: 'MIGRATED' },
  { family: 'Expertise', rules: ['expertise_concentration.bus_factor', 'expertise_concentration.knowledge_risk'], status: 'MIGRATED' },
  { family: 'Review', rules: ['review_diversity.knowledge_distribution', 'knowledge_distribution.succession_readiness', 'succession_readiness.engineering_risk'], status: 'MIGRATED' },
  { family: 'Documentation', rules: ['doc.knowledge_retention', 'knowledge_retention.bus_factor', 'bus_factor.health'], status: 'MIGRATED' },
  { family: 'Velocity', rules: ['commit_velocity.coverage', 'coverage.health'], status: 'MIGRATED' },
  { family: 'Risk', rules: ['rule_spof'], status: 'MIGRATED' },
];

export default function RulesPage() {
  const totalRules = RULE_FAMILIES.reduce((sum, f) => sum + f.rules.length, 0);
  return (
    <div className="page">
      <div className="page-header"><div className="page-header__title"><BookOpen size={24} /><div><h1>Rules</h1><div className="page-header__subtitle">Rule inventory, families, and migration status</div></div></div></div>

      <div className="stat-row">
        <div className="stat-card"><div className="stat-card__label">Total Rules</div><div className="stat-card__value accent-blue">{totalRules}</div></div>
        <div className="stat-card"><div className="stat-card__label">Families</div><div className="stat-card__value accent-purple">{RULE_FAMILIES.length}</div></div>
        <div className="stat-card"><div className="stat-card__label">Migrated</div><div className="stat-card__value accent-green">{totalRules}</div></div>
        <div className="stat-card"><div className="stat-card__label">Remaining</div><div className="stat-card__value accent-green">0</div></div>
      </div>

      <div className="card">
        <table className="data-table">
          <thead><tr><th>Family</th><th>Rules</th><th>Count</th><th>Status</th></tr></thead>
          <tbody>
            {RULE_FAMILIES.map((f) => (
              <tr key={f.family}>
                <td style={{ fontWeight: 500 }}>{f.family}</td>
                <td className="mono" style={{ fontSize: 11 }}>{f.rules.join(', ')}</td>
                <td>{f.rules.length}</td>
                <td><span className="badge badge--success">{f.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
