import { useEffect, useRef, useState } from 'react';
import { BrainCircuit, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import cytoscape from 'cytoscape';

export default function ReasoningGraphPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [loading, setLoading] = useState(true);
  const [nodeCount, setNodeCount] = useState(0);
  const [edgeCount, setEdgeCount] = useState(0);
  const [selectedNode, setSelectedNode] = useState<any>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const fetchGraph = async () => {
      setLoading(true);
      try {
        const res = await fetch('http://localhost:8000/api/v1/graph/latest');
        if (!res.ok) throw new Error('Failed to load graph');
        const data = await res.json();

        const nodeTypeColors: Record<string, string> = {
          developer: '#3b82f6',
          file: '#8b5cf6',
          commit: '#10b981',
          measurement: '#f59e0b',
          evidence: '#06b6d4',
          reasoning: '#ef4444',
          fact: '#f97316',
          rule: '#ec4899',
          default: '#64748b',
        };

        const elements = [
          ...data.nodes.map((n: any) => ({
            data: {
              id: n.id,
              label: n.label || n.id.substring(0, 12),
              type: n.type || 'default',
              ...n
            }
          })),
          ...data.edges.map((e: any) => ({
            data: {
              id: `${e.source}-${e.target}-${e.type || ''}`,
              source: e.source,
              target: e.target,
              label: e.type || '',
              weight: e.weight || 1,
            }
          }))
        ];

        setNodeCount(data.nodes.length);
        setEdgeCount(data.edges.length);

        if (cyRef.current) cyRef.current.destroy();

        cyRef.current = cytoscape({
          container: containerRef.current,
          elements,
          style: [
            {
              selector: 'node',
              style: {
                'background-color': (ele: any) => nodeTypeColors[ele.data('type')] || nodeTypeColors.default,
                'label': 'data(label)',
                'color': '#e2e8f0',
                'text-valign': 'bottom',
                'text-halign': 'center',
                'font-size': '9px',
                'width': 24,
                'height': 24,
                'border-width': 2,
                'border-color': 'rgba(255,255,255,0.1)',
                'text-margin-y': 6,
              }
            },
            {
              selector: 'node:selected',
              style: {
                'border-color': '#3b82f6',
                'border-width': 3,
                'background-color': '#3b82f6',
              }
            },
            {
              selector: 'edge',
              style: {
                'width': 1.5,
                'line-color': 'rgba(71, 85, 105, 0.6)',
                'target-arrow-color': 'rgba(71, 85, 105, 0.6)',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'label': 'data(label)',
                'font-size': '7px',
                'color': '#64748b',
                'text-background-opacity': 1,
                'text-background-color': '#0a0e1a',
              }
            },
            {
              selector: 'edge:selected',
              style: {
                'line-color': '#3b82f6',
                'target-arrow-color': '#3b82f6',
                'width': 2.5,
              }
            },
          ],
          layout: { name: 'cose', padding: 40, nodeRepulsion: () => 8000, idealEdgeLength: () => 80 },
        });

        cyRef.current.on('tap', 'node', (evt: any) => {
          setSelectedNode(evt.target.data());
        });

        cyRef.current.on('tap', (evt: any) => {
          if (evt.target === cyRef.current) setSelectedNode(null);
        });

      } catch (e) {
        console.error('Graph load failed', e);
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();

    return () => { if (cyRef.current) cyRef.current.destroy(); };
  }, []);

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.3);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() / 1.3);
  const handleFit = () => cyRef.current?.fit(undefined, 40);

  return (
    <div className="page" style={{ height: 'calc(100vh - var(--header-height))' }}>
      <div className="page-header">
        <div className="page-header__title">
          <BrainCircuit size={24} />
          <div>
            <h1>Reasoning Graph</h1>
            <div className="page-header__subtitle">Deterministic reasoning nodes, inferences, and rule executions</div>
          </div>
        </div>
      </div>

      <div className="stat-row">
        <div className="stat-card">
          <div className="stat-card__label">Nodes</div>
          <div className="stat-card__value accent-blue">{nodeCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Edges</div>
          <div className="stat-card__value accent-purple">{edgeCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Rules Migrated</div>
          <div className="stat-card__value accent-green">14</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Replay</div>
          <div className="stat-card__value accent-green">100%</div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 12, height: 'calc(100% - 180px)' }}>
        {/* Graph Canvas */}
        <div className="card" style={{ flex: 1, padding: 0, overflow: 'hidden', position: 'relative' }}>
          {/* Toolbar */}
          <div style={{ position: 'absolute', top: 8, right: 8, zIndex: 10, display: 'flex', gap: 4 }}>
            <button onClick={handleZoomIn} style={{ padding: '4px 8px', background: 'var(--bg-elevated)', border: '1px solid var(--panel-border)' }}><ZoomIn size={14} /></button>
            <button onClick={handleZoomOut} style={{ padding: '4px 8px', background: 'var(--bg-elevated)', border: '1px solid var(--panel-border)' }}><ZoomOut size={14} /></button>
            <button onClick={handleFit} style={{ padding: '4px 8px', background: 'var(--bg-elevated)', border: '1px solid var(--panel-border)' }}><Maximize2 size={14} /></button>
          </div>
          {loading && (
            <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(10,14,26,0.8)', zIndex: 5 }}>
              <div style={{ animation: 'pulse 1.5s infinite', color: 'var(--text-tertiary)' }}>Loading graph topology...</div>
            </div>
          )}
          <div ref={containerRef} style={{ width: '100%', height: '100%', background: 'rgba(0,0,0,0.2)' }} />
        </div>

        {/* Node Detail Panel */}
        {selectedNode && (
          <div className="card" style={{ width: 300, overflow: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h3 style={{ fontSize: 13, fontWeight: 600 }}>Node Inspector</h3>
              <button onClick={() => setSelectedNode(null)} style={{ background: 'transparent', border: '1px solid var(--panel-border)', color: 'var(--text-secondary)', fontSize: 10, padding: '2px 6px' }}>✕</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div>
                <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', fontWeight: 600 }}>ID</div>
                <div className="mono" style={{ fontSize: 11, wordBreak: 'break-all' }}>{selectedNode.id}</div>
              </div>
              <div>
                <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', fontWeight: 600 }}>Type</div>
                <span className="badge badge--info">{selectedNode.type}</span>
              </div>
              <div>
                <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', fontWeight: 600 }}>Label</div>
                <div style={{ fontSize: 12 }}>{selectedNode.label}</div>
              </div>
              <div>
                <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-tertiary)', fontWeight: 600, marginBottom: 4 }}>Raw Data</div>
                <pre className="mono" style={{ fontSize: 10, whiteSpace: 'pre-wrap', color: 'var(--text-tertiary)', background: 'var(--bg-tertiary)', padding: 8, borderRadius: 'var(--radius-md)', maxHeight: 200, overflow: 'auto' }}>{JSON.stringify(selectedNode, null, 2)}</pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
