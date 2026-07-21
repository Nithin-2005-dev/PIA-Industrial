import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, Loader2, Maximize2, Minimize2, Terminal, Code, Zap, MessageSquare } from 'lucide-react';
import { useQueryAgent } from '../api/useQueryAgent';
import { useWorkspaceStore } from '../store/workspaceStore';

export default function ChatAgentSidebar({ onClose, isExpanded, setIsExpanded }: { onClose: () => void, isExpanded: boolean, setIsExpanded: (val: boolean) => void }) {
  const [input, setInput] = useState('');
  const { messages, sendMessage, loading, error, clearMessages } = useQueryAgent();
  const { workspace } = useWorkspaceStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && workspace) {
      sendMessage(input, workspace.id);
      setInput('');
    }
  };

  const renderTrace = (trace: any) => {
    if (!trace) return null;
    return (
      <div className="mt-2 text-[10px] bg-slate-900/80 rounded border border-slate-700/50 overflow-hidden">
        <div className="bg-slate-800/80 px-2 py-1 text-slate-300 font-mono border-b border-slate-700/50 flex justify-between items-center">
          <span className="flex items-center gap-1"><Terminal size={10} /> Reasoning Trace</span>
          <span className="text-slate-500">{trace.total_latency_ms?.toFixed(1) || '0'}ms</span>
        </div>
        <div className="p-2 space-y-2">
          {trace.stages?.map((stage: any, i: number) => (
            <div key={i} className="flex flex-col gap-1">
              <div className="flex justify-between text-slate-400 font-medium">
                <span className="text-blue-400">{stage.stage_name}</span>
                <span>{stage.latency_ms?.toFixed(1)}ms</span>
              </div>
              <div className="pl-2 border-l border-slate-700 space-y-1">
                {stage.tools_used?.map((tool: any, j: number) => (
                  <div key={j} className="text-slate-300 font-mono flex items-center gap-1">
                    <Code size={10} className="text-slate-500" />
                    {tool.name}
                    {tool.cache_hit && <Zap size={10} className="text-amber-400" aria-label="Cache hit" />}
                  </div>
                ))}
                {stage.summary && <div className="text-slate-400 italic text-[9px]">{stage.summary}</div>}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className={`flex flex-col bg-slate-800/90 backdrop-blur-md border-l border-slate-700 transition-all duration-300 shadow-2xl h-full ${isExpanded ? 'w-[400px]' : 'w-[300px]'}`}>
      <div className="flex justify-between items-center p-3 border-b border-slate-700 bg-slate-900/50">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-blue-500/20 text-blue-400 rounded-md">
            <Bot size={16} />
          </div>
          <h2 className="font-semibold text-slate-100 text-sm">Copilot</h2>
        </div>
        <div className="flex items-center gap-1">
          <button 
            onClick={() => clearMessages()} 
            className="p-1 text-slate-400 hover:text-slate-200 transition-colors"
            title="Clear Chat"
          >
            <MessageSquare size={14} />
          </button>
          <button 
            onClick={() => setIsExpanded(!isExpanded)} 
            className="p-1 text-slate-400 hover:text-slate-200 transition-colors"
          >
            {isExpanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
          <button 
            onClick={onClose} 
            className="p-1 text-slate-400 hover:text-slate-200 transition-colors ml-1"
          >
            ✕
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-3 text-center">
            <Bot size={32} className="opacity-50" />
            <p className="text-sm">PIA Industrial Copilot<br/>Ask about assets, maintenance, failures, evidence, RCA, compliance, operational risks.</p>
          </div>
        ) : (
          messages.map(msg => (
            <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`max-w-[90%] rounded-lg p-3 text-sm ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-200 border border-slate-600/50'}`}>
                <div className="whitespace-pre-wrap">{msg.content}</div>
              </div>
              {msg.trace && renderTrace(msg.trace)}
            </div>
          ))
        )}
        {loading && (
          <div className="flex items-center gap-2 text-slate-400 text-sm">
            <Loader2 size={14} className="animate-spin" /> Thinking...
          </div>
        )}
        {error && (
          <div className="text-red-400 text-xs bg-red-400/10 p-2 rounded border border-red-400/20">
            {error}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-3 bg-slate-900/50 border-t border-slate-700">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={workspace ? "Ask about assets, failures, maintenance, or evidence..." : "Select a workspace first"}
            disabled={!workspace || loading}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-blue-500 disabled:opacity-50 transition-colors"
          />
          <button 
            type="submit" 
            disabled={!input.trim() || !workspace || loading}
            className="bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors flex items-center justify-center"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
