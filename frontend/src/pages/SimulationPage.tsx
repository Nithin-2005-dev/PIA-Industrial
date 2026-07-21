import { useState } from 'react';
import { FlaskConical, Play, Users, FileCode, AlertTriangle } from 'lucide-react';

const SCENARIOS = [
  { id: 'bus-factor', icon: <Users size={16} />, title: 'Bus Factor Simulation', desc: 'Simulate what happens when a key developer leaves the project', color: 'var(--accent-red)' },
  { id: 'ownership-transfer', icon: <FileCode size={16} />, title: 'Ownership Transfer', desc: 'Model the impact of transferring file ownership between developers', color: 'var(--accent-blue)' },
  { id: 'risk-intervention', icon: <AlertTriangle size={16} />, title: 'Risk Intervention', desc: 'Predict risk reduction from proposed code review policy changes', color: 'var(--accent-yellow)' },
];

export default function SimulationPage() {
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-header__title">
          <FlaskConical size={24} />
          <div>
            <h1>Simulation</h1>
            <div className="page-header__subtitle">What-if scenario simulation and intervention modeling</div>
          </div>
        </div>
      </div>

      <div className="stat-row">
        <div className="stat-card">
          <div className="stat-card__label">Available Scenarios</div>
          <div className="stat-card__value accent-blue">{SCENARIOS.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Simulations Run</div>
          <div className="stat-card__value accent-purple">0</div>
        </div>
      </div>

      <div className="card-grid">
        {SCENARIOS.map(s => (
          <div key={s.id} className="card" style={{ cursor: 'pointer', borderColor: selectedScenario === s.id ? s.color : undefined }} onClick={() => setSelectedScenario(s.id)}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <div style={{ color: s.color }}>{s.icon}</div>
              <h3 style={{ fontSize: 14, fontWeight: 600 }}>{s.title}</h3>
            </div>
            <p style={{ fontSize: 12, color: 'var(--text-tertiary)', lineHeight: 1.6 }}>{s.desc}</p>
            <div style={{ marginTop: 12 }}>
              <button style={{ fontSize: 11, display: 'flex', alignItems: 'center', gap: 4 }}>
                <Play size={12} /> Run Simulation
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
