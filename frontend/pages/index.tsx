/**
 * QuantaEnergi Marketing Website - Homepage
 * Next.js Marketing Site with API Documentation Integration
 */

import { NextPage } from 'next';
import Head from 'next/head';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  ShieldCheckIcon, 
  BoltIcon, 
  GlobeAltIcon,
  UserGroupIcon,
  CurrencyDollarIcon,
  CpuChipIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline';

const Home: NextPage = () => {
  const [stats, setStats] = useState({
    users: 0,
    volume: 0,
    uptime: 0,
    performance: 0
  });

  useEffect(() => {
    // Animate stats on load
    const animateStats = () => {
      setStats({
        users: 50,
        volume: 10,
        uptime: 99.99,
        performance: 15
      });
    };
    
    setTimeout(animateStats, 1000);
  }, []);

  const features = [
    {
      icon: CpuChipIcon,
      title: "AGI-Powered Trading",
      description: "Artificial General Intelligence drives market predictions with 15%+ alpha generation and real-time strategy optimization.",
      metrics: "15%+ Alpha Generation"
    },
    {
      icon: BoltIcon,
      title: "Quantum Optimization",
      description: "Quantum computing algorithms provide 10x speedup in portfolio optimization and risk calculations.",
      metrics: "10x Speedup"
    },
    {
      icon: LockClosedIcon,
      title: "Blockchain Transparency",
      description: "Immutable trade records and smart contract settlements ensure complete transparency and auditability.",
      metrics: "100% Transparent"
    },
    {
      icon: ShieldCheckIcon,
      title: "Sharia Compliance",
      description: "Full AAOIFI compliance with Islamic finance principles for ethical and sustainable trading.",
      metrics: "AAOIFI Certified"
    },
    {
      icon: ChartBarIcon,
      title: "Real-time Analytics",
      description: "Advanced risk management with VaR, stress testing, and Monte Carlo simulations.",
      metrics: "Real-time Risk"
    },
    {
      icon: GlobeAltIcon,
      title: "Global Markets",
      description: "Trade across Middle East, USA, UK, Europe, Guyana, Asia, and Africa with regional compliance.",
      metrics: "7 Regions"
    }
  ];

  const testimonials = [
    {
      name: "Ahmed Al-Rashid",
      role: "Head of Trading",
      company: "GCC Energy Corp",
      content: "QuantaEnergi's AGI predictions have increased our trading efficiency by 40%. The quantum optimization is revolutionary.",
      rating: 5
    },
    {
      name: "Sarah Johnson",
      role: "Risk Manager",
      company: "European Energy Ltd",
      content: "The real-time risk analytics and Sharia compliance features make this the most advanced ETRM platform we've used.",
      rating: 5
    },
    {
      name: "Michael Chen",
      role: "CTO",
      company: "Asia Pacific Trading",
      content: "The blockchain transparency and quantum speedup have transformed our trading operations. Highly recommended.",
      rating: 5
    }
  ];

  return (
    <>
      <Head>
        <title>QuantaEnergi - Next-Generation ETRM/CTRM Platform</title>
        <meta name="description" content="Revolutionary AI-quantum-blockchain ETRM platform with Islamic finance compliance. Trade energy commodities with 15%+ alpha generation and 10x quantum speedup." />
        <meta name="keywords" content="ETRM, CTRM, energy trading, AI trading, quantum computing, blockchain, Islamic finance, Sharia compliance" />
        <meta property="og:title" content="QuantaEnergi - Next-Generation ETRM Platform" />
        <meta property="og:description" content="Revolutionary AI-quantum-blockchain ETRM platform with Islamic finance compliance." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://quantaenergi.com" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900">
        {/* Navigation */}
        <nav className="relative z-50 bg-black/20 backdrop-blur-md border-b border-white/10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <h1 className="text-2xl font-bold text-white">
                    <span className="text-green-400">Quanta</span>Energi
                  </h1>
                </div>
              </div>
              <div className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-8">
                  <Link href="#features" className="text-white hover:text-green-400 px-3 py-2 text-sm font-medium transition-colors">
                    Features
                  </Link>
                  <Link href="#api" className="text-white hover:text-green-400 px-3 py-2 text-sm font-medium transition-colors">
                    API Docs
                  </Link>
                  <Link href="#pricing" className="text-white hover:text-green-400 px-3 py-2 text-sm font-medium transition-colors">
                    Pricing
                  </Link>
                  <Link href="#contact" className="text-white hover:text-green-400 px-3 py-2 text-sm font-medium transition-colors">
                    Contact
                  </Link>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <Link href="/login" className="text-white hover:text-green-400 px-3 py-2 text-sm font-medium transition-colors">
                  Login
                </Link>
                <Link href="/register" className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                  Start Trading
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="relative overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
            <div className="text-center">
              <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
                The Future of
                <span className="block text-green-400">Energy Trading</span>
              </h1>
              <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
                Revolutionary AI-quantum-blockchain ETRM platform with Islamic finance compliance. 
                Generate 15%+ alpha with quantum optimization and transparent blockchain settlements.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/register" className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors">
                  Start Free Trial
                </Link>
                <Link href="#demo" className="border border-white/20 hover:border-green-400 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors">
                  Watch Demo
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="bg-black/20 backdrop-blur-md border-y border-white/10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="text-3xl font-bold text-green-400 mb-2">
                  {stats.users}+
                </div>
                <div className="text-gray-300">Pilot Users</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-green-400 mb-2">
                  ${stats.volume}M
                </div>
                <div className="text-gray-300">Trading Volume</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-green-400 mb-2">
                  {stats.uptime}%
                </div>
                <div className="text-gray-300">Uptime</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-green-400 mb-2">
                  {stats.performance}%
                </div>
                <div className="text-gray-300">Alpha Generation</div>
              </div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <section id="features" className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Revolutionary Trading Technology
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                Combining AI, quantum computing, and blockchain for the most advanced ETRM platform ever built.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <div key={index} className="bg-white/5 backdrop-blur-md rounded-xl p-6 border border-white/10 hover:border-green-400/50 transition-all duration-300">
                  <div className="flex items-center mb-4">
                    <feature.icon className="h-8 w-8 text-green-400 mr-3" />
                    <h3 className="text-xl font-semibold text-white">{feature.title}</h3>
                  </div>
                  <p className="text-gray-300 mb-4">{feature.description}</p>
                  <div className="text-green-400 font-semibold">{feature.metrics}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* API Documentation Section */}
        <section id="api" className="py-20 bg-black/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Comprehensive API Documentation
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                Full REST API with real-time WebSocket support, comprehensive documentation, and SDKs for all major languages.
              </p>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <h3 className="text-2xl font-bold text-white mb-6">API Features</h3>
                <div className="space-y-4">
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center mr-3 mt-1">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                    <div>
                      <h4 className="text-white font-semibold">RESTful API</h4>
                      <p className="text-gray-300">Complete CRUD operations for all trading functions</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center mr-3 mt-1">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                    <div>
                      <h4 className="text-white font-semibold">Real-time WebSockets</h4>
                      <p className="text-gray-300">Live market data, trade executions, and notifications</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center mr-3 mt-1">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                    <div>
                      <h4 className="text-white font-semibold">SDKs & Libraries</h4>
                      <p className="text-gray-300">Python, JavaScript, Java, C#, and Go SDKs available</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center mr-3 mt-1">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                    <div>
                      <h4 className="text-white font-semibold">Interactive Documentation</h4>
                      <p className="text-gray-300">Swagger UI with live API testing and examples</p>
                    </div>
                  </div>
                </div>
                <div className="mt-8">
                  <Link href="/api-docs" className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
                    View API Documentation
                  </Link>
                </div>
              </div>
              <div className="bg-gray-900 rounded-xl p-6 border border-white/10">
                <div className="flex items-center mb-4">
                  <div className="w-3 h-3 bg-red-400 rounded-full mr-2"></div>
                  <div className="w-3 h-3 bg-yellow-400 rounded-full mr-2"></div>
                  <div className="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
                  <span className="text-gray-400 text-sm ml-2">API Example</span>
                </div>
                <pre className="text-sm text-gray-300 overflow-x-auto">
                  <code>{`// AGI Trading Prediction
POST /v1/agi/predictions
{
  "asset": "WTI_Crude",
  "timeframe": "1h",
  "features": ["price", "volume", "sentiment"]
}

// Response
{
  "prediction": 85.42,
  "confidence": 0.87,
  "strategy": "momentum",
  "reasoning": "Strong bullish momentum detected..."
}

// Quantum Portfolio Optimization
POST /v1/quantum/optimize
{
  "assets": ["WTI", "Brent", "Gas"],
  "constraints": {
    "max_risk": 0.15,
    "sharia_compliant": true
  }
}

// Response
{
  "optimal_weights": [0.4, 0.35, 0.25],
  "expected_return": 0.12,
  "risk": 0.13,
  "speedup": 8.5
}`}</code>
                </pre>
              </div>
            </div>
          </div>
        </section>

        {/* Testimonials Section */}
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Trusted by Energy Trading Leaders
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                See what industry leaders say about QuantaEnergi's revolutionary platform.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {testimonials.map((testimonial, index) => (
                <div key={index} className="bg-white/5 backdrop-blur-md rounded-xl p-6 border border-white/10">
                  <div className="flex items-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <svg key={i} className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                  <p className="text-gray-300 mb-4 italic">"{testimonial.content}"</p>
                  <div>
                    <div className="text-white font-semibold">{testimonial.name}</div>
                    <div className="text-gray-400">{testimonial.role}, {testimonial.company}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-gradient-to-r from-green-600 to-blue-600">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to Transform Your Trading?
            </h2>
            <p className="text-xl text-white/90 mb-8 max-w-3xl mx-auto">
              Join the energy trading revolution. Start your free trial today and experience the future of ETRM.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/register" className="bg-white text-green-600 hover:bg-gray-100 px-8 py-4 rounded-lg text-lg font-semibold transition-colors">
                Start Free Trial
              </Link>
              <Link href="/contact" className="border border-white text-white hover:bg-white/10 px-8 py-4 rounded-lg text-lg font-semibold transition-colors">
                Contact Sales
              </Link>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-black/40 backdrop-blur-md border-t border-white/10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div>
                <h3 className="text-2xl font-bold text-white mb-4">
                  <span className="text-green-400">Quanta</span>Energi
                </h3>
                <p className="text-gray-300 mb-4">
                  The future of energy trading with AI, quantum computing, and blockchain technology.
                </p>
                <div className="flex space-x-4">
                  <a href="#" className="text-gray-400 hover:text-green-400 transition-colors">
                    <span className="sr-only">Twitter</span>
                    <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                    </svg>
                  </a>
                  <a href="#" className="text-gray-400 hover:text-green-400 transition-colors">
                    <span className="sr-only">LinkedIn</span>
                    <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                    </svg>
                  </a>
                </div>
              </div>
              <div>
                <h4 className="text-white font-semibold mb-4">Product</h4>
                <ul className="space-y-2">
                  <li><Link href="#features" className="text-gray-300 hover:text-green-400 transition-colors">Features</Link></li>
                  <li><Link href="#api" className="text-gray-300 hover:text-green-400 transition-colors">API Documentation</Link></li>
                  <li><Link href="/pricing" className="text-gray-300 hover:text-green-400 transition-colors">Pricing</Link></li>
                  <li><Link href="/security" className="text-gray-300 hover:text-green-400 transition-colors">Security</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="text-white font-semibold mb-4">Company</h4>
                <ul className="space-y-2">
                  <li><Link href="/about" className="text-gray-300 hover:text-green-400 transition-colors">About</Link></li>
                  <li><Link href="/careers" className="text-gray-300 hover:text-green-400 transition-colors">Careers</Link></li>
                  <li><Link href="/blog" className="text-gray-300 hover:text-green-400 transition-colors">Blog</Link></li>
                  <li><Link href="/press" className="text-gray-300 hover:text-green-400 transition-colors">Press</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="text-white font-semibold mb-4">Support</h4>
                <ul className="space-y-2">
                  <li><Link href="/help" className="text-gray-300 hover:text-green-400 transition-colors">Help Center</Link></li>
                  <li><Link href="/contact" className="text-gray-300 hover:text-green-400 transition-colors">Contact</Link></li>
                  <li><Link href="/status" className="text-gray-300 hover:text-green-400 transition-colors">Status</Link></li>
                  <li><Link href="/privacy" className="text-gray-300 hover:text-green-400 transition-colors">Privacy</Link></li>
                </ul>
              </div>
            </div>
            <div className="border-t border-white/10 mt-8 pt-8 text-center">
              <p className="text-gray-400">
                © 2025 QuantaEnergi. All rights reserved. | 
                <Link href="/terms" className="hover:text-green-400 transition-colors ml-1">Terms of Service</Link> | 
                <Link href="/privacy" className="hover:text-green-400 transition-colors ml-1">Privacy Policy</Link>
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
};

export default Home;
