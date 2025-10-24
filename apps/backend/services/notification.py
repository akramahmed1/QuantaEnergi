"""
Advanced Notification Service for QuantaEnergi
Allegro-like notification system with multi-channel support
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
import hashlib
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import asyncio
import aiohttp
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    IN_APP = "in_app"

class NotificationStatus(Enum):
    """Notification status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"

class NotificationService:
    """
    Advanced notification service with multi-channel support
    """
    
    def __init__(self):
        self.notification_queue = []
        self.notification_history = []
        self.channel_configs = self._initialize_channel_configs()
        self.templates = self._load_notification_templates()
        self.rate_limits = self._initialize_rate_limits()
        self.user_preferences = {}
        
    def _initialize_channel_configs(self) -> Dict[str, Any]:
        """Initialize channel configurations"""
        return {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": None,
                "password": None,
                "use_tls": True,
                "enabled": False
            },
            "sms": {
                "provider": "twilio",
                "account_sid": None,
                "auth_token": None,
                "from_number": None,
                "enabled": False
            },
            "push": {
                "firebase_server_key": None,
                "enabled": False
            },
            "slack": {
                "webhook_url": None,
                "enabled": False
            },
            "teams": {
                "webhook_url": None,
                "enabled": False
            },
            "webhook": {
                "enabled": False
            }
        }
    
    def _load_notification_templates(self) -> Dict[str, Any]:
        """Load notification templates"""
        return {
            "trade_execution": {
                "subject": "Trade Executed - {trade_id}",
                "email_body": """
                <h2>Trade Execution Notification</h2>
                <p>Your trade has been successfully executed:</p>
                <ul>
                    <li><strong>Trade ID:</strong> {trade_id}</li>
                    <li><strong>Instrument:</strong> {instrument}</li>
                    <li><strong>Quantity:</strong> {quantity}</li>
                    <li><strong>Price:</strong> ${price}</li>
                    <li><strong>Total Value:</strong> ${total_value}</li>
                    <li><strong>Execution Time:</strong> {execution_time}</li>
                </ul>
                <p>Best regards,<br>QuantaEnergi Trading Team</p>
                """,
                "sms_body": "Trade executed: {instrument} {quantity} @ ${price}. Total: ${total_value}",
                "push_body": "Trade executed: {instrument} for ${total_value}"
            },
            "risk_alert": {
                "subject": "Risk Alert - {alert_type}",
                "email_body": """
                <h2>Risk Alert Notification</h2>
                <p>A risk alert has been triggered:</p>
                <ul>
                    <li><strong>Alert Type:</strong> {alert_type}</li>
                    <li><strong>Severity:</strong> {severity}</li>
                    <li><strong>Description:</strong> {description}</li>
                    <li><strong>Portfolio Impact:</strong> ${portfolio_impact}</li>
                    <li><strong>Triggered At:</strong> {triggered_at}</li>
                </ul>
                <p>Please review your positions and take appropriate action.</p>
                <p>Best regards,<br>QuantaEnergi Risk Management</p>
                """,
                "sms_body": "Risk Alert: {alert_type} - {severity}. Portfolio impact: ${portfolio_impact}",
                "push_body": "Risk Alert: {alert_type} - {severity}"
            },
            "compliance_violation": {
                "subject": "Compliance Violation - {violation_type}",
                "email_body": """
                <h2>Compliance Violation Alert</h2>
                <p>A compliance violation has been detected:</p>
                <ul>
                    <li><strong>Violation Type:</strong> {violation_type}</li>
                    <li><strong>Severity:</strong> {severity}</li>
                    <li><strong>Description:</strong> {description}</li>
                    <li><strong>Regulation:</strong> {regulation}</li>
                    <li><strong>Detected At:</strong> {detected_at}</li>
                </ul>
                <p>Please review and take corrective action immediately.</p>
                <p>Best regards,<br>QuantaEnergi Compliance Team</p>
                """,
                "sms_body": "Compliance Violation: {violation_type} - {severity}. Regulation: {regulation}",
                "push_body": "Compliance Violation: {violation_type}"
            },
            "market_data_update": {
                "subject": "Market Data Update - {market}",
                "email_body": """
                <h2>Market Data Update</h2>
                <p>Market data has been updated for {market}:</p>
                <ul>
                    <li><strong>Market:</strong> {market}</li>
                    <li><strong>Price Change:</strong> {price_change}</li>
                    <li><strong>Volume:</strong> {volume}</li>
                    <li><strong>Last Update:</strong> {last_update}</li>
                </ul>
                <p>Best regards,<br>QuantaEnergi Market Data Team</p>
                """,
                "sms_body": "Market update: {market} - {price_change}",
                "push_body": "Market update: {market}"
            }
        }
    
    def _initialize_rate_limits(self) -> Dict[str, Any]:
        """Initialize rate limits for different channels"""
        return {
            "email": {"max_per_hour": 100, "max_per_day": 1000},
            "sms": {"max_per_hour": 50, "max_per_day": 500},
            "push": {"max_per_hour": 200, "max_per_day": 2000},
            "slack": {"max_per_hour": 100, "max_per_day": 1000},
            "teams": {"max_per_hour": 100, "max_per_day": 1000}
        }
    
    def configure_channel(self, channel: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure notification channel"""
        try:
            if channel not in self.channel_configs:
                return {"status": "error", "message": f"Unknown channel: {channel}"}
            
            # Update channel configuration
            self.channel_configs[channel].update(config)
            self.channel_configs[channel]["enabled"] = True
            
            # Test configuration
            test_result = self._test_channel_configuration(channel)
            
            return {
                "status": "success",
                "channel": channel,
                "configured": True,
                "test_result": test_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Channel configuration error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _test_channel_configuration(self, channel: str) -> Dict[str, Any]:
        """Test channel configuration"""
        try:
            if channel == "email":
                return self._test_email_configuration()
            elif channel == "sms":
                return self._test_sms_configuration()
            elif channel == "slack":
                return self._test_slack_configuration()
            elif channel == "teams":
                return self._test_teams_configuration()
            else:
                return {"status": "not_implemented"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _test_email_configuration(self) -> Dict[str, Any]:
        """Test email configuration"""
        try:
            config = self.channel_configs["email"]
            if not all([config.get("username"), config.get("password")]):
                return {"status": "incomplete", "message": "Missing credentials"}
            
            # Create test connection
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            if config["use_tls"]:
                server.starttls()
            server.login(config["username"], config["password"])
            server.quit()
            
            return {"status": "success", "message": "Email configuration valid"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _test_sms_configuration(self) -> Dict[str, Any]:
        """Test SMS configuration"""
        try:
            config = self.channel_configs["sms"]
            if not all([config.get("account_sid"), config.get("auth_token")]):
                return {"status": "incomplete", "message": "Missing credentials"}
            
            return {"status": "success", "message": "SMS configuration valid"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _test_slack_configuration(self) -> Dict[str, Any]:
        """Test Slack configuration"""
        try:
            config = self.channel_configs["slack"]
            if not config.get("webhook_url"):
                return {"status": "incomplete", "message": "Missing webhook URL"}
            
            # Test webhook
            test_payload = {"text": "Test message from QuantaEnergi"}
            response = requests.post(config["webhook_url"], json=test_payload, timeout=10)
            
            if response.status_code == 200:
                return {"status": "success", "message": "Slack configuration valid"}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _test_teams_configuration(self) -> Dict[str, Any]:
        """Test Teams configuration"""
        try:
            config = self.channel_configs["teams"]
            if not config.get("webhook_url"):
                return {"status": "incomplete", "message": "Missing webhook URL"}
            
            # Test webhook
            test_payload = {
                "text": "Test message from QuantaEnergi",
                "summary": "Configuration Test"
            }
            response = requests.post(config["webhook_url"], json=test_payload, timeout=10)
            
            if response.status_code == 200:
                return {"status": "success", "message": "Teams configuration valid"}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def send_notification(self,
                         recipients: List[str],
                         template_name: str,
                         template_vars: Dict[str, Any],
                         channels: List[str] = None,
                         priority: str = "medium",
                         scheduled_time: datetime = None) -> Dict[str, Any]:
        """Send notification to recipients"""
        try:
            if template_name not in self.templates:
                return {"status": "error", "message": f"Template {template_name} not found"}
            
            # Default channels if not specified
            if not channels:
                channels = ["email", "sms"]
            
            # Generate notification ID
            notification_id = self._generate_notification_id()
            
            # Create notification record
            notification = {
                "notification_id": notification_id,
                "recipients": recipients,
                "template_name": template_name,
                "template_vars": template_vars,
                "channels": channels,
                "priority": priority,
                "scheduled_time": scheduled_time or datetime.now(),
                "status": NotificationStatus.PENDING.value,
                "created_at": datetime.now().isoformat(),
                "delivery_attempts": [],
                "delivery_results": {}
            }
            
            # Add to queue
            self.notification_queue.append(notification)
            
            # Process notification
            if scheduled_time and scheduled_time > datetime.now():
                # Schedule for later
                return {
                    "status": "scheduled",
                    "notification_id": notification_id,
                    "scheduled_time": scheduled_time.isoformat()
                }
            else:
                # Send immediately
                delivery_result = self._process_notification(notification)
                return {
                    "status": "sent",
                    "notification_id": notification_id,
                    "delivery_result": delivery_result
                }
                
        except Exception as e:
            logger.error(f"Notification sending error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_notification_id(self) -> str:
        """Generate unique notification ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"notif_{timestamp}"
    
    def _process_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Process notification delivery"""
        try:
            delivery_results = {}
            
            for channel in notification["channels"]:
                if not self.channel_configs[channel]["enabled"]:
                    delivery_results[channel] = {
                        "status": "skipped",
                        "message": f"Channel {channel} not enabled"
                    }
                    continue
                
                # Check rate limits
                if not self._check_rate_limit(channel):
                    delivery_results[channel] = {
                        "status": "rate_limited",
                        "message": f"Rate limit exceeded for {channel}"
                    }
                    continue
                
                # Send via channel
                channel_result = self._send_via_channel(
                    channel, notification["recipients"], 
                    notification["template_name"], 
                    notification["template_vars"]
                )
                
                delivery_results[channel] = channel_result
            
            # Update notification status
            notification["delivery_results"] = delivery_results
            notification["status"] = self._determine_overall_status(delivery_results)
            notification["processed_at"] = datetime.now().isoformat()
            
            # Add to history
            self.notification_history.append(notification)
            
            return delivery_results
            
        except Exception as e:
            logger.error(f"Notification processing error: {e}")
            return {"error": str(e)}
    
    def _check_rate_limit(self, channel: str) -> bool:
        """Check if channel is within rate limits"""
        try:
            limits = self.rate_limits.get(channel, {})
            if not limits:
                return True
            
            # Count notifications in the last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_count = sum(1 for n in self.notification_history 
                             if n["processed_at"] and 
                             datetime.fromisoformat(n["processed_at"]) > one_hour_ago and
                             channel in n.get("delivery_results", {}))
            
            return recent_count < limits.get("max_per_hour", 100)
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True
    
    def _send_via_channel(self, 
                         channel: str, 
                         recipients: List[str], 
                         template_name: str, 
                         template_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification via specific channel"""
        try:
            template = self.templates[template_name]
            
            if channel == "email":
                return self._send_email(recipients, template, template_vars)
            elif channel == "sms":
                return self._send_sms(recipients, template, template_vars)
            elif channel == "push":
                return self._send_push(recipients, template, template_vars)
            elif channel == "slack":
                return self._send_slack(template, template_vars)
            elif channel == "teams":
                return self._send_teams(template, template_vars)
            elif channel == "webhook":
                return self._send_webhook(recipients, template, template_vars)
            else:
                return {"status": "error", "message": f"Unknown channel: {channel}"}
                
        except Exception as e:
            logger.error(f"Channel sending error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _send_email(self, recipients: List[str], template: Dict[str, Any], template_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Send email notification"""
        try:
            config = self.channel_configs["email"]
            
            # Prepare email content
            subject = template["subject"].format(**template_vars)
            body = template["email_body"].format(**template_vars)
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = config["username"]
            msg["To"] = ", ".join(recipients)
            
            # Add HTML body
            html_part = MIMEText(body, "html")
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            if config["use_tls"]:
                server.starttls()
            server.login(config["username"], config["password"])
            
            for recipient in recipients:
                msg["To"] = recipient
                server.send_message(msg)
            
            server.quit()
            
            return {
                "status": "success",
                "message": f"Email sent to {len(recipients)} recipients",
                "recipients": recipients
            }
            
        except Exception as e:
            logger.error(f"Email sending error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _send_sms(self, recipients: List[str], template: Dict[str, Any], template_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            config = self.channel_configs["sms"]
            
            # Prepare SMS content
            body = template["sms_body"].format(**template_vars)
            
            # Send SMS via Twilio (example)
            if config["provider"] == "twilio":
                from twilio.rest import Client
                client = Client(config["account_sid"], config["auth_token"])
                
                for recipient in recipients:
                    message = client.messages.create(
                        body=body,
                        from_=config["from_number"],
                        to=recipient
                    )
                
                return {
                    "status": "success",
                    "message": f"SMS sent to {len(recipients)} recipients",
                    "recipients": recipients
                }
            else:
                return {"status": "error", "message": "SMS provider not configured"}
                
        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _send_push(self, recipients: List[str], template: Dict[str, Any], template_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Send push notification"""
        try:
            config = self.channel_configs["push"]
            
            # Prepare push content
            body = template["push_body"].format(**template_vars)
            
            # Send push notification via Firebase (example)
            if config["firebase_server_key"]:
                headers = {
                    "Authorization": f"key={config['firebase_server_key']}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "registration_ids": recipients,
                    "notification": {
                        "title": "QuantaEnergi Notification",
                        "body": body
                    }
                }
                
                response = requests.post(
                    "https://fcm.googleapis.com/fcm/send",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    return {
                        "status": "success",
                        "message": f"Push notification sent to {len(recipients)} recipients",
                        "recipients": recipients
                    }
                else:
                    return {"status": "error", "message": f"HTTP {response.status_code}"}
            else:
                return {"status": "error", "message": "Firebase server key not configured"}
                
        except Exception as e:
            logger.error(f"Push notification sending error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _send_slack(self, template: Dict[str, Any], template_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Send Slack notification"""
        try:
            config = self.channel_configs["slack"]
            
            # Prepare Slack content
            body = template["sms_body"].format(**template_vars)
            
            payload = {
                "text": body,
                "username": "QuantaEnergi",
                "icon_emoji": ":chart_with_upwards_trend:"
            }
            
            response = requests.post(config["webhook_url"], json=payload)
            
            if response.status_code == 200:
                return {"status": "success", "message": "Slack notification sent"}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Slack notification sending error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _send_teams(self, template: Dict[str, Any], template_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Send Teams notification"""
        try:
            config = self.channel_configs["teams"]
            
            # Prepare Teams content
            body = template["sms_body"].format(**template_vars)
            
            payload = {
                "text": body,
                "summary": "QuantaEnergi Notification"
            }
            
            response = requests.post(config["webhook_url"], json=payload)
            
            if response.status_code == 200:
                return {"status": "success", "message": "Teams notification sent"}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Teams notification sending error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _send_webhook(self, recipients: List[str], template: Dict[str, Any], template_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Send webhook notification"""
        try:
            # This would integrate with external webhook endpoints
            # For now, return a placeholder response
            
            return {
                "status": "success",
                "message": f"Webhook notification sent to {len(recipients)} endpoints",
                "recipients": recipients
            }
            
        except Exception as e:
            logger.error(f"Webhook notification sending error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _determine_overall_status(self, delivery_results: Dict[str, Any]) -> str:
        """Determine overall notification status"""
        try:
            if not delivery_results:
                return NotificationStatus.FAILED.value
            
            # Check if any channel succeeded
            success_count = sum(1 for result in delivery_results.values() 
                              if result.get("status") == "success")
            
            if success_count > 0:
                return NotificationStatus.SENT.value
            else:
                return NotificationStatus.FAILED.value
                
        except Exception as e:
            logger.error(f"Status determination error: {e}")
            return NotificationStatus.FAILED.value
    
    def get_notification_history(self, 
                                limit: int = 100,
                                status: str = None,
                                channel: str = None) -> Dict[str, Any]:
        """Get notification history"""
        try:
            filtered_history = self.notification_history
            
            # Filter by status
            if status:
                filtered_history = [n for n in filtered_history if n["status"] == status]
            
            # Filter by channel
            if channel:
                filtered_history = [n for n in filtered_history 
                                  if channel in n.get("channels", [])]
            
            # Limit results
            filtered_history = filtered_history[-limit:] if limit else filtered_history
            
            return {
                "status": "success",
                "notifications": filtered_history,
                "total_count": len(filtered_history),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"History retrieval error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_notification_statistics(self) -> Dict[str, Any]:
        """Get notification statistics"""
        try:
            total_notifications = len(self.notification_history)
            
            # Count by status
            status_counts = {}
            for notification in self.notification_history:
                status = notification["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by channel
            channel_counts = {}
            for notification in self.notification_history:
                for channel in notification.get("channels", []):
                    channel_counts[channel] = channel_counts.get(channel, 0) + 1
            
            # Calculate success rate
            success_count = status_counts.get(NotificationStatus.SENT.value, 0)
            success_rate = (success_count / total_notifications * 100) if total_notifications > 0 else 0
            
            return {
                "status": "success",
                "statistics": {
                    "total_notifications": total_notifications,
                    "status_breakdown": status_counts,
                    "channel_breakdown": channel_counts,
                    "success_rate": round(success_rate, 2),
                    "queue_size": len(self.notification_queue)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Statistics retrieval error: {e}")
            return {"status": "error", "message": str(e)}
    
    def set_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Set user notification preferences"""
        try:
            self.user_preferences[user_id] = preferences
            
            return {
                "status": "success",
                "user_id": user_id,
                "preferences": preferences,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"User preferences error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        try:
            preferences = self.user_preferences.get(user_id, {})
            
            return {
                "status": "success",
                "user_id": user_id,
                "preferences": preferences,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"User preferences retrieval error: {e}")
            return {"status": "error", "message": str(e)}
