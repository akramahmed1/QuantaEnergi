import { useTradingStore } from '../store/tradingStore'

export interface WebSocketMessage {
  type: 'market_data' | 'order_update' | 'position_update' | 'trading_signal' | 'risk_alert'
  data: any
  timestamp: string
}

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private heartbeatInterval: number | null = null
  private subscriptions = new Set<string>()

  async connect(userId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = 'ws://localhost:8000/ws'
        this.ws = new WebSocket(`${wsUrl}?user_id=${userId}`)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }

        this.ws.onmessage = (event) => {
          this.handleMessage(event.data)
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.stopHeartbeat()
          this.handleReconnect()
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }

        // Set connection timeout
        setTimeout(() => {
          if (this.ws?.readyState !== WebSocket.OPEN) {
            reject(new Error('WebSocket connection timeout'))
          }
        }, 5000)

      } catch (error) {
        reject(error)
      }
    })
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.stopHeartbeat()
    this.subscriptions.clear()
  }

  private handleMessage(data: string): void {
    try {
      const message: WebSocketMessage = JSON.parse(data)
      const store = useTradingStore.getState()

      switch (message.type) {
        case 'market_data':
          this.handleMarketData(message.data)
          break
        case 'order_update':
          this.handleOrderUpdate(message.data)
          break
        case 'position_update':
          this.handlePositionUpdate(message.data)
          break
        case 'trading_signal':
          this.handleTradingSignal(message.data)
          break
        case 'risk_alert':
          this.handleRiskAlert(message.data)
          break
        default:
          console.warn('Unknown message type:', message.type)
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error)
    }
  }

  private handleMarketData(data: any): void {
    const store = useTradingStore.getState()
    // Update market data in store
    // This would typically update the marketData array
    console.log('Received market data:', data)
  }

  private handleOrderUpdate(data: any): void {
    const store = useTradingStore.getState()
    // Update order in store
    store.updateOrder(data.id, data)
    console.log('Received order update:', data)
  }

  private handlePositionUpdate(data: any): void {
    const store = useTradingStore.getState()
    // Update position in store
    store.updatePosition(data.symbol, data)
    console.log('Received position update:', data)
  }

  private handleTradingSignal(data: any): void {
    const store = useTradingStore.getState()
    // Add trading signal to store
    // store.addTradingSignal(data)
    console.log('Received trading signal:', data)
  }

  private handleRiskAlert(data: any): void {
    const store = useTradingStore.getState()
    // Add risk alert to store
    store.addAlert({
      id: Date.now().toString(),
      type: 'warning',
      title: 'Risk Alert',
      message: data.message,
      timestamp: new Date().toISOString(),
      read: false
    })
    console.log('Received risk alert:', data)
  }

  subscribeToSymbol(symbol: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.subscriptions.add(symbol)
      this.send({
        type: 'subscribe',
        symbol: symbol
      })
    }
  }

  unsubscribeFromSymbol(symbol: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.subscriptions.delete(symbol)
      this.send({
        type: 'unsubscribe',
        symbol: symbol
      })
    }
  }

  subscribeToUserUpdates(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.send({
        type: 'subscribe_user_updates'
      })
    }
  }

  private send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'heartbeat' })
      }
    }, 30000) // Send heartbeat every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      
      setTimeout(() => {
        // Attempt to reconnect
        this.connect('demo_user').catch(error => {
          console.error('Reconnection failed:', error)
        })
      }, this.reconnectDelay * this.reconnectAttempts)
    } else {
      console.error('Max reconnection attempts reached')
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  getConnectionState(): string {
    if (!this.ws) return 'disconnected'
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting'
      case WebSocket.OPEN: return 'connected'
      case WebSocket.CLOSING: return 'closing'
      case WebSocket.CLOSED: return 'closed'
      default: return 'unknown'
    }
  }
}

export const websocketService = new WebSocketService()

