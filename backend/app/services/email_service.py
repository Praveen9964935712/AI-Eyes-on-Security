import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import os
from config.settings import *

class EmailAlertService:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.email_address = EMAIL_ADDRESS
        self.email_password = EMAIL_PASSWORD
        self.recipients = ALERT_RECIPIENTS
        
        # Email templates
        self.templates = {
            'intruder': {
                'subject': '🚨 SECURITY ALERT: Unauthorized Person Detected',
                'priority': 'High'
            },
            'suspicious_activity': {
                'subject': '⚠️ SECURITY ALERT: Suspicious Activity Detected',
                'priority': 'Medium'
            },
            'weapon_detected': {
                'subject': '🚨 CRITICAL ALERT: Weapon Detected',
                'priority': 'Critical'
            },
            'armed_threat': {
                'subject': '🚨 EMERGENCY: Armed Threat Detected',
                'priority': 'Critical'
            }
        }
    
    def send_alert(self, alert_data):
        """Send email alert with image attachment"""
        try:
            # Get template based on alert type
            template = self.templates.get(alert_data['type'], self.templates['suspicious_activity'])
            
            # Create message
            msg = MIMEMultipart('related')
            msg['From'] = self.email_address
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = template['subject']
            msg['X-Priority'] = '1' if template['priority'] == 'Critical' else '2'
            
            # Create HTML body
            html_body = self._create_html_body(alert_data, template)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach image if available
            if 'image_path' in alert_data and os.path.exists(alert_data['image_path']):
                with open(alert_data['image_path'], 'rb') as f:
                    img_data = f.read()
                    image = MIMEImage(img_data)
                    image.add_header('Content-ID', '<alert_image>')
                    image.add_header('Content-Disposition', 'inline', filename='alert_image.jpg')
                    msg.attach(image)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            print(f"Alert email sent successfully for {alert_data['type']}")
            return True
            
        except Exception as e:
            print(f"Error sending email alert: {e}")
            return False
    
    def _create_html_body(self, alert_data, template):
        """Create HTML email body"""
        
        # Get icon based on alert type
        icons = {
            'intruder': '👤',
            'suspicious_activity': '⚠️',
            'weapon_detected': '🔫',
            'armed_threat': '🚨'
        }
        
        icon = icons.get(alert_data['type'], '⚠️')
        
        # Get severity color
        severity_colors = {
            'Critical': '#dc3545',
            'High': '#fd7e14',
            'Medium': '#ffc107',
            'Low': '#28a745'
        }
        
        severity_color = severity_colors.get(template['priority'], '#ffc107')
        
        # Format timestamp
        timestamp = datetime.fromisoformat(alert_data['timestamp'].replace('Z', '+00:00'))
        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 20px;
                }}
                .alert-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .alert-header {{
                    background: {severity_color};
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .alert-body {{
                    padding: 20px;
                }}
                .alert-image {{
                    text-align: center;
                    margin: 20px 0;
                }}
                .alert-details {{
                    background: #f8f9fa;
                    border-left: 4px solid {severity_color};
                    padding: 15px;
                    margin: 20px 0;
                }}
                .detail-row {{
                    margin: 10px 0;
                    display: flex;
                    justify-content: space-between;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #666;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }}
                .confidence-bar {{
                    background: #e9ecef;
                    height: 20px;
                    border-radius: 10px;
                    overflow: hidden;
                    margin: 10px 0;
                }}
                .confidence-fill {{
                    height: 100%;
                    background: {severity_color};
                    width: {alert_data.get('confidence', 0)}%;
                    transition: width 0.3s ease;
                }}
            </style>
        </head>
        <body>
            <div class="alert-container">
                <div class="alert-header">
                    <h1 style="margin: 0;">{icon} AI Eyes Security Alert</h1>
                    <p style="margin: 10px 0 0 0; font-size: 18px;">{template['priority']} Priority Alert</p>
                </div>
                
                <div class="alert-body">
                    <h2 style="color: {severity_color}; margin-top: 0;">{alert_data.get('description', 'Security Alert')}</h2>
                    
                    <div class="alert-details">
                        <div class="detail-row">
                            <span class="detail-label">Alert Type:</span>
                            <span>{alert_data['type'].replace('_', ' ').title()}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Location:</span>
                            <span>{alert_data.get('location', 'Unknown')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Time:</span>
                            <span>{formatted_time}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Confidence:</span>
                            <span>{alert_data.get('confidence', 0):.1f}%</span>
                        </div>
                        <div class="confidence-bar">
                            <div class="confidence-fill"></div>
                        </div>
                    </div>
                    
                    {"<div class='alert-image'><img src='cid:alert_image' alt='Alert Image' style='max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);' /></div>" if 'image_path' in alert_data else ""}
                    
                    <div style="background: #fff3cd; border: 1px solid #ffeeba; color: #856404; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>⚠️ Immediate Action Required:</strong><br>
                        Please review the security footage and take appropriate action. If this is a genuine threat, contact security personnel or authorities immediately.
                    </div>
                </div>
                
                <div class="footer">
                    <p>This alert was generated by AI Eyes Security System<br>
                    Powered by Deep Learning • Real-time Surveillance</p>
                    <p style="margin: 5px 0 0 0;">
                        <strong>System Status:</strong> Active • 
                        <strong>Camera ID:</strong> {alert_data.get('camera_id', 'Unknown')} • 
                        <strong>Alert ID:</strong> {alert_data.get('id', 'N/A')}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def send_test_alert(self):
        """Send a test alert to verify email configuration"""
        test_alert = {
            'type': 'system_test',
            'description': 'AI Eyes Security System Test Alert',
            'location': 'System Configuration',
            'timestamp': datetime.now().isoformat(),
            'confidence': 100,
            'camera_id': 'TEST',
            'id': 'TEST-001'
        }
        
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = ', '.join(self.recipients)
        msg['Subject'] = '✅ AI Eyes Security System - Test Alert'
        
        html_body = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background: #28a745; color: white; padding: 20px; text-align: center; border-radius: 10px;">
                <h2>✅ AI Eyes Security System</h2>
                <p>Test Alert - System Configuration Successful</p>
            </div>
            <div style="padding: 20px;">
                <p>This is a test email to confirm that your AI Eyes Security System email configuration is working correctly.</p>
                <p><strong>System Status:</strong> ✅ Active and Ready</p>
                <p><strong>Email Alerts:</strong> ✅ Configured Successfully</p>
                <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            print("Test email sent successfully!")
            return True
            
        except Exception as e:
            print(f"Error sending test email: {e}")
            return False
    
    def add_recipient(self, email):
        """Add new email recipient"""
        if email not in self.recipients:
            self.recipients.append(email)
            return True
        return False
    
    def remove_recipient(self, email):
        """Remove email recipient"""
        if email in self.recipients:
            self.recipients.remove(email)
            return True
        return False