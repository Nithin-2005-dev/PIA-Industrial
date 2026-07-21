import { Box } from 'lucide-react';
import ObjectInspectorView from '../features/runtime/ObjectInspectorView';

export default function ObjectsPage() {
  return (
    <div className="page" style={{ height: 'calc(100vh - var(--header-height))' }}>
      <div className="page-header">
        <div className="page-header__title">
          <Box size={24} />
          <div>
            <h1>Objects</h1>
            <div className="page-header__subtitle">Universal object inspector — search any object by ID</div>
          </div>
        </div>
      </div>
      <div style={{ height: 'calc(100% - 80px)' }}>
        <ObjectInspectorView />
      </div>
    </div>
  );
}
