import React, { useState, useEffect, useRef } from 'react';
import { Search } from 'lucide-react';
import { NAV_SECTIONS } from './Sidebar';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (pageId: string) => void;
}

export default function CommandPalette({ isOpen, onClose, onNavigate }: CommandPaletteProps) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const allItems = NAV_SECTIONS.flatMap(section =>
    section.items.map(item => ({ ...item, section: section.title }))
  );

  const filtered = query.trim()
    ? allItems.filter(item =>
      item.label.toLowerCase().includes(query.toLowerCase()) ||
      item.section.toLowerCase().includes(query.toLowerCase())
    )
    : allItems;

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        // Toggle is handled by parent
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(i => Math.min(i + 1, filtered.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(i => Math.max(i - 1, 0));
    } else if (e.key === 'Enter' && filtered[selectedIndex]) {
      onNavigate(filtered[selectedIndex].id);
      onClose();
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="cmd-overlay" onClick={onClose}>
      <div className="cmd-modal" onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '0 20px' }}>
          <Search size={18} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
          <input
            ref={inputRef}
            type="text"
            className="cmd-input"
            placeholder="Search pages, objects, rules, measurements..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            style={{ paddingLeft: 0, borderBottom: 'none' }}
          />
        </div>
        <div style={{ borderTop: '1px solid var(--panel-border)' }} />
        <div className="cmd-results">
          {filtered.map((item, index) => (
            <div
              key={item.id}
              className={`cmd-result-item ${index === selectedIndex ? 'selected' : ''}`}
              onClick={() => { onNavigate(item.id); onClose(); }}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              {item.icon}
              <span>{item.label}</span>
              <span className="cmd-result-item__category">{item.section}</span>
            </div>
          ))}
          {filtered.length === 0 && (
            <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-tertiary)', fontSize: 13 }}>
              No results for "{query}"
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
