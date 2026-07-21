import { useEffect, useState } from 'react';
import { Activity, Database, CheckCircle, AlertTriangle } from 'lucide-react';

export default function ProjectionHealthConsole() {
  const [health, setHealth] = useState<any>(null);
  
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/health');
        const data = await res.json();
        setHealth(data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!health) return <div className="text-muted text-xs p-2">Loading Health...</div>;

  return (
    <div className="flex flex-col gap-4 text-sm mt-4">
      <div className="p-2 rounded bg-black bg-opacity-20 border border-transparent hover:border-panel-border transition-all">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Database size={14}/>
            <span className="font-semibold text-text-main">Operational Store</span>
          </div>
          <div className="text-xs">
            {health.database_status === 'healthy' ? (
              <span className="text-accent-green flex items-center gap-1"><CheckCircle size={12}/> OK</span>
            ) : (
              <span className="text-red-500 flex items-center gap-1"><AlertTriangle size={12}/> Error</span>
            )}
          </div>
        </div>
      </div>

      <div className="p-2 rounded bg-black bg-opacity-20 border border-transparent hover:border-panel-border transition-all">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Activity size={14}/>
            <span className="font-semibold text-text-main">Projections</span>
          </div>
        </div>
        <div className="pl-6 flex flex-col gap-2 text-xs">
          {Object.entries(health.projections || {}).map(([id, proj]: [string, any]) => (
            <div key={id} className="flex flex-col gap-1 border-l border-panel-border pl-2">
              <div className="flex justify-between items-center text-text-main">
                <span>├── {id}</span>
                <span className={proj.status === 'valid' || proj.status === 'active' ? 'text-accent-green' : 'text-accent-blue'}>
                  {proj.status}
                </span>
              </div>
              <div className="flex gap-4 text-muted pl-4">
                <span>Nodes: <span className="text-accent-blue">{proj.node_count || 0}</span></span>
                <span>Records: <span className="text-accent-blue">{proj.record_count || 0}</span></span>
              </div>
            </div>
          ))}
          {Object.keys(health.projections || {}).length === 0 && (
            <div className="text-muted">No projections registered</div>
          )}
        </div>
      </div>
    </div>
  );
}
