import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  BellIcon, 
  ExclamationTriangleIcon, 
  InformationCircleIcon,
  CheckCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState([
    {
      id: 1,
      type: 'warning',
      title: 'High Volatility Alert',
      message: 'WTI crude oil has experienced 15% price movement in the last hour. Consider reviewing your positions.',
      timestamp: '5 minutes ago',
      read: false
    },
    {
      id: 2,
      type: 'info',
      title: 'System Maintenance',
      message: 'Scheduled maintenance will occur tonight at 2:00 AM UTC. Trading will remain available.',
      timestamp: '1 hour ago',
      read: false
    },
    {
      id: 3,
      type: 'success',
      title: 'Order Executed',
      message: 'Your BUY order for 1000 WTI barrels at $78.45 has been successfully executed.',
      timestamp: '2 hours ago',
      read: true
    },
    {
      id: 4,
      type: 'error',
      title: 'Connection Issue',
      message: 'Temporary connection issue with ICE data feed. Using backup data sources.',
      timestamp: '3 hours ago',
      read: false
    }
  ])

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'warning': return <ExclamationTriangleIcon className="w-5 h-5 text-warning-500" />
      case 'info': return <InformationCircleIcon className="w-5 h-5 text-info-500" />
      case 'success': return <CheckCircleIcon className="w-5 h-5 text-success-500" />
      case 'error': return <ExclamationTriangleIcon className="w-5 h-5 text-danger-500" />
      default: return <BellIcon className="w-5 h-5 text-secondary-500" />
    }
  }

  const getAlertStyle = (type: string) => {
    switch (type) {
      case 'warning': return 'border-warning-200 bg-warning-50'
      case 'info': return 'border-info-200 bg-info-50'
      case 'success': return 'border-success-200 bg-success-50'
      case 'error': return 'border-danger-200 bg-danger-50'
      default: return 'border-secondary-200 bg-secondary-50'
    }
  }

  const getAlertTextColor = (type: string) => {
    switch (type) {
      case 'warning': return 'text-warning-800'
      case 'info': return 'text-info-800'
      case 'success': return 'text-success-800'
      case 'error': return 'text-danger-800'
      default: return 'text-secondary-800'
    }
  }

  const markAsRead = (id: number) => {
    setAlerts(alerts.map(alert => 
      alert.id === id ? { ...alert, read: true } : alert
    ))
  }

  const dismissAlert = (id: number) => {
    setAlerts(alerts.filter(alert => alert.id !== id))
  }

  const unreadCount = alerts.filter(alert => !alert.read).length

  return (
    <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-secondary-900">Alerts & Notifications</h2>
        <div className="flex items-center space-x-2">
          <BellIcon className="w-5 h-5 text-primary-500" />
          <span className="text-sm text-primary-600 font-medium">
            {unreadCount} unread
          </span>
        </div>
      </div>
      
      <div className="space-y-4">
        {alerts.map((alert, index) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`border rounded-lg p-4 ${getAlertStyle(alert.type)} ${
              alert.read ? 'opacity-75' : ''
            }`}
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 mt-0.5">
                {getAlertIcon(alert.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className={`text-sm font-medium ${getAlertTextColor(alert.type)}`}>
                    {alert.title}
                  </h3>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-secondary-500">
                      {alert.timestamp}
                    </span>
                    
                    {!alert.read && (
                      <button
                        onClick={() => markAsRead(alert.id)}
                        className="text-xs text-primary-600 hover:text-primary-800 transition-colors"
                      >
                        Mark as read
                      </button>
                    )}
                    
                    <button
                      onClick={() => dismissAlert(alert.id)}
                      className="text-secondary-400 hover:text-secondary-600 transition-colors"
                    >
                      <XMarkIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <p className={`mt-1 text-sm ${getAlertTextColor(alert.type)}`}>
                  {alert.message}
                </p>
                
                {!alert.read && (
                  <div className="mt-2">
                    <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      {alerts.length === 0 && (
        <div className="text-center py-8">
          <BellIcon className="w-12 h-12 text-secondary-300 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-secondary-900 mb-1">No Alerts</h3>
          <p className="text-sm text-secondary-600">
            You're all caught up! No new alerts at the moment.
          </p>
        </div>
      )}
      
      <div className="mt-6 p-4 bg-secondary-50 rounded-lg border border-secondary-200">
        <div className="flex items-center space-x-2 mb-2">
          <InformationCircleIcon className="w-5 h-5 text-secondary-500" />
          <span className="text-sm font-medium text-secondary-700">Alert Settings</span>
        </div>
        <p className="text-sm text-secondary-600">
          Configure your alert preferences for price movements, system updates, and trading notifications 
          in your account settings.
        </p>
      </div>
    </div>
  )
}

export default Alerts
