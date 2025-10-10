from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from open_webui.models.chat_logs import ChatLogs, ChatLogModel, ChatLog
from open_webui.models.users import Users
from open_webui.utils.auth import get_verified_user, get_admin_user
from open_webui.utils.middleware import process_chat_payload, process_chat_response
from open_webui.internal.db import get_db

router = APIRouter()

class ChatLogResponse(BaseModel):
    conversation_id: str
    user_id: str
    user_name: str
    model: str
    messages: List[dict]
    response: Optional[str] = None
    title: Optional[str] = None
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
        
        # Get user names for all logs
        user_ids = [log.user_id for log in logs]
        user_dict = {}
        if user_ids:
            users = Users.get_users_by_user_ids(user_ids)
            user_dict = {user.id: user.name for user in users}
        
        # Convert to response format
        response_logs = [
            ChatLogResponse(
                conversation_id=log.conversation_id,
                user_id=log.user_id,
                user_name=user_dict.get(log.user_id, "Unknown User"),
                model=log.model,
                messages=log.messages,
                response=log.response,
                title=log.title,
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

@router.get("/admin", response_model=ChatLogsResponse)
async def get_all_chat_logs(
    filter: ChatLogFilter = None,
    user=Depends(get_admin_user)
):
    """Get all chat logs (admin only)"""
    try:
        # If no filter is provided, default to all logs
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
        elif filter.user_id:
            # Get logs by specific user ID
            logs = ChatLogs.get_chat_logs_by_user_id(
                filter.user_id,
                skip=filter.skip,
                limit=filter.limit
            )
            count = len(logs)
        else:
            # Get all logs (paginated)
            with get_db() as db:
                query = db.query(ChatLog)
                
                # Apply ordering
                query = query.order_by(ChatLog.created_at.desc())
                
                # Apply pagination
                query = query.offset(filter.skip).limit(filter.limit)
                
                all_logs = query.all()
                logs = [ChatLogModel.model_validate(log) for log in all_logs]
                count = db.query(ChatLog).count()
        
        # Get user names for all logs
        user_ids = [log.user_id for log in logs]
        user_dict = {}
        if user_ids:
            users = Users.get_users_by_user_ids(user_ids)
            user_dict = {user.id: user.name for user in users}
        
        # Convert to response format
        response_logs = [
            ChatLogResponse(
                conversation_id=log.conversation_id,
                user_id=log.user_id,
                user_name=user_dict.get(log.user_id, "Unknown User"),
                model=log.model,
                messages=log.messages,
                response=log.response,
                title=log.title,
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

@router.delete("/admin", response_model=bool)
async def delete_all_chat_logs(
    filter: ChatLogFilter = None,
    user=Depends(get_admin_user)
):
    """Delete all chat logs (admin only)"""
    try:
        # If no filter is provided, delete all logs
        if filter is None:
            filter = ChatLogFilter()
        
        # Delete by conversation ID if specified
        if filter.conversation_id:
            return ChatLogs.delete_chat_log_by_conversation_id(filter.conversation_id)
        # Delete by user ID if specified
        elif filter.user_id:
            with get_db() as db:
                db.query(ChatLog).filter_by(user_id=filter.user_id).delete()
                db.commit()
                return True
        else:
            # Delete all logs
            with get_db() as db:
                db.query(ChatLog).delete()
                db.commit()
                return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chat logs: {str(e)}"
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
        
        # Get user name
        user_name = "Unknown User"
        user_obj = Users.get_user_by_id(log.user_id)
        if user_obj:
            user_name = user_obj.name
        
        return ChatLogResponse(
            conversation_id=log.conversation_id,
            user_id=log.user_id,
            user_name=user_name,
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
