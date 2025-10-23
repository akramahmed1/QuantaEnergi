"""
Web Application Firewall (WAF) Configuration
Provides protection against common web attacks and malicious traffic
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import re
import ipaddress
import hashlib
import json
from collections import defaultdict, deque

import structlog

logger = structlog.get_logger(__name__)


class ThreatLevel(str, Enum):
    """Threat level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackType(str, Enum):
    """Type of attack detected"""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    RATE_LIMITING = "rate_limiting"
    DDoS = "ddos"
    BRUTE_FORCE = "brute_force"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    LDAP_INJECTION = "ldap_injection"
    NO_SQL_INJECTION = "nosql_injection"
    XML_INJECTION = "xml_injection"
    SSRF = "ssrf"
    FILE_UPLOAD = "file_upload"
    MALICIOUS_USER_AGENT = "malicious_user_agent"
    SUSPICIOUS_IP = "suspicious_ip"


@dataclass
class WAFRule:
    """WAF rule definition"""
    rule_id: str
    name: str
    description: str
    attack_type: AttackType
    threat_level: ThreatLevel
    pattern: str
    is_regex: bool = True
    is_enabled: bool = True
    action: str = "block"  # block, log, redirect, challenge
    rate_limit: Optional[int] = None  # requests per minute
    whitelist: List[str] = None  # IP addresses or patterns to whitelist
    blacklist: List[str] = None  # IP addresses or patterns to blacklist


@dataclass
class WAFEvent:
    """WAF security event"""
    event_id: str
    timestamp: datetime
    client_ip: str
    user_agent: str
    request_method: str
    request_path: str
    request_headers: Dict[str, str]
    request_body: Optional[str]
    attack_type: AttackType
    threat_level: ThreatLevel
    rule_id: str
    matched_pattern: str
    action_taken: str
    response_status: int


class WAFEngine:
    """Web Application Firewall engine"""
    
    def __init__(self):
        """Initialize WAF engine with security rules"""
        self.rules = self._load_default_rules()
        self.rate_limiter = RateLimiter()
        self.ip_reputation = IPReputationChecker()
        self.request_history = RequestHistory()
        
        logger.info("WAF engine initialized", rules_count=len(self.rules))
    
    def _load_default_rules(self) -> List[WAFRule]:
        """Load default WAF security rules"""
        rules = []
        
        # SQL Injection Rules
        sql_injection_patterns = [
            r"('|(\\')|(;)|(\\;)|(--)|(\\-\\-)|(\\/\\*)|(\\*\\/)|(xp_)|(sp_))",
            r"(union|select|insert|update|delete|drop|create|alter|exec|execute)",
            r"(script|javascript|vbscript|onload|onerror|onclick)",
            r"(<script|</script|javascript:|vbscript:|onload=|onerror=)",
            r"(eval\\(|expression\\(|settimeout\\(|setinterval\\()",
            r"(document\\.|window\\.|location\\.|navigator\\.)"
        ]
        
        for i, pattern in enumerate(sql_injection_patterns):
            rules.append(WAFRule(
                rule_id=f"SQL_INJ_{i+1:03d}",
                name=f"SQL Injection Pattern {i+1}",
                description=f"Detects SQL injection attempts using pattern {i+1}",
                attack_type=AttackType.SQL_INJECTION,
                threat_level=ThreatLevel.HIGH,
                pattern=pattern
            ))
        
        # XSS Rules
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\\s*=",
            r"onerror\\s*=",
            r"onclick\\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"expression\\s*\\(",
            r"url\\s*\\("
        ]
        
        for i, pattern in enumerate(xss_patterns):
            rules.append(WAFRule(
                rule_id=f"XSS_{i+1:03d}",
                name=f"XSS Pattern {i+1}",
                description=f"Detects XSS attempts using pattern {i+1}",
                attack_type=AttackType.XSS,
                threat_level=ThreatLevel.HIGH,
                pattern=pattern
            ))
        
        # Path Traversal Rules
        path_traversal_patterns = [
            r"\\.\\.\\/",
            r"\\.\\.\\\\",
            r"\\.\\.%2f",
            r"\\.\\.%5c",
            r"\\.\\.%252f",
            r"\\.\\.%255c",
            r"\\.\\.%c0%af",
            r"\\.\\.%c1%9c"
        ]
        
        for i, pattern in enumerate(path_traversal_patterns):
            rules.append(WAFRule(
                rule_id=f"PATH_{i+1:03d}",
                name=f"Path Traversal Pattern {i+1}",
                description=f"Detects path traversal attempts using pattern {i+1}",
                attack_type=AttackType.PATH_TRAVERSAL,
                threat_level=ThreatLevel.MEDIUM,
                pattern=pattern
            ))
        
        # Command Injection Rules
        command_injection_patterns = [
            r";\\s*(ls|cat|pwd|whoami|id|ps|netstat|ifconfig|ping|nslookup)",
            r"\\|\\s*(ls|cat|pwd|whoami|id|ps|netstat|ifconfig|ping|nslookup)",
            r"`\\s*(ls|cat|pwd|whoami|id|ps|netstat|ifconfig|ping|nslookup)",
            r"\\$\\s*\\(\\s*(ls|cat|pwd|whoami|id|ps|netstat|ifconfig|ping|nslookup)",
            r"exec\\s*\\(",
            r"system\\s*\\(",
            r"shell_exec\\s*\\(",
            r"passthru\\s*\\(",
            r"proc_open\\s*\\(",
            r"popen\\s*\\("
        ]
        
        for i, pattern in enumerate(command_injection_patterns):
            rules.append(WAFRule(
                rule_id=f"CMD_{i+1:03d}",
                name=f"Command Injection Pattern {i+1}",
                description=f"Detects command injection attempts using pattern {i+1}",
                attack_type=AttackType.COMMAND_INJECTION,
                threat_level=ThreatLevel.CRITICAL,
                pattern=pattern
            ))
        
        # LDAP Injection Rules
        ldap_patterns = [
            r"\\*\\s*\\(",
            r"\\*\\s*\\)",
            r"\\*\\s*\\|",
            r"\\*\\s*&",
            r"\\*\\s*!",
            r"\\(\\s*\\|",
            r"\\(\\s*&",
            r"\\(\\s*!",
            r"\\)\\s*\\|",
            r"\\)\\s*&",
            r"\\)\\s*!"
        ]
        
        for i, pattern in enumerate(ldap_patterns):
            rules.append(WAFRule(
                rule_id=f"LDAP_{i+1:03d}",
                name=f"LDAP Injection Pattern {i+1}",
                description=f"Detects LDAP injection attempts using pattern {i+1}",
                attack_type=AttackType.LDAP_INJECTION,
                threat_level=ThreatLevel.MEDIUM,
                pattern=pattern
            ))
        
        # NoSQL Injection Rules
        nosql_patterns = [
            r"\\$where\\s*:",
            r"\\$regex\\s*:",
            r"\\$ne\\s*:",
            r"\\$gt\\s*:",
            r"\\$lt\\s*:",
            r"\\$gte\\s*:",
            r"\\$lte\\s*:",
            r"\\$in\\s*:",
            r"\\$nin\\s*:",
            r"\\$exists\\s*:",
            r"\\$all\\s*:",
            r"\\$or\\s*:",
            r"\\$and\\s*:",
            r"\\$not\\s*:",
            r"\\$nor\\s*:"
        ]
        
        for i, pattern in enumerate(nosql_patterns):
            rules.append(WAFRule(
                rule_id=f"NOSQL_{i+1:03d}",
                name=f"NoSQL Injection Pattern {i+1}",
                description=f"Detects NoSQL injection attempts using pattern {i+1}",
                attack_type=AttackType.NO_SQL_INJECTION,
                threat_level=ThreatLevel.MEDIUM,
                pattern=pattern
            ))
        
        # XML Injection Rules
        xml_patterns = [
            r"<!DOCTYPE\\s+[^>]*\\s*\\[",
            r"<!ENTITY\\s+[^>]*>",
            r"&[a-zA-Z0-9_]+;",
            r"<\\?xml\\s+[^>]*\\?>",
            r"<![CDATA\\[",
            r"]]>",
            r"<\\?php",
            r"<\\?=",
            r"<\\?\\s*echo"
        ]
        
        for i, pattern in enumerate(xml_patterns):
            rules.append(WAFRule(
                rule_id=f"XML_{i+1:03d}",
                name=f"XML Injection Pattern {i+1}",
                description=f"Detects XML injection attempts using pattern {i+1}",
                attack_type=AttackType.XML_INJECTION,
                threat_level=ThreatLevel.MEDIUM,
                pattern=pattern
            ))
        
        # SSRF Rules
        ssrf_patterns = [
            r"file://",
            r"gopher://",
            r"dict://",
            r"ftp://",
            r"localhost",
            r"127\\.0\\.0\\.1",
            r"0\\.0\\.0\\.0",
            r"169\\.254\\.169\\.254",
            r"metadata\\.googleapis\\.com",
            r"169\\.254\\.169\\.254/latest/meta-data"
        ]
        
        for i, pattern in enumerate(ssrf_patterns):
            rules.append(WAFRule(
                rule_id=f"SSRF_{i+1:03d}",
                name=f"SSRF Pattern {i+1}",
                description=f"Detects SSRF attempts using pattern {i+1}",
                attack_type=AttackType.SSRF,
                threat_level=ThreatLevel.HIGH,
                pattern=pattern
            ))
        
        # Rate Limiting Rules
        rules.append(WAFRule(
            rule_id="RATE_001",
            name="General Rate Limiting",
            description="General rate limiting for all requests",
            attack_type=AttackType.RATE_LIMITING,
            threat_level=ThreatLevel.MEDIUM,
            pattern=".*",
            rate_limit=100  # 100 requests per minute
        ))
        
        rules.append(WAFRule(
            rule_id="RATE_002",
            name="API Rate Limiting",
            description="Rate limiting for API endpoints",
            attack_type=AttackType.RATE_LIMITING,
            threat_level=ThreatLevel.MEDIUM,
            pattern="^/api/.*",
            rate_limit=60  # 60 requests per minute for API
        ))
        
        # Brute Force Protection
        rules.append(WAFRule(
            rule_id="BRUTE_001",
            name="Login Brute Force Protection",
            description="Protect against brute force login attempts",
            attack_type=AttackType.BRUTE_FORCE,
            threat_level=ThreatLevel.HIGH,
            pattern="^/auth/login",
            rate_limit=5  # 5 login attempts per minute
        ))
        
        return rules
    
    async def inspect_request(self,
                            client_ip: str,
                            user_agent: str,
                            method: str,
                            path: str,
                            headers: Dict[str, str],
                            body: Optional[str] = None) -> Dict[str, Any]:
        """
        Inspect incoming request for security threats
        
        Args:
            client_ip: Client IP address
            user_agent: User agent string
            method: HTTP method
            path: Request path
            headers: Request headers
            body: Request body
            
        Returns:
            Inspection result with action and details
        """
        try:
            # Check IP reputation
            ip_reputation = await self.ip_reputation.check_ip(client_ip)
            if ip_reputation["threat_level"] == ThreatLevel.CRITICAL:
                return self._create_block_response(
                    AttackType.SUSPICIOUS_IP,
                    ThreatLevel.CRITICAL,
                    "BLACKLIST_001",
                    f"Suspicious IP: {client_ip}",
                    "IP address is blacklisted"
                )
            
            # Check rate limiting
            rate_limit_result = await self.rate_limiter.check_rate_limit(
                client_ip, path, headers
            )
            if not rate_limit_result["allowed"]:
                return self._create_block_response(
                    AttackType.RATE_LIMITING,
                    ThreatLevel.MEDIUM,
                    "RATE_001",
                    f"Rate limit exceeded for {client_ip}",
                    f"Limit: {rate_limit_result['limit']}, Current: {rate_limit_result['current']}"
                )
            
            # Check user agent
            ua_result = self._check_user_agent(user_agent)
            if not ua_result["safe"]:
                return self._create_block_response(
                    AttackType.MALICIOUS_USER_AGENT,
                    ThreatLevel.MEDIUM,
                    "UA_001",
                    f"Malicious user agent: {user_agent}",
                    ua_result["reason"]
                )
            
            # Check request content against WAF rules
            content_to_check = f"{method} {path}\n{json.dumps(headers)}\n{body or ''}"
            
            for rule in self.rules:
                if not rule.is_enabled:
                    continue
                
                # Check if IP is whitelisted for this rule
                if rule.whitelist and client_ip in rule.whitelist:
                    continue
                
                # Check if IP is blacklisted for this rule
                if rule.blacklist and client_ip in rule.blacklist:
                    return self._create_block_response(
                        rule.attack_type,
                        rule.threat_level,
                        rule.rule_id,
                        f"Blacklisted IP: {client_ip}",
                        "IP address is blacklisted for this rule"
                    )
                
                # Apply rule pattern matching
                if rule.is_regex:
                    if re.search(rule.pattern, content_to_check, re.IGNORECASE | re.MULTILINE):
                        return self._create_block_response(
                            rule.attack_type,
                            rule.threat_level,
                            rule.rule_id,
                            f"Rule {rule.rule_id} matched",
                            f"Pattern: {rule.pattern}"
                        )
                else:
                    if rule.pattern.lower() in content_to_check.lower():
                        return self._create_block_response(
                            rule.attack_type,
                            rule.threat_level,
                            rule.rule_id,
                            f"Rule {rule.rule_id} matched",
                            f"Pattern: {rule.pattern}"
                        )
            
            # Log successful request
            await self.request_history.log_request(
                client_ip, user_agent, method, path, headers, body
            )
            
            return {
                "action": "allow",
                "threat_level": ThreatLevel.LOW,
                "reason": "Request passed all security checks"
            }
            
        except Exception as e:
            logger.error("WAF inspection failed", error=str(e))
            # Fail open - allow request if WAF fails
            return {
                "action": "allow",
                "threat_level": ThreatLevel.LOW,
                "reason": "WAF inspection failed, allowing request"
            }
    
    def _create_block_response(self,
                             attack_type: AttackType,
                             threat_level: ThreatLevel,
                             rule_id: str,
                             description: str,
                             details: str) -> Dict[str, Any]:
        """Create block response for security violation"""
        return {
            "action": "block",
            "attack_type": attack_type.value,
            "threat_level": threat_level.value,
            "rule_id": rule_id,
            "description": description,
            "details": details,
            "status_code": 403,
            "response_body": {
                "error": "Access Denied",
                "message": "Request blocked by security policy",
                "request_id": f"WAF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
        }
    
    def _check_user_agent(self, user_agent: str) -> Dict[str, Any]:
        """Check user agent for malicious patterns"""
        if not user_agent:
            return {"safe": False, "reason": "Missing user agent"}
        
        # Known malicious user agents
        malicious_patterns = [
            r"sqlmap",
            r"nikto",
            r"nmap",
            r"masscan",
            r"zap",
            r"burp",
            r"scanner",
            r"bot",
            r"crawler",
            r"spider",
            r"wget",
            r"curl",
            r"python-requests",
            r"java/",
            r"perl/",
            r"ruby/",
            r"php/"
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return {"safe": False, "reason": f"Malicious user agent pattern: {pattern}"}
        
        return {"safe": True, "reason": "User agent appears legitimate"}
    
    async def add_rule(self, rule: WAFRule):
        """Add new WAF rule"""
        self.rules.append(rule)
        logger.info("WAF rule added", rule_id=rule.rule_id, name=rule.name)
    
    async def remove_rule(self, rule_id: str):
        """Remove WAF rule by ID"""
        self.rules = [rule for rule in self.rules if rule.rule_id != rule_id]
        logger.info("WAF rule removed", rule_id=rule_id)
    
    async def update_rule(self, rule_id: str, updates: Dict[str, Any]):
        """Update existing WAF rule"""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                logger.info("WAF rule updated", rule_id=rule_id)
                return
        
        logger.warning("WAF rule not found for update", rule_id=rule_id)
    
    def get_rules(self) -> List[WAFRule]:
        """Get all WAF rules"""
        return self.rules.copy()
    
    def get_rule(self, rule_id: str) -> Optional[WAFRule]:
        """Get specific WAF rule by ID"""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None


class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self, window_size: int = 60):
        """
        Initialize rate limiter
        
        Args:
            window_size: Time window in seconds
        """
        self.window_size = window_size
        self.requests = defaultdict(lambda: deque())
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = datetime.now(timezone.utc)
    
    async def check_rate_limit(self,
                             client_ip: str,
                             path: str,
                             headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Check if request is within rate limit
        
        Args:
            client_ip: Client IP address
            path: Request path
            headers: Request headers
            
        Returns:
            Rate limit check result
        """
        now = datetime.now(timezone.utc)
        
        # Cleanup old requests
        if (now - self.last_cleanup).total_seconds() > self.cleanup_interval:
            await self._cleanup_old_requests()
            self.last_cleanup = now
        
        # Create rate limit key
        rate_key = f"{client_ip}:{path}"
        
        # Remove old requests outside window
        cutoff_time = now - timedelta(seconds=self.window_size)
        while self.requests[rate_key] and self.requests[rate_key][0] < cutoff_time:
            self.requests[rate_key].popleft()
        
        # Add current request
        self.requests[rate_key].append(now)
        
        # Check rate limit (default: 100 requests per minute)
        limit = 100
        current = len(self.requests[rate_key])
        
        return {
            "allowed": current <= limit,
            "limit": limit,
            "current": current,
            "window_size": self.window_size,
            "reset_time": cutoff_time + timedelta(seconds=self.window_size)
        }
    
    async def _cleanup_old_requests(self):
        """Cleanup old request records"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=self.window_size)
        
        for key in list(self.requests.keys()):
            while self.requests[key] and self.requests[key][0] < cutoff_time:
                self.requests[key].popleft()
            
            # Remove empty entries
            if not self.requests[key]:
                del self.requests[key]


class IPReputationChecker:
    """IP reputation and blacklist checking"""
    
    def __init__(self):
        """Initialize IP reputation checker"""
        self.blacklisted_ips = set()
        self.whitelisted_ips = set()
        self.suspicious_ips = set()
        self._load_blacklists()
    
    def _load_blacklists(self):
        """Load IP blacklists from various sources"""
        # Known malicious IP ranges (simplified)
        malicious_ranges = [
            "10.0.0.0/8",      # Private networks (for testing)
            "192.168.0.0/16",  # Private networks (for testing)
            "172.16.0.0/12",   # Private networks (for testing)
        ]
        
        for ip_range in malicious_ranges:
            try:
                network = ipaddress.ip_network(ip_range)
                for ip in network:
                    self.blacklisted_ips.add(str(ip))
            except ValueError:
                continue
    
    async def check_ip(self, ip_address: str) -> Dict[str, Any]:
        """
        Check IP address reputation
        
        Args:
            ip_address: IP address to check
            
        Returns:
            IP reputation result
        """
        if ip_address in self.whitelisted_ips:
            return {"threat_level": ThreatLevel.LOW, "reason": "Whitelisted IP"}
        
        if ip_address in self.blacklisted_ips:
            return {"threat_level": ThreatLevel.CRITICAL, "reason": "Blacklisted IP"}
        
        if ip_address in self.suspicious_ips:
            return {"threat_level": ThreatLevel.HIGH, "reason": "Suspicious IP"}
        
        # Check if IP is in private range (potential SSRF)
        try:
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private:
                return {"threat_level": ThreatLevel.MEDIUM, "reason": "Private IP address"}
        except ValueError:
            return {"threat_level": ThreatLevel.HIGH, "reason": "Invalid IP address"}
        
        return {"threat_level": ThreatLevel.LOW, "reason": "Clean IP address"}
    
    async def add_to_blacklist(self, ip_address: str):
        """Add IP to blacklist"""
        self.blacklisted_ips.add(ip_address)
        logger.info("IP added to blacklist", ip=ip_address)
    
    async def add_to_whitelist(self, ip_address: str):
        """Add IP to whitelist"""
        self.whitelisted_ips.add(ip_address)
        logger.info("IP added to whitelist", ip=ip_address)
    
    async def remove_from_blacklist(self, ip_address: str):
        """Remove IP from blacklist"""
        self.blacklisted_ips.discard(ip_address)
        logger.info("IP removed from blacklist", ip=ip_address)


class RequestHistory:
    """Request history tracking for analysis"""
    
    def __init__(self, max_history: int = 10000):
        """
        Initialize request history
        
        Args:
            max_history: Maximum number of requests to keep in history
        """
        self.max_history = max_history
        self.requests = deque(maxlen=max_history)
    
    async def log_request(self,
                         client_ip: str,
                         user_agent: str,
                         method: str,
                         path: str,
                         headers: Dict[str, str],
                         body: Optional[str]):
        """Log request to history"""
        request_data = {
            "timestamp": datetime.now(timezone.utc),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "method": method,
            "path": path,
            "headers": headers,
            "body": body
        }
        
        self.requests.append(request_data)
    
    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent requests"""
        return list(self.requests)[-limit:]
    
    def get_requests_by_ip(self, client_ip: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get requests by IP address"""
        matching_requests = [
            req for req in self.requests 
            if req["client_ip"] == client_ip
        ]
        return matching_requests[-limit:]


# Global WAF engine instance
_waf_engine: Optional[WAFEngine] = None


def get_waf_engine() -> WAFEngine:
    """Get the global WAF engine instance"""
    global _waf_engine
    
    if _waf_engine is None:
        _waf_engine = WAFEngine()
    
    return _waf_engine
