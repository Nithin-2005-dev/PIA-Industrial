import { useState, useCallback } from 'react';
import { industrialApi } from './industrialApi';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  trace?: any;
}

export function useQueryAgent() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (query: string, workspaceId: string) => {
    if (!query.trim()) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
    };
    
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    setError(null);

    try {
      const data = await industrialApi.query(workspaceId, query);
      const answer =
        typeof data.answer === 'string'
          ? data.answer
          : data.answer?.response || data.executive_response || 'No response';
      
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: answer,
        trace: data.reasoning_trace || null
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: any) {
      setError(err.message || 'An error occurred while querying the agent.');
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    messages,
    sendMessage,
    loading,
    error,
    clearMessages: () => setMessages([])
  };
}
