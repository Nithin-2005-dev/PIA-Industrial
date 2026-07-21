import { useState } from 'react';
import { useWorkspaceStore } from '../../store/workspaceStore';

export default function QueryPlayground() {
  const [query, setQuery] = useState('');
  const [executing, setExecuting] = useState(false);
  const [messages, setMessages] = useState<{role: string, text: string}[]>([]);
  const { workspace } = useWorkspaceStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', text: query }]);
    setExecuting(true);
    setQuery('');
    
    try {
      const res = await fetch('http://localhost:8000/api/v1/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          workspace_id: workspace.repository
        })
      });
      
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'agent', text: data.answer || "Query executed." }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'system', text: `Error: ${err}` }]);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto mb-4 p-2 rounded" style={{ background: 'rgba(0,0,0,0.2)' }}>
        {messages.length === 0 ? (
            <div className="text-sm text-muted">Ready for queries...</div>
        ) : (
            messages.map((m, i) => (
                <div key={i} className={`mb-2 text-sm ${m.role === 'user' ? 'text-blue-400' : 'text-gray-200'}`}>
                    <strong>{m.role === 'user' ? 'You' : 'PIA'}:</strong> {m.text}
                </div>
            ))
        )}
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input 
          type="text" 
          className="flex-1 p-2 rounded text-black"
          placeholder="Ask a question about the repository..." 
          value={query} 
          onChange={e => setQuery(e.target.value)} 
          disabled={executing}
        />
        <button type="submit" className="p-2 bg-blue-500 rounded text-white" disabled={executing || !query.trim()}>
          {executing ? '...' : 'Send'}
        </button>
      </form>
    </div>
  );
}
