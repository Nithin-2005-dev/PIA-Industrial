import { useState, useEffect } from 'react';
import { Wrench, Loader2, AlertCircle, Calendar, Info } from 'lucide-react';
import { industrialApi } from '../api/industrialApi';
import { useWorkspaceStore } from '../store/workspaceStore';

export default function MaintenancePage() {
  const { workspace } = useWorkspaceStore();
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    industrialApi.maintenance(workspace.id)
      .then(data => {
        setRecommendations(data.deferred_recommendations || []);
      })
      .catch(err => setError(err.message || 'Failed to load maintenance intelligence'))
      .finally(() => setLoading(false));
  }, [workspace.id]);

  return (
    <div className="industrial-page">
      <div className="page-header">
        <div className="page-header__title">
          <Wrench size={24} className="text-amber-400" />
          <div>
            <h1>Maintenance Intelligence</h1>
            <div className="page-header__subtitle">Priority Maintenance and Deferred Recommendations</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-4 text-slate-100 flex items-center gap-2">
          <AlertCircle size={18} className="text-amber-400" />
          Deferred Recommendations
        </h2>
        
        {error && (
          <div className="border border-red-900/50 rounded-lg p-4 bg-red-950/20 text-red-400 text-sm mb-4">
            Failed to load maintenance data: {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center gap-2 text-slate-400"><Loader2 className="animate-spin" size={16} /> Loading maintenance intelligence...</div>
        ) : !error && (
          <div className="space-y-4">
            {recommendations.map((rec, idx) => (
              <div key={idx} className="border border-slate-700/50 rounded-lg p-4 bg-slate-800/30">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-3">
                    <span className="bg-slate-700 text-slate-200 px-2 py-1 rounded font-mono text-sm">{rec.asset_id}</span>
                    <h3 className="font-medium text-slate-200">{rec.recommendation}</h3>
                  </div>
                  <span className="badge badge--danger">
                    {rec.priority} PRIORITY
                  </span>
                </div>
                
                <div className="flex gap-4 mt-4 pt-4 border-t border-slate-700/50">
                  <div className="text-xs text-slate-400 flex items-center gap-1">
                    <span className="text-slate-500 font-semibold">Reason:</span> {rec.reason}
                  </div>
                  <div className="text-xs text-slate-400 flex items-center gap-1">
                    <span className="text-slate-500 font-semibold">Status:</span> <span className="text-amber-400">{rec.status}</span>
                  </div>
                  {rec.timestamp && (
                    <div className="text-xs text-slate-400 flex items-center gap-1">
                      <Calendar size={12} className="text-slate-500" /> {new Date(rec.timestamp).toLocaleDateString()}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {recommendations.length === 0 && (
              <div className="border border-slate-700/50 rounded-lg p-6 bg-slate-800/20 flex flex-col items-center justify-center text-center">
                <Info size={28} className="text-slate-500 mb-3" />
                <h3 className="text-base font-medium text-slate-400">Insufficient Evidence</h3>
                <p className="text-sm text-slate-500 mt-1">No recurring maintenance pattern established. Upload additional maintenance records to enable this analysis.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
