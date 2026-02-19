"""
Appointment scheduling service

Manages appointment scheduling and integration with calendars and providers.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class AppointmentStatus(Enum):
    """Appointment status enum"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    RESCHEDULED = "rescheduled"


class AppointmentType(Enum):
    """Types of appointments"""
    IN_PERSON = "in_person"
    TELEHEALTH = "telehealth"
    PHONE = "phone"


class AppointmentService:
    """Manages appointment scheduling"""
    
    def __init__(self):
        """Initialize appointment service"""
        logger.info("AppointmentService initialized")
    
    def schedule_appointment(
        self,
        user_id: str,
        provider_name: str,
        appointment_date: datetime,
        appointment_type: str = "telehealth",
        notes: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Schedule an appointment
        
        Args:
            user_id: Patient user ID
            provider_name: Healthcare provider name
            appointment_date: Appointment datetime
            appointment_type: Type of appointment
            notes: Optional appointment notes
        
        Returns:
            Dictionary with appointment details
        """
        try:
            if appointment_date <= datetime.utcnow():
                return {
                    "success": False,
                    "error": "Appointment date must be in the future"
                }
            
            appointment_id = f"APT_{user_id}_{int(appointment_date.timestamp())}"
            
            appointment = {
                "id": appointment_id,
                "user_id": user_id,
                "provider_name": provider_name,
                "appointment_date": appointment_date.isoformat(),
                "appointment_type": appointment_type,
                "status": AppointmentStatus.SCHEDULED.value,
                "notes": notes,
                "created_at": datetime.utcnow().isoformat(),
                "confirmation_code": f"CONF{appointment_id[:10].upper()}"
            }
            
            logger.info(f"Appointment scheduled: {appointment_id}")
            
            return {
                "success": True,
                "appointment": appointment
            }
        
        except Exception as e:
            logger.error(f"Error scheduling appointment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def reschedule_appointment(
        self,
        appointment_id: str,
        new_date: datetime
    ) -> Dict[str, any]:
        """Reschedule an existing appointment"""
        try:
            if new_date <= datetime.utcnow():
                return {
                    "success": False,
                    "error": "New appointment date must be in the future"
                }
            
            logger.info(f"Appointment rescheduled: {appointment_id}")
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "new_date": new_date.isoformat(),
                "status": AppointmentStatus.RESCHEDULED.value
            }
        
        except Exception as e:
            logger.error(f"Error rescheduling appointment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cancel_appointment(
        self,
        appointment_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, any]:
        """Cancel an appointment"""
        try:
            logger.info(f"Appointment cancelled: {appointment_id}")
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "status": AppointmentStatus.CANCELLED.value,
                "reason": reason
            }
        
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_slots(
        self,
        provider_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Get available time slots for a provider"""
        try:
            slots = []
            current = start_date
            
            while current <= end_date:
                # Generate slots (every 30 minutes, 9 AM - 5 PM)
                if current.hour >= 9 and current.hour < 17:
                    slots.append({
                        "start_time": current.isoformat(),
                        "end_time": (current + timedelta(minutes=30)).isoformat(),
                        "available": True
                    })
                
                current += timedelta(minutes=30)
            
            logger.info(f"Generated {len(slots)} available slots for {provider_name}")
            
            return slots
        
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return []


# Global instance
_appointment_service = None


def get_appointment_service() -> AppointmentService:
    """Get or create global appointment service instance"""
    global _appointment_service
    if _appointment_service is None:
        _appointment_service = AppointmentService()
    return _appointment_service
