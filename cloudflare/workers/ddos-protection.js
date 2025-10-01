/**
 * Cloudflare Workers DDoS Protection Script
 * Advanced DDoS protection for QuantaEnergi energy trading platform
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

// DDoS protection configuration
const DDOS_CONFIG = {
  // Rate limiting thresholds
  rateLimits: {
    api: { requests: 100, window: 60 }, // 100 requests per minute for API
    auth: { requests: 10, window: 60 },  // 10 requests per minute for auth
    global: { requests: 1000, window: 60 } // 1000 requests per minute global
  },
  
  // Suspicious patterns
  suspiciousPatterns: [
    'bot', 'crawler', 'spider', 'scanner', 'nikto', 'sqlmap', 
    'nmap', 'masscan', 'burp', 'zap', 'wget', 'curl',
    'python-requests', 'go-http-client', 'java-http-client'
  ],
  
  // Blocked IP ranges (CIDR notation)
  blockedIPRanges: [
    '10.0.0.0/8',
    '172.16.0.0/12',
    '192.168.0.0/16',
    '127.0.0.0/8'
  ],
  
  // Malicious domains
  maliciousDomains: [
    'malware.com', 'phishing.com', 'botnet.com', 'scam.com'
  ],
  
  // Security headers
  securityHeaders: {
    'X-DDoS-Protection': 'Cloudflare',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
  }
}

// Cache for rate limiting (in production, use KV storage)
const rateLimitCache = new Map()

async function handleRequest(request) {
  try {
    // Extract request information
    const url = new URL(request.url)
    const clientIP = request.headers.get('CF-Connecting-IP') || 'unknown'
    const userAgent = request.headers.get('User-Agent') || ''
    const path = url.pathname
    
    // Perform DDoS protection checks
    const ddosCheck = await performDDoSProtection(request, clientIP, userAgent, path)
    
    if (ddosCheck.blocked) {
      return createBlockedResponse(ddosCheck.reason, ddosCheck.retryAfter)
    }
    
    // Forward request to origin
    const response = await fetch(request)
    
    // Add security headers to response
    return addSecurityHeaders(response)
    
  } catch (error) {
    console.error('DDoS protection error:', error)
    // Allow request to proceed if protection fails
    return fetch(request)
  }
}

async function performDDoSProtection(request, clientIP, userAgent, path) {
  const checks = [
    checkIPBlacklist(clientIP),
    checkRateLimit(clientIP, path),
    checkSuspiciousUserAgent(userAgent),
    checkMissingHeaders(request),
    checkMaliciousDomain(request),
    checkRequestSize(request),
    checkRequestFrequency(clientIP)
  ]
  
  const results = await Promise.all(checks)
  
  // Check if any protection rule was triggered
  for (const result of results) {
    if (result.blocked) {
      return result
    }
  }
  
  return { blocked: false }
}

function checkIPBlacklist(clientIP) {
  // Check if IP is in blocked ranges
  for (const cidr of DDOS_CONFIG.blockedIPRanges) {
    if (isIPInCIDR(clientIP, cidr)) {
      return {
        blocked: true,
        reason: 'IP address blocked',
        retryAfter: 3600 // 1 hour
      }
    }
  }
  
  return { blocked: false }
}

async function checkRateLimit(clientIP, path) {
  const now = Date.now()
  const window = 60 * 1000 // 1 minute in milliseconds
  
  // Determine rate limit based on path
  let limit = DDOS_CONFIG.rateLimits.global
  if (path.startsWith('/api/auth/')) {
    limit = DDOS_CONFIG.rateLimits.auth
  } else if (path.startsWith('/api/')) {
    limit = DDOS_CONFIG.rateLimits.api
  }
  
  // Get or create rate limit entry
  const key = `${clientIP}:${path}`
  let entry = rateLimitCache.get(key)
  
  if (!entry) {
    entry = { requests: [], windowStart: now }
    rateLimitCache.set(key, entry)
  }
  
  // Clean old requests outside the window
  entry.requests = entry.requests.filter(timestamp => now - timestamp < window)
  
  // Check if rate limit exceeded
  if (entry.requests.length >= limit.requests) {
    return {
      blocked: true,
      reason: 'Rate limit exceeded',
      retryAfter: Math.ceil((entry.requests[0] + window - now) / 1000)
    }
  }
  
  // Add current request
  entry.requests.push(now)
  
  return { blocked: false }
}

function checkSuspiciousUserAgent(userAgent) {
  const userAgentLower = userAgent.toLowerCase()
  
  for (const pattern of DDOS_CONFIG.suspiciousPatterns) {
    if (userAgentLower.includes(pattern)) {
      return {
        blocked: true,
        reason: 'Suspicious user agent detected',
        retryAfter: 1800 // 30 minutes
      }
    }
  }
  
  return { blocked: false }
}

function checkMissingHeaders(request) {
  const requiredHeaders = ['Accept', 'Accept-Language', 'User-Agent']
  const missingHeaders = requiredHeaders.filter(header => !request.headers.get(header))
  
  if (missingHeaders.length > 0) {
    return {
      blocked: true,
      reason: `Missing required headers: ${missingHeaders.join(', ')}`,
      retryAfter: 300 // 5 minutes
    }
  }
  
  return { blocked: false }
}

function checkMaliciousDomain(request) {
  const host = request.headers.get('Host')
  
  if (host) {
    for (const domain of DDOS_CONFIG.maliciousDomains) {
      if (host.includes(domain)) {
        return {
          blocked: true,
          reason: 'Malicious domain detected',
          retryAfter: 3600 // 1 hour
        }
      }
    }
  }
  
  return { blocked: false }
}

function checkRequestSize(request) {
  const contentLength = request.headers.get('Content-Length')
  const maxSize = 10 * 1024 * 1024 // 10MB
  
  if (contentLength && parseInt(contentLength) > maxSize) {
    return {
      blocked: true,
      reason: 'Request size too large',
      retryAfter: 300 // 5 minutes
    }
  }
  
  return { blocked: false }
}

async function checkRequestFrequency(clientIP) {
  const now = Date.now()
  const window = 1000 // 1 second
  const maxRequests = 10
  
  const key = `${clientIP}:frequency`
  let entry = rateLimitCache.get(key)
  
  if (!entry) {
    entry = { requests: [], windowStart: now }
    rateLimitCache.set(key, entry)
  }
  
  // Clean old requests outside the window
  entry.requests = entry.requests.filter(timestamp => now - timestamp < window)
  
  // Check burst frequency
  if (entry.requests.length >= maxRequests) {
    return {
      blocked: true,
      reason: 'Request frequency too high',
      retryAfter: 60 // 1 minute
    }
  }
  
  // Add current request
  entry.requests.push(now)
  
  return { blocked: false }
}

function isIPInCIDR(ip, cidr) {
  try {
    const [network, prefixLength] = cidr.split('/')
    const ipNum = ipToNumber(ip)
    const networkNum = ipToNumber(network)
    const mask = (0xFFFFFFFF << (32 - parseInt(prefixLength))) >>> 0
    
    return (ipNum & mask) === (networkNum & mask)
  } catch (error) {
    return false
  }
}

function ipToNumber(ip) {
  return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet), 0)
}

function createBlockedResponse(reason, retryAfter) {
  return new Response(JSON.stringify({
    error: 'Request blocked',
    message: reason,
    retry_after: retryAfter,
    timestamp: new Date().toISOString()
  }), {
    status: 429,
    statusText: 'Too Many Requests',
    headers: {
      'Content-Type': 'application/json',
      'Retry-After': retryAfter.toString(),
      'X-DDoS-Protection': 'Cloudflare',
      'X-Block-Reason': reason,
      ...DDOS_CONFIG.securityHeaders
    }
  })
}

function addSecurityHeaders(response) {
  const newHeaders = new Headers(response.headers)
  
  // Add all security headers
  Object.entries(DDOS_CONFIG.securityHeaders).forEach(([key, value]) => {
    newHeaders.set(key, value)
  })
  
  // Add DDoS protection status
  newHeaders.set('X-DDoS-Protection', 'Cloudflare')
  newHeaders.set('X-DDoS-Status', 'Protected')
  
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders
  })
}

// Cleanup rate limit cache periodically
setInterval(() => {
  const now = Date.now()
  const maxAge = 60 * 60 * 1000 // 1 hour
  
  for (const [key, entry] of rateLimitCache.entries()) {
    if (now - entry.windowStart > maxAge) {
      rateLimitCache.delete(key)
    }
  }
}, 5 * 60 * 1000) // Cleanup every 5 minutes
