from collections.abc import Iterator
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.ai.providers.base import LLMMessage
from app.ai.router import route_chat, route_stream
from app.models.conversation import Conversation
from app.models.knowledge_base import KnowledgeBase
from app.models.message import Message, MessageRole
from app.rag.retriever import build_rag_prompt, retrieve_context_with_sources
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.tools.web_search import web_search


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
        return self._conversations.get_by_id_and_workspace(
            conversation_id, workspace_id
        )

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

    def _auto_generate_title(self, content: str) -> str:
        cleaned = content.strip().replace("\n", " ")
        words = cleaned.split()
        if not words:
            return "New conversation"
        title = " ".join(words[:6])
        title = title.strip(".,!?:;\"'").capitalize()
        return title[:50] if title else "New conversation"

    def _classify_request(
        self,
        content: str,
        knowledge_bases: list[KnowledgeBase] | None = None,
    ) -> str:
        text = content.lower()
        web_keywords = (
            "latest",
            "news",
            "today",
            "current",
            "recent",
            "update",
            "price",
            "rate",
            "stock",
            "weather",
            "trend",
            "what happened",
            "breaking",
            "release",
            "forecast",
            "upcoming",
            "compare",
            "vs",
            "who is",
            "who was",
            "who won",
            "where is",
            "where was",
            "when did",
            "how much",
            "cost",
            "launch",
            "search web",
            "google",
            "online",
            "http",
            "https",
            "www",
            "internet",
            "live",
        )
        rag_keywords = (
            "document",
            "documents",
            "file",
            "pdf",
            "uploaded",
            "upload",
            "knowledge base",
            "resume",
            "cv",
            "according to",
            "from the docs",
            "from the document",
            "my doc",
            "my docs",
            "in the doc",
            "in the document",
        )

        # Prefer live/web intents over RAG when both could match
        # (e.g. "tell me about the gold rate today").
        if any(keyword in text for keyword in web_keywords):
            return "web"
        if any(keyword in text for keyword in rag_keywords):
            return "rag"
        if knowledge_bases and any(
            hint in text
            for hint in (
                "experience",
                "work ex",
                "work history",
                "skills",
                "education",
                "summarize",
            )
        ):
            return "rag"

        # Only route to RAG when retrieved chunks are actually similar.
        if knowledge_bases and self._session:
            for kb in knowledge_bases:
                try:
                    chunks, _ = retrieve_context_with_sources(
                        self._session, kb.id, content, top_k=3
                    )
                    if chunks:
                        return "rag"
                except Exception:
                    pass

        return "chat"

    def _get_active_knowledge_bases(self, workspace_id: UUID) -> list[KnowledgeBase]:
        if not self._session:
            return []
        return list(
            self._session.query(KnowledgeBase)
            .filter(
                KnowledgeBase.workspace_id == workspace_id,
                KnowledgeBase.is_active.is_(True),
            )
            .all()
        )

    def _build_rag_context(
        self,
        workspace_id: UUID,
        query: str,
        knowledge_base_id: UUID | None = None,
    ) -> tuple[str, list[str]]:
        if not self._session:
            return "", []

        knowledge_bases = self._get_active_knowledge_bases(workspace_id)
        if knowledge_base_id:
            knowledge_bases = [
                kb for kb in knowledge_bases if str(kb.id) == str(knowledge_base_id)
            ]

        if not knowledge_bases:
            return "", []

        context_parts: list[str] = []
        sources: list[str] = []
        for kb in knowledge_bases:
            chunks, kb_sources = retrieve_context_with_sources(
                self._session,
                kb.id,
                query,
                top_k=12,
            )
            if chunks:
                context_parts.append(
                    f"[Knowledge Base: {kb.name}]\n" + "\n\n".join(chunks)
                )
                sources.extend([f"{source}" for source in kb_sources])

        return "\n\n".join(context_parts), sources

    def _build_contextual_messages(
        self,
        *,
        conversation: Conversation,
        content: str,
        mode: str,
        knowledge_base_id: UUID | None = None,
    ) -> tuple[list[LLMMessage], list[str]]:
        llm_messages: list[LLMMessage] = []

        if conversation.system_prompt:
            llm_messages.append(
                LLMMessage(role="system", content=conversation.system_prompt)
            )

        history = self._messages.get_by_conversation(conversation.id)
        # The current user turn is persisted before generation. Do not send it
        # twice — Gemini rejects / blanks on consecutive user roles.
        if (
            history
            and str(getattr(history[-1].role, "value", history[-1].role)) == "user"
            and history[-1].content == content
        ):
            history = history[:-1]

        for msg in history:
            role = msg.role if isinstance(msg.role, str) else msg.role.value
            if not (msg.content or "").strip():
                continue
            llm_messages.append(LLMMessage(role=role, content=msg.content))

        user_message = LLMMessage(role="user", content=content)

        if mode == "web":
            search_results = web_search(content, max_results=5)
            user_message = LLMMessage(
                role="user",
                content=(
                    "You have live web search results below. Answer the user's question "
                    "using these results. Extract concrete facts (prices, scores, dates, "
                    "numbers, names) when present. Cite source URLs. Do not say you lack "
                    "access to real-time data when the results contain relevant information. "
                    "Only say results are insufficient if they truly do not answer the question.\n\n"
                    f"Search results:\n{search_results}\n\nQuestion: {content}"
                ),
            )
        elif mode == "rag":
            rag_context, rag_sources = self._build_rag_context(
                conversation.workspace_id,
                content,
                knowledge_base_id=knowledge_base_id,
            )
            if rag_context:
                user_message = LLMMessage(
                    role="user",
                    content=build_rag_prompt(rag_context, content),
                )
                return [*llm_messages, user_message], rag_sources
            return [*llm_messages, user_message], []

        return [*llm_messages, user_message], []

    def _build_provenance_note(
        self,
        mode: str,
        provider: str | None,
        model: str | None,
        sources: list[str] | None = None,
    ) -> str:
        if mode == "rag":
            if sources:
                unique_sources = list(dict.fromkeys(sources))
                joined_sources = ", ".join(unique_sources[:5])
                return f"Source: knowledge base context from {joined_sources}"
            return "Source: knowledge base context was not found"
        if mode == "web":
            return "Source: web search"
        provider_name = provider or "auto"
        model_name = model or "default model"
        return f"Source: direct LLM response via {provider_name} / {model_name}"

    def send_message(
        self,
        *,
        conversation: Conversation,
        content: str,
        knowledge_base_id: UUID | None = None,
        mode: str | None = None,
    ) -> Message:
        """Persist user message and route it to chat, web search, or RAG automatically."""
        # Auto-update conversation title if default
        if conversation.title in ("New conversation", "New chat"):
            conversation.title = self._auto_generate_title(content)
            try:
                self._conversations.commit()
            except Exception:
                self._conversations.rollback()

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


        knowledge_bases = self._get_active_knowledge_bases(conversation.workspace_id)
        selected_mode = (
            mode or self._classify_request(content, knowledge_bases)
        ).lower()
        llm_messages, rag_sources = self._build_contextual_messages(
            conversation=conversation,
            content=content,
            mode=selected_mode,
            knowledge_base_id=knowledge_base_id,
        )
        if selected_mode == "rag" and not rag_sources:
            selected_mode = "chat"

        response = route_chat(
            llm_messages,
            provider_name=conversation.provider,
            model_id=conversation.model,
        )

        provenance_note = self._build_provenance_note(
            selected_mode,
            response.provider,
            response.model,
            sources=rag_sources if selected_mode == "rag" else None,
        )
        assistant_content = response.content
        if provenance_note:
            assistant_content = f"{assistant_content}\n\n---\n{provenance_note}"

        assistant_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content=assistant_content,
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
        self,
        *,
        conversation: Conversation,
        content: str,
        mode: str | None = None,
        knowledge_base_id: UUID | None = None,
    ) -> Iterator[str]:
        """
        Persist user message, stream LLM tokens, then persist the
        full assistant reply once streaming is complete.
        """
        if conversation.title in ("New conversation", "New chat"):
            conversation.title = self._auto_generate_title(content)
            try:
                self._conversations.commit()
            except Exception:
                self._conversations.rollback()

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


        knowledge_bases = self._get_active_knowledge_bases(conversation.workspace_id)
        selected_mode = (
            mode or self._classify_request(content, knowledge_bases)
        ).lower()
        llm_messages, rag_sources = self._build_contextual_messages(
            conversation=conversation,
            content=content,
            mode=selected_mode,
            knowledge_base_id=knowledge_base_id,
        )
        if selected_mode == "rag" and not rag_sources:
            selected_mode = "chat"

        full_content = ""
        for chunk in route_stream(
            llm_messages,
            provider_name=conversation.provider,
            model_id=conversation.model,
        ):
            full_content += chunk
            yield chunk

        provenance_note = self._build_provenance_note(
            selected_mode,
            conversation.provider,
            conversation.model,
            sources=rag_sources if selected_mode == "rag" else None,
        )
        if provenance_note:
            full_content = f"{full_content}\n\n---\n{provenance_note}"

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
