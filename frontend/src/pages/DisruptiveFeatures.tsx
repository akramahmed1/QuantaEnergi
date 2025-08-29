import React from 'react';
import { motion } from 'framer-motion';
import { 
  CpuChipIcon, 
  CubeIcon, 
  ShieldCheckIcon, 
  WifiIcon,
  ChartBarIcon,
  TrendingUpIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  CogIcon,
  BellIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';

const DisruptiveFeatures: React.FC = () => {
  const features = [
    {
      id: 'ai-forecasting',
      title: 'AI-Powered Forecasting',
      description: 'Advanced machine learning algorithms for energy demand prediction, price breakout detection, and ESG scoring',
      icon: CpuChipIcon,
      color: 'from-blue-500 to-cyan-500',
      benefits: ['Demand forecasting with 95% accuracy', 'Price breakout detection', 'ESG scoring and analysis', 'Grok AI integration'],
      route: '/dashboard?tab=ai-forecasting'
    },
    {
      id: 'quantum-optimization',
      title: 'Quantum Portfolio Optimization',
      description: 'Quantum computing algorithms (QAOA, VQE) for optimal portfolio allocation with classical fallbacks',
      icon: CubeIcon,
      color: 'from-purple-500 to-pink-500',
      benefits: ['Quantum advantage up to 25%', 'Portfolio risk optimization', 'Real-time rebalancing', 'Classical fallback systems'],
      route: '/dashboard?tab=quantum'
    },
    {
      id: 'blockchain',
      title: 'Blockchain Smart Contracts',
      description: 'Secure and transparent energy trading, carbon credits, and ESG certificates on the blockchain',
      icon: ShieldCheckIcon,
      color: 'from-green-500 to-emerald-500',
      benefits: ['Smart contract automation', 'Carbon credit trading', 'ESG certificate verification', 'Transparent transactions'],
      route: '/dashboard?tab=blockchain'
    },
    {
      id: 'iot-integration',
      title: 'IoT Integration Hub',
      description: 'Real-time monitoring of energy infrastructure, weather data, and grid stability analysis',
      icon: WifiIcon,
      color: 'from-orange-500 to-red-500',
      benefits: ['Real-time sensor data', 'Weather integration', 'Grid stability monitoring', 'Predictive maintenance'],
      route: '/dashboard?tab=iot'
    },
    {
      id: 'compliance',
      title: 'Multi-Region Compliance',
      description: 'Comprehensive compliance monitoring across US, EU, UK, Middle East, and Guyana regulations',
      icon: ShieldCheckIcon,
      color: 'from-indigo-500 to-purple-500',
      benefits: ['FERC, REMIT, UK-ETS compliance', 'ADNOC and Islamic Finance', 'Real-time audit tracking', 'Risk assessment'],
      route: '/dashboard?tab=compliance'
    }
  ];

  const stats = [
    { label: 'AI Models', value: '15+', description: 'Machine learning algorithms' },
    { label: 'Quantum Advantage', value: '25%', description: 'Portfolio optimization improvement' },
    { label: 'Compliance Regions', value: '5', description: 'Multi-jurisdictional coverage' },
    { label: 'IoT Devices', value: '1000+', description: 'Connected sensors and controllers' },
    { label: 'Smart Contracts', value: '50+', description: 'Deployed on blockchain' },
    { label: 'ESG Score', value: '92', description: 'Average compliance rating' }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative overflow-hidden bg-white"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.8 }}
              className="text-5xl md:text-6xl font-bold text-gray-900 mb-6"
            >
              Disruptive Energy Trading
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                Technology Stack
              </span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.8 }}
              className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto"
            >
              Experience the future of energy trading with AI forecasting, quantum optimization, 
              blockchain smart contracts, IoT integration, and multi-region compliance.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.8 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link
                to="/dashboard"
                className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                <ChartBarIcon className="w-5 h-5 mr-2" />
                Launch Platform
              </Link>
              <Link
                to="/optimization"
                className="inline-flex items-center px-8 py-4 bg-white text-gray-700 font-semibold rounded-lg border-2 border-gray-300 hover:border-gray-400 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                <TrendingUpIcon className="w-5 h-5 mr-2" />
                View Demo
              </Link>
            </motion.div>
          </div>
        </div>
        
        {/* Background Pattern */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-50/50 to-purple-50/50" />
          <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%239C92AC" fill-opacity="0.05"%3E%3Ccircle cx="30" cy="30" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')]" />
        </div>
      </motion.div>

      {/* Stats Section */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="py-16 bg-white"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                variants={itemVariants}
                className="text-center"
              >
                <div className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
                <div className="text-sm font-medium text-gray-600 mb-1">{stat.label}</div>
                <div className="text-xs text-gray-500">{stat.description}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Features Grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="py-16"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            variants={itemVariants}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Revolutionary Features
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Each feature is designed to address real industry pain points and provide 
              measurable competitive advantages in energy trading.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => (
              <motion.div
                key={feature.id}
                variants={itemVariants}
                className="group relative"
              >
                <div className="relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden">
                  {/* Icon Header */}
                  <div className={`bg-gradient-to-r ${feature.color} p-6 text-white`}>
                    <feature.icon className="w-12 h-12" />
                  </div>
                  
                  {/* Content */}
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-3">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 mb-4">
                      {feature.description}
                    </p>
                    
                    {/* Benefits */}
                    <ul className="space-y-2 mb-6">
                      {feature.benefits.map((benefit, index) => (
                        <li key={index} className="flex items-center text-sm text-gray-600">
                          <div className="w-2 h-2 bg-green-500 rounded-full mr-3" />
                          {benefit}
                        </li>
                      ))}
                    </ul>
                    
                    {/* CTA Button */}
                    <Link
                      to={feature.route}
                      className="inline-flex items-center justify-center w-full px-4 py-3 bg-gray-900 text-white font-medium rounded-lg hover:bg-gray-800 transition-colors duration-200 group-hover:bg-gradient-to-r group-hover:from-blue-600 group-hover:to-purple-600"
                    >
                      Explore Feature
                      <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </Link>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* CTA Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="py-16 bg-gradient-to-r from-blue-600 to-purple-600"
      >
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Energy Trading?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join the future of energy trading with our disruptive technology stack. 
            Experience unprecedented efficiency, accuracy, and compliance.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/signup"
              className="inline-flex items-center px-8 py-4 bg-white text-blue-600 font-semibold rounded-lg hover:bg-gray-100 transition-colors duration-200 shadow-lg"
            >
              <CurrencyDollarIcon className="w-5 h-5 mr-2" />
              Start Free Trial
            </Link>
            <Link
              to="/dashboard"
              className="inline-flex items-center px-8 py-4 bg-transparent text-white font-semibold rounded-lg border-2 border-white hover:bg-white hover:text-blue-600 transition-all duration-200"
            >
              <CogIcon className="w-5 h-5 mr-2" />
              View Platform
            </Link>
          </div>
        </div>
      </motion.div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">EnergyOpti-Pro</h3>
              <p className="text-gray-400">
                Disruptive energy trading SaaS platform powered by AI, quantum computing, 
                blockchain, and IoT technologies.
              </p>
            </div>
            <div>
              <h4 className="text-md font-semibold mb-4">Features</h4>
              <ul className="space-y-2 text-gray-400">
                <li>AI Forecasting</li>
                <li>Quantum Optimization</li>
                <li>Blockchain Contracts</li>
                <li>IoT Integration</li>
              </ul>
            </div>
            <div>
              <h4 className="text-md font-semibold mb-4">Compliance</h4>
              <ul className="space-y-2 text-gray-400">
                <li>FERC (US)</li>
                <li>REMIT (EU)</li>
                <li>UK-ETS</li>
                <li>ADNOC (ME)</li>
              </ul>
            </div>
            <div>
              <h4 className="text-md font-semibold mb-4">Contact</h4>
              <ul className="space-y-2 text-gray-400">
                <li>support@energyopti-pro.com</li>
                <li>+1 (555) 123-4567</li>
                <li>24/7 Support</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 EnergyOpti-Pro. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default DisruptiveFeatures;
