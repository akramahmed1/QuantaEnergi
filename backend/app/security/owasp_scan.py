"""
OWASP ZAP Security Scanning Integration
Provides automated security scanning and vulnerability detection
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger(__name__)


class OWASPScanner:
    """OWASP ZAP security scanner integration"""
    
    def __init__(self, target_url: str = "http://localhost:8000"):
        """
        Initialize OWASP scanner
        
        Args:
            target_url: Target URL to scan
        """
        self.target_url = target_url
        self.zap_path = self._find_zap_path()
        self.results_dir = Path(".zap")
        self.results_dir.mkdir(exist_ok=True)
    
    def _find_zap_path(self) -> str:
        """Find ZAP executable path"""
        try:
            # Try to find ZAP in common locations
            zap_paths = [
                "/usr/share/zaproxy/zap.sh",
                "/opt/zaproxy/zap.sh",
                "zap.sh",  # If in PATH
                "zap.bat"  # Windows
            ]
            
            for path in zap_paths:
                try:
                    subprocess.run([path, "--version"], capture_output=True, check=True)
                    return path
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            raise FileNotFoundError("ZAP executable not found")
            
        except Exception as e:
            logger.error("Failed to find ZAP executable", error=str(e))
            raise
    
    def run_baseline_scan(self, timeout: int = 600) -> Dict[str, Any]:
        """
        Run OWASP ZAP baseline scan
        
        Args:
            timeout: Scan timeout in seconds
            
        Returns:
            Scan results dictionary
        """
        try:
            logger.info("Starting OWASP ZAP baseline scan", target=self.target_url)
            
            # Create scan script
            scan_script = self._create_scan_script()
            
            # Run ZAP scan
            cmd = [
                self.zap_path,
                "-cmd",
                "-autorun", scan_script,
                "-dir", str(self.results_dir),
                "-config", "api.disablekey=true"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                logger.error("ZAP scan failed", 
                           returncode=result.returncode,
                           stderr=result.stderr)
                raise RuntimeError(f"ZAP scan failed: {result.stderr}")
            
            # Parse results
            results = self._parse_scan_results()
            
            logger.info("OWASP ZAP baseline scan completed", 
                       vulnerabilities=len(results.get("vulnerabilities", [])))
            
            return results
            
        except subprocess.TimeoutExpired:
            logger.error("ZAP scan timed out", timeout=timeout)
            raise RuntimeError(f"ZAP scan timed out after {timeout} seconds")
        except Exception as e:
            logger.error("ZAP scan failed", error=str(e))
            raise
    
    def run_full_scan(self, timeout: int = 1800) -> Dict[str, Any]:
        """
        Run OWASP ZAP full scan (spider + active scan)
        
        Args:
            timeout: Scan timeout in seconds
            
        Returns:
            Scan results dictionary
        """
        try:
            logger.info("Starting OWASP ZAP full scan", target=self.target_url)
            
            # Create full scan script
            scan_script = self._create_full_scan_script()
            
            # Run ZAP scan
            cmd = [
                self.zap_path,
                "-cmd",
                "-autorun", scan_script,
                "-dir", str(self.results_dir),
                "-config", "api.disablekey=true"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                logger.error("ZAP full scan failed", 
                           returncode=result.returncode,
                           stderr=result.stderr)
                raise RuntimeError(f"ZAP full scan failed: {result.stderr}")
            
            # Parse results
            results = self._parse_scan_results()
            
            logger.info("OWASP ZAP full scan completed", 
                       vulnerabilities=len(results.get("vulnerabilities", [])))
            
            return results
            
        except subprocess.TimeoutExpired:
            logger.error("ZAP full scan timed out", timeout=timeout)
            raise RuntimeError(f"ZAP full scan timed out after {timeout} seconds")
        except Exception as e:
            logger.error("ZAP full scan failed", error=str(e))
            raise
    
    def _create_scan_script(self) -> str:
        """Create ZAP baseline scan script"""
        script_content = f"""
# OWASP ZAP Baseline Scan Script
core = org.parosproxy.paros.core.Core
control = core.getSingleton().getControl()

# Start ZAP
control.init(null, 0, null, null)

# Wait for ZAP to start
time.sleep(5)

# Import required packages
from org.parosproxy.paros.network import HttpRequestHeader
from org.parosproxy.paros.network import HttpHeader
from org.zaproxy.zap.extension.ascan import ExtensionActiveScan

# Access ZAP API
api = control.getExtensionLoader().getExtension(org.zaproxy.zap.extension.api.API.class)

# Baseline scan
print("Starting baseline scan of {self.target_url}")
result = api.callApi("ascan", "action", "scan", [["url", "{self.target_url}"]])
print("Baseline scan started, waiting for completion...")

# Wait for scan to complete
while True:
    status = api.callApi("ascan", "view", "status", [])
    if "100" in status:
        break
    time.sleep(5)

print("Baseline scan completed")

# Generate report
report = api.callApi("core", "other", "xmlreport", [])
with open("{self.results_dir}/baseline-report.xml", "w") as f:
    f.write(report)

# Get alerts
alerts = api.callApi("core", "view", "alerts", [])
with open("{self.results_dir}/alerts.json", "w") as f:
    f.write(alerts)

print("Baseline scan report generated")
"""
        
        script_path = self.results_dir / "baseline-scan.py"
        script_path.write_text(script_content)
        return str(script_path)
    
    def _create_full_scan_script(self) -> str:
        """Create ZAP full scan script"""
        script_content = f"""
# OWASP ZAP Full Scan Script
core = org.parosproxy.paros.core.Core
control = core.getSingleton().getControl()

# Start ZAP
control.init(null, 0, null, null)

# Wait for ZAP to start
time.sleep(5)

# Import required packages
from org.parosproxy.paros.network import HttpRequestHeader
from org.parosproxy.paros.network import HttpHeader
from org.zaproxy.zap.extension.spider import ExtensionSpider
from org.zaproxy.zap.extension.ascan import ExtensionActiveScan

# Access ZAP API
api = control.getExtensionLoader().getExtension(org.zaproxy.zap.extension.api.API.class)

# Spider scan
print("Starting spider scan of {self.target_url}")
spider_result = api.callApi("spider", "action", "scan", [["url", "{self.target_url}"]])
print("Spider scan started, waiting for completion...")

# Wait for spider to complete
while True:
    spider_status = api.callApi("spider", "view", "status", [])
    if "100" in spider_status:
        break
    time.sleep(5)

print("Spider scan completed")

# Active scan
print("Starting active scan of {self.target_url}")
active_result = api.callApi("ascan", "action", "scan", [["url", "{self.target_url}"]])
print("Active scan started, waiting for completion...")

# Wait for active scan to complete
while True:
    active_status = api.callApi("ascan", "view", "status", [])
    if "100" in active_status:
        break
    time.sleep(10)

print("Active scan completed")

# Generate report
report = api.callApi("core", "other", "xmlreport", [])
with open("{self.results_dir}/full-report.xml", "w") as f:
    f.write(report)

# Get alerts
alerts = api.callApi("core", "view", "alerts", [])
with open("{self.results_dir}/alerts.json", "w") as f:
    f.write(alerts)

print("Full scan report generated")
"""
        
        script_path = self.results_dir / "full-scan.py"
        script_path.write_text(script_content)
        return str(script_path)
    
    def _parse_scan_results(self) -> Dict[str, Any]:
        """Parse ZAP scan results"""
        try:
            results = {
                "scan_timestamp": datetime.now(timezone.utc).isoformat(),
                "target_url": self.target_url,
                "vulnerabilities": [],
                "summary": {
                    "total_alerts": 0,
                    "high_risk": 0,
                    "medium_risk": 0,
                    "low_risk": 0,
                    "informational": 0
                }
            }
            
            # Parse alerts JSON
            alerts_file = self.results_dir / "alerts.json"
            if alerts_file.exists():
                alerts_data = json.loads(alerts_file.read_text())
                
                if "alerts" in alerts_data:
                    for alert in alerts_data["alerts"]:
                        vulnerability = {
                            "name": alert.get("name", ""),
                            "risk": alert.get("risk", ""),
                            "risk_code": alert.get("riskcode", ""),
                            "description": alert.get("desc", ""),
                            "solution": alert.get("solution", ""),
                            "url": alert.get("url", ""),
                            "parameter": alert.get("param", ""),
                            "evidence": alert.get("evidence", ""),
                            "reference": alert.get("reference", ""),
                            "cwe_id": alert.get("cweid", ""),
                            "wasc_id": alert.get("wascid", ""),
                            "confidence": alert.get("confidence", ""),
                            "instances": alert.get("instances", [])
                        }
                        
                        results["vulnerabilities"].append(vulnerability)
                        
                        # Update summary
                        risk_code = alert.get("riskcode", "0")
                        results["summary"]["total_alerts"] += 1
                        
                        if risk_code == "3":  # High
                            results["summary"]["high_risk"] += 1
                        elif risk_code == "2":  # Medium
                            results["summary"]["medium_risk"] += 1
                        elif risk_code == "1":  # Low
                            results["summary"]["low_risk"] += 1
                        else:  # Informational
                            results["summary"]["informational"] += 1
            
            return results
            
        except Exception as e:
            logger.error("Failed to parse scan results", error=str(e))
            return {
                "scan_timestamp": datetime.now(timezone.utc).isoformat(),
                "target_url": self.target_url,
                "vulnerabilities": [],
                "summary": {"total_alerts": 0},
                "error": str(e)
            }
    
    def generate_sarif_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SARIF format report for GitHub Security tab"""
        sarif_report = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "OWASP ZAP",
                        "version": "2.11.0",
                        "informationUri": "https://www.zaproxy.org/"
                    }
                },
                "results": [],
                "invocations": [{
                    "executionSuccessful": True,
                    "endTimeUtc": results["scan_timestamp"]
                }]
            }]
        }
        
        for vuln in results["vulnerabilities"]:
            severity_map = {
                "3": "error",    # High
                "2": "warning",  # Medium
                "1": "note",     # Low
                "0": "note"      # Informational
            }
            
            result = {
                "ruleId": vuln["cwe_id"] or "ZAP-" + vuln["risk_code"],
                "level": severity_map.get(vuln["risk_code"], "note"),
                "message": {
                    "text": vuln["description"]
                },
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": vuln["url"]
                        }
                    }
                }]
            }
            
            sarif_report["runs"][0]["results"].append(result)
        
        return sarif_report
    
    def save_results(self, results: Dict[str, Any], filename: str = "zap-results.json"):
        """Save scan results to file"""
        results_file = self.results_dir / filename
        results_file.write_text(json.dumps(results, indent=2))
        logger.info("ZAP scan results saved", file=str(results_file))


def run_security_scan(target_url: str = "http://localhost:8000", 
                     scan_type: str = "baseline") -> Dict[str, Any]:
    """
    Run OWASP ZAP security scan
    
    Args:
        target_url: URL to scan
        scan_type: Type of scan (baseline or full)
        
    Returns:
        Scan results dictionary
    """
    scanner = OWASPScanner(target_url)
    
    if scan_type == "baseline":
        results = scanner.run_baseline_scan()
    elif scan_type == "full":
        results = scanner.run_full_scan()
    else:
        raise ValueError("scan_type must be 'baseline' or 'full'")
    
    # Save results
    scanner.save_results(results)
    
    # Generate SARIF report
    sarif_report = scanner.generate_sarif_report(results)
    scanner.save_results(sarif_report, "zap-results.sarif")
    
    return results
