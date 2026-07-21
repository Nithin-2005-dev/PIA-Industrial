import { useState, useEffect } from 'react';
import { FileText, Loader2, CheckCircle2, Upload, Database } from 'lucide-react';
import { industrialApi } from '../api/industrialApi';
import { useWorkspaceStore } from '../store/workspaceStore';

export default function DocumentsPage() {
  const { workspace } = useWorkspaceStore();
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDocuments = () => {
    setLoading(true);
    industrialApi.documents(workspace.id)
      .then(data => setDocuments(data.documents))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDocuments();
  }, [workspace.id]);

  const uploadDocument = async (file: File | undefined) => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      await industrialApi.uploadDocument(workspace.id, file);
      loadDocuments();
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="industrial-page">
      <div className="page-header">
        <div className="page-header__title">
          <FileText size={24} className="text-blue-400" />
          <div>
            <h1>Document Intelligence</h1>
            <div className="page-header__subtitle">Universal Industrial Document Ingestion Pipeline</div>
          </div>
        </div>
        <label className="industrial-btn" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {uploading ? <Loader2 className="animate-spin" size={16} /> : <Upload size={16} />}
          Upload Documents
          <input
            type="file"
            accept=".pdf,.txt,.md,.text,.log,.csv,.xlsx,.xls"
            style={{ display: 'none' }}
            disabled={uploading}
            onChange={event => uploadDocument(event.target.files?.[0])}
          />
        </label>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-4 text-slate-100 flex items-center gap-2">
          <Database size={18} className="text-slate-400" />
          Ingested Documents
        </h2>
        
        {error && <div className="text-red-400 text-sm mb-4">{error}</div>}
        {loading ? (
          <div className="flex items-center gap-2 text-slate-400"><Loader2 className="animate-spin" size={16} /> Loading documents...</div>
        ) : (
          <div className="space-y-4">
            {documents.map((doc, idx) => (
              <div key={idx} className="border border-slate-700/50 rounded-lg p-4 bg-slate-800/30">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-medium text-slate-200">{doc.name}</h3>
                    <div className="text-xs text-slate-500 mt-1">ID: {doc.document_id} • Type: {doc.type} • Uploaded: {new Date(doc.timestamp).toLocaleString()}</div>
                  </div>
                  <span className="badge badge--success flex items-center gap-1">
                    <CheckCircle2 size={12} /> {doc.status}
                  </span>
                </div>
                
                <div className="mb-4">
                  <div className="text-xs text-slate-400 mb-2 font-semibold uppercase">Processing Pipeline</div>
                  <div className="flex items-center gap-2">
                    {doc.stages.map((stage: string, i: number) => (
                      <div key={stage} className="flex items-center gap-2">
                        <span className="text-xs bg-blue-900/40 text-blue-300 border border-blue-800/50 px-2 py-1 rounded">
                          {stage}
                        </span>
                        {i < doc.stages.length - 1 && <span className="text-slate-600">→</span>}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex gap-6 border-t border-slate-700/50 pt-4">
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Generated Evidence</div>
                    <div className="text-sm text-slate-300 font-medium">{doc.evidence_count} Facts</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Related Assets</div>
                    <div className="flex gap-2">
                      {doc.extracted_entities.map((e: string) => (
                        <span key={e} className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded">{e}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {documents.length === 0 && (
              <div className="empty-state">
                <div className="empty-state__title">No industrial knowledge has been ingested yet.</div>
                <div className="empty-state__description">Upload TXT, CSV, XLSX, or text-based PDF files to build this workspace.</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
