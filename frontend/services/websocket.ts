/**
 * WebSocket Service for Real-time Updates
 * Handles WebSocket connections for streaming conversations and real-time notifications
 */

type MessageHandler = (data: any) => void;
type ErrorHandler = (error: Error) => void;
type StateHandler = (state: 'connected' | 'disconnected' | 'connecting') => void;

interface WebSocketConfig {
  url?: string;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  timeout?: number;
}

/**
 * WebSocket Service
 */
class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnect: boolean;
  private reconnectInterval: number;
  private maxReconnectAttempts: number;
  private reconnectAttempts = 0;
  private timeout: number;
  private messageHandlers: Map<string, MessageHandler[]> = new Map();
  private errorHandlers: ErrorHandler[] = [];
  private stateHandlers: StateHandler[] = [];
  private state: 'connected' | 'disconnected' | 'connecting' = 'disconnected';
  private reconnectTimer: NodeJS.Timeout | null = null;
  private pingInterval: NodeJS.Timeout | null = null;

  constructor(config: WebSocketConfig = {}) {
    const baseUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    this.url = config.url || `${baseUrl}/ws`;
    this.reconnect = config.reconnect !== false;
    this.reconnectInterval = config.reconnectInterval || 3000;
    this.maxReconnectAttempts = config.maxReconnectAttempts || 10;
    this.timeout = config.timeout || 30000;
  }

  /**
   * Connect to WebSocket server
   */
  async connect(token?: string): Promise<void> {
    if (this.state === 'connecting' || this.state === 'connected') {
      console.warn('WebSocket already connecting or connected');
      return;
    }

    this.setState('connecting');

    return new Promise((resolve, reject) => {
      try {
        const url = token ? `${this.url}?token=${token}` : this.url;
        this.ws = new WebSocket(url);

        const timeout = setTimeout(() => {
          reject(new Error('WebSocket connection timeout'));
          this.ws?.close();
        }, this.timeout);

        this.ws.onopen = () => {
          clearTimeout(timeout);
          this.reconnectAttempts = 0;
          this.setState('connected');
          this.startPingInterval();
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event.data);
        };

        this.ws.onerror = () => {
          clearTimeout(timeout);
          const wsError = new Error('WebSocket error');
          this.notifyError(wsError);
          reject(wsError);
        };

        this.ws.onclose = () => {
          clearTimeout(timeout);
          this.setState('disconnected');
          this.stopPingInterval();
          
          if (this.reconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect(token);
          }
        };
      } catch (error: any) {
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.reconnect = false;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    this.stopPingInterval();
    this.ws?.close();
    this.setState('disconnected');
  }

  /**
   * Send message through WebSocket
   */
  send<T = any>(type: string, data?: T): void {
    if (this.state !== 'connected' || !this.ws) {
      throw new Error('WebSocket is not connected');
    }

    const message = JSON.stringify({
      type,
      data: data || {},
      timestamp: new Date().toISOString(),
    });

    this.ws.send(message);
  }

  /**
   * Subscribe to message type
   */
  on(type: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }

    this.messageHandlers.get(type)!.push(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(type);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }

  /**
   * Subscribe to errors
   */
  onError(handler: ErrorHandler): () => void {
    this.errorHandlers.push(handler);
    return () => {
      const index = this.errorHandlers.indexOf(handler);
      if (index > -1) {
        this.errorHandlers.splice(index, 1);
      }
    };
  }

  /**
   * Subscribe to state changes
   */
  onStateChange(handler: StateHandler): () => void {
    this.stateHandlers.push(handler);
    return () => {
      const index = this.stateHandlers.indexOf(handler);
      if (index > -1) {
        this.stateHandlers.splice(index, 1);
      }
    };
  }

  /**
   * Get current connection state
   */
  getState(): typeof this.state {
    return this.state;
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.state === 'connected';
  }

  /**
   * Handle incoming message
   */
  private handleMessage(rawData: string): void {
    try {
      const message = JSON.parse(rawData);
      const handlers = this.messageHandlers.get(message.type) || [];

      handlers.forEach((handler) => {
        try {
          handler(message.data);
        } catch (error: any) {
          this.notifyError(error);
        }
      });
    } catch (error: any) {
      this.notifyError(new Error(`Failed to parse WebSocket message: ${error.message}`));
    }
  }

  /**
   * Update state and notify handlers
   */
  private setState(newState: typeof this.state): void {
    if (this.state !== newState) {
      this.state = newState;
      this.stateHandlers.forEach((handler) => {
        try {
          handler(newState);
        } catch (error: any) {
          console.error('State handler error:', error);
        }
      });
    }
  }

  /**
   * Notify error handlers
   */
  private notifyError(error: Error): void {
    this.errorHandlers.forEach((handler) => {
      try {
        handler(error);
      } catch (err: any) {
        console.error('Error handler error:', err);
      }
    });
  }

  /**
   * Schedule reconnect
   */
  private scheduleReconnect(token?: string): void {
    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1),
      30000
    );

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.connect(token).catch((error) => {
        console.error('Reconnect failed:', error);
      });
    }, delay);
  }

  /**
   * Start ping interval to keep connection alive
   */
  private startPingInterval(): void {
    this.pingInterval = setInterval(() => {
      if (this.isConnected()) {
        try {
          this.send('ping');
        } catch (error) {
          console.error('Ping failed:', error);
        }
      }
    }, 30000); // Ping every 30 seconds
  }

  /**
   * Stop ping interval
   */
  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }
}

// Create singleton instance
const wsService = new WebSocketService();
const websocketService = wsService; // Named export for convenience

export default wsService;
export { WebSocketService, websocketService };
export type { WebSocketConfig };
