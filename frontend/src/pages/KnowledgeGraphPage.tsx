import { Network } from 'lucide-react';
import InteractiveGraph from '../features/graph/InteractiveGraph';

export default function KnowledgeGraphPage() {
  return (
    <div className="page" style={{ height: 'calc(100vh - var(--header-height))' }}>
      <div className="page-header">
        <div className="page-header__title">
          <Network size={24} />
          <div>
            <h1>Knowledge Graph</h1>
            <div className="page-header__subtitle">Interactive exploration of the knowledge graph projection</div>
          </div>
        </div>
      </div>
      <div className="card" style={{ height: 'calc(100% - 100px)', padding: 0, overflow: 'hidden' }}>
        <InteractiveGraph />
      </div>
    </div>
  );
}
