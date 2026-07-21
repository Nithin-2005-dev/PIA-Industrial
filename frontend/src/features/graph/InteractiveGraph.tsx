import { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { Filter, GitMerge, Maximize2, Search, RotateCcw, Tags, Network } from 'lucide-react';
import { industrialApi } from '../../api/industrialApi';
import { useWorkspaceStore } from '../../store/workspaceStore';

export default function InteractiveGraph() {
  const { workspace } = useWorkspaceStore();
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [graphMode, setGraphMode] = useState<'knowledge' | 'reasoning' | 'execution'>('knowledge');
  const [loading, setLoading] = useState(false);
  const [selectedElement, setSelectedElement] = useState<any | null>(null);
  
  // Advanced features state
  const [nodeTypes, setNodeTypes] = useState<string[]>([]);
  const [hiddenTypes, setHiddenTypes] = useState<Set<string>>(new Set());
  const [pathMode, setPathMode] = useState(false);
  const [pathSelection, setPathSelection] = useState<string[]>([]);
  const [query, setQuery] = useState('');
  const [layoutName, setLayoutName] = useState<'cose' | 'breadthfirst' | 'circle' | 'grid'>('cose');
  const [showEdgeLabels, setShowEdgeLabels] = useState(true);
  const [graphStats, setGraphStats] = useState({ nodes: 0, edges: 0 });

  const getLabel = (n: any) => {
    if (n.attributes?.metric_name) return n.attributes.metric_name;
    if (n.attributes?.evidence_type) return n.attributes.evidence_type;
    return n.type || n.id.substring(0, 6);
  };

  useEffect(() => {
    if (!containerRef.current) return;

    const fetchGraph = async () => {
      setLoading(true);
      try {
        const data = await industrialApi.graph(workspace.id);

        const types = new Set<string>();
        const elements = [
          ...data.nodes.map((n: any) => {
            types.add(n.type);
            return { 
              data: { 
                id: n.id, 
                label: getLabel(n), 
                type: n.type,
                fullData: n 
              } 
            };
          }),
          ...data.edges.map((e: any) => ({ 
            data: { 
              id: `${e.source}-${e.target}-${e.type}`, 
              source: e.source, 
              target: e.target, 
              label: e.type,
              fullData: e
            } 
          }))
        ];
        
        setNodeTypes(Array.from(types));
        setGraphStats({ nodes: data.nodes.length, edges: data.edges.length });

        const cy = cytoscape({
          container: containerRef.current,
          elements: elements,
          style: ([
            {
              selector: 'node',
              style: {
                'background-color': '#3b82f6',
                'background-gradient-stop-colors': '#60a5fa #3b82f6 #2563eb',
                'background-gradient-direction': 'to-bottom-right',
                'label': 'data(label)',
                'color': '#f8fafc',
                'text-valign': 'bottom',
                'text-halign': 'center',
                'text-margin-y': 6,
                'font-size': '12px',
                'font-family': 'Inter, sans-serif',
                'text-outline-color': '#0f172a',
                'text-outline-width': 2,
                'width': 40,
                'height': 40,
                'border-width': 2,
                'border-color': '#1d4ed8',
                'shadow-blur': 10,
                'shadow-color': '#3b82f6',
                'shadow-opacity': 0.3
              }
            },
            {
              selector: 'node[degree >= 6]',
              style: {
                'width': 58,
                'height': 58,
                'font-size': '13px'
              }
            },
            {
              selector: 'node[type="EVIDENCE"]',
              style: {
                'background-color': '#10b981',
                'background-gradient-stop-colors': '#34d399 #10b981 #059669',
                'border-color': '#047857',
                'shadow-color': '#10b981',
                'shape': 'hexagon'
              }
            },
            {
              selector: 'node[type="MEASUREMENT"]',
              style: {
                'background-color': '#8b5cf6',
                'background-gradient-stop-colors': '#a78bfa #8b5cf6 #7c3aed',
                'border-color': '#6d28d9',
                'shadow-color': '#8b5cf6',
                'shape': 'round-diamond'
              }
            },
            {
              selector: 'node.highlighted',
              style: {
                'border-width': 4,
                'border-color': '#f59e0b',
                'shadow-blur': 15,
                'shadow-color': '#f59e0b',
                'shadow-opacity': 0.8
              }
            },
            {
              selector: 'node:selected',
              style: {
                'border-width': 4,
                'border-color': '#f1f5f9',
                'shadow-blur': 15,
                'shadow-opacity': 0.6
              }
            },
            {
              selector: 'edge',
              style: {
                'width': 2,
                'line-color': '#475569',
                'target-arrow-color': '#475569',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'label': 'data(label)',
                'font-size': '10px',
                'font-family': 'Inter, sans-serif',
                'color': '#cbd5e1',
                'text-background-opacity': 1,
                'text-background-color': '#0f172a',
                'text-background-padding': '4px',
                'text-background-shape': 'roundrectangle',
                'text-border-color': '#334155',
                'text-border-width': 1,
                'edge-text-rotation': 'autorotate'
              }
            },
            {
              selector: 'edge.hideLabel',
              style: {
                'label': ''
              }
            },
            {
              selector: 'edge.highlighted',
              style: {
                'width': 4,
                'line-color': '#f59e0b',
                'target-arrow-color': '#f59e0b',
                'z-index': 10
              }
            },
            {
              selector: 'edge:selected',
              style: {
                'width': 4,
                'line-color': '#94a3b8',
                'target-arrow-color': '#94a3b8',
                'z-index': 10
              }
            },
            {
              selector: '.faded',
              style: {
                'opacity': 0.2
              }
            }
          ] as any),
          layout: {
            name: layoutName,
            padding: 50,
            nodeRepulsion: () => 4000,
            idealEdgeLength: () => 100,
            edgeElasticity: () => 100,
            nestingFactor: 5,
            gravity: 80,
            numIter: 1000,
            animate: true
          }
        });

        cy.nodes().forEach(node => {
          node.data('degree', node.degree(false));
        });

        cyRef.current = cy;

        // Double click for neighborhood expansion
        cy.on('dblclick', 'node', (evt) => {
          const node = evt.target;
          cy.elements().removeClass('faded');
          const neighborhood = node.neighborhood().add(node);
          cy.elements().not(neighborhood).addClass('faded');
        });

        cy.on('tap', 'node, edge', (evt) => {
          setSelectedElement({
            type: evt.target.isNode() ? 'Node' : 'Edge',
            data: evt.target.data('fullData')
          });
        });

        cy.on('tap', (evt) => {
          if (evt.target === cy) {
            setSelectedElement(null);
            cy.elements().removeClass('faded highlighted');
          }
        });

        cy.on('mouseover', 'node, edge', () => {
          containerRef.current!.style.cursor = 'pointer';
        });
        cy.on('mouseout', 'node, edge', () => {
          containerRef.current!.style.cursor = 'default';
        });

      } catch (e) {
        console.error("Failed to load graph", e);
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();

    return () => {
      if (cyRef.current) cyRef.current.destroy();
    };
  }, [graphMode, layoutName, workspace.id]);

  // Apply hidden types filter
  useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current;
    
    cy.nodes().forEach(node => {
      if (hiddenTypes.has(node.data('type'))) {
        node.style('display', 'none');
      } else {
        node.style('display', 'element');
      }
    });
  }, [hiddenTypes]);

  useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current;
    cy.edges().toggleClass('hideLabel', !showEdgeLabels);
  }, [showEdgeLabels]);

  const focusSearch = () => {
    if (!cyRef.current || !query.trim()) return;
    const needle = query.trim().toLowerCase();
    const cy = cyRef.current;
    const matches = cy.nodes().filter(((node: any) => {
      const data = node.data();
      return String(data.label || '').toLowerCase().includes(needle) || String(data.id || '').toLowerCase().includes(needle);
    }) as any);
    cy.elements().removeClass('highlighted faded');
    if (matches.length > 0) {
      const neighborhood = matches.neighborhood().add(matches);
      neighborhood.addClass('highlighted');
      cy.elements().not(neighborhood).addClass('faded');
      cy.fit(neighborhood, 80);
    }
  };

  const resetView = () => {
    if (!cyRef.current) return;
    cyRef.current.elements().removeClass('highlighted faded');
    setHiddenTypes(new Set());
    setPathSelection([]);
    setPathMode(false);
    cyRef.current.fit(undefined, 50);
  };

  // Handle shortest path selection
  useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current;

    const handleTap = (evt: cytoscape.EventObject) => {
      if (!pathMode || !evt.target.isNode()) return;
      const nodeId = evt.target.id();
      
      setPathSelection(prev => {
        if (prev.length === 0) return [nodeId];
        if (prev.length === 1) {
          const source = prev[0];
          const target = nodeId;
          
          // Calculate A*
          const astar = cy.elements().aStar({
            root: cy.getElementById(source),
            goal: cy.getElementById(target),
            directed: false
          });

          cy.elements().removeClass('highlighted faded');
          
          if (astar.found) {
            astar.path.addClass('highlighted');
            cy.elements().not(astar.path).addClass('faded');
          } else {
            alert('No path found between these nodes.');
          }
          return []; // Reset after finding path
        }
        return [];
      });
    };

    cy.on('tap', 'node', handleTap);
    return () => {
      cy.off('tap', 'node', handleTap);
    };
  }, [pathMode]);

  return (
    <div className="flex flex-col h-full w-full relative">
      <div className="flex gap-4 mb-2 items-center z-10 absolute top-4 left-4">
        <select 
          value={graphMode} 
          onChange={e => setGraphMode(e.target.value as any)}
          className="text-sm bg-slate-900 border border-slate-700 rounded-md px-3 py-1.5 text-slate-200 outline-none focus:border-blue-500 shadow-lg backdrop-blur-md bg-opacity-80"
        >
          <option value="knowledge">Knowledge Graph</option>
          <option value="reasoning">Reasoning Graph</option>
          <option value="execution">Execution Graph</option>
        </select>

        <select
          value={layoutName}
          onChange={e => setLayoutName(e.target.value as any)}
          className="text-sm bg-slate-900 border border-slate-700 rounded-md px-3 py-1.5 text-slate-200 outline-none focus:border-blue-500 shadow-lg backdrop-blur-md bg-opacity-80"
        >
          <option value="cose">Force Layout</option>
          <option value="breadthfirst">Hierarchy</option>
          <option value="circle">Circle</option>
          <option value="grid">Grid</option>
        </select>

        <div className="flex gap-1 items-center bg-slate-900/80 border border-slate-700 rounded-md px-2 py-1.5 shadow-lg backdrop-blur-md">
          <Search size={14} className="text-slate-400" />
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') focusSearch(); }}
            placeholder="Find node"
            className="bg-transparent border-none outline-none text-sm text-slate-200"
            style={{ width: 120, padding: 0 }}
          />
        </div>
        
        {/* Shortest Path Toggle */}
        <button
          onClick={() => {
            setPathMode(!pathMode);
            setPathSelection([]);
            if (pathMode && cyRef.current) cyRef.current.elements().removeClass('highlighted faded');
          }}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm border shadow-lg backdrop-blur-md transition-colors ${pathMode ? 'bg-amber-600/20 border-amber-500 text-amber-400' : 'bg-slate-900/80 border-slate-700 text-slate-300'}`}
        >
          <GitMerge size={14} />
          {pathMode ? (pathSelection.length === 0 ? 'Select start node...' : 'Select end node...') : 'Shortest Path'}
        </button>

        <button
          onClick={() => setShowEdgeLabels(prev => !prev)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm border shadow-lg backdrop-blur-md transition-colors ${showEdgeLabels ? 'bg-blue-600/20 border-blue-500 text-blue-400' : 'bg-slate-900/80 border-slate-700 text-slate-300'}`}
        >
          <Tags size={14} />
          Labels
        </button>

        <button
          onClick={resetView}
          className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm border shadow-lg backdrop-blur-md transition-colors bg-slate-900/80 border-slate-700 text-slate-300"
        >
          <RotateCcw size={14} />
          Reset
        </button>

        {/* Filter Dropdown (simplified as horizontal pills for now) */}
        <div className="flex gap-2 items-center bg-slate-900/80 border border-slate-700 rounded-md px-3 py-1.5 shadow-lg backdrop-blur-md">
          <Filter size={14} className="text-slate-400" />
          <div className="flex gap-1">
            {nodeTypes.map(type => (
              <span 
                key={type}
                onClick={() => {
                  setHiddenTypes(prev => {
                    const next = new Set(prev);
                    if (next.has(type)) next.delete(type);
                    else next.add(type);
                    return next;
                  });
                }}
                className={`text-[10px] px-2 py-0.5 rounded cursor-pointer transition-colors ${hiddenTypes.has(type) ? 'bg-slate-700 text-slate-400' : 'bg-blue-600 text-white'}`}
              >
                {type}
              </span>
            ))}
          </div>
        </div>

        {loading && <span className="text-xs text-blue-400 font-medium px-2 py-1 bg-blue-900/30 rounded-md">Loading topology...</span>}
      </div>

      <div className="absolute right-4 z-10 bg-slate-900/80 border border-slate-700 rounded-md px-3 py-1.5 shadow-lg backdrop-blur-md text-xs text-slate-300" style={{ bottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
        <Network size={14} className="text-blue-400" />
        {graphStats.nodes} nodes | {graphStats.edges} edges
      </div>
      
      <div 
        ref={containerRef} 
        style={{ flex: 1, background: 'radial-gradient(circle at center, #1e293b 0%, #0f172a 100%)', borderRadius: '12px', overflow: 'hidden' }} 
        className="shadow-2xl border border-slate-800"
      />

      {/* Detail Panel overlay */}
      {selectedElement && (
        <div className="absolute top-4 right-4 w-80 max-h-[90%] overflow-y-auto bg-slate-900/90 backdrop-blur-md border border-slate-700 rounded-xl shadow-2xl p-4 text-sm z-10 custom-scrollbar">
          <div className="flex justify-between items-center mb-4 border-b border-slate-700 pb-2">
            <h3 className="font-semibold text-slate-100 flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${selectedElement.type === 'Node' ? 'bg-blue-400' : 'bg-slate-400'}`}></span>
              {selectedElement.type} Details
            </h3>
            <div className="flex gap-2">
              {selectedElement.type === 'Node' && (
                <button 
                  onClick={() => {
                    if (!cyRef.current) return;
                    const cy = cyRef.current;
                    const node = cy.getElementById(selectedElement.data.id);
                    cy.elements().removeClass('faded');
                    const neighborhood = node.neighborhood().add(node);
                    cy.elements().not(neighborhood).addClass('faded');
                  }}
                  className="text-slate-400 hover:text-blue-400 transition-colors"
                  title="Highlight Lineage / Neighborhood"
                >
                  <Maximize2 size={14} />
                </button>
              )}
              <button 
                onClick={() => setSelectedElement(null)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
          </div>
          <div className="space-y-3">
            {selectedElement.data.id && (
              <div>
                <span className="block text-xs font-medium text-slate-500 mb-1">ID</span>
                <span className="text-slate-300 font-mono text-xs break-all">{selectedElement.data.id}</span>
              </div>
            )}
            {selectedElement.data.type && (
              <div>
                <span className="block text-xs font-medium text-slate-500 mb-1">Type</span>
                <span className="inline-block px-2 py-0.5 rounded bg-slate-800 text-blue-300 border border-slate-700 text-xs font-medium">
                  {selectedElement.data.type}
                </span>
              </div>
            )}
            
            {/* Show specific properties if Edge */}
            {selectedElement.data.source && (
              <div>
                <span className="block text-xs font-medium text-slate-500 mb-1">Source</span>
                <span className="text-slate-300 font-mono text-xs break-all">{selectedElement.data.source}</span>
              </div>
            )}
            {selectedElement.data.target && (
              <div>
                <span className="block text-xs font-medium text-slate-500 mb-1">Target</span>
                <span className="text-slate-300 font-mono text-xs break-all">{selectedElement.data.target}</span>
              </div>
            )}

            {/* Show Attributes if Node */}
            {selectedElement.data.attributes && Object.keys(selectedElement.data.attributes).length > 0 && (
              <div className="pt-2 border-t border-slate-800">
                <span className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Attributes</span>
                <div className="space-y-2">
                  {Object.entries(selectedElement.data.attributes).map(([key, val]) => (
                    <div key={key} className="bg-slate-800/50 rounded p-2 border border-slate-700/50">
                      <span className="block text-xs text-slate-400">{key}</span>
                      <span className="text-slate-200 text-xs font-medium break-words">
                        {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
