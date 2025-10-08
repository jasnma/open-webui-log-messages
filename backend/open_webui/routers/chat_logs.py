from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from open_webui.models.chat_logs import ChatLogs, ChatLogModel
from open_webui.utils.auth import get_verified_user
from open_webui.utils.middleware import process_chat_payload, process_chat_response

router = APIRouter()

class ChatLogResponse(BaseModel):
    conversation_id: str
    user_id: str
    model: str
    messages: List[dict]
    response: Optional[str] = None
    created_at: int

class ChatLogsResponse(BaseModel):
    data: List[ChatLogResponse]
    count: int

class ChatLogFilter(BaseModel):
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    model: Optional[str] = None
    limit: Optional[int] = 50
    skip: Optional[int] = 0

@router.get("/", response_model=ChatLogsResponse)
async def get_chat_logs(
    filter: ChatLogFilter = None,
    user=Depends(get_verified_user)
):
    """Get chat logs with optional filtering"""
    try:
        # If no filter is provided, default to user's logs
        if filter is None:
            filter = ChatLogFilter()
        
        # Apply filters
        if filter.conversation_id:
            # Get logs by conversation ID
            logs = ChatLogs.get_chat_logs_by_conversation_id(
                filter.conversation_id,
                skip=filter.skip,
                limit=filter.limit
            )
            count = len(logs)
        else:
            # Get logs by user ID (default behavior)
            logs = ChatLogs.get_chat_logs_by_user_id(
                user.id,
                skip=filter.skip,
                limit=filter.limit
            )
            count = len(logs)
        
        # Convert to response format
        response_logs = [
            ChatLogResponse(
                conversation_id=log.conversation_id,
                user_id=log.user_id,
                model=log.model,
                messages=log.messages,
                response=log.response,
                created_at=log.created_at
            )
            for log in logs
        ]
        
        return ChatLogsResponse(data=response_logs, count=count)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat logs: {str(e)}"
        )

@router.get("/{conversation_id}", response_model=ChatLogResponse)
async def get_chat_log_by_conversation_id(
    conversation_id: str,
    user=Depends(get_verified_user)
):
    """Get a specific chat log by conversation ID"""
    try:
        log = ChatLogs.get_chat_log_by_conversation_id(conversation_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat log not found"
            )
        
        # Verify ownership
        if log.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this chat log"
            )
        
        return ChatLogResponse(
            conversation_id=log.conversation_id,
            user_id=log.user_id,
            model=log.model,
            messages=log.messages,
            response=log.response,
            created_at=log.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat log: {str(e)}"
        )

@router.delete("/{conversation_id}", response_model=bool)
async def delete_chat_log_by_conversation_id(
    conversation_id: str,
    user=Depends(get_verified_user)
):
    """Delete a specific chat log by conversation ID"""
    try:
        log = ChatLogs.get_chat_log_by_conversation_id(conversation_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat log not found"
            )
        
        # Verify ownership
        if log.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to delete this chat log"
            )
        
        return ChatLogs.delete_chat_log_by_conversation_id(conversation_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chat log: {str(e)}"
        )
