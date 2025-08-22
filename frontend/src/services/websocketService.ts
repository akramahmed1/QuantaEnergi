import { WebSocketMessage } from '@/types/trading'
import { useTradingStore } from '@/store/tradingStore'

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private heartbeatInterval: NodeJS.Timeout | null = null
  private messageQueue: WebSocketMessage[] = []
  private isConnected = false
  private url: string

  constructor(url: string = 'ws://localhost:8000/ws') {
    this.url = url
  }

  connect(userId?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = userId ? `${this.url}?user_id=${userId}` : this.url
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.isConnected = true
          this.reconnectAttempts = 0
          this.startHeartbeat()
          this.processMessageQueue()
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.isConnected = false
          this.stopHeartbeat()
          
          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect()
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }

        // Set connection timeout
        setTimeout(() => {
          if (!this.isConnected) {
            reject(new Error('WebSocket connection timeout'))
          }
        }, 10000)

      } catch (error) {
        reject(error)
      }
    })
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'User disconnect')
      this.ws = null
    }
    this.isConnected = false
    this.stopHeartbeat()
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    
    console.log(`Scheduling WebSocket reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`)
    
    setTimeout(() => {
      if (!this.isConnected) {
        this.connect()
      }
    }, delay)
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected && this.ws) {
        this.send({
          type: 'heartbeat',
          data: { timestamp: new Date().toISOString() },
          timestamp: new Date().toISOString()
        })
      }
    }, 30000) // 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  send(message: WebSocketMessage): void {
    if (this.isConnected && this.ws) {
      this.ws.send(JSON.stringify(message))
    } else {
      this.messageQueue.push(message)
    }
  }

  private processMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift()
      if (message && this.isConnected && this.ws) {
        this.ws.send(JSON.stringify(message))
      }
    }
  }

  private handleMessage(message: WebSocketMessage): void {
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
      
      case 'system_status':
        this.handleSystemStatus(message.data)
        break
      
      case 'heartbeat':
        // Heartbeat response, no action needed
        break
      
      default:
        console.warn('Unknown WebSocket message type:', message.type)
    }
  }

  private handleMarketData(data: any): void {
    const store = useTradingStore.getState()
    
    if (data.symbol && data.price !== undefined) {
      store.setMarketData(data.symbol, {
        symbol: data.symbol,
        price: data.price,
        change: data.change || 0,
        changePercent: data.changePercent || 0,
        volume: data.volume || 0,
        high: data.high || data.price,
        low: data.low || data.price,
        open: data.open || data.price,
        previousClose: data.previousClose || data.price,
        timestamp: data.timestamp || new Date().toISOString(),
        bid: data.bid,
        ask: data.ask,
        spread: data.spread
      })
    }
  }

  private handleOrderUpdate(data: any): void {
    const store = useTradingStore.getState()
    
    if (data.orderId) {
      const existingOrder = store.orders.find(order => order.id === data.orderId)
      
      if (existingOrder) {
        store.updateOrder(data.orderId, {
          status: data.status,
          filledQuantity: data.filledQuantity || existingOrder.filledQuantity,
          averagePrice: data.averagePrice || existingOrder.averagePrice,
          commission: data.commission || existingOrder.commission
        })
      } else {
        // New order
        store.addOrder({
          id: data.orderId,
          symbol: data.symbol,
          side: data.side,
          type: data.type,
          quantity: data.quantity,
          price: data.price,
          stopPrice: data.stopPrice,
          status: data.status,
          filledQuantity: data.filledQuantity || 0,
          averagePrice: data.averagePrice || 0,
          commission: data.commission || 0,
          timestamp: data.timestamp || new Date().toISOString(),
          userId: data.userId,
          accountId: data.accountId,
          timeInForce: data.timeInForce || 'GTC'
        })
      }
    }
  }

  private handlePositionUpdate(data: any): void {
    const store = useTradingStore.getState()
    
    if (data.positionId) {
      const existingPosition = store.positions.find(pos => pos.id === data.positionId)
      
      if (existingPosition) {
        store.updatePosition(data.positionId, {
          currentPrice: data.currentPrice,
          marketValue: data.marketValue,
          unrealizedPnL: data.unrealizedPnL,
          margin: data.margin,
          timestamp: data.timestamp || new Date().toISOString()
        })
      } else {
        // New position
        store.positions.push({
          id: data.positionId,
          symbol: data.symbol,
          side: data.side,
          quantity: data.quantity,
          averagePrice: data.averagePrice,
          currentPrice: data.currentPrice,
          marketValue: data.marketValue,
          unrealizedPnL: data.unrealizedPnL || 0,
          realizedPnL: data.realizedPnL || 0,
          totalPnL: data.totalPnL || 0,
          margin: data.margin || 0,
          leverage: data.leverage || 1,
          timestamp: data.timestamp || new Date().toISOString(),
          userId: data.userId,
          accountId: data.accountId
        })
      }
    }
  }

  private handleTradingSignal(data: any): void {
    const store = useTradingStore.getState()
    
    if (data.id && data.symbol) {
      store.addTradingSignal({
        id: data.id,
        symbol: data.symbol,
        signal: data.signal,
        confidence: data.confidence,
        price: data.price,
        targetPrice: data.targetPrice,
        stopLoss: data.stopLoss,
        reasoning: data.reasoning,
        source: data.source,
        timestamp: data.timestamp || new Date().toISOString(),
        expiry: data.expiry,
        riskLevel: data.riskLevel
      })
    }
  }

  private handleRiskAlert(data: any): void {
    const store = useTradingStore.getState()
    
    if (data.alertId) {
      store.addAlert({
        id: data.alertId,
        userId: data.userId,
        type: 'risk',
        symbol: data.symbol,
        condition: data.condition,
        value: data.value,
        status: 'active',
        message: data.message,
        createdAt: data.timestamp || new Date().toISOString()
      })
    }
  }

  private handleSystemStatus(data: any): void {
    console.log('System status update:', data)
    
    if (data.status === 'maintenance') {
      // Handle maintenance mode
      console.warn('System entering maintenance mode')
    }
  }

  // Public methods for external use
  subscribeToSymbol(symbol: string): void {
    this.send({
      type: 'subscribe',
      data: { topic: `market_data:${symbol}` },
      timestamp: new Date().toISOString()
    })
  }

  unsubscribeFromSymbol(symbol: string): void {
    this.send({
      type: 'unsubscribe',
      data: { topic: `market_data:${symbol}` },
      timestamp: new Date().toISOString()
    })
  }

  subscribeToUserUpdates(userId: string): void {
    this.send({
      type: 'subscribe',
      data: { topic: `user:${userId}` },
      timestamp: new Date().toISOString()
    })
  }

  getConnectionStatus(): boolean {
    return this.isConnected
  }
}

// Create singleton instance
export const websocketService = new WebSocketService()

// Export for use in components
export default websocketService
