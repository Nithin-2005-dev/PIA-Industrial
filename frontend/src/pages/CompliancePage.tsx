import { useState, useEffect } from 'react';
import { ShieldAlert, Loader2, HelpCircle } from 'lucide-react';
import { industrialApi } from '../api/industrialApi';
import { useWorkspaceStore } from '../store/workspaceStore';

export default function CompliancePage() {
  const { workspace } = useWorkspaceStore();
  const [gaps, setGaps] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    industrialApi.compliance(workspace.id)
      .then(data => {
        setGaps(data.compliance_gaps || []);
      })
      .catch(err => setError(err.message || 'Failed to load compliance engine'))
      .finally(() => setLoading(false));
  }, [workspace.id]);

  return (
    <div className="industrial-page">
      <div className="page-header">
        <div className="page-header__title">
          <ShieldAlert size={24} className="text-purple-400" />
          <div>
            <h1>Compliance Engine</h1>
            <div className="page-header__subtitle">Active Compliance Gaps and Requirements</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-4 text-slate-100 flex items-center gap-2">
          <ShieldAlert size={18} className="text-purple-400" />
          Regulatory Status
        </h2>
        
        {error && (
          <div className="border border-red-900/50 rounded-lg p-4 bg-red-950/20 text-red-400 text-sm mb-4">
            Failed to load compliance data: {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center gap-2 text-slate-400"><Loader2 className="animate-spin" size={16} /> Loading compliance engine...</div>
        ) : !error && (
          <div className="space-y-4">
            {gaps.map((gap, idx) => (
              <div key={idx} className="border border-purple-900/50 rounded-lg p-4 bg-purple-950/20">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-3">
                    <span className="bg-slate-700 text-slate-200 px-2 py-1 rounded font-mono text-sm">{gap.asset_id}</span>
                    <h3 className="font-medium text-slate-200">{gap.requirement}</h3>
                  </div>
                  <span className={`badge ${gap.severity === 'HIGH' ? 'badge--danger' : 'badge--warning'}`}>
                    {gap.status}
                  </span>
                </div>
                
                <div className="flex gap-6 mt-4 pt-4 border-t border-purple-900/30">
                  <div className="text-xs text-slate-400 flex items-center gap-1">
                    <span className="text-slate-500 font-semibold">Reason:</span> {gap.reason}
                  </div>
                  <div className="text-xs text-slate-400 flex items-center gap-1">
                    <span className="text-slate-500 font-semibold">Severity:</span> {gap.severity}
                  </div>
                </div>
              </div>
            ))}
            
            {gaps.length === 0 && (
              <div className="border border-slate-700/50 rounded-lg p-6 bg-slate-800/20 flex flex-col items-center justify-center text-center">
                <HelpCircle size={28} className="text-slate-500 mb-3" />
                <h3 className="text-base font-medium text-slate-400">Not Evaluated</h3>
                <p className="text-sm text-slate-500 mt-1">No applicable compliance requirements found for this workspace. Upload inspection records or regulatory documents to enable compliance evaluation.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
