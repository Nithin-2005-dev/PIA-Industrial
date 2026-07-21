import { useQuery } from '@tanstack/react-query';
import { industrialApi } from '../api/industrialApi';
import { useWorkspaceStore } from '../store/workspaceStore';

export default function DecisionsPage() {
  const { workspace } = useWorkspaceStore();
  const { data, isLoading, error } = useQuery({
    queryKey: ['industrial-decisions', workspace.id],
    queryFn: () => industrialApi.decisions(workspace.id),
  });

  if (isLoading) return <div className="industrial-page">Loading decisions...</div>;
  if (error) return <div className="industrial-page">Error loading decisions</div>;

  return (
    <div className="industrial-page">
      <h1 className="industrial-title">Decision Intelligence</h1>
      <h2 className="industrial-subtitle">Industrial Intervention Portfolio</h2>
      
      <div className="industrial-feed-list" style={{ marginTop: '32px' }}>
        {data?.interventions?.map((item: any, i: number) => (
          <div key={item.intervention_id} className="industrial-feed-item" style={{ flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <span className={`industrial-badge ${i === 0 ? 'critical' : 'high'}`}>PRIORITY {i + 1}</span>
                <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>{item.asset_id}</span>
              </div>
              <span className="industrial-badge low">Risk Reduction: {(item.risk_reduction_score * 10).toFixed(1)}</span>
            </div>
            <div style={{ fontSize: '18px', fontWeight: 600, color: '#fff' }}>{item.title}</div>
            <div style={{ color: 'var(--text-secondary)' }}>{item.description}</div>
            <div style={{ display: 'flex', gap: '24px', marginTop: '8px', fontSize: '13px' }}>
              <div><span style={{ color: 'var(--text-tertiary)' }}>Action:</span> <span style={{ color: '#fff' }}>{item.action_type}</span></div>
              <div><span style={{ color: 'var(--text-tertiary)' }}>Est. Cost:</span> <span style={{ color: '#fff' }}>${item.estimated_cost}</span></div>
              {item.compliance_impact && <div><span className="industrial-badge medium">Compliance Requirement</span></div>}
            </div>
          </div>
        ))}
        {data?.interventions?.length === 0 && (
          <div className="empty-state">
            <div className="empty-state__title">No decisions available yet.</div>
            <div className="empty-state__description">PIA needs evidence before it can recommend interventions.</div>
          </div>
        )}
      </div>
    </div>
  );
}
