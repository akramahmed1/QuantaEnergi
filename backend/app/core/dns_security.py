"""
DNS Security and Protection Module
Enterprise-grade DNS security with DNSSEC, DNS over HTTPS/TLS, and DNS filtering
"""

import asyncio
import aiohttp
import dns.resolver
import dns.rdatatype
import dns.rdataclass
import dns.message
import dns.query
import dns.dnssec
import dns.zone
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
import json
import hashlib
import ipaddress
import structlog
from fastapi import HTTPException, status

logger = structlog.get_logger()

class DNSSecurityManager:
    """Comprehensive DNS security management"""
    
    def __init__(self):
        # DNS security configuration
        self.config = {
            'dns_servers': [
                '1.1.1.1',  # Cloudflare DNS
                '1.0.0.1',  # Cloudflare DNS
                '8.8.8.8',  # Google DNS
                '8.8.4.4',  # Google DNS
                '9.9.9.9',  # Quad9 DNS
                '9.9.9.10'  # Quad9 DNS (with security)
            ],
            'doh_servers': [
                'https://cloudflare-dns.com/dns-query',
                'https://dns.google/dns-query',
                'https://dns.quad9.net/dns-query'
            ],
            'dot_servers': [
                '1.1.1.1:853',
                '1.0.0.1:853',
                '8.8.8.8:853',
                '8.8.4.4:853'
            ],
            'malicious_domains': [
                'malware.com', 'phishing.com', 'botnet.com'
            ],
            'blocked_tlds': [
                '.tk', '.ml', '.ga', '.cf'  # Free TLDs often used for malicious purposes
            ],
            'cache_ttl': 300,  # 5 minutes
            'max_retries': 3,
            'timeout': 5
        }
        
        # DNS cache
        self.dns_cache: Dict[str, Dict[str, Any]] = {}
        self.negative_cache: Dict[str, datetime] = {}
        
        # Security statistics
        self.stats = {
            'total_queries': 0,
            'blocked_queries': 0,
            'malicious_domains_blocked': 0,
            'dnssec_validations': 0,
            'doh_queries': 0,
            'dot_queries': 0
        }
        
        # Threat intelligence feeds
        self.threat_feeds = [
            'https://reputation.alienvault.com/reputation.data',
            'https://feodotracker.abuse.ch/downloads/ipblocklist_recommended.txt'
        ]
    
    def _is_malicious_domain(self, domain: str) -> bool:
        """Check if domain is in malicious domain list"""
        domain_lower = domain.lower()
        
        # Check direct match
        if domain_lower in self.config['malicious_domains']:
            return True
        
        # Check subdomain matches
        for malicious in self.config['malicious_domains']:
            if domain_lower.endswith('.' + malicious):
                return True
        
        # Check blocked TLDs
        for tld in self.config['blocked_tlds']:
            if domain_lower.endswith(tld):
                return True
        
        return False
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private/internal"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local
        except ValueError:
            return True
    
    async def _query_doh(self, domain: str, record_type: str = 'A') -> Optional[Dict[str, Any]]:
        """Query DNS over HTTPS"""
        try:
            self.stats['doh_queries'] += 1
            
            async with aiohttp.ClientSession() as session:
                params = {
                    'name': domain,
                    'type': record_type
                }
                
                async with session.get(
                    self.config['doh_servers'][0],
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.config['timeout'])
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'method': 'doh',
                            'data': data,
                            'timestamp': datetime.now().isoformat()
                        }
        except Exception as e:
            logger.error(f"DoH query failed for {domain}: {e}")
        
        return None
    
    async def _query_dot(self, domain: str, record_type: str = 'A') -> Optional[Dict[str, Any]]:
        """Query DNS over TLS"""
        try:
            self.stats['dot_queries'] += 1
            
            # Create DNS query
            query = dns.message.make_query(domain, record_type)
            
            # Query DNS over TLS
            response = dns.query.tls(
                query,
                self.config['dot_servers'][0].split(':')[0],
                port=int(self.config['dot_servers'][0].split(':')[1]),
                timeout=self.config['timeout']
            )
            
            return {
                'method': 'dot',
                'data': response,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"DoT query failed for {domain}: {e}")
        
        return None
    
    async def _query_standard_dns(self, domain: str, record_type: str = 'A') -> Optional[Dict[str, Any]]:
        """Query standard DNS"""
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [self.config['dns_servers'][0]]
            resolver.timeout = self.config['timeout']
            
            result = resolver.resolve(domain, record_type)
            
            return {
                'method': 'standard',
                'data': [str(rdata) for rdata in result],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Standard DNS query failed for {domain}: {e}")
        
        return None
    
    async def _validate_dnssec(self, domain: str, response: Dict[str, Any]) -> bool:
        """Validate DNS response with DNSSEC"""
        try:
            self.stats['dnssec_validations'] += 1
            
            # This is a simplified DNSSEC validation
            # In production, use proper DNSSEC validation libraries
            
            # Check for RRSIG records in response
            if 'rrsig' in str(response.get('data', '')).lower():
                logger.info(f"DNSSEC signature found for {domain}")
                return True
            
            # For domains without DNSSEC, log warning
            logger.warning(f"No DNSSEC signature found for {domain}")
            return False
            
        except Exception as e:
            logger.error(f"DNSSEC validation failed for {domain}: {e}")
            return False
    
    async def resolve_domain(self, domain: str, record_type: str = 'A', 
                           secure_only: bool = False) -> Dict[str, Any]:
        """Resolve domain with security checks"""
        self.stats['total_queries'] += 1
        
        # Check cache first
        cache_key = f"{domain}:{record_type}"
        if cache_key in self.dns_cache:
            cached_data = self.dns_cache[cache_key]
            if datetime.now() - datetime.fromisoformat(cached_data['timestamp']) < timedelta(seconds=self.config['cache_ttl']):
                logger.debug(f"DNS cache hit for {domain}")
                return cached_data
        
        # Check negative cache
        if cache_key in self.negative_cache:
            if datetime.now() - self.negative_cache[cache_key] < timedelta(seconds=self.config['cache_ttl']):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Domain {domain} is temporarily blocked"
                )
        
        # Check if domain is malicious
        if self._is_malicious_domain(domain):
            self.stats['blocked_queries'] += 1
            self.stats['malicious_domains_blocked'] += 1
            logger.warning(f"Malicious domain blocked: {domain}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Domain {domain} is blocked for security reasons"
            )
        
        # Try different DNS methods
        result = None
        methods_tried = []
        
        # Try DoH first (most secure)
        if secure_only or not result:
            result = await self._query_doh(domain, record_type)
            methods_tried.append('doh')
        
        # Try DoT if DoH fails
        if not result:
            result = await self._query_dot(domain, record_type)
            methods_tried.append('dot')
        
        # Try standard DNS as fallback
        if not result:
            result = await self._query_standard_dns(domain, record_type)
            methods_tried.append('standard')
        
        if not result:
            # Add to negative cache
            self.negative_cache[cache_key] = datetime.now()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Domain {domain} could not be resolved"
            )
        
        # Validate DNSSEC if available
        dnssec_valid = await self._validate_dnssec(domain, result)
        result['dnssec_valid'] = dnssec_valid
        
        # Security checks on resolved IPs
        if 'data' in result:
            ips = []
            if isinstance(result['data'], list):
                ips = result['data']
            elif isinstance(result['data'], dict) and 'Answer' in result['data']:
                # Parse DoH response format
                for answer in result['data']['Answer']:
                    if answer.get('type') == 1:  # A record
                        ips.append(answer.get('data'))
            
            # Filter out private IPs
            public_ips = [ip for ip in ips if not self._is_private_ip(ip)]
            if not public_ips and ips:
                logger.warning(f"Only private IPs resolved for {domain}: {ips}")
            
            result['filtered_ips'] = public_ips
            result['original_ips'] = ips
        
        # Cache successful result
        self.dns_cache[cache_key] = result
        
        result['methods_tried'] = methods_tried
        result['domain'] = domain
        result['record_type'] = record_type
        
        logger.info(f"DNS resolution successful for {domain}: {result['method']}")
        return result
    
    async def update_threat_feeds(self):
        """Update threat intelligence feeds"""
        try:
            async with aiohttp.ClientSession() as session:
                for feed_url in self.threat_feeds:
                    try:
                        async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                            if response.status == 200:
                                content = await response.text()
                                # Parse and update malicious domains list
                                # This is a simplified implementation
                                lines = content.split('\n')
                                for line in lines:
                                    if line.strip() and not line.startswith('#'):
                                        parts = line.strip().split()
                                        if len(parts) > 0:
                                            domain_or_ip = parts[0]
                                            if '.' in domain_or_ip and not domain_or_ip.replace('.', '').isdigit():
                                                # It's a domain
                                                if domain_or_ip not in self.config['malicious_domains']:
                                                    self.config['malicious_domains'].append(domain_or_ip)
                        
                        logger.info(f"Updated threat feed from {feed_url}")
                        
                    except Exception as e:
                        logger.error(f"Failed to update threat feed {feed_url}: {e}")
        
        except Exception as e:
            logger.error(f"Threat feed update failed: {e}")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get DNS security statistics"""
        return {
            'stats': self.stats.copy(),
            'config': {
                'dns_servers_count': len(self.config['dns_servers']),
                'doh_servers_count': len(self.config['doh_servers']),
                'dot_servers_count': len(self.config['dot_servers']),
                'malicious_domains_count': len(self.config['malicious_domains']),
                'blocked_tlds_count': len(self.config['blocked_tlds']),
                'cache_ttl': self.config['cache_ttl']
            },
            'cache_stats': {
                'dns_cache_size': len(self.dns_cache),
                'negative_cache_size': len(self.negative_cache)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform DNS security health check"""
        health_status = {
            'status': 'healthy',
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Test DNS resolution
        try:
            result = await self.resolve_domain('google.com', 'A')
            health_status['checks']['dns_resolution'] = {
                'status': 'healthy',
                'method': result.get('method', 'unknown'),
                'dnssec_valid': result.get('dnssec_valid', False)
            }
        except Exception as e:
            health_status['checks']['dns_resolution'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['status'] = 'unhealthy'
        
        # Test DoH
        try:
            result = await self._query_doh('cloudflare.com', 'A')
            health_status['checks']['doh'] = {
                'status': 'healthy' if result else 'unhealthy'
            }
        except Exception as e:
            health_status['checks']['doh'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Test DoT
        try:
            result = await self._query_dot('quad9.net', 'A')
            health_status['checks']['dot'] = {
                'status': 'healthy' if result else 'unhealthy'
            }
        except Exception as e:
            health_status['checks']['dot'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        return health_status

# Global DNS security manager
dns_security = DNSSecurityManager()

# Background task to update threat feeds
async def update_threat_feeds_task():
    """Background task to update threat intelligence feeds"""
    while True:
        try:
            await dns_security.update_threat_feeds()
            await asyncio.sleep(3600)  # Update every hour
        except Exception as e:
            logger.error(f"Threat feed update task error: {e}")
            await asyncio.sleep(300)  # Retry in 5 minutes on error

# Start background task
threat_feed_task = asyncio.create_task(update_threat_feeds_task())
