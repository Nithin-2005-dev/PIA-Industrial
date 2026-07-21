import { useState } from 'react';
import { Search } from 'lucide-react';
import { ObjectInspector } from './ObjectInspector';

export default function ObjectInspectorView() {
    const [objectId, setObjectId] = useState('');
    const [objectData, setObjectData] = useState<any>(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const fetchObject = async (id: string) => {
        if (!id) return;
        setLoading(true);
        setError('');
        try {
            const res = await fetch(`http://localhost:8000/api/v1/store/objects/${id}`);
            if (!res.ok) throw new Error('Object not found');
            const data = await res.json();
            setObjectData(data);
        } catch (err: any) {
            setError(err.message);
            setObjectData(null);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full">
            <div className="flex gap-2 mb-4 p-4 glass-panel items-center">
                <Search size={18} className="text-muted" />
                <input
                    type="text"
                    placeholder="Enter Object ID (Commit, Developer, Projection, Measurement...)"
                    value={objectId}
                    onChange={e => setObjectId(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && fetchObject(objectId)}
                    className="bg-transparent border-none outline-none flex-1 font-mono text-sm"
                />
                <button onClick={() => fetchObject(objectId)}>Inspect</button>
            </div>

            <div className="flex-1 overflow-hidden">
                {loading && <div className="text-muted p-4">Loading object...</div>}
                {error && <div className="text-red-500 p-4">{error}</div>}
                {!loading && !error && objectData && (
                    <ObjectInspector objectData={objectData} onClose={() => setObjectData(null)} />
                )}
                {!loading && !error && !objectData && (
                    <div className="flex items-center justify-center h-full text-muted">
                        Enter an Object ID to open it in the Inspector.
                    </div>
                )}
            </div>
        </div>
    );
}
