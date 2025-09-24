# QuantaEnergi Mobile Application

A comprehensive React Native mobile application for the QuantaEnergi ETRM platform, providing real-time trading, portfolio management, and analytics capabilities.

## Features

### Core Trading Features
- **Real-time Market Data**: Live commodity prices, volume, and market updates
- **Portfolio Management**: View positions, P&L, and portfolio performance
- **Order Placement**: Buy/sell orders with real-time execution
- **Trade History**: Complete trade history with status tracking

### Advanced Analytics
- **Performance Metrics**: Sharpe ratio, max drawdown, VaR calculations
- **Risk Analytics**: Real-time risk monitoring and alerts
- **Islamic Compliance**: Built-in Sharia compliance checking
- **Multi-timeframe Analysis**: 1D, 1W, 1M, 3M, 1Y performance views

### Mobile-Specific Features
- **Offline Capabilities**: Cache market data and positions for offline viewing
- **Push Notifications**: Real-time alerts for price movements and trade executions
- **Biometric Authentication**: Secure login with fingerprint/face ID
- **Dark Mode**: Modern UI with dark/light theme support

## Technical Architecture

### React Native Stack
- **React Native 0.72.7**: Latest stable version with Hermes engine
- **TypeScript**: Full type safety and better developer experience
- **React Navigation 6**: Modern navigation with bottom tabs and stack navigation
- **Vector Icons**: Material Design icons for consistent UI

### State Management
- **React Hooks**: useState, useEffect for local state management
- **AsyncStorage**: Persistent storage for user preferences and cached data
- **Context API**: Global state for user authentication and settings

### API Integration
- **Axios**: HTTP client for API communication
- **WebSocket**: Real-time market data streaming
- **RESTful APIs**: Integration with QuantaEnergi backend services

### Security Features
- **Biometric Authentication**: Secure device-based authentication
- **Keychain Storage**: Secure storage for sensitive data
- **Certificate Pinning**: Enhanced security for API communications
- **JWT Tokens**: Stateless authentication with refresh tokens

## Installation & Setup

### Prerequisites
- Node.js 16+ 
- React Native CLI
- Android Studio (for Android development)
- Xcode (for iOS development)

### Installation Steps

1. **Install Dependencies**
   ```bash
   cd apps/mobile
   npm install
   ```

2. **iOS Setup**
   ```bash
   cd ios
   pod install
   cd ..
   ```

3. **Android Setup**
   ```bash
   # No additional setup required for Android
   ```

4. **Start Metro Bundler**
   ```bash
   npm start
   ```

5. **Run on Device/Simulator**
   ```bash
   # Android
   npm run android
   
   # iOS
   npm run ios
   ```

## Project Structure

```
apps/mobile/
├── App.tsx                 # Main application component
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── babel.config.js        # Babel configuration
├── metro.config.js        # Metro bundler configuration
├── src/
│   ├── components/        # Reusable UI components
│   ├── screens/          # Screen components
│   ├── services/         # API and business logic
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions
│   └── constants/       # App constants
├── android/             # Android-specific code
├── ios/                 # iOS-specific code
└── __tests__/           # Test files
```

## Development Guidelines

### Code Style
- **ESLint**: Enforced code quality and consistency
- **Prettier**: Automatic code formatting
- **TypeScript**: Strict type checking enabled
- **React Native Best Practices**: Following official guidelines

### Testing
- **Jest**: Unit testing framework
- **React Native Testing Library**: Component testing
- **E2E Testing**: Playwright for end-to-end testing

### Performance
- **Hermes Engine**: Faster startup and reduced memory usage
- **Image Optimization**: Lazy loading and caching
- **Bundle Splitting**: Optimized bundle sizes
- **Memory Management**: Proper cleanup and garbage collection

## API Integration

### Authentication
```typescript
// Biometric authentication
const authenticate = async () => {
  const result = await Biometrics.authenticate({
    promptMessage: 'Authenticate to access QuantaEnergi'
  });
  return result.success;
};
```

### Market Data
```typescript
// Real-time market data
const fetchMarketData = async () => {
  const response = await api.get('/market-data');
  return response.data;
};
```

### Trading Operations
```typescript
// Place order
const placeOrder = async (order: OrderRequest) => {
  const response = await api.post('/orders', order);
  return response.data;
};
```

## Deployment

### Android
```bash
# Build release APK
npm run build:android

# Generate signed APK
cd android
./gradlew assembleRelease
```

### iOS
```bash
# Build for App Store
npm run build:ios

# Archive for distribution
cd ios
xcodebuild -workspace QuantaEnergiMobile.xcworkspace -scheme QuantaEnergiMobile -configuration Release -destination generic/platform=iOS -archivePath QuantaEnergiMobile.xcarchive archive
```

## Security Considerations

### Data Protection
- **Encryption**: All sensitive data encrypted at rest
- **Secure Communication**: HTTPS/TLS for all API calls
- **Authentication**: Multi-factor authentication support
- **Session Management**: Secure token handling and refresh

### Compliance
- **GDPR**: Data privacy and user consent management
- **PCI DSS**: Secure payment processing
- **SOX**: Financial data integrity and audit trails
- **Islamic Finance**: Sharia compliance validation

## Monitoring & Analytics

### Performance Monitoring
- **Crash Reporting**: Automatic crash detection and reporting
- **Performance Metrics**: App performance and user experience tracking
- **Analytics**: User behavior and feature usage analytics

### Business Metrics
- **Trading Volume**: Track mobile trading activity
- **User Engagement**: Feature usage and session analytics
- **Revenue Tracking**: Mobile app revenue attribution

## Support & Maintenance

### Bug Reporting
- **Crash Reporting**: Automatic crash logs with stack traces
- **User Feedback**: In-app feedback and rating system
- **Support Tickets**: Integrated support ticket system

### Updates
- **Over-the-Air Updates**: CodePush for JavaScript updates
- **App Store Updates**: Regular app store releases
- **Feature Flags**: Dynamic feature enablement/disablement

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

Proprietary - QuantaEnergi Technologies
