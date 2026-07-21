import { useQuery } from '@tanstack/react-query';
import { industrialApi } from '../api/industrialApi';
import { useWorkspaceStore } from '../store/workspaceStore';

export default function IndustrialOverviewPage() {
  const { workspace } = useWorkspaceStore();
  const { data, isLoading, error } = useQuery({
    queryKey: ['industrial-overview', workspace.id],
    queryFn: () => industrialApi.overview(workspace.id),
  });

  if (isLoading) return <div className="industrial-page">Loading overview...</div>;
  if (error) return <div className="industrial-page">Error loading overview</div>;

  return (
    <div className="industrial-page">
      <h1 className="industrial-title">PIA Industrial</h1>
      <h2 className="industrial-subtitle">{workspace.name} Knowledge Intelligence</h2>
      
      <div className="industrial-grid-5">
        <div className="industrial-metric-card">
          <div className="industrial-metric-label">Total Assets</div>
          <div className="industrial-metric-value">{data?.metrics?.total_assets}</div>
        </div>
        <div className="industrial-metric-card danger">
          <div className="industrial-metric-label">Assets At Risk</div>
          <div className="industrial-metric-value danger">{data?.metrics?.assets_at_risk}</div>
        </div>
        <div className="industrial-metric-card danger">
          <div className="industrial-metric-label">Critical Assets</div>
          <div className="industrial-metric-value danger">{data?.metrics?.critical_assets}</div>
        </div>
        <div className="industrial-metric-card warning">
          <div className="industrial-metric-label">Open Recommendations</div>
          <div className="industrial-metric-value warning">{data?.metrics?.open_recommendations}</div>
        </div>
        <div className="industrial-metric-card warning">
          <div className="industrial-metric-label">Active Compliance Gaps</div>
          <div className="industrial-metric-value warning">{data?.metrics?.active_compliance_gaps}</div>
        </div>
      </div>

      <h3 className="industrial-section-title">Intelligence Feed</h3>
      <div className="industrial-feed-list">
        {data?.feed?.map((item: any, i: number) => (
          <div key={i} className="industrial-feed-item">
            <div className={`industrial-badge ${item.severity === 'CRITICAL' ? 'critical' : item.severity === 'HIGH' ? 'high' : 'medium'}`}>
              {item.type}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>{item.asset_id}</div>
              <div style={{ color: 'var(--text-secondary)' }}>{item.description}</div>
              <div style={{ marginTop: 8, fontSize: '12px', color: 'var(--accent-blue)', cursor: 'pointer' }}>{item.action}</div>
            </div>
          </div>
        ))}
        {data?.feed?.length === 0 && (
          <div className="empty-state">
            <div className="empty-state__title">No industrial knowledge has been ingested yet.</div>
            <div className="empty-state__description">Upload documents from the Documents page, or load the P-101 demo dataset in a demo workspace.</div>
          </div>
        )}
      </div>
    </div>
  );
}
