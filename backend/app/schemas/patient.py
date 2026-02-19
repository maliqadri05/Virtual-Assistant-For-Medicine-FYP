"""
Pydantic schemas for Patient Profile and Medical History

Used for request/response validation in API endpoints
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


# ==================== PATIENT PROFILE SCHEMAS ====================

class AllergySchema(BaseModel):
    """Allergy information"""
    id: Optional[int] = None
    allergen: str = Field(..., description="Allergen name (e.g., Penicillin)")
    reaction: str = Field(..., description="Reaction type")
    severity: str = Field(default="moderate", description="Mild, Moderate, or Severe")
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MedicationSchema(BaseModel):
    """Current medication information"""
    id: Optional[int] = None
    name: str = Field(..., description="Medication name")
    dosage: str = Field(..., description="Dosage (e.g., 500mg)")
    frequency: str = Field(..., description="Frequency (e.g., Once daily)")
    reason: str = Field(..., description="Reason for taking")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MedicalHistorySchema(BaseModel):
    """Past medical conditions"""
    id: Optional[int] = None
    condition: str = Field(..., description="Medical condition")
    diagnosis_date: Optional[datetime] = None
    resolution_date: Optional[datetime] = None
    status: str = Field(default="active", description="active, resolved, or ongoing")
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FamilyHistorySchema(BaseModel):
    """Family medical history"""
    id: Optional[int] = None
    relation: str = Field(..., description="Relationship (Mother, Father, etc)")
    condition: str = Field(..., description="Medical condition")
    age_of_onset: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PatientProfileUpdateRequest(BaseModel):
    """Update patient profile"""
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    phone: Optional[str] = None


class PatientProfileResponse(BaseModel):
    """Full patient profile"""
    id: str
    email: str
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Medical information
    medical_histories: List[MedicalHistorySchema] = []
    allergies: List[AllergySchema] = []
    medications: List[MedicationSchema] = []
    family_history: List[FamilyHistorySchema] = []
    
    class Config:
        from_attributes = True


# ==================== CONVERSATION HISTORY SCHEMAS ====================

class ConversationMessageSchema(BaseModel):
    """Individual message in conversation"""
    id: Optional[int] = None
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message content")
    message_type: str = Field(default="text")
    message_metadata: dict = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConversationSummarySchema(BaseModel):
    """Conversation summary for listings"""
    id: str
    title: str
    initial_symptoms: str
    status: str
    confidence_score: float
    message_count: int
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConversationDetailSchema(ConversationSummarySchema):
    """Full conversation with all messages"""
    ai_diagnosis: Optional[str] = None
    messages: List[ConversationMessageSchema] = []
    
    class Config:
        from_attributes = True


class ConversationCreateRequest(BaseModel):
    """Create new conversation"""
    title: str = Field(..., description="Conversation title")
    initial_symptoms: str = Field(..., description="Initial symptoms/complaint")
    tags: Optional[List[str]] = Field(default_factory=list)


class ConversationUpdateRequest(BaseModel):
    """Update conversation"""
    title: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    ai_diagnosis: Optional[str] = None
    confidence_score: Optional[float] = None


class ConversationSearchRequest(BaseModel):
    """Search conversations"""
    query: Optional[str] = Field(None, description="Search in title/symptoms")
    status: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at", description="created_at or updated_at")
    sort_order: str = Field(default="desc", description="asc or desc")


class ConversationSearchResponse(BaseModel):
    """Search results"""
    total: int
    limit: int
    offset: int
    results: List[ConversationSummarySchema]


# ==================== SMART FEATURES SCHEMAS ====================

class SymptomTrendSchema(BaseModel):
    """Symptom trend analysis"""
    symptom: str
    occurrence_count: int
    first_occurrence: datetime
    last_occurrence: datetime
    average_severity: Optional[float] = None
    related_conditions: List[str] = []


class HealthInsightSchema(BaseModel):
    """Health insights"""
    type: str  # "pattern", "trend", "recommendation", "warning"
    title: str
    description: str
    confidence: float
    related_conditions: List[str]
    recommendation: Optional[str] = None
    severity: Optional[str] = None


class WellnessReportSchema(BaseModel):
    """Overall wellness report"""
    total_conversations: int
    active_conditions: int
    medication_count: int
    recent_symptoms: List[str]
    symptom_trends: List[SymptomTrendSchema]
    recurring_issues: List[dict]
    health_insights: List[HealthInsightSchema]
    follow_up_recommendations: List[str]
