"""
Conversations API Endpoint

Handles:
- Starting new consultations
- Sending messages to AI agents
- Retrieving conversation history
- Getting conversation status
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import uuid
from datetime import datetime

from app.agents import AgentManager
from app.api.dependencies import get_current_user, get_agent_manager

logger = logging.getLogger(__name__)


# ==================== SCHEMAS ====================

class PatientContext(BaseModel):
    """Patient demographic context"""
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    weight: Optional[float] = None
    medical_history: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None


class Message(BaseModel):
    """Single message in conversation"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationCreateRequest(BaseModel):
    """Request to create new conversation"""
    patient_context: Optional[PatientContext] = None
    initial_message: Optional[str] = None


class ConversationCreateResponse(BaseModel):
    """Response when creating conversation"""
    conversation_id: str
    created_at: datetime
    initial_message: Message
    patient_context: Optional[PatientContext] = None


class MessageRequest(BaseModel):
    """Request to send message in conversation"""
    content: str = Field(..., description="User message content")
    patient_context: Optional[PatientContext] = None


class MessageResponse(BaseModel):
    """Response from sending message"""
    conversation_id: str
    user_message: Message
    assistant_response: Message
    validation_status: Dict[str, Any]
    conversation_length: int


class ConversationHistory(BaseModel):
    """Get conversation history"""
    conversation_id: str
    messages: List[Message]
    patient_context: Optional[PatientContext] = None
    created_at: datetime
    updated_at: datetime


class ConversationStatus(BaseModel):
    """Get conversation status"""
    conversation_id: str
    is_complete: bool
    message_count: int
    missing_category: Optional[str] = None
    can_generate_report: bool


# ==================== IN-MEMORY STORAGE ====================
# TODO: Replace with database

conversations_db: Dict[str, Dict[str, Any]] = {}


# ==================== ROUTER ====================

router = APIRouter(prefix="/conversations", tags=["conversations"])


# ==================== ENDPOINTS ====================

@router.post(
    "/",
    response_model=ConversationCreateResponse,
    summary="Start new consultation"
)
async def create_conversation(
    request: ConversationCreateRequest,
    current_user: dict = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager)
) -> ConversationCreateResponse:
    """
    Start a new medical consultation conversation.
    
    Returns:
    - conversation_id: Unique identifier for the conversation
    - initial_message: Opening message from the AI assistant
    - patient_context: Stored patient information
    """
    try:
        conversation_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Get opening message from agent manager
        opening = agent_manager.start_conversation(
            patient_context=request.patient_context.dict() if request.patient_context else None
        )
        
        # Store conversation
        conversations_db[conversation_id] = {
            "created_at": now,
            "updated_at": now,
            "patient_context": request.patient_context,
            "user_id": current_user.get("user_id"),
            "messages": [],
            "agent_manager": agent_manager
        }
        
        # Create opening message
        initial_message = Message(
            role="assistant",
            content=opening["content"],
            timestamp=now
        )
        
        logger.info(f"Created conversation: {conversation_id}")
        
        return ConversationCreateResponse(
            conversation_id=conversation_id,
            created_at=now,
            initial_message=initial_message,
            patient_context=request.patient_context
        )
    
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.post(
    "/{conversation_id}/message",
    response_model=MessageResponse,
    summary="Send message in conversation"
)
async def send_message(
    conversation_id: str,
    request: MessageRequest,
    current_user: dict = Depends(get_current_user)
) -> MessageResponse:
    """
    Send a message in the conversation and get AI response.
    
    The AI agents will:
    1. Validate if enough information has been gathered
    2. Ask clarifying questions if needed
    3. Generate medical report when ready
    
    Returns:
    - Full conversation flow with user message and assistant response
    - Validation status showing if conversation is complete
    """
    try:
        # Verify conversation exists
        if conversation_id not in conversations_db:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conversations_db[conversation_id]
        
        # Verify user owns conversation
        if conv_data["user_id"] != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        now = datetime.utcnow()
        
        # Create user message
        user_message = Message(
            role="user",
            content=request.content,
            timestamp=now
        )
        
        # Get conversation history (user messages only)
        history = [msg["content"] for msg in conv_data["messages"] if msg["role"] == "user"]
        
        # Update patient context if provided
        if request.patient_context:
            conv_data["patient_context"] = request.patient_context
        
        # Process message through agents
        agent_manager = conv_data["agent_manager"]
        patient_context = conv_data["patient_context"].dict() if conv_data["patient_context"] else None
        
        agent_response = agent_manager.process_message(
            user_message=request.content,
            conversation_history=history,
            patient_context=patient_context
        )
        
        # Create assistant message
        assistant_message = Message(
            role="assistant",
            content=agent_response.get("content", ""),
            timestamp=datetime.utcnow(),
            metadata={
                "agent": agent_response.get("agent", "unknown"),
                "validation": agent_response.get("validation", {})
            }
        )
        
        # Store messages in conversation
        conv_data["messages"].append(user_message.dict())
        conv_data["messages"].append(assistant_message.dict())
        conv_data["updated_at"] = now
        
        logger.info(
            f"Message processed in conversation {conversation_id}. "
            f"Length: {len(conv_data['messages'])}"
        )
        
        return MessageResponse(
            conversation_id=conversation_id,
            user_message=user_message,
            assistant_response=assistant_message,
            validation_status=agent_response.get("validation", {}),
            conversation_length=len(conv_data["messages"])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")


@router.get(
    "/{conversation_id}",
    response_model=ConversationHistory,
    summary="Get conversation history"
)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
) -> ConversationHistory:
    """
    Get full conversation history.
    
    Returns:
    - All messages (user and assistant)
    - Conversation metadata
    - Patient information
    """
    try:
        if conversation_id not in conversations_db:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conversations_db[conversation_id]
        
        # Verify user owns conversation
        if conv_data["user_id"] != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Build messages list
        messages = [Message(**msg) for msg in conv_data["messages"]]
        
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=messages,
            patient_context=conv_data["patient_context"],
            created_at=conv_data["created_at"],
            updated_at=conv_data["updated_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")


@router.get(
    "/{conversation_id}/status",
    response_model=ConversationStatus,
    summary="Get conversation completion status"
)
async def get_status(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
) -> ConversationStatus:
    """
    Get conversation status.
    
    Returns:
    - Whether conversation is complete and ready for report
    - What information (if any) is still missing
    - Total message count
    """
    try:
        if conversation_id not in conversations_db:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conversations_db[conversation_id]
        
        # Verify user owns conversation
        if conv_data["user_id"] != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get history
        history = [msg["content"] for msg in conv_data["messages"] if msg["role"] == "user"]
        
        # Get status from agent manager
        agent_manager = conv_data["agent_manager"]
        patient_context = conv_data["patient_context"].dict() if conv_data["patient_context"] else None
        
        status_info = agent_manager.get_conversation_status(history, patient_context)
        
        return ConversationStatus(
            conversation_id=conversation_id,
            is_complete=status_info["is_complete"],
            message_count=len(conv_data["messages"]),
            missing_category=status_info.get("missing_category"),
            can_generate_report=status_info["is_complete"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get status")


@router.post(
    "/{conversation_id}/generate-report",
    response_model=Dict[str, Any],
    summary="Generate medical report (force)"
)
async def generate_report(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Force generation of medical report.
    
    Can be called at any point in conversation.
    
    Returns:
    - Generated medical report
    - Report metadata
    """
    try:
        if conversation_id not in conversations_db:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conversations_db[conversation_id]
        
        # Verify user owns conversation
        if conv_data["user_id"] != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get history
        history = [msg["content"] for msg in conv_data["messages"] if msg["role"] == "user"]
        
        # Generate report
        agent_manager = conv_data["agent_manager"]
        patient_context = conv_data["patient_context"].dict() if conv_data["patient_context"] else None
        
        report = agent_manager.force_report_generation(history, patient_context)
        
        logger.info(f"Report generated for conversation: {conversation_id}")
        
        return {
            "conversation_id": conversation_id,
            "report": report,
            "generated_at": datetime.utcnow(),
            "message_count": len(conv_data["messages"])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate report")
