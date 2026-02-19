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
    id: str
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
            id=conversation_id,
            created_at=now,
            initial_message=initial_message,
            patient_context=request.patient_context
        )
    
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.post(
    "/{conversation_id}/messages",
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


@router.get(
    "/",
    response_model=List[Dict[str, Any]],
    summary="List all conversations"
)
async def list_conversations(
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    List all conversations for authenticated user.
    
    Query Parameters:
    - skip: Number of conversations to skip (pagination)
    - limit: Maximum conversations to return
    
    Returns:
    - List of conversation summaries
    """
    try:
        user_id = current_user.get("user_id")
        user_conversations = [
            {
                "id": conv_id,
                "title": f"Consultation {conv_id[:8]}",
                "messageCount": len(conv_data.get("messages", [])),
                "createdAt": conv_data.get("created_at"),
                "updatedAt": conv_data.get("updated_at"),
                "status": "completed" if len(conv_data.get("messages", [])) > 4 else "in-progress",
                "lastMessage": conv_data.get("messages", [])[-1].get("content", "No messages") if conv_data.get("messages") else "No messages",
                "timestamp": conv_data.get("updated_at")
            }
            for conv_id, conv_data in conversations_db.items()
            if conv_data.get("user_id") == user_id
        ]
        
        # Sort by updated_at descending
        user_conversations.sort(key=lambda x: x["updatedAt"] or datetime.utcnow(), reverse=True)
        
        # Apply pagination
        return user_conversations[skip : skip + limit]
    
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list conversations")


@router.delete(
    "/{conversation_id}",
    summary="Delete conversation"
)
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete a conversation permanently.
    
    Returns:
    - Confirmation of deletion
    """
    try:
        if conversation_id not in conversations_db:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conversations_db[conversation_id]
        
        # Verify user owns conversation
        if conv_data["user_id"] != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        del conversations_db[conversation_id]
        
        logger.info(f"Deleted conversation: {conversation_id}")
        
        return {"status": "deleted", "conversation_id": conversation_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete conversation")


@router.get(
    "/{conversation_id}/report",
    response_model=Dict[str, Any],
    summary="Get conversation report"
)
async def get_report(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the generated report for a conversation.
    
    Returns:
    - Generated medical report with all sections
    """
    try:
        if conversation_id not in conversations_db:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conversations_db[conversation_id]
        
        # Verify user owns conversation
        if conv_data["user_id"] != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate report
        history = [msg["content"] for msg in conv_data["messages"] if msg["role"] == "user"]
        agent_manager = conv_data["agent_manager"]
        patient_context = conv_data["patient_context"].dict() if conv_data["patient_context"] else None
        
        report = agent_manager.force_report_generation(history, patient_context)
        
        return {
            "conversation_id": conversation_id,
            "report": report,
            "generated_at": datetime.utcnow(),
            "message_count": len(conv_data["messages"])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get report")


@router.post(
    "/{conversation_id}/share",
    summary="Share conversation"
)
async def share_conversation(
    conversation_id: str,
    request: Dict[str, str],
    current_user: dict = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Share a conversation with another user via email.
    
    Request body:
    - email: Email address to share with
    
    Returns:
    - Confirmation of sharing
    """
    try:
        if conversation_id not in conversations_db:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conversations_db[conversation_id]
        
        # Verify user owns conversation
        if conv_data["user_id"] != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        email = request.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        logger.info(f"Conversation {conversation_id} shared with {email}")
        
        return {
            "status": "shared",
            "conversation_id": conversation_id,
            "shared_with": email
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sharing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to share conversation")


@router.get(
    "/search",
    response_model=List[Dict[str, Any]],
    summary="Search conversations"
)
async def search_conversations(
    current_user: dict = Depends(get_current_user),
    q: str = ""
) -> List[Dict[str, Any]]:
    """
    Search conversations by keyword.
    
    Query Parameters:
    - q: Search query
    
    Returns:
    - List of matching conversations
    """
    try:
        user_id = current_user.get("user_id")
        query_lower = q.lower()
        
        results = [
            {
                "id": conv_id,
                "title": f"Consultation {conv_id[:8]}",
                "messageCount": len(conv_data.get("messages", [])),
                "createdAt": conv_data.get("created_at"),
                "updatedAt": conv_data.get("updated_at"),
            }
            for conv_id, conv_data in conversations_db.items()
            if conv_data.get("user_id") == user_id
            and (query_lower in conv_id.lower() or 
                 any(query_lower in msg.get("content", "").lower() 
                     for msg in conv_data.get("messages", [])))
        ]
        
        return results
    
    except Exception as e:
        logger.error(f"Error searching conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search conversations")


@router.get(
    "/stats",
    response_model=Dict[str, Any],
    summary="Get conversation statistics"
)
async def get_stats(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get statistics for all user conversations.
    
    Returns:
    - Total conversations
    - Total messages
    - Average messages per conversation
    - Completed vs in-progress counts
    """
    try:
        user_id = current_user.get("user_id")
        user_conversations = {
            conv_id: conv_data
            for conv_id, conv_data in conversations_db.items()
            if conv_data.get("user_id") == user_id
        }
        
        total_conversations = len(user_conversations)
        total_messages = sum(len(conv.get("messages", [])) for conv in user_conversations.values())
        completed = sum(1 for conv in user_conversations.values() 
                       if len(conv.get("messages", [])) > 4)
        in_progress = total_conversations - completed
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "average_messages_per_conversation": total_messages / max(total_conversations, 1),
            "completed": completed,
            "in_progress": in_progress
        }
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")
