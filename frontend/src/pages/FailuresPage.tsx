import { useState, useEffect } from 'react';
import { Activity, Loader2, AlertTriangle, ArrowRight, Info } from 'lucide-react';
import { industrialApi } from '../api/industrialApi';
import { useWorkspaceStore } from '../store/workspaceStore';

export default function FailuresPage() {
  const { workspace } = useWorkspaceStore();
  const [failures, setFailures] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    industrialApi.failures(workspace.id)
      .then(data => {
        setFailures(data.recurring_failures || []);
      })
      .catch(err => setError(err.message || 'Failed to load failure intelligence'))
      .finally(() => setLoading(false));
  }, [workspace.id]);

  return (
    <div className="industrial-page">
      <div className="page-header">
        <div className="page-header__title">
          <Activity size={24} className="text-red-400" />
          <div>
            <h1>Failure Patterns</h1>
            <div className="page-header__subtitle">Recurring Failures and Sequences</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-4 text-slate-100 flex items-center gap-2">
          <AlertTriangle size={18} className="text-red-400" />
          Failure Analysis
        </h2>
        
        {error && (
          <div className="border border-red-900/50 rounded-lg p-4 bg-red-950/20 text-red-400 text-sm mb-4">
            Failed to load failure data: {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center gap-2 text-slate-400"><Loader2 className="animate-spin" size={16} /> Loading failure intelligence...</div>
        ) : !error && (
          <div className="space-y-4">
            {failures.map((fail, idx) => (
              <div key={idx} className="border border-red-900/50 rounded-lg p-5 bg-red-950/20">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    <span className="bg-slate-700 text-slate-200 px-2 py-1 rounded font-mono text-sm">{fail.asset_id}</span>
                    <h3 className="font-medium text-slate-200">{fail.pattern}</h3>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-red-400">{fail.occurrences} Occurrences</div>
                    <div className="text-xs text-slate-400">{(fail.confidence * 100).toFixed(0)}% Confidence</div>
                  </div>
                </div>
                
                {(fail.potential_precursors?.length > 0) && (
                  <div className="mt-4 pt-4 border-t border-red-900/30">
                    <div className="text-xs text-slate-400 mb-2 font-semibold uppercase tracking-wider">Potential Precursors</div>
                    <div className="flex items-center gap-2 flex-wrap">
                      {fail.potential_precursors.map((prec: string, i: number) => (
                        <div key={prec} className="flex items-center gap-2">
                          <span className="text-xs bg-amber-900/40 text-amber-300 border border-amber-800/50 px-2 py-1 rounded">
                            {prec}
                          </span>
                          {i < fail.potential_precursors.length - 1 && <ArrowRight size={12} className="text-slate-600" />}
                        </div>
                      ))}
                      <ArrowRight size={12} className="text-slate-600 mx-1" />
                      <span className="text-xs bg-red-900/40 text-red-300 border border-red-800/50 px-2 py-1 rounded">
                        {fail.pattern}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))}
            
            {failures.length === 0 && (
              <div className="border border-slate-700/50 rounded-lg p-6 bg-slate-800/20 flex flex-col items-center justify-center text-center">
                <Info size={28} className="text-slate-500 mb-3" />
                <h3 className="text-base font-medium text-slate-400">Insufficient Evidence</h3>
                <p className="text-sm text-slate-500 mt-1">No failure pattern established. Upload failure reports, incident logs, or inspection records to enable this analysis.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
