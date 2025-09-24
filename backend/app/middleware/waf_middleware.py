"""
WAF Middleware for FastAPI
Integrates Web Application Firewall with FastAPI application
"""

from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import structlog

from app.security.waf_config import get_waf_engine, WAFEvent, AttackType, ThreatLevel

logger = structlog.get_logger(__name__)


class WAFMiddleware:
    """WAF middleware for FastAPI"""
    
    def __init__(self, app, waf_engine=None):
        """
        Initialize WAF middleware
        
        Args:
            app: FastAPI application
            waf_engine: WAF engine instance (optional)
        """
        self.app = app
        self.waf_engine = waf_engine or get_waf_engine()
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through WAF
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        try:
            # Extract request information
            client_ip = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")
            method = request.method
            path = str(request.url.path)
            headers = dict(request.headers)
            
            # Get request body if available
            body = None
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body_bytes = await request.body()
                    body = body_bytes.decode("utf-8") if body_bytes else None
                except Exception:
                    body = None
            
            # Inspect request with WAF
            inspection_result = await self.waf_engine.inspect_request(
                client_ip=client_ip,
                user_agent=user_agent,
                method=method,
                path=path,
                headers=headers,
                body=body
            )
            
            # Handle WAF decision
            if inspection_result["action"] == "block":
                # Log security event
                await self._log_security_event(
                    request, inspection_result, client_ip, user_agent, method, path
                )
                
                # Return block response
                return JSONResponse(
                    status_code=inspection_result.get("status_code", 403),
                    content=inspection_result.get("response_body", {
                        "error": "Access Denied",
                        "message": "Request blocked by security policy"
                    }),
                    headers={
                        "X-WAF-Action": "block",
                        "X-WAF-Rule": inspection_result.get("rule_id", "unknown"),
                        "X-WAF-Threat-Level": inspection_result.get("threat_level", "unknown")
                    }
                )
            
            # Add WAF headers to response
            response = await call_next(request)
            response.headers["X-WAF-Action"] = "allow"
            response.headers["X-WAF-Threat-Level"] = inspection_result.get("threat_level", "low")
            
            return response
            
        except Exception as e:
            logger.error("WAF middleware error", error=str(e))
            # Fail open - allow request if WAF middleware fails
            return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request
        
        Args:
            request: FastAPI request
            
        Returns:
            Client IP address
        """
        # Check for forwarded IP headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def _log_security_event(self,
                                request: Request,
                                inspection_result: dict,
                                client_ip: str,
                                user_agent: str,
                                method: str,
                                path: str):
        """
        Log security event
        
        Args:
            request: FastAPI request
            inspection_result: WAF inspection result
            client_ip: Client IP address
            user_agent: User agent string
            method: HTTP method
            path: Request path
        """
        try:
            # Create WAF event
            event = WAFEvent(
                event_id=f"WAF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hash(client_ip) % 10000:04d}",
                timestamp=datetime.now(timezone.utc),
                client_ip=client_ip,
                user_agent=user_agent,
                request_method=method,
                request_path=path,
                request_headers=dict(request.headers),
                request_body=None,  # Don't log body for security
                attack_type=AttackType(inspection_result.get("attack_type", "unknown")),
                threat_level=ThreatLevel(inspection_result.get("threat_level", "low")),
                rule_id=inspection_result.get("rule_id", "unknown"),
                matched_pattern=inspection_result.get("description", ""),
                action_taken="block",
                response_status=inspection_result.get("status_code", 403)
            )
            
            # Log security event
            logger.warning(
                "Security threat blocked",
                event_id=event.event_id,
                client_ip=client_ip,
                attack_type=event.attack_type.value,
                threat_level=event.threat_level.value,
                rule_id=event.rule_id,
                path=path,
                user_agent=user_agent
            )
            
            # In production, you would:
            # 1. Store event in database
            # 2. Send alerts for high/critical threats
            # 3. Update IP reputation
            # 4. Trigger incident response
            
        except Exception as e:
            logger.error("Failed to log security event", error=str(e))


def setup_waf_middleware(app):
    """
    Setup WAF middleware for FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    waf_middleware = WAFMiddleware(app)
    app.middleware("http")(waf_middleware)
    
    logger.info("WAF middleware configured")


# Cloudflare WAF Configuration
CLOUDFLARE_WAF_RULES = """
# Cloudflare WAF Rules for QuantaEnergi

# Block SQL Injection attempts
(http.request.uri contains "'" and http.request.uri contains "union") or
(http.request.uri contains "select" and http.request.uri contains "from") or
(http.request.uri contains "insert" and http.request.uri contains "into") or
(http.request.uri contains "update" and http.request.uri contains "set") or
(http.request.uri contains "delete" and http.request.uri contains "from")

# Block XSS attempts
(http.request.uri contains "<script") or
(http.request.uri contains "javascript:") or
(http.request.uri contains "onload=") or
(http.request.uri contains "onerror=") or
(http.request.uri contains "onclick=")

# Block path traversal attempts
(http.request.uri contains "../") or
(http.request.uri contains "..\\") or
(http.request.uri contains "%2e%2e%2f") or
(http.request.uri contains "%2e%2e%5c")

# Block command injection attempts
(http.request.uri contains "; ls") or
(http.request.uri contains "; cat") or
(http.request.uri contains "; pwd") or
(http.request.uri contains "; whoami") or
(http.request.uri contains "; id") or
(http.request.uri contains "| ls") or
(http.request.uri contains "| cat") or
(http.request.uri contains "` ls") or
(http.request.uri contains "` cat")

# Block suspicious user agents
(http.user_agent contains "sqlmap") or
(http.user_agent contains "nikto") or
(http.user_agent contains "nmap") or
(http.user_agent contains "masscan") or
(http.user_agent contains "zap") or
(http.user_agent contains "burp") or
(http.user_agent contains "scanner") or
(http.user_agent contains "bot") or
(http.user_agent contains "crawler") or
(http.user_agent contains "spider")

# Rate limiting rules
(http.rate_limit.requests_per_minute > 100) or
(http.rate_limit.requests_per_minute > 60 and http.request.uri starts_with "/api/") or
(http.rate_limit.requests_per_minute > 5 and http.request.uri starts_with "/auth/login")

# Block requests from known bad IPs
(ip.src in {bad_ips_list}) or
(ip.geoip.country in {"CN", "RU", "KP"})  # Adjust based on threat intelligence

# Block requests with missing or suspicious headers
(not http.host) or
(not http.user_agent) or
(http.user_agent == "") or
(http.user_agent == "-")

# Block requests with suspicious content types
(http.request.body contains "eval(") or
(http.request.body contains "expression(") or
(http.request.body contains "setTimeout(") or
(http.request.body contains "setInterval(")

# Block requests with suspicious file uploads
(http.request.body contains "<script") or
(http.request.body contains "javascript:") or
(http.request.body contains "vbscript:") or
(http.request.body contains "onload=") or
(http.request.body contains "onerror=")

# Allow legitimate requests
(http.request.uri starts_with "/api/health") or
(http.request.uri starts_with "/docs") or
(http.request.uri starts_with "/redoc") or
(http.request.uri == "/")

# Geo-blocking for specific regions (optional)
(ip.geoip.country in {"CN", "RU", "KP"}) and
(http.request.uri starts_with "/api/")

# Block requests with suspicious referers
(http.referer contains "malicious-site.com") or
(http.referer contains "phishing-site.com") or
(http.referer contains "scam-site.com")

# Block requests with suspicious query parameters
(http.request.uri.query contains "cmd=") or
(http.request.uri.query contains "exec=") or
(http.request.uri.query contains "system=") or
(http.request.uri.query contains "shell=")

# Block requests with suspicious POST data
(http.request.method == "POST") and
(http.request.body contains "cmd=") or
(http.request.body contains "exec=") or
(http.request.body contains "system=") or
(http.request.body contains "shell=")

# Block requests with suspicious cookies
(http.cookie contains "admin=true") or
(http.cookie contains "debug=true") or
(http.cookie contains "test=true")

# Block requests with suspicious headers
(http.request.headers["x-forwarded-for"] contains "127.0.0.1") or
(http.request.headers["x-real-ip"] contains "127.0.0.1") or
(http.request.headers["x-originating-ip"] contains "127.0.0.1")

# Block requests with suspicious content-length
(http.request.headers["content-length"] > 10485760)  # 10MB limit

# Block requests with suspicious content-type
(http.request.headers["content-type"] contains "application/x-php") or
(http.request.headers["content-type"] contains "text/x-php") or
(http.request.headers["content-type"] contains "application/x-httpd-php")

# Block requests with suspicious accept headers
(http.request.headers["accept"] contains "application/x-php") or
(http.request.headers["accept"] contains "text/x-php") or
(http.request.headers["accept"] contains "application/x-httpd-php")

# Block requests with suspicious authorization headers
(http.request.headers["authorization"] contains "Basic ") and
(http.request.headers["authorization"] contains "admin:") or
(http.request.headers["authorization"] contains "root:") or
(http.request.headers["authorization"] contains "test:")

# Block requests with suspicious x-forwarded-proto headers
(http.request.headers["x-forwarded-proto"] == "http") and
(http.request.uri starts_with "/api/")

# Block requests with suspicious x-forwarded-port headers
(http.request.headers["x-forwarded-port"] == "80") and
(http.request.uri starts_with "/api/")

# Block requests with suspicious x-forwarded-host headers
(http.request.headers["x-forwarded-host"] contains "localhost") or
(http.request.headers["x-forwarded-host"] contains "127.0.0.1") or
(http.request.headers["x-forwarded-host"] contains "0.0.0.0")

# Block requests with suspicious x-forwarded-server headers
(http.request.headers["x-forwarded-server"] contains "localhost") or
(http.request.headers["x-forwarded-server"] contains "127.0.0.1") or
(http.request.headers["x-forwarded-server"] contains "0.0.0.0")

# Block requests with suspicious x-forwarded-for headers containing private IPs
(http.request.headers["x-forwarded-for"] contains "192.168.") or
(http.request.headers["x-forwarded-for"] contains "10.") or
(http.request.headers["x-forwarded-for"] contains "172.16.") or
(http.request.headers["x-forwarded-for"] contains "172.17.") or
(http.request.headers["x-forwarded-for"] contains "172.18.") or
(http.request.headers["x-forwarded-for"] contains "172.19.") or
(http.request.headers["x-forwarded-for"] contains "172.20.") or
(http.request.headers["x-forwarded-for"] contains "172.21.") or
(http.request.headers["x-forwarded-for"] contains "172.22.") or
(http.request.headers["x-forwarded-for"] contains "172.23.") or
(http.request.headers["x-forwarded-for"] contains "172.24.") or
(http.request.headers["x-forwarded-for"] contains "172.25.") or
(http.request.headers["x-forwarded-for"] contains "172.26.") or
(http.request.headers["x-forwarded-for"] contains "172.27.") or
(http.request.headers["x-forwarded-for"] contains "172.28.") or
(http.request.headers["x-forwarded-for"] contains "172.29.") or
(http.request.headers["x-forwarded-for"] contains "172.30.") or
(http.request.headers["x-forwarded-for"] contains "172.31.")

# Block requests with suspicious x-real-ip headers containing private IPs
(http.request.headers["x-real-ip"] contains "192.168.") or
(http.request.headers["x-real-ip"] contains "10.") or
(http.request.headers["x-real-ip"] contains "172.16.") or
(http.request.headers["x-real-ip"] contains "172.17.") or
(http.request.headers["x-real-ip"] contains "172.18.") or
(http.request.headers["x-real-ip"] contains "172.19.") or
(http.request.headers["x-real-ip"] contains "172.20.") or
(http.request.headers["x-real-ip"] contains "172.21.") or
(http.request.headers["x-real-ip"] contains "172.22.") or
(http.request.headers["x-real-ip"] contains "172.23.") or
(http.request.headers["x-real-ip"] contains "172.24.") or
(http.request.headers["x-real-ip"] contains "172.25.") or
(http.request.headers["x-real-ip"] contains "172.26.") or
(http.request.headers["x-real-ip"] contains "172.27.") or
(http.request.headers["x-real-ip"] contains "172.28.") or
(http.request.headers["x-real-ip"] contains "172.29.") or
(http.request.headers["x-real-ip"] contains "172.30.") or
(http.request.headers["x-real-ip"] contains "172.31.")

# Block requests with suspicious x-originating-ip headers containing private IPs
(http.request.headers["x-originating-ip"] contains "192.168.") or
(http.request.headers["x-originating-ip"] contains "10.") or
(http.request.headers["x-originating-ip"] contains "172.16.") or
(http.request.headers["x-originating-ip"] contains "172.17.") or
(http.request.headers["x-originating-ip"] contains "172.18.") or
(http.request.headers["x-originating-ip"] contains "172.19.") or
(http.request.headers["x-originating-ip"] contains "172.20.") or
(http.request.headers["x-originating-ip"] contains "172.21.") or
(http.request.headers["x-originating-ip"] contains "172.22.") or
(http.request.headers["x-originating-ip"] contains "172.23.") or
(http.request.headers["x-originating-ip"] contains "172.24.") or
(http.request.headers["x-originating-ip"] contains "172.25.") or
(http.request.headers["x-originating-ip"] contains "172.26.") or
(http.request.headers["x-originating-ip"] contains "172.27.") or
(http.request.headers["x-originating-ip"] contains "172.28.") or
(http.request.headers["x-originating-ip"] contains "172.29.") or
(http.request.headers["x-originating-ip"] contains "172.30.") or
(http.request.headers["x-originating-ip"] contains "172.31.")
"""

# AWS WAF Configuration
AWS_WAF_RULES = """
# AWS WAF Rules for QuantaEnergi

# SQL Injection Protection
{
  "Name": "SQLInjectionRule",
  "Priority": 1,
  "Statement": {
    "SqlInjectionMatchStatement": {
      "FieldToMatch": {
        "AllQueryArguments": {}
      },
      "TextTransformations": [
        {
          "Priority": 0,
          "Type": "URL_DECODE"
        },
        {
          "Priority": 1,
          "Type": "HTML_ENTITY_DECODE"
        }
      ]
    }
  },
  "Action": {
    "Block": {}
  }
}

# XSS Protection
{
  "Name": "XSSRule",
  "Priority": 2,
  "Statement": {
    "XssMatchStatement": {
      "FieldToMatch": {
        "AllQueryArguments": {}
      },
      "TextTransformations": [
        {
          "Priority": 0,
          "Type": "URL_DECODE"
        },
        {
          "Priority": 1,
          "Type": "HTML_ENTITY_DECODE"
        }
      ]
    }
  },
  "Action": {
    "Block": {}
  }
}

# Rate Limiting
{
  "Name": "RateLimitRule",
  "Priority": 3,
  "Statement": {
    "RateBasedStatement": {
      "Limit": 10000,
      "AggregateKeyType": "IP"
    }
  },
  "Action": {
    "Block": {}
  }
}

# Geo-blocking
{
  "Name": "GeoBlockRule",
  "Priority": 4,
  "Statement": {
    "GeoMatchStatement": {
      "CountryCodes": ["CN", "RU", "KP"]
    }
  },
  "Action": {
    "Block": {}
  }
}

# IP Reputation
{
  "Name": "IPReputationRule",
  "Priority": 5,
  "Statement": {
    "IPSetReferenceStatement": {
      "ARN": "arn:aws:wafv2:region:account:regional/ipset/bad-ips"
    }
  },
  "Action": {
    "Block": {}
  }
}
"""
