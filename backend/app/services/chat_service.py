from collections.abc import Iterator
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.ai.providers.base import LLMMessage
from app.ai.router import route_chat, route_stream
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.rag.retriever import build_rag_prompt, retrieve_context
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.conversation import ConversationCreate, ConversationUpdate


class ChatService:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        session: Session | None = None,
    ) -> None:
        self._conversations = conversation_repository
        self._messages = message_repository
        self._session = session

    # ------------------------------------------------------------------
    # Conversations
    # ------------------------------------------------------------------

    def list_conversations(self, *, workspace_id: UUID) -> list[Conversation]:
        return self._conversations.get_by_workspace(workspace_id)

    def get_conversation(
        self, *, conversation_id: UUID, workspace_id: UUID
    ) -> Conversation | None:
        return self._conversations.get_by_id_and_workspace(conversation_id, workspace_id)

    def create_conversation(
        self, *, workspace_id: UUID, data: ConversationCreate
    ) -> Conversation:
        conversation = Conversation(
            title=data.title,
            workspace_id=workspace_id,
            provider=data.provider,
            model=data.model,
            system_prompt=data.system_prompt,
        )
        try:
            self._conversations.create(conversation)
            self._conversations.commit()
            self._conversations.refresh(conversation)
            return conversation
        except SQLAlchemyError:
            self._conversations.rollback()
            raise

    def update_conversation(
        self, *, conversation: Conversation, data: ConversationUpdate
    ) -> Conversation:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(conversation, field, value)
        try:
            self._conversations.commit()
            return conversation
        except SQLAlchemyError:
            self._conversations.rollback()
            raise

    def delete_conversation(self, *, conversation: Conversation) -> None:
        try:
            self._conversations.delete(conversation)
            self._conversations.commit()
        except SQLAlchemyError:
            self._conversations.rollback()
            raise

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    def get_messages(self, *, conversation_id: UUID) -> list[Message]:
        return self._messages.get_by_conversation(conversation_id)

    def _build_llm_history(
        self, conversation: Conversation, new_content: str
    ) -> list[LLMMessage]:
        messages: list[LLMMessage] = []

        if conversation.system_prompt:
            messages.append(LLMMessage(role="system", content=conversation.system_prompt))

        for msg in self._messages.get_by_conversation(conversation.id):
            messages.append(LLMMessage(role=msg.role if isinstance(msg.role, str) else msg.role.value, content=msg.content))

        messages.append(LLMMessage(role="user", content=new_content))
        return messages

    def send_message(
        self,
        *,
        conversation: Conversation,
        content: str,
        knowledge_base_id: UUID | None = None,
    ) -> Message:
        """Persist user message, optionally retrieve RAG context, call LLM, persist reply."""
        user_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER.value,
            content=content,
        )
        try:
            self._messages.create(user_msg)
            self._messages.commit()
        except SQLAlchemyError:
            self._messages.rollback()
            raise

        # Build LLM message history
        llm_messages: list[LLMMessage] = []
        if conversation.system_prompt:
            llm_messages.append(LLMMessage(role="system", content=conversation.system_prompt))
        for msg in self._messages.get_by_conversation(conversation.id):
            llm_messages.append(LLMMessage(role=msg.role if isinstance(msg.role, str) else msg.role.value, content=msg.content))

        # RAG: replace last user message with context-enriched prompt
        if knowledge_base_id and self._session:
            context = retrieve_context(self._session, knowledge_base_id, content)
            if context:
                rag_content = build_rag_prompt(context, content)
                llm_messages[-1] = LLMMessage(role="user", content=rag_content)

        response = route_chat(
            llm_messages,
            provider_name=conversation.provider,
            model_id=conversation.model,
        )

        assistant_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content=response.content,
            provider=response.provider,
            model=response.model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
        )
        try:
            self._messages.create(assistant_msg)
            self._messages.commit()
            return assistant_msg
        except SQLAlchemyError:
            self._messages.rollback()
            raise

    def stream_message(
        self, *, conversation: Conversation, content: str
    ) -> Iterator[str]:
        """
        Persist user message, stream LLM tokens, then persist the
        full assistant reply once streaming is complete.
        """
        user_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER.value,
            content=content,
        )
        try:
            self._messages.create(user_msg)
            self._messages.commit()
        except SQLAlchemyError:
            self._messages.rollback()
            raise

        llm_messages: list[LLMMessage] = []
        if conversation.system_prompt:
            llm_messages.append(
                LLMMessage(role="system", content=conversation.system_prompt)
            )
        for msg in self._messages.get_by_conversation(conversation.id):
            llm_messages.append(LLMMessage(role=msg.role if isinstance(msg.role, str) else msg.role.value, content=msg.content))

        full_content = ""
        for chunk in route_stream(
            llm_messages,
            provider_name=conversation.provider,
            model_id=conversation.model,
        ):
            full_content += chunk
            yield chunk

        # Persist the complete assistant reply
        assistant_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content=full_content,
            provider=conversation.provider,
            model=conversation.model,
        )
        try:
            self._messages.create(assistant_msg)
            self._messages.commit()
        except SQLAlchemyError:
            self._messages.rollback()
            raise
