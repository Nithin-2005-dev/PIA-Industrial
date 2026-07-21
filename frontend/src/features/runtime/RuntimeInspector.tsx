import { useState } from 'react';
import { useTelemetryStore } from '../../api/useLiveTelemetry';
import { ChevronRight, ChevronDown, CheckCircle, Clock } from 'lucide-react';

export default function RuntimeInspector() {
  const { events } = useTelemetryStore();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ planner: true, capabilities: true });

  const toggle = (section: string) => setExpanded(prev => ({ ...prev, [section]: !prev[section] }));

  const capabilities = events.filter(e => e.event_type === 'CapabilityFinished');
  const plannerFinished = events.find(e => e.event_type === 'PlannerFinished');

  return (
    <div className="flex flex-col gap-4 text-sm">
      {/* Planner Section */}
      <div className="p-2 rounded bg-black bg-opacity-20 border border-transparent hover:border-panel-border transition-all">
        <div className="flex items-center justify-between cursor-pointer" onClick={() => toggle('planner')}>
          <div className="flex items-center gap-2">
            {expanded['planner'] ? <ChevronDown size={14}/> : <ChevronRight size={14}/>}
            <span className="font-semibold text-text-main">Planner</span>
          </div>
          {plannerFinished ? (
            <div className="flex items-center gap-1 text-accent-green text-xs"><CheckCircle size={12}/> {plannerFinished.latency_ms.toFixed(0)}ms</div>
          ) : (
            <div className="flex items-center gap-1 text-muted text-xs"><Clock size={12}/> Waiting</div>
          )}
        </div>
        
        {expanded['planner'] && plannerFinished && (
          <div className="pl-6 mt-2 flex flex-col gap-1 text-xs">
            {plannerFinished.capabilities_selected.map((cap: string, idx: number) => (
              <div key={idx} className="flex justify-between items-center text-muted border-l border-panel-border pl-2">
                <span>├── {cap}</span>
                <span className="text-accent-blue font-mono">Queued</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Capabilities Section */}
      <div className="p-2 rounded bg-black bg-opacity-20 border border-transparent hover:border-panel-border transition-all">
        <div className="flex items-center justify-between cursor-pointer" onClick={() => toggle('capabilities')}>
          <div className="flex items-center gap-2">
            {expanded['capabilities'] ? <ChevronDown size={14}/> : <ChevronRight size={14}/>}
            <span className="font-semibold text-text-main">Capabilities Executed</span>
          </div>
          <div className="text-xs text-muted">{capabilities.length} completed</div>
        </div>

        {expanded['capabilities'] && capabilities.length > 0 && (
          <div className="pl-6 mt-2 flex flex-col gap-2 text-xs">
            {capabilities.map((cap: any, idx: number) => (
              <div key={idx} className="flex flex-col gap-1 border-l border-panel-border pl-2 pb-2">
                <div className="flex justify-between items-center text-text-main">
                  <span>├── {cap.capability_name}</span>
                  <span className="text-accent-green font-mono">{cap.latency_ms.toFixed(0)}ms</span>
                </div>
                <div className="flex gap-4 text-muted pl-4">
                  <span>Confidence: <span className="text-accent-blue">{(cap.confidence * 100).toFixed(0)}%</span></span>
                  <span>Rules: <span className="text-accent-blue">{cap.rules_fired}</span></span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
