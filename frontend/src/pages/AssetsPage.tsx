import { useQuery } from '@tanstack/react-query';
import { industrialApi } from '../api/industrialApi';
import { useWorkspaceStore } from '../store/workspaceStore';

export default function AssetsPage({ onSelectAsset }: { onSelectAsset: (id: string) => void }) {
  const { workspace } = useWorkspaceStore();
  const { data, isLoading, error } = useQuery({
    queryKey: ['industrial-assets', workspace.id],
    queryFn: () => industrialApi.assets(workspace.id),
  });

  if (isLoading) return <div className="industrial-page">Loading assets...</div>;
  if (error) return <div className="industrial-page">Error loading assets</div>;

  return (
    <div className="industrial-page">
      <h1 className="industrial-title">Industrial Assets</h1>
      
      <div className="industrial-table-container" style={{ marginTop: '24px' }}>
        <table className="industrial-table">
          <thead>
            <tr>
              <th>Tag</th>
              <th>Name</th>
              <th>Type</th>
              <th>Risk Level</th>
              <th>Findings</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {data?.assets?.map((asset: any) => (
              <tr key={asset.asset_id}>
                <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-blue)' }}>{asset.equipment_tag}</td>
                <td style={{ fontWeight: 500 }}>{asset.name}</td>
                <td style={{ color: 'var(--text-secondary)' }}>{asset.asset_type}</td>
                <td>
                  <span className={`industrial-badge ${asset.risk === 'HIGH' ? 'critical' : asset.risk === 'MEDIUM' ? 'high' : 'low'}`}>
                    {asset.risk}
                  </span>
                </td>
                <td>{asset.open_findings}</td>
                <td>
                  <button 
                    onClick={() => onSelectAsset(asset.asset_id)}
                    className="industrial-btn"
                  >
                    Analyze
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {data?.assets?.length === 0 && (
          <div className="empty-state">
            <div className="empty-state__title">No assets discovered yet.</div>
            <div className="empty-state__description">Upload industrial documents and PIA will discover assets from evidence.</div>
          </div>
        )}
      </div>
    </div>
  );
}
