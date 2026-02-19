"""
Conversation History API Endpoints

Implements:
- Store conversations in database
- Retrieve conversation history with pagination
- Search and filter conversations
- Conversation tagging and metadata
- Smart analytics and insights
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
from collections import Counter, defaultdict

from app.core.database import get_db
from app.models.patient import (
    Conversation, ConversationMessage, ConversationTag, User,
    MedicalHistory, Allergy
)
from app.schemas.patient import (
    ConversationCreateRequest, ConversationUpdateRequest,
    ConversationDetailSchema, ConversationSummarySchema,
    ConversationSearchRequest, ConversationSearchResponse,
    ConversationMessageSchema, SymptomTrendSchema,
    HealthInsightSchema, WellnessReportSchema
)
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/conversations", tags=["conversation-history"])


# ==================== CONVERSATION HISTORY ENDPOINTS ====================

@router.get("/", response_model=ConversationSearchResponse)
async def list_conversations(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|updated_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    user_id: str = None
) -> ConversationSearchResponse:
    """
    List conversations with pagination
    
    Parameters:
    - limit: Number of results (max 100)
    - offset: Number to skip
    - status: Filter by status (active, completed, archived)
    - sort_by: Sort by created_at or updated_at
    - sort_order: ascending or descending
    """
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        query = db.query(Conversation).filter(Conversation.user_id == user_id)
        
        if status:
            query = query.filter(Conversation.status == status)
        
        # Count total
        total = query.count()
        
        # Sort
        sort_col = Conversation.created_at if sort_by == "created_at" else Conversation.updated_at
        if sort_order == "desc":
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())
        
        # Paginate
        conversations = query.offset(offset).limit(limit).all()
        
        logger.info(f"Conversations listed for user: {user_id} (total: {total})")
        
        return ConversationSearchResponse(
            total=total,
            limit=limit,
            offset=offset,
            results=[ConversationSummarySchema.from_orm(c) for c in conversations]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list conversations")


@router.post("/", response_model=ConversationDetailSchema, status_code=201)
async def create_conversation(
    request: ConversationCreateRequest,
    db: Session = Depends(get_db),
    user_id: str = None
) -> ConversationDetailSchema:
    """Create new conversation"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=request.title,
            initial_symptoms=request.initial_symptoms,
            status="active",
            tags=request.tags or [],
            message_count=0
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Conversation created: {conversation.id}")
        return ConversationDetailSchema.from_orm(conversation)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.get("/{conversation_id}", response_model=ConversationDetailSchema)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    user_id: str = None
) -> ConversationDetailSchema:
    """Get specific conversation with all messages"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        logger.info(f"Conversation retrieved: {conversation_id}")
        return ConversationDetailSchema.from_orm(conversation)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")


@router.put("/{conversation_id}", response_model=ConversationDetailSchema)
async def update_conversation(
    conversation_id: str,
    request: ConversationUpdateRequest,
    db: Session = Depends(get_db),
    user_id: str = None
) -> ConversationDetailSchema:
    """Update conversation"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(conversation, field, value)
        
        if request.status == "completed" and not conversation.completed_at:
            conversation.completed_at = datetime.utcnow()
        
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Conversation updated: {conversation_id}")
        return ConversationDetailSchema.from_orm(conversation)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update conversation")


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    user_id: str = None
):
    """Delete conversation"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        db.delete(conversation)
        db.commit()
        
        logger.info(f"Conversation deleted: {conversation_id}")
        return {"status": "deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete conversation")


# ==================== SEARCH & FILTER ====================

@router.post("/search", response_model=ConversationSearchResponse)
async def search_conversations(
    request: ConversationSearchRequest,
    db: Session = Depends(get_db),
    user_id: str = None
) -> ConversationSearchResponse:
    """
    Advanced search conversations
    
    Can search and filter by:
    - Query text (title/symptoms)
    - Status
    - Tags
    - Date range
    - Sorting options
    """
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        query = db.query(Conversation).filter(Conversation.user_id == user_id)
        
        # Text search
        if request.query:
            search_term = f"%{request.query}%"
            query = query.filter(
                or_(
                    Conversation.title.ilike(search_term),
                    Conversation.initial_symptoms.ilike(search_term)
                )
            )
        
        # Status filter
        if request.status:
            query = query.filter(Conversation.status == request.status)
        
        # Date range filter
        if request.start_date:
            query = query.filter(Conversation.created_at >= request.start_date)
        if request.end_date:
            query = query.filter(Conversation.created_at <= request.end_date)
        
        # Total count
        total = query.count()
        
        # Tag filter
        if request.tags:
            for tag in request.tags:
                query = query.filter(Conversation.tags.contains([tag]))
        
        # Sorting
        sort_col = Conversation.created_at if request.sort_by == "created_at" else Conversation.updated_at
        if request.sort_order.lower() == "desc":
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())
        
        # Pagination
        conversations = query.offset(request.offset).limit(request.limit).all()
        
        logger.info(f"Conversations searched for user: {user_id} (query: {request.query})")
        
        return ConversationSearchResponse(
            total=total,
            limit=request.limit,
            offset=request.offset,
            results=[ConversationSummarySchema.from_orm(c) for c in conversations]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search conversations")


# ==================== MESSAGES ====================

@router.get("/{conversation_id}/messages", response_model=List[ConversationMessageSchema])
async def get_messages(
    conversation_id: str,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user_id: str = None
) -> List[ConversationMessageSchema]:
    """Get messages for a conversation with pagination"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Verify ownership
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = (
            db.query(ConversationMessage)
            .filter(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        logger.info(f"Messages retrieved for conversation: {conversation_id}")
        return [ConversationMessageSchema.from_orm(m) for m in messages]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve messages")


@router.post("/{conversation_id}/messages", response_model=ConversationMessageSchema)
async def add_message(
    conversation_id: str,
    content: str,
    role: str = Query("user", regex="^(user|assistant|system)$"),
    message_type: str = Query("text"),
    message_metadata: dict = Query(None),
    db: Session = Depends(get_db),
    user_id: str = None
) -> ConversationMessageSchema:
    """Add message to conversation"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Verify ownership
        conversation = db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_type=message_type,
            message_metadata=message_metadata or {}
        )
        
        db.add(message)
        
        # Update message count
        conversation.message_count += 1
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        
        logger.info(f"Message added to conversation: {conversation_id}")
        return ConversationMessageSchema.from_orm(message)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add message")


# ==================== SMART ANALYTICS ====================

@router.get("/{user_id}/wellness-report", response_model=WellnessReportSchema)
async def get_wellness_report(
    user_id: str,
    db: Session = Depends(get_db)
) -> WellnessReportSchema:
    """
    Get comprehensive wellness report with insights
    
    Includes:
    - Total conversations and active conditions
    - Symptom trends and patterns
    - Recurring issues
    - Health insights and recommendations
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all conversations
        conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
        
        # Extract symptoms from initial_symptoms
        symptom_list = []
        for conv in conversations:
            if conv.initial_symptoms:
                # Simple parsing - in production use NLP
                symptoms = [s.strip() for s in conv.initial_symptoms.lower().split(",")]
                symptom_list.extend(symptoms)
        
        # Analyze symptoms
        symptom_counter = Counter(symptom_list)
        symptom_trends = [
            SymptomTrendSchema(
                symptom=symptom,
                occurrence_count=count,
                first_occurrence=conversations[0].created_at,
                last_occurrence=conversations[-1].created_at if conversations else datetime.utcnow(),
                average_severity=None,
                related_conditions=[]
            )
            for symptom, count in symptom_counter.most_common(5)
        ]
        
        # Get active conditions
        active_conditions = db.query(MedicalHistory).filter(
            and_(
                MedicalHistory.user_id == user_id,
                MedicalHistory.status == "active"
            )
        ).count()
        
        # Get medications
        medication_count = db.query(Allergy).filter(
            Allergy.user_id == user_id
        ).count()
        
        # Recent symptoms
        recent_symptoms = [s for s, _ in symptom_counter.most_common(3)]
        
        # Recurring issues
        condition_counter = Counter()
        for conv in conversations:
            if conv.ai_diagnosis:
                conditions = [c.strip() for c in conv.ai_diagnosis.lower().split(",")]
                condition_counter.update(conditions)
        
        recurring_issues = [
            {"issue": issue, "occurrences": count}
            for issue, count in condition_counter.most_common(5) if count > 1
        ]
        
        # Generate insights
        insights = []
        
        # Insight: Frequent symptoms
        if len(symptom_trends) > 0:
            insights.append(HealthInsightSchema(
                type="pattern",
                title="Frequent Symptoms",
                description=f"You've reported '{symptom_trends[0].symptom}' multiple times",
                confidence=0.9,
                related_conditions=[],
                recommendation="Consider consulting a specialist for persistent symptoms"
            ))
        
        # Insight: Recurring conditions
        if len(recurring_issues) > 0:
            insights.append(HealthInsightSchema(
                type="trend",
                title="Recurring Condition",
                description=f"'{recurring_issues[0]['issue']}' appears in {recurring_issues[0]['occurrences']} consultations",
                confidence=0.85,
                related_conditions=[recurring_issues[0]['issue']],
                recommendation="Monitor this condition closely and maintain regular check-ups"
            ))
        
        # Insight: Active conditions
        if active_conditions > 0:
            insights.append(HealthInsightSchema(
                type="warning",
                title="Active Conditions",
                description=f"You have {active_conditions} active medical conditions",
                confidence=0.95,
                related_conditions=[],
                severity="high" if active_conditions > 3 else "medium",
                recommendation="Ensure regular monitoring and follow-ups for all conditions"
            ))
        
        # Follow-up recommendations
        follow_ups = []
        if len(recurring_issues) > 0:
            follow_ups.append(f"Follow-up on {recurring_issues[0]['issue']}")
        if active_conditions > 0:
            follow_ups.append("Schedule routine check-ups for active conditions")
        if len(symptom_trends) > 0:
            follow_ups.append(f"Monitor '{symptom_trends[0].symptom}' for changes")
        
        logger.info(f"Wellness report generated for user: {user_id}")
        
        return WellnessReportSchema(
            total_conversations=len(conversations),
            active_conditions=active_conditions,
            medication_count=medication_count,
            recent_symptoms=recent_symptoms,
            symptom_trends=symptom_trends,
            recurring_issues=recurring_issues,
            health_insights=insights,
            follow_up_recommendations=follow_ups
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating wellness report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate wellness report")
