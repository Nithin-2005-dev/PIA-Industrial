import { Fragment } from 'react';
import { useTelemetryStore } from '../../api/useLiveTelemetry';

export default function TraceTimeline() {
  const { events } = useTelemetryStore();
  
  // Extract stage timings from events
  const timelineSteps = [];
  const startEvent = events.find(e => e.event_type === 'PlannerStarted');
  
  if (startEvent) {
    const plannerFinish = events.find(e => e.event_type === 'PlannerFinished');
    timelineSteps.push({
      name: 'Planner',
      time: plannerFinish ? `${plannerFinish.latency_ms.toFixed(0)}ms` : '...'
    });
  }
  
  const capEvents = events.filter(e => e.event_type === 'CapabilityFinished');
  if (capEvents.length > 0) {
    const totalLatency = capEvents.reduce((sum, e) => sum + e.latency_ms, 0);
    timelineSteps.push({
      name: 'Capabilities',
      time: `${totalLatency.toFixed(0)}ms (${capEvents.length})`
    });
  }

  const graphUpdate = events.find(e => e.event_type === 'GraphUpdated');
  if (graphUpdate) {
    timelineSteps.push({
      name: 'Graph',
      time: `+${graphUpdate.nodes_added}N`
    });
  }

  const reasoningFinish = events.find(e => e.event_type === 'ReasoningFinished');
  if (reasoningFinish) {
    timelineSteps.push({
      name: 'Reasoning',
      time: `${reasoningFinish.latency_ms.toFixed(0)}ms`
    });
  }

  const presentation = events.find(e => e.event_type === 'PresentationGenerated');
  if (presentation) {
    timelineSteps.push({
      name: 'Presentation',
      time: `${presentation.latency_ms.toFixed(0)}ms`
    });
  }

  if (timelineSteps.length === 0) {
    return <div className="text-sm text-muted">Awaiting execution trace...</div>;
  }

  return (
    <div className="flex gap-4 items-center overflow-x-auto p-2">
      {timelineSteps.map((step, idx) => (
        <Fragment key={step.name}>
          <div className="flex flex-col items-center flex-shrink-0">
            <div className="text-sm font-medium">{step.name}</div>
            <div className="text-xs text-accent-blue font-mono">{step.time}</div>
          </div>
          {idx < timelineSteps.length - 1 && <div className="text-muted">→</div>}
        </Fragment>
      ))}
    </div>
  );
}
