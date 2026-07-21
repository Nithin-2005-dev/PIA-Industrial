import { useState } from 'react';
import { useWorkspaceStore } from '../../store/workspaceStore';
import { useTelemetryStore } from '../../api/useLiveTelemetry';

export default function BenchmarkCenter() {
  const { workspace } = useWorkspaceStore();
  const { events } = useTelemetryStore();
  const [runningJob, setRunningJob] = useState<string | null>(null);

  // Find latest progress event
  const benchmarkEvents = events.filter(e => e.event_type === 'BenchmarkProgress');
  const latestEvent = benchmarkEvents.length > 0 ? benchmarkEvents[benchmarkEvents.length - 1] : null;

  const triggerBenchmark = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/benchmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dataset: workspace.repository })
      });
      const data = await res.json();
      setRunningJob(data.job_id);
    } catch (e) {
      console.error(e);
    }
  };

  const isRunning = latestEvent?.status === 'RUNNING';

  return (
    <div className="flex flex-col h-full w-full">
      <div className="flex justify-between items-center mb-4 border-b pb-2" style={{ borderBottomColor: 'var(--panel-border)' }}>
        <h3 className="text-lg">Run #17 <span className="text-sm text-muted">({workspace.dataset})</span></h3>
        <button onClick={triggerBenchmark} disabled={isRunning}>
          {isRunning ? 'Running...' : 'Trigger Benchmark'}
        </button>
      </div>

      {isRunning && (
        <div className="mb-4">
          <div className="text-sm mb-1 text-accent-blue">
            Executing ({latestEvent.progress}%){runningJob ? ` | ${runningJob.substring(0, 8)}` : ''}
          </div>
          <div className="w-full bg-black bg-opacity-30 rounded h-2">
            <div className="bg-accent-blue h-2 rounded transition-all" style={{ width: `${latestEvent.progress}%` }}></div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 rounded" style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid var(--accent-green)' }}>
          <div className="text-sm text-muted flex justify-between">
            Score
            <span className="text-accent-green text-xs bg-accent-green bg-opacity-20 px-1 rounded">Graph +6</span>
          </div>
          <div className="text-2xl font-bold text-accent-green mt-1">100 / 100</div>
        </div>
        <div className="p-4 rounded" style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid var(--accent-blue)' }}>
          <div className="text-sm text-muted flex justify-between">
            Latency
            <span className="text-accent-blue text-xs bg-accent-blue bg-opacity-20 px-1 rounded">-11%</span>
          </div>
          <div className="text-2xl font-bold text-accent-blue mt-1">145 ms</div>
        </div>
        <div className="p-4 rounded" style={{ background: 'rgba(148, 163, 184, 0.1)', border: '1px solid var(--panel-border)' }}>
          <div className="text-sm text-muted flex justify-between">
            Coverage
            <span className="text-accent-green text-xs bg-accent-green bg-opacity-20 px-1 rounded">+3%</span>
          </div>
          <div className="text-2xl font-bold text-text-main mt-1">97%</div>
        </div>
        <div className="p-4 rounded" style={{ background: 'rgba(148, 163, 184, 0.1)', border: '1px solid var(--panel-border)' }}>
          <div className="text-sm text-muted flex justify-between">
            Identity Resolution
            <span className="text-accent-green text-xs bg-accent-green bg-opacity-20 px-1 rounded">+5%</span>
          </div>
          <div className="text-2xl font-bold text-text-main mt-1">93%</div>
        </div>
      </div>
    </div>
  );
}
