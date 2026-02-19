"""
Patient Profile API Endpoints

Implements CRUD operations for:
- Patient profiles
- Medical history
- Allergies
- Medications
- Family history
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.patient import (
    User, MedicalHistory, Allergy, Medication, FamilyHistory
)
from app.schemas.patient import (
    PatientProfileResponse, PatientProfileUpdateRequest,
    MedicalHistorySchema, AllergySchema, MedicationSchema,
    FamilyHistorySchema
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profile", tags=["patient-profile"])


# ==================== PATIENT PROFILE ====================

@router.get("/me", response_model=PatientProfileResponse)
async def get_profile(db: Session = Depends(get_db), user_id: str = None) -> PatientProfileResponse:
    """
    Get current patient profile with all medical information
    
    Returns complete profile including:
    - Basic information
    - Medical history
    - Allergies
    - Medications
    - Family history
    """
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        logger.info(f"Profile retrieved for user: {user_id}")
        return PatientProfileResponse.from_orm(user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")


@router.put("/me", response_model=PatientProfileResponse)
async def update_profile(
    request: PatientProfileUpdateRequest,
    db: Session = Depends(get_db),
    user_id: str = None
) -> PatientProfileResponse:
    """
    Update patient profile information
    
    Can update:
    - Date of birth
    - Gender
    - Blood type
    - Phone number
    """
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Update fields if provided
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        logger.info(f"Profile updated for user: {user_id}")
        return PatientProfileResponse.from_orm(user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update profile")


# ==================== MEDICAL HISTORY ====================

@router.get("/medical-history", response_model=List[MedicalHistorySchema])
async def get_medical_history(
    status: Optional[str] = Query(None, description="Filter by status: active, resolved, ongoing"),
    db: Session = Depends(get_db),
    user_id: str = None
) -> List[MedicalHistorySchema]:
    """
    Get patient medical history
    
    Can filter by status:
    - active: Currently active conditions
    - resolved: Past conditions
    - ongoing: Long-term conditions
    """
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        query = db.query(MedicalHistory).filter(MedicalHistory.user_id == user_id)
        
        if status:
            query = query.filter(MedicalHistory.status == status)
        
        history = query.order_by(MedicalHistory.created_at.desc()).all()
        logger.info(f"Medical history retrieved for user: {user_id}")
        return [MedicalHistorySchema.from_orm(h) for h in history]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving medical history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve medical history")


@router.post("/medical-history", response_model=MedicalHistorySchema)
async def add_medical_history(
    request: MedicalHistorySchema,
    db: Session = Depends(get_db),
    user_id: str = None
) -> MedicalHistorySchema:
    """Add new medical history entry"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        history = MedicalHistory(
            user_id=user_id,
            condition=request.condition,
            diagnosis_date=request.diagnosis_date,
            resolution_date=request.resolution_date,
            status=request.status or "active",
            notes=request.notes
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        
        logger.info(f"Medical history added for user: {user_id}")
        return MedicalHistorySchema.from_orm(history)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding medical history: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add medical history")


@router.put("/medical-history/{history_id}", response_model=MedicalHistorySchema)
async def update_medical_history(
    history_id: int,
    request: MedicalHistorySchema,
    db: Session = Depends(get_db),
    user_id: str = None
) -> MedicalHistorySchema:
    """Update medical history entry"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        history = db.query(MedicalHistory).filter(
            MedicalHistory.id == history_id,
            MedicalHistory.user_id == user_id
        ).first()
        
        if not history:
            raise HTTPException(status_code=404, detail="Medical history not found")
        
        # Update fields
        history.condition = request.condition
        history.diagnosis_date = request.diagnosis_date
        history.resolution_date = request.resolution_date
        history.status = request.status or history.status
        history.notes = request.notes
        history.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(history)
        
        logger.info(f"Medical history updated for user: {user_id}")
        return MedicalHistorySchema.from_orm(history)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating medical history: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update medical history")


@router.delete("/medical-history/{history_id}")
async def delete_medical_history(
    history_id: int,
    db: Session = Depends(get_db),
    user_id: str = None
):
    """Delete medical history entry"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        history = db.query(MedicalHistory).filter(
            MedicalHistory.id == history_id,
            MedicalHistory.user_id == user_id
        ).first()
        
        if not history:
            raise HTTPException(status_code=404, detail="Medical history not found")
        
        db.delete(history)
        db.commit()
        
        logger.info(f"Medical history deleted for user: {user_id}")
        return {"status": "deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting medical history: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete medical history")


# ==================== ALLERGIES ====================

@router.get("/allergies", response_model=List[AllergySchema])
async def get_allergies(
    db: Session = Depends(get_db),
    user_id: str = None
) -> List[AllergySchema]:
    """Get patient allergies"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        allergies = (
            db.query(Allergy)
            .filter(Allergy.user_id == user_id)
            .order_by(Allergy.created_at.desc())
            .all()
        )
        
        logger.info(f"Allergies retrieved for user: {user_id}")
        return [AllergySchema.from_orm(a) for a in allergies]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving allergies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve allergies")


@router.post("/allergies", response_model=AllergySchema)
async def add_allergy(
    request: AllergySchema,
    db: Session = Depends(get_db),
    user_id: str = None
) -> AllergySchema:
    """Add new allergy"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        allergy = Allergy(
            user_id=user_id,
            allergen=request.allergen,
            reaction=request.reaction,
            severity=request.severity or "moderate",
            notes=request.notes
        )
        db.add(allergy)
        db.commit()
        db.refresh(allergy)
        
        logger.info(f"Allergy added for user: {user_id}")
        return AllergySchema.from_orm(allergy)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding allergy: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add allergy")


@router.put("/allergies/{allergy_id}", response_model=AllergySchema)
async def update_allergy(
    allergy_id: int,
    request: AllergySchema,
    db: Session = Depends(get_db),
    user_id: str = None
) -> AllergySchema:
    """Update allergy"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        allergy = db.query(Allergy).filter(
            Allergy.id == allergy_id,
            Allergy.user_id == user_id
        ).first()
        
        if not allergy:
            raise HTTPException(status_code=404, detail="Allergy not found")
        
        allergy.allergen = request.allergen
        allergy.reaction = request.reaction
        allergy.severity = request.severity or allergy.severity
        allergy.notes = request.notes
        
        db.commit()
        db.refresh(allergy)
        
        logger.info(f"Allergy updated for user: {user_id}")
        return AllergySchema.from_orm(allergy)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating allergy: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update allergy")


@router.delete("/allergies/{allergy_id}")
async def delete_allergy(
    allergy_id: int,
    db: Session = Depends(get_db),
    user_id: str = None
):
    """Delete allergy"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        allergy = db.query(Allergy).filter(
            Allergy.id == allergy_id,
            Allergy.user_id == user_id
        ).first()
        
        if not allergy:
            raise HTTPException(status_code=404, detail="Allergy not found")
        
        db.delete(allergy)
        db.commit()
        
        logger.info(f"Allergy deleted for user: {user_id}")
        return {"status": "deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting allergy: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete allergy")


# ==================== MEDICATIONS ====================

@router.get("/medications", response_model=List[MedicationSchema])
async def get_medications(
    active_only: bool = Query(False, description="Get only active medications"),
    db: Session = Depends(get_db),
    user_id: str = None
) -> List[MedicationSchema]:
    """Get patient medications"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        query = db.query(Medication).filter(Medication.user_id == user_id)
        
        if active_only:
            query = query.filter(Medication.is_active == True)
        
        medications = query.order_by(Medication.created_at.desc()).all()
        
        logger.info(f"Medications retrieved for user: {user_id}")
        return [MedicationSchema.from_orm(m) for m in medications]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving medications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve medications")


@router.post("/medications", response_model=MedicationSchema)
async def add_medication(
    request: MedicationSchema,
    db: Session = Depends(get_db),
    user_id: str = None
) -> MedicationSchema:
    """Add new medication"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        medication = Medication(
            user_id=user_id,
            name=request.name,
            dosage=request.dosage,
            frequency=request.frequency,
            reason=request.reason,
            start_date=request.start_date,
            end_date=request.end_date,
            is_active=request.is_active if request.is_active is not None else True
        )
        db.add(medication)
        db.commit()
        db.refresh(medication)
        
        logger.info(f"Medication added for user: {user_id}")
        return MedicationSchema.from_orm(medication)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding medication: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add medication")


@router.put("/medications/{medication_id}", response_model=MedicationSchema)
async def update_medication(
    medication_id: int,
    request: MedicationSchema,
    db: Session = Depends(get_db),
    user_id: str = None
) -> MedicationSchema:
    """Update medication"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        medication = db.query(Medication).filter(
            Medication.id == medication_id,
            Medication.user_id == user_id
        ).first()
        
        if not medication:
            raise HTTPException(status_code=404, detail="Medication not found")
        
        medication.name = request.name
        medication.dosage = request.dosage
        medication.frequency = request.frequency
        medication.reason = request.reason
        medication.start_date = request.start_date
        medication.end_date = request.end_date
        medication.is_active = request.is_active if request.is_active is not None else medication.is_active
        medication.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(medication)
        
        logger.info(f"Medication updated for user: {user_id}")
        return MedicationSchema.from_orm(medication)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating medication: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update medication")


@router.delete("/medications/{medication_id}")
async def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    user_id: str = None
):
    """Delete medication"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        medication = db.query(Medication).filter(
            Medication.id == medication_id,
            Medication.user_id == user_id
        ).first()
        
        if not medication:
            raise HTTPException(status_code=404, detail="Medication not found")
        
        db.delete(medication)
        db.commit()
        
        logger.info(f"Medication deleted for user: {user_id}")
        return {"status": "deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting medication: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete medication")


# ==================== FAMILY HISTORY ====================

@router.get("/family-history", response_model=List[FamilyHistorySchema])
async def get_family_history(
    db: Session = Depends(get_db),
    user_id: str = None
) -> List[FamilyHistorySchema]:
    """Get patient family history"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        history = (
            db.query(FamilyHistory)
            .filter(FamilyHistory.user_id == user_id)
            .order_by(FamilyHistory.created_at.desc())
            .all()
        )
        
        logger.info(f"Family history retrieved for user: {user_id}")
        return [FamilyHistorySchema.from_orm(h) for h in history]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving family history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve family history")


@router.post("/family-history", response_model=FamilyHistorySchema)
async def add_family_history(
    request: FamilyHistorySchema,
    db: Session = Depends(get_db),
    user_id: str = None
) -> FamilyHistorySchema:
    """Add new family history entry"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        history = FamilyHistory(
            user_id=user_id,
            relation=request.relation,
            condition=request.condition,
            age_of_onset=request.age_of_onset,
            notes=request.notes
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        
        logger.info(f"Family history added for user: {user_id}")
        return FamilyHistorySchema.from_orm(history)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding family history: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add family history")


@router.put("/family-history/{history_id}", response_model=FamilyHistorySchema)
async def update_family_history(
    history_id: int,
    request: FamilyHistorySchema,
    db: Session = Depends(get_db),
    user_id: str = None
) -> FamilyHistorySchema:
    """Update family history"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        history = db.query(FamilyHistory).filter(
            FamilyHistory.id == history_id,
            FamilyHistory.user_id == user_id
        ).first()
        
        if not history:
            raise HTTPException(status_code=404, detail="Family history not found")
        
        history.relation = request.relation
        history.condition = request.condition
        history.age_of_onset = request.age_of_onset
        history.notes = request.notes
        
        db.commit()
        db.refresh(history)
        
        logger.info(f"Family history updated for user: {user_id}")
        return FamilyHistorySchema.from_orm(history)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating family history: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update family history")


@router.delete("/family-history/{history_id}")
async def delete_family_history(
    history_id: int,
    db: Session = Depends(get_db),
    user_id: str = None
):
    """Delete family history entry"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        history = db.query(FamilyHistory).filter(
            FamilyHistory.id == history_id,
            FamilyHistory.user_id == user_id
        ).first()
        
        if not history:
            raise HTTPException(status_code=404, detail="Family history not found")
        
        db.delete(history)
        db.commit()
        
        logger.info(f"Family history deleted for user: {user_id}")
        return {"status": "deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting family history: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete family history")
