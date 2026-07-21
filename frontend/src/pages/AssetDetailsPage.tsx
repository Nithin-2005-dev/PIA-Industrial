import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { industrialApi } from '../api/industrialApi';
import { useWorkspaceStore } from '../store/workspaceStore';

export default function AssetDetailsPage({ assetId, onBack }: { assetId: string, onBack: () => void }) {
  const { workspace } = useWorkspaceStore();
  const [activeTab, setActiveTab] = useState('overview');
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['industrial-asset', workspace.id, assetId],
    queryFn: () => industrialApi.asset(workspace.id, assetId),
  });

  const { data: rcaData } = useQuery({
    queryKey: ['industrial-asset-rca', workspace.id, assetId],
    queryFn: () => industrialApi.rca(workspace.id, assetId),
    enabled: activeTab === 'rca',
  });

  const { data: simData } = useQuery({
    queryKey: ['industrial-asset-sim', workspace.id, assetId],
    queryFn: () => industrialApi.simulation(workspace.id, assetId),
    enabled: activeTab === 'simulation',
  });

  if (isLoading) return <div className="industrial-page">Loading Asset {assetId}...</div>;
  if (error) return <div className="industrial-page">Error loading asset</div>;

  return (
    <div className="industrial-page" style={{ display: 'flex', flexDirection: 'column' }}>
      <div style={{ marginBottom: '16px' }}>
        <button className="industrial-btn" onClick={onBack}>&larr; Back to Assets</button>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 className="industrial-title">{data?.profile?.equipment_tag} - {data?.profile?.name}</h1>
          <div className="industrial-subtitle">{data?.profile?.asset_type} | Status: {data?.profile?.operational_status}</div>
        </div>
        <div className={`industrial-badge ${data?.profile?.risk === 'HIGH' ? 'critical' : data?.profile?.risk === 'MEDIUM' ? 'high' : 'low'}`} style={{ fontSize: '14px', padding: '8px 12px' }}>
          RISK: {data?.profile?.risk}
        </div>
      </div>

      <div style={{ display: 'flex', borderBottom: '1px solid var(--panel-border)', marginBottom: '24px', gap: '24px' }}>
        {['overview', 'timeline', 'rca', 'simulation'].map(tab => (
          <div 
            key={tab} 
            onClick={() => setActiveTab(tab)}
            style={{ 
              paddingBottom: '12px', 
              cursor: 'pointer',
              color: activeTab === tab ? 'var(--accent-blue)' : 'var(--text-secondary)',
              borderBottom: activeTab === tab ? '2px solid var(--accent-blue)' : '2px solid transparent',
              textTransform: 'capitalize',
              fontWeight: activeTab === tab ? 600 : 400,
            }}
          >
            {tab === 'rca' ? 'RCA' : tab}
          </div>
        ))}
      </div>

      <div style={{ flex: 1, overflowY: 'auto' }}>
        {activeTab === 'overview' && (
          <div className="industrial-grid-5">
            <div className="industrial-metric-card">
              <div className="industrial-metric-label">Confidence</div>
              <div className="industrial-metric-value safe">{(data?.profile?.confidence * 100).toFixed(0)}%</div>
            </div>
            <div className="industrial-metric-card warning">
              <div className="industrial-metric-label">Open Findings</div>
              <div className="industrial-metric-value warning">{data?.profile?.open_recommendations?.length}</div>
            </div>
            <div className="industrial-metric-card danger">
              <div className="industrial-metric-label">Compliance Gaps</div>
              <div className="industrial-metric-value danger">{data?.compliance?.gaps?.length}</div>
            </div>
          </div>
        )}

        {activeTab === 'timeline' && (
          <div>
            <h3 className="industrial-section-title">Operational Timeline</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', position: 'relative', paddingLeft: '24px', borderLeft: '2px solid var(--panel-border)' }}>
              {data?.timeline?.map((evt: any) => (
                <div key={evt.event_id} style={{ position: 'relative' }}>
                  <div style={{ position: 'absolute', left: '-31px', top: '4px', width: '12px', height: '12px', borderRadius: '50%', background: 'var(--accent-blue)' }} />
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>{new Date(evt.date).toLocaleDateString()}</div>
                  <div style={{ fontWeight: 600, color: '#fff', marginBottom: '4px' }}>{evt.event_type}</div>
                  <div style={{ color: 'var(--text-secondary)' }}>{evt.description}</div>
                  {evt.source_document_id && (
                    <div style={{ fontSize: '11px', color: 'var(--accent-cyan)', marginTop: '4px', cursor: 'pointer' }}>
                      Evidence: {evt.source_document_id}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'rca' && (
          <div>
            <h3 className="industrial-section-title">Causal Root Cause Analysis</h3>
            {rcaData ? (
              <div className="industrial-feed-list">
                {rcaData.root_causes?.map((rc: any) => (
                  <div key={rc.hypothesis_id} className="industrial-feed-item" style={{ flexDirection: 'column', gap: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                      <span className="industrial-badge critical">ROOT CAUSE</span>
                      <span style={{ color: 'var(--text-secondary)' }}>Confidence: {(rc.score * 100).toFixed(0)}%</span>
                    </div>
                    <div style={{ fontSize: '16px', fontWeight: 600, color: '#fff' }}>{rc.target}</div>
                    <div style={{ marginTop: '8px' }}>
                      <div className="industrial-metric-label">Supporting Evidence ({rc.evidence_count})</div>
                      <ul style={{ paddingLeft: '16px', color: 'var(--text-secondary)', fontSize: '13px' }}>
                        {rc.evidence?.map((e: any, i: number) => (
                          <li key={i}>{e.description}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
                {rcaData.root_causes?.length === 0 && (
                  <div className="empty-state">
                    <div className="empty-state__title">NO SUPPORTED CAUSAL HYPOTHESIS</div>
                    <div className="empty-state__description">PIA needs stronger causal evidence before producing RCA output.</div>
                  </div>
                )}
                
                <div className="industrial-metric-card" style={{ marginTop: '16px' }}>
                  <div className="industrial-metric-label">Recommended Investigation</div>
                  {rcaData.recommendations?.map((r: string, i: number) => (
                    <div key={i} style={{ color: '#fff', marginBottom: '4px' }}>- {r}</div>
                  ))}
                </div>
              </div>
            ) : (
              <div>Running RCA...</div>
            )}
          </div>
        )}

        {activeTab === 'simulation' && (
          <div>
            <h3 className="industrial-section-title">Counterfactual Simulation</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
              Counterfactuals are shown only when this workspace has enough asset history.
            </p>
            {simData ? (
              simData.status === 'INSUFFICIENT EVIDENCE' ? (
                <div className="empty-state">
                  <div className="empty-state__title">Counterfactual unavailable</div>
                  <div className="empty-state__description">{simData.message}</div>
                </div>
              ) : (
              <div style={{ display: 'flex', gap: '24px' }}>
                <div className="industrial-metric-card" style={{ flex: 1 }}>
                  <div className="industrial-metric-label">BASELINE RISK SCORE</div>
                  <div className="industrial-metric-value">{(simData.baseline_risk * 100).toFixed(0)}</div>
                </div>
                <div className="industrial-metric-card danger" style={{ flex: 1 }}>
                  <div className="industrial-metric-label">SIMULATED RISK SCORE</div>
                  <div className="industrial-metric-value danger">{(simData.counterfactual_risk * 100).toFixed(0)}</div>
                </div>
                <div className="industrial-metric-card warning" style={{ flex: 1 }}>
                  <div className="industrial-metric-label">RISK SCORE DELTA</div>
                  <div className="industrial-metric-value warning">+{(simData.risk_delta * 100).toFixed(0)}</div>
                </div>
              </div>
              )
            ) : (
              <div>Running simulation...</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
