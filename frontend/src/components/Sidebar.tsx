import {
  Box, Network, Wrench, AlertTriangle, ShieldCheck, FileText, Scale,
  ChevronLeft, ChevronRight, LayoutDashboard
} from 'lucide-react';

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const NAV_SECTIONS: NavSection[] = [
  {
    title: 'Operations',
    items: [
      { id: 'overview', label: 'Overview', icon: <LayoutDashboard size={16} /> },
      { id: 'assets', label: 'Assets', icon: <Box size={16} /> },
      { id: 'knowledge-graph', label: 'Knowledge Graph', icon: <Network size={16} /> },
    ],
  },
  {
    title: 'Intelligence',
    items: [
      { id: 'maintenance', label: 'Maintenance', icon: <Wrench size={16} /> },
      { id: 'failures', label: 'Failure Patterns', icon: <AlertTriangle size={16} /> },
      { id: 'compliance', label: 'Compliance', icon: <ShieldCheck size={16} /> },
      { id: 'decisions', label: 'Decisions', icon: <Scale size={16} /> },
    ],
  },
  {
    title: 'Data',
    items: [
      { id: 'documents', label: 'Documents', icon: <FileText size={16} /> },
    ],
  },
];

interface SidebarProps {
  activePage: string;
  onNavigate: (pageId: string) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export default function Sidebar({ activePage, onNavigate, collapsed, onToggleCollapse }: SidebarProps) {
  return (
    <nav className="ide-sidebar">
      <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden' }}>
        {NAV_SECTIONS.map((section) => (
          <div key={section.title} className="sidebar-section">
            {!collapsed && (
              <div className="sidebar-section__title">{section.title}</div>
            )}
            {section.items.map((item) => (
              <div
                key={item.id}
                className={`sidebar-item ${activePage === item.id ? 'active' : ''}`}
                onClick={() => onNavigate(item.id)}
                title={collapsed ? item.label : undefined}
              >
                {item.icon}
                {!collapsed && (
                  <>
                    <span className="truncate">{item.label}</span>
                    {item.badge && (
                      <span className="sidebar-item__badge">{item.badge}</span>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Collapse toggle */}
      <div
        style={{
          padding: '8px 16px',
          borderTop: '1px solid var(--panel-border)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-end',
          color: 'var(--text-tertiary)',
          transition: 'color 150ms',
        }}
        onClick={onToggleCollapse}
        title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </div>
    </nav>
  );
}

export { NAV_SECTIONS };
export type { NavItem, NavSection };
