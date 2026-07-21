import { useEffect } from 'react';
import { create } from 'zustand';

export interface TelemetryEvent {
  event_type: string;
  session_id: string;
  query_id?: string;
  timestamp: string;
  [key: string]: any;
}

interface TelemetryState {
  events: TelemetryEvent[];
  connectionStatus: 'connecting' | 'connected' | 'disconnected';
  addEvent: (event: TelemetryEvent) => void;
  setConnectionStatus: (status: 'connecting' | 'connected' | 'disconnected') => void;
  clearEvents: () => void;
}

export const useTelemetryStore = create<TelemetryState>((set) => ({
  events: [],
  connectionStatus: 'disconnected',
  addEvent: (event) => set((state) => ({ events: [...state.events, event] })),
  setConnectionStatus: (status) => set({ connectionStatus: status }),
  clearEvents: () => set({ events: [] })
}));

let wsInstance: WebSocket | null = null;
let reconnectTimeout: any = null;

export function useLiveTelemetry() {
  const { addEvent, setConnectionStatus } = useTelemetryStore();

  useEffect(() => {
    const connect = () => {
      if (wsInstance && (wsInstance.readyState === WebSocket.OPEN || wsInstance.readyState === WebSocket.CONNECTING)) {
        return;
      }
      
      const ws = new WebSocket('ws://localhost:8000/ws/v1/runtime');
      wsInstance = ws;
      
      setConnectionStatus('connecting');

      ws.onopen = () => {
        setConnectionStatus('connected');
        if (reconnectTimeout) {
          clearTimeout(reconnectTimeout);
          reconnectTimeout = null;
        }
      };

      ws.onmessage = (message) => {
        try {
          const data = JSON.parse(message.data);
          addEvent(data);
        } catch (e) {
          console.error("Failed to parse telemetry event", e);
        }
      };

      ws.onclose = () => {
        setConnectionStatus('disconnected');
        wsInstance = null;
        reconnectTimeout = setTimeout(connect, 3000);
      };
      
      ws.onerror = () => {
        ws.close();
      };
    };

    connect();

    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (wsInstance) {
        wsInstance.close();
        wsInstance = null;
      }
    };
  }, []);
}
