"""Authenticated tenant-aware conversational energy assistant routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.schemas.chatbot import ChatQueryRequest, ChatQueryResponse, ConversationCreateRequest, ConversationResponse
from api.security.chat_auth import get_current_user
from api.services.chatbot_service import answer_message, conversation_response, create_conversation, get_conversation, list_conversations
from database.chatbot_models import AppUser
from database.config import get_db


router = APIRouter(prefix="/api/v1/chat", tags=["chatbot"])


@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create scoped chat conversation",
    description="Creates a conversation bound to an authenticated user's authorized client and portfolio scope.",
)
async def start_conversation(
    payload: ConversationCreateRequest,
    db: Session = Depends(get_db),
    user: AppUser = Depends(get_current_user),
) -> ConversationResponse:
    return conversation_response(create_conversation(db, user, payload))


@router.get(
    "/conversations",
    response_model=list[ConversationResponse],
    summary="List own chat conversations",
    description="Lists only conversations owned by the authenticated user.",
)
async def conversations(db: Session = Depends(get_db), user: AppUser = Depends(get_current_user)) -> list[ConversationResponse]:
    return [conversation_response(item) for item in list_conversations(db, user)]


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    summary="Get own chat conversation",
    description="Returns messages, evidence metadata, and limitations for an owned authorized conversation.",
)
async def conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    user: AppUser = Depends(get_current_user),
) -> ConversationResponse:
    return conversation_response(get_conversation(db, user, conversation_id))


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ChatQueryResponse,
    summary="Ask tenant-scoped energy assistant",
    description="Routes a question to approved read-only tools, optionally narrates verified facts, and records evidence and safety metadata.",
)
async def send_message(
    conversation_id: str,
    payload: ChatQueryRequest,
    db: Session = Depends(get_db),
    user: AppUser = Depends(get_current_user),
) -> ChatQueryResponse:
    return answer_message(db, user, conversation_id, payload)
