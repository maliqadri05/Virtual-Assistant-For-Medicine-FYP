"""
Notification service

Handles email and SMS notifications for appointments, reminders, and alerts.
"""

import logging
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications"""
    APPOINTMENT_REMINDER = "appointment_reminder"
    APPOINTMENT_CONFIRMATION = "appointment_confirmation"
    HEALTH_ALERT = "health_alert"
    REPORT_READY = "report_ready"
    FOLLOW_UP_REMINDER = "follow_up_reminder"
    PRESCRIPTION_REMINDER = "prescription_reminder"


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationService:
    """Manages sending notifications to users"""
    
    def __init__(self):
        """Initialize notification service"""
        logger.info("NotificationService initialized")
        self.sent_notifications = []
    
    def send_notification(
        self,
        user_id: str,
        notification_type: str,
        message: str,
        channels: List[str] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Send notification to user
        
        Args:
            user_id: User ID
            notification_type: Type of notification
            message: Notification message
            channels: Delivery channels (email, sms, push, in_app)
            data: Additional notification data
        
        Returns:
            Dictionary with notification status
        """
        try:
            if channels is None:
                channels = ["email", "in_app"]
            
            notification_id = f"NOTIF_{user_id}_{int(datetime.utcnow().timestamp())}"
            
            notification = {
                "id": notification_id,
                "user_id": user_id,
                "type": notification_type,
                "message": message,
                "channels": channels,
                "data": data or {},
                "created_at": datetime.utcnow().isoformat(),
                "status": "sent"
            }
            
            # Send through each channel
            for channel in channels:
                self._send_through_channel(channel, user_id, message, notification)
            
            self.sent_notifications.append(notification)
            logger.info(f"Notification sent: {notification_id} to {user_id}")
            
            return {
                "success": True,
                "notification_id": notification_id,
                "channels_used": channels
            }
        
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _send_through_channel(
        self,
        channel: str,
        user_id: str,
        message: str,
        notification: Dict
    ) -> bool:
        """Send notification through specific channel"""
        try:
            if channel == "email":
                return self._send_email(user_id, message, notification)
            elif channel == "sms":
                return self._send_sms(user_id, message, notification)
            elif channel == "push":
                return self._send_push_notification(user_id, message, notification)
            elif channel == "in_app":
                return self._send_in_app(user_id, message, notification)
            else:
                logger.warning(f"Unknown notification channel: {channel}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending through {channel}: {e}")
            return False
    
    def _send_email(self, user_id: str, message: str, notification: Dict) -> bool:
        """Send email notification (placeholder)"""
        logger.info(f"Sending email to user {user_id}: {message[:50]}...")
        # In production, integrate with email service (SendGrid, SES, Mailgun)
        return True
    
    def _send_sms(self, user_id: str, message: str, notification: Dict) -> bool:
        """Send SMS notification (placeholder)"""
        logger.info(f"Sending SMS to user {user_id}: {message[:50]}...")
        # In production, integrate with SMS service (Twilio, AWS SNS)
        return True
    
    def _send_push_notification(
        self,
        user_id: str,
        message: str,
        notification: Dict
    ) -> bool:
        """Send push notification (placeholder)"""
        logger.info(f"Sending push notification to user {user_id}: {message[:50]}...")
        # In production, integrate with push service (Firebase, OneSignal)
        return True
    
    def _send_in_app(self, user_id: str, message: str, notification: Dict) -> bool:
        """Send in-app notification"""
        logger.info(f"Storing in-app notification for user {user_id}")
        return True
    
    def send_appointment_reminder(
        self,
        user_id: str,
        appointment_date: datetime,
        provider_name: str
    ) -> Dict[str, any]:
        """
        Send appointment reminder notification
        
        Args:
            user_id: User ID
            appointment_date: Appointment date/time
            provider_name: Provider name
        
        Returns:
            Notification result
        """
        message = f"Reminder: Appointment with {provider_name} on {appointment_date.strftime('%B %d at %I:%M %p')}"
        
        return self.send_notification(
            user_id,
            NotificationType.APPOINTMENT_REMINDER.value,
            message,
            channels=["email", "sms", "push"],
            data={
                "appointment_date": appointment_date.isoformat(),
                "provider_name": provider_name
            }
        )
    
    def send_health_alert(
        self,
        user_id: str,
        alert_title: str,
        alert_message: str
    ) -> Dict[str, any]:
        """Send health alert notification"""
        full_message = f"{alert_title}: {alert_message}"
        
        return self.send_notification(
            user_id,
            NotificationType.HEALTH_ALERT.value,
            full_message,
            channels=["email", "push"],
            data={
                "alert_title": alert_title,
                "alert_severity": "high"
            }
        )
    
    def send_follow_up_reminder(
        self,
        user_id: str,
        follow_up_task: str,
        due_date: datetime
    ) -> Dict[str, any]:
        """Send follow-up task reminder"""
        message = f"Follow-up: {follow_up_task} (Due: {due_date.strftime('%B %d')})"
        
        return self.send_notification(
            user_id,
            NotificationType.FOLLOW_UP_REMINDER.value,
            message,
            channels=["email", "in_app"],
            data={
                "task": follow_up_task,
                "due_date": due_date.isoformat()
            }
        )
    
    def get_notification_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """Get notification history for user"""
        user_notifications = [
            n for n in self.sent_notifications
            if n["user_id"] == user_id
        ]
        return user_notifications[-limit:]


# Global instance
_notification_service = None


def get_notification_service() -> NotificationService:
    """Get or create global notification service instance"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
