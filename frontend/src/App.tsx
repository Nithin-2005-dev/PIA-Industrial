import { useState, useEffect } from 'react';
import { useWorkspaceStore } from './store/workspaceStore';
import { Layers, Search, Database, Bot, Menu } from 'lucide-react';
import Sidebar from './components/Sidebar';
import CommandPalette from './components/CommandPalette';
import ChatAgentSidebar from './components/ChatAgentSidebar';
import { useLiveTelemetry } from './api/useLiveTelemetry';
import { industrialApi, type WorkspaceSummary } from './api/industrialApi';

// Pages
import IndustrialOverviewPage from './pages/IndustrialOverviewPage';
import AssetsPage from './pages/AssetsPage';
import AssetDetailsPage from './pages/AssetDetailsPage';
import KnowledgeGraphPage from './pages/KnowledgeGraphPage';
import DecisionsPage from './pages/DecisionsPage';

import DocumentsPage from './pages/DocumentsPage';
import MaintenancePage from './pages/MaintenancePage';
import FailuresPage from './pages/FailuresPage';
import CompliancePage from './pages/CompliancePage';

const PAGE_MAP: Record<string, React.ReactNode> = {
  'overview': <IndustrialOverviewPage />,
  'knowledge-graph': <KnowledgeGraphPage />,
  'maintenance': <MaintenancePage />,
  'failures': <FailuresPage />,
  'compliance': <CompliancePage />,
  'decisions': <DecisionsPage />,
  'documents': <DocumentsPage />,
};

function App() {
  useLiveTelemetry();
  const { workspace, setActiveWorkspace } = useWorkspaceStore();
  const [activePage, setActivePage] = useState('overview');
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [isMobileViewport, setIsMobileViewport] = useState(false);
  const [cmdPaletteOpen, setCmdPaletteOpen] = useState(false);
  const [workspaces, setWorkspaces] = useState<WorkspaceSummary[]>([]);
  const [creatingWorkspace, setCreatingWorkspace] = useState(false);
  
  // Chat Agent State
  const [chatOpen, setChatOpen] = useState(false);
  const [chatExpanded, setChatExpanded] = useState(false);

  // Global Ctrl+K handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCmdPaletteOpen(prev => !prev);
      }
      if (e.key === 'Escape') {
        setCmdPaletteOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    industrialApi.listWorkspaces()
      .then(data => setWorkspaces(data.workspaces))
      .catch(console.error);
  }, []);

  const createEmptyWorkspace = async () => {
    setCreatingWorkspace(true);
    try {
      const data = await industrialApi.createWorkspace(`Industrial Workspace ${workspaces.length + 1}`);
      setWorkspaces(prev => [...prev, data.workspace]);
      setActiveWorkspace(data.workspace.id, data.workspace.name);
    } finally {
      setCreatingWorkspace(false);
    }
  };

  useEffect(() => {
    const media = window.matchMedia('(max-width: 900px)');
    const syncViewport = () => setIsMobileViewport(media.matches);
    syncViewport();
    media.addEventListener('change', syncViewport);
    return () => media.removeEventListener('change', syncViewport);
  }, []);

  const navigate = (pageId: string) => {
    setActivePage(pageId);
    setSelectedAsset(null);
    setMobileSidebarOpen(false);
  };

  return (
    <>
      <div className={`ide-shell ${sidebarCollapsed ? 'sidebar-collapsed' : ''} ${mobileSidebarOpen ? 'mobile-sidebar-open' : ''}`}>
        {/* Header */}
        <header className="ide-header">
          <div className="ide-header__brand">
            <button
              type="button"
              className="mobile-nav-toggle"
              onClick={() => setMobileSidebarOpen(prev => !prev)}
              aria-label="Toggle navigation"
            >
              <Menu size={18} />
            </button>
            <Layers size={20} />
            <span>PIA</span>
          </div>

          <div className="ide-header__center">
            <div className="cmd-trigger" onClick={() => setCmdPaletteOpen(true)}>
              <Search size={14} />
              <span>Search everything...</span>
              <kbd>Ctrl K</kbd>
            </div>
          </div>

          <div className="ide-header__actions">
            <div className="workspace-badge">
              <div className="workspace-badge__dot" />
              <Database size={12} />
              <select
                value={workspace.id}
                onChange={event => {
                  const selected = workspaces.find(item => item.id === event.target.value);
                  setActiveWorkspace(event.target.value, selected?.name || event.target.value);
                }}
                style={{ background: 'transparent', border: 0, color: 'inherit', outline: 0, maxWidth: 220 }}
              >
                {workspaces.map(item => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
              <button
                type="button"
                onClick={createEmptyWorkspace}
                disabled={creatingWorkspace}
                className="industrial-btn"
                style={{ padding: '4px 8px', fontSize: 12 }}
              >
                New
              </button>
            </div>
            
            {/* Copilot Toggle */}
            <button 
              onClick={() => setChatOpen(!chatOpen)}
              className={`flex items-center justify-center p-2 rounded-md transition-colors ${chatOpen ? 'bg-blue-600 text-white' : 'hover:bg-slate-800 text-slate-400 hover:text-slate-200'}`}
              title="Toggle Copilot"
            >
              <Bot size={16} />
            </button>
          </div>
        </header>

        {/* Sidebar */}
          <Sidebar
            activePage={activePage}
            onNavigate={navigate}
            collapsed={isMobileViewport ? false : sidebarCollapsed}
            onToggleCollapse={() => setSidebarCollapsed(prev => !prev)}
          />
        {mobileSidebarOpen && (
          <button
            type="button"
            className="mobile-sidebar-backdrop"
            onClick={() => setMobileSidebarOpen(false)}
            aria-label="Close navigation"
          />
        )}

        {/* Main Content & Chat */}
        <div className="app-workspace flex flex-1 overflow-hidden">
          <main className="ide-main flex-1">
            {activePage === 'assets' ? (
              selectedAsset ? (
                <AssetDetailsPage assetId={selectedAsset} onBack={() => setSelectedAsset(null)} />
              ) : (
                <AssetsPage onSelectAsset={(id) => setSelectedAsset(id)} />
              )
            ) : PAGE_MAP[activePage] || (
              <div className="empty-state" style={{ height: '100%' }}>
                <div className="empty-state__title">Page not found</div>
              </div>
            )}
          </main>
          
          {chatOpen && (
            <ChatAgentSidebar 
              onClose={() => setChatOpen(false)}
              isExpanded={chatExpanded}
              setIsExpanded={setChatExpanded}
            />
          )}
        </div>
      </div>

      {/* Command Palette */}
      <CommandPalette
        isOpen={cmdPaletteOpen}
        onClose={() => setCmdPaletteOpen(false)}
        onNavigate={navigate}
      />
    </>
  );
}

export default App;
