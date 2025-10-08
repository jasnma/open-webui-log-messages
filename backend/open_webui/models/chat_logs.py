import logging
import json
import time
from typing import Optional

from open_webui.internal.db import Base, get_db
from open_webui.env import SRC_LOG_LEVELS

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, JSON, Index
from sqlalchemy.sql import select

####################
# Chat Log DB Schema
####################

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])


class ChatLog(Base):
    __tablename__ = "chat_log"

    conversation_id = Column(String, primary_key=True)  # For multi-turn conversation tracking
    user_id = Column(String)
    model = Column(String)
    messages = Column(JSON)  # Store the messages exchanged
    response = Column(Text)  # Store the response from the model
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)  # Track when the log was last updated
    
    # Add index for better query performance (conversation_id_idx not needed as it's primary key)
    __table_args__ = (
        Index("chat_log_user_id_idx", "user_id"),
        Index("chat_log_created_at_idx", "created_at"),
        Index("chat_log_updated_at_idx", "updated_at"),  # Added index for updated_at
    )


class ChatLogModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conversation_id: str
    user_id: str
    model: str
    messages: list[dict]
    response: Optional[str] = None
    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch


class ChatLogTable:
    def create_chat_log(
        self, 
        conversation_id: str,
        user_id: str, 
        model: str, 
        messages: list[dict], 
        response: str
    ) -> Optional[ChatLogModel]:
        """Create a new chat log entry"""
        with get_db() as db:
            timestamp = int(time.time())
            chat_log = ChatLogModel(
                **{
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "model": model,
                    "messages": messages,
                    "response": response,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }
            )

            result = ChatLog(**chat_log.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            return ChatLogModel.model_validate(result) if result else None

    def get_chat_logs_by_user_id(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> list[ChatLogModel]:
        """Get chat logs by user ID"""
        with get_db() as db:
            all_logs = (
                db.query(ChatLog)
                .filter_by(user_id=user_id)
                .order_by(ChatLog.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return [ChatLogModel.model_validate(log) for log in all_logs]

    def get_chat_logs_by_conversation_id(
        self, 
        conversation_id: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> list[ChatLogModel]:
        """Get chat logs by conversation ID"""
        with get_db() as db:
            all_logs = (
                db.query(ChatLog)
                .filter_by(conversation_id=conversation_id)
                .order_by(ChatLog.created_at.asc())
                .offset(skip)
                .limit(limit)
            )
            return [ChatLogModel.model_validate(log) for log in all_logs]

    def get_chat_log_by_conversation_id(self, conversation_id: str) -> Optional[ChatLogModel]:
        """Get a specific chat log by conversation ID"""
        try:
            with get_db() as db:
                chat_log = db.get(ChatLog, conversation_id)
                return ChatLogModel.model_validate(chat_log)
        except Exception:
            return None

    def delete_chat_log_by_conversation_id(self, conversation_id: str) -> bool:
        """Delete a chat log by conversation ID"""
        try:
            with get_db() as db:
                db.query(ChatLog).filter_by(conversation_id=conversation_id).delete()
                db.commit()
                return True
        except Exception:
            return False

    def update_chat_log(
        self, 
        conversation_id: str,
        user_id: str,
        model: str,
        messages: list[dict],
        response: str,
    ) -> Optional[ChatLogModel]:
        """Update an existing chat log entry"""
        try:
            with get_db() as db:
                timestamp = int(time.time())
                # Get the existing chat log
                chat_log = db.query(ChatLog).filter_by(conversation_id=conversation_id).first()
                if not chat_log:
                    return None
                
                # Update fields
                chat_log.user_id = user_id
                chat_log.model = model
                chat_log.messages = messages
                chat_log.response = response
                chat_log.updated_at = timestamp  # Update the timestamp
                
                db.commit()
                db.refresh(chat_log)
                return ChatLogModel.model_validate(chat_log)
        except Exception:
            return None


ChatLogs = ChatLogTable()
