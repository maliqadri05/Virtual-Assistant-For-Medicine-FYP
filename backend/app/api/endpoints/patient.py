"""
Patient API Endpoints

Handles:
- Patient profile management
- Medical history
- Allergies and medications
- Family history
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# In-memory storage (TODO: Replace with database)
patient_profiles: Dict[str, Dict[str, Any]] = {}


# ==================== SCHEMAS ====================

class PatientProfile(BaseModel):
    """Patient profile information"""
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class MedicalHistory(BaseModel):
    """Medical history entry"""
    condition: str
    diagnosed_year: Optional[int] = None
    status: Optional[str] = None  # active, resolved, etc.
    notes: Optional[str] = None


class Allergy(BaseModel):
    """Allergy information"""
    allergen: str
    reaction: Optional[str] = None
    severity: Optional[str] = None  # mild, moderate, severe


class Medication(BaseModel):
    """Medication information"""
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    reason: Optional[str] = None


class FamilyHistory(BaseModel):
    """Family history information"""
    relation: str
    condition: str
    notes: Optional[str] = None


# ==================== ROUTER ====================

router = APIRouter(prefix="/patient", tags=["patient"])


# ==================== HELPER ====================

def get_user_id(token: Optional[str] = None) -> str:
    """Extract user ID from token (simplified)"""
    # In production, parse JWT token
    return "default-user"


# ==================== ENDPOINTS ====================

@router.get(
    "/profile",
    response_model=PatientProfile,
    summary="Get patient profile"
)
async def get_profile() -> PatientProfile:
    """
    Get authenticated patient's profile.
    
    Returns:
    - Patient personal information
    """
    try:
        user_id = get_user_id()
        
        if user_id not in patient_profiles:
            # Return default profile
            return PatientProfile(
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                phone="+1 (555) 123-4567",
                date_of_birth="1990-01-15"
            )
        
        profile = patient_profiles[user_id]
        return PatientProfile(**profile)
    
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get profile")


@router.put(
    "/profile",
    response_model=PatientProfile,
    summary="Update patient profile"
)
async def update_profile(profile: PatientProfile) -> PatientProfile:
    """
    Update authenticated patient's profile.
    
    Returns:
    - Updated patient information
    """
    try:
        user_id = get_user_id()
        
        patient_profiles[user_id] = {
            **profile.dict(),
            "updated_at": datetime.utcnow()
        }
        
        logger.info(f"Profile updated for user: {user_id}")
        
        return profile
    
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.get(
    "/medical-history",
    response_model=List[MedicalHistory],
    summary="Get medical history"
)
async def get_medical_history() -> List[MedicalHistory]:
    """
    Get patient's medical history.
    
    Returns:
    - List of medical conditions and history
    """
    try:
        user_id = get_user_id()
        
        # Return mock data
        return [
            MedicalHistory(
                condition="Hypertension",
                diagnosed_year=2018,
                status="active",
                notes="Managed with medication"
            ),
            MedicalHistory(
                condition="Type 2 Diabetes",
                diagnosed_year=2019,
                status="active",
                notes="Controlled with diet and exercise"
            )
        ]
    
    except Exception as e:
        logger.error(f"Error getting medical history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get medical history")


@router.post(
    "/medical-history",
    response_model=MedicalHistory,
    summary="Add medical history entry"
)
async def add_medical_history(entry: MedicalHistory) -> MedicalHistory:
    """
    Add new medical history entry.
    
    Returns:
    - Added entry
    """
    try:
        user_id = get_user_id()
        
        logger.info(f"Medical history entry added for user: {user_id}")
        
        return entry
    
    except Exception as e:
        logger.error(f"Error adding medical history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add medical history")


@router.get(
    "/allergies",
    response_model=List[Allergy],
    summary="Get allergies"
)
async def get_allergies() -> List[Allergy]:
    """
    Get patient's allergies.
    
    Returns:
    - List of known allergies
    """
    try:
        user_id = get_user_id()
        
        # Return mock data
        return [
            Allergy(
                allergen="Penicillin",
                reaction="Rash",
                severity="mild"
            ),
            Allergy(
                allergen="Shellfish",
                reaction="Anaphylaxis",
                severity="severe"
            )
        ]
    
    except Exception as e:
        logger.error(f"Error getting allergies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get allergies")


@router.post(
    "/allergies",
    response_model=Allergy,
    summary="Add allergy"
)
async def add_allergy(allergy: Allergy) -> Allergy:
    """
    Add new allergy entry.
    
    Returns:
    - Added allergy
    """
    try:
        user_id = get_user_id()
        
        logger.info(f"Allergy added for user: {user_id}")
        
        return allergy
    
    except Exception as e:
        logger.error(f"Error adding allergy: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add allergy")


@router.get(
    "/medications",
    response_model=List[Medication],
    summary="Get medications"
)
async def get_medications() -> List[Medication]:
    """
    Get patient's current medications.
    
    Returns:
    - List of medications
    """
    try:
        user_id = get_user_id()
        
        # Return mock data
        return [
            Medication(
                name="Lisinopril",
                dosage="10mg",
                frequency="Once daily",
                reason="Hypertension"
            ),
            Medication(
                name="Metformin",
                dosage="500mg",
                frequency="Twice daily",
                reason="Type 2 Diabetes"
            )
        ]
    
    except Exception as e:
        logger.error(f"Error getting medications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get medications")


@router.post(
    "/medications",
    response_model=Medication,
    summary="Add medication"
)
async def add_medication(medication: Medication) -> Medication:
    """
    Add new medication entry.
    
    Returns:
    - Added medication
    """
    try:
        user_id = get_user_id()
        
        logger.info(f"Medication added for user: {user_id}")
        
        return medication
    
    except Exception as e:
        logger.error(f"Error adding medication: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add medication")


@router.get(
    "/family-history",
    response_model=List[FamilyHistory],
    summary="Get family history"
)
async def get_family_history() -> List[FamilyHistory]:
    """
    Get patient's family medical history.
    
    Returns:
    - List of family medical history
    """
    try:
        user_id = get_user_id()
        
        # Return mock data
        return [
            FamilyHistory(
                relation="Father",
                condition="Heart Disease",
                notes="Diagnosed at age 55"
            ),
            FamilyHistory(
                relation="Mother",
                condition="Type 2 Diabetes",
                notes="Diagnosed at age 60"
            )
        ]
    
    except Exception as e:
        logger.error(f"Error getting family history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get family history")


@router.post(
    "/family-history",
    response_model=FamilyHistory,
    summary="Add family history entry"
)
async def add_family_history(entry: FamilyHistory) -> FamilyHistory:
    """
    Add new family history entry.
    
    Returns:
    - Added entry
    """
    try:
        user_id = get_user_id()
        
        logger.info(f"Family history entry added for user: {user_id}")
        
        return entry
    
    except Exception as e:
        logger.error(f"Error adding family history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add family history")
