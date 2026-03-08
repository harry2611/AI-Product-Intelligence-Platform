import { useEffect, useMemo, useState } from 'react';
import { LiveEvent } from '../types';

export function useLiveUpdates() {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [connected, setConnected] = useState(false);

  const wsUrl = useMemo(() => {
    if (import.meta.env.VITE_WS_URL) return import.meta.env.VITE_WS_URL as string;
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    return `${protocol}://${window.location.host}/ws/updates`;
  }, []);

  useEffect(() => {
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setConnected(true);
      ws.send('subscribe');
    };

    ws.onclose = () => setConnected(false);

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as LiveEvent;
        setEvents((prev) => [payload, ...prev].slice(0, 50));
      } catch {
        // Ignore malformed websocket payload
      }
    };

    return () => ws.close();
  }, [wsUrl]);

  return {
    connected,
    events,
    latestEvent: events[0] || null,
  };
}
