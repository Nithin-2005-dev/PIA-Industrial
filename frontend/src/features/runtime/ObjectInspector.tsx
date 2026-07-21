import { useState } from 'react';
import './ObjectInspector.css';

interface ObjectInspectorProps {
    objectData: any;
    onClose?: () => void;
}

export const ObjectInspector: React.FC<ObjectInspectorProps> = ({ objectData, onClose }) => {
    const [activeTab, setActiveTab] = useState<string>('metadata');

    if (!objectData) return <div className="object-inspector-empty">Select an object to inspect</div>;

    const tabs = [
        { id: 'metadata', label: 'Metadata' },
        { id: 'identity', label: 'Identity' },
        { id: 'validation', label: 'Validation' },
        { id: 'lineage', label: 'Lineage' },
        { id: 'events', label: 'Events / History' },
        { id: 'evidence', label: 'Measurements & Evidence' },
        { id: 'raw', label: 'Raw JSON' }
    ];

    return (
        <div className="object-inspector-panel glass-panel">
            <div className="inspector-header">
                <h3>{objectData?.identity?.object_type?.toUpperCase() || 'OBJECT'} INSPECTOR</h3>
                <span className="object-id-badge">{objectData?.identity?.object_id || objectData?.object_id || 'unknown'}</span>
                {onClose && <button className="close-btn" onClick={onClose}>×</button>}
            </div>
            
            <div className="inspector-tabs">
                {tabs.map(t => (
                    <button 
                        key={t.id} 
                        className={`tab-btn ${activeTab === t.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(t.id)}
                    >
                        {t.label}
                    </button>
                ))}
            </div>

            <div className="inspector-content">
                {activeTab === 'metadata' && (
                    <div className="inspector-section">
                        <h4>General Metadata</h4>
                        <pre>{JSON.stringify(objectData?.metadata || objectData?.attributes || objectData, null, 2)}</pre>
                    </div>
                )}
                {activeTab === 'identity' && (
                    <div className="inspector-section">
                        <h4>Identity Scope</h4>
                        <pre>{JSON.stringify(objectData?.identity, null, 2)}</pre>
                    </div>
                )}
                {activeTab === 'validation' && (
                    <div className="inspector-section">
                        <h4>Validation Contracts</h4>
                        {objectData?.validation_report ? (
                            <pre>{JSON.stringify(objectData.validation_report, null, 2)}</pre>
                        ) : (
                            <p className="no-data">No validation report found.</p>
                        )}
                    </div>
                )}
                {activeTab === 'lineage' && (
                    <div className="inspector-section">
                        <h4>Parents & Children</h4>
                        <p>Parent ID: {objectData?.parent_projection_id || 'None'}</p>
                        <p>Dataset ID: {objectData?.dataset_id || 'None'}</p>
                        <p>Execution ID: {objectData?.execution_id || 'None'}</p>
                    </div>
                )}
                {activeTab === 'raw' && (
                    <div className="inspector-section">
                        <h4>Raw JSON</h4>
                        <pre className="raw-json">{JSON.stringify(objectData, null, 2)}</pre>
                    </div>
                )}
                {/* Fallback for others currently empty */}
                {['events', 'evidence'].includes(activeTab) && (
                    <div className="inspector-section">
                        <p className="no-data">No data available for {activeTab}</p>
                    </div>
                )}
            </div>
        </div>
    );
};
