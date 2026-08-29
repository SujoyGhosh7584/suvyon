from collections.abc import Iterator
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.agents.runner import _call_tool, _normalize_arguments
from app.ai.providers.base import LLMMessage
from app.ai.router import route_chat, route_stream
from app.models.conversation import Conversation
from app.models.knowledge_base import KnowledgeBase
from app.models.message import Message, MessageRole
from app.rag.retriever import build_rag_prompt, retrieve_context_with_sources
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.tools.registry import get_tool_schemas
from app.tools.research import wikipedia
from app.tools.web_search import web_search

AUTO_RAG_MAX_DISTANCE = 0.42
_MAX_TOOL_ROUNDS = 3

_TOOL_INSTRUCTIONS = (
    "\n\nYou can call tools. Decide from the meaning of the question.\n"
    "- wikipedia: people, places, public offices, encyclopedic facts that can change.\n"
    "- web_search: news, prices, scores, or to confirm a wikipedia result.\n"
    "- search_knowledge: only when the user is asking about THEIR uploaded files.\n"
    "- generate_image: when the user wants a picture, illustration, or logo. Keep the markdown image.\n"
    "Do not search the knowledge base for coding, writing, or general how-tos.\n"
    "Never answer who currently holds a public office from memory — look it up.\n"
    "If the user says a previous answer was wrong, look the fact up with tools.\n"
    "Prefer Wikipedia over random blogs. Never invent URLs. Markdown, never HTML."
)

_SYNTHESIZE = (
    "Using the tool results above, answer the user now. "
    "Cite only URLs that appeared in the tool output. "
    "Prefer the Wikipedia result for office-holders. "
    "Keep any markdown images from generate_image. "
    "Do not call tools again."
)

_SEARCH_KNOWLEDGE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_knowledge",
        "description": (
            "Search the user's uploaded documents in this workspace. "
            "Use only when the question is about those files."
        ),
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
}


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
        max_distance: float | None = None,
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
                max_distance=max_distance,
            )
            if chunks:
                context_parts.append(
                    f"[Knowledge Base: {kb.name}]\n" + "\n\n".join(chunks)
                )
                sources.extend([f"{source}" for source in kb_sources])

        return "\n\n".join(context_parts), sources

    def _auto_tool_schemas(self, workspace_id: UUID) -> list[dict]:
        schemas = get_tool_schemas(["wikipedia", "web_search", "generate_image"])
        if self._get_active_knowledge_bases(workspace_id):
            schemas.append(_SEARCH_KNOWLEDGE_SCHEMA)
        return schemas

    def _run_chat_tool(
        self,
        name: str,
        arguments,
        workspace_id: UUID,
        user_content: str = "",
    ) -> tuple[str, list[str]]:
        if name == "search_knowledge":
            args = _normalize_arguments(arguments)
            query = str(args.get("query") or args.get("q") or "").strip()
            if not query:
                return "search_knowledge requires a query.", []
            context, sources = self._build_rag_context(
                workspace_id,
                query,
                max_distance=AUTO_RAG_MAX_DISTANCE,
            )
            if not context:
                return (
                    "No relevant documents matched. Answer from general knowledge; "
                    "do not say the files cover this topic.",
                    [],
                )
            return context, sources
        try:
            return _call_tool(name, arguments, user_content=user_content), []
        except Exception as exc:
            return f"Tool error: {exc}", []

    def _collect_tool_sources(self, name: str, result: str, rag_sources: list[str]) -> list[str]:
        if name == "search_knowledge":
            return rag_sources
        if name in {
            "generate_image",
            "generate_storyboard",
            "generate_speech",
            "qr_code",
            "draw_diagram",
            "brand_kit",
        }:
            return []
        return self._source_links_from_search(result)

    def _mode_from_tools(self, used: list[str], extra_sources: list[str]) -> str:
        if "search_knowledge" in used and extra_sources:
            return "rag"
        if any(name in used for name in ("web_search", "wikipedia")):
            return "web"
        return "chat"

    def _answer_with_tools(
        self,
        *,
        conversation: Conversation,
        content: str,
    ) -> tuple[str, str, list[str], str | None, str | None]:
        messages, _ = self._build_contextual_messages(
            conversation=conversation,
            content=content,
            mode="chat",
        )
        messages[0].content = messages[0].content.rstrip() + _TOOL_INSTRUCTIONS
        schemas = self._auto_tool_schemas(conversation.workspace_id)
        used: list[str] = []
        extra_sources: list[str] = []
        last_provider = conversation.provider
        last_model = conversation.model

        for _ in range(_MAX_TOOL_ROUNDS):
            response = route_chat(
                messages,
                provider_name=conversation.provider,
                model_id=conversation.model,
                tools=schemas or None,
            )
            last_provider, last_model = response.provider, response.model
            if response.tool_calls:
                messages.append(
                    LLMMessage(role="assistant", content="", tool_calls=response.tool_calls)
                )
                for call in response.tool_calls:
                    name = call.get("name") or ""
                    used.append(name)
                    result, rag_sources = self._run_chat_tool(
                        name,
                        call.get("arguments"),
                        conversation.workspace_id,
                        user_content=content,
                    )
                    extra_sources.extend(self._collect_tool_sources(name, result, rag_sources))
                    messages.append(
                        LLMMessage(
                            role="tool",
                            content=str(result),
                            tool_call_id=call.get("id"),
                            name=name,
                        )
                    )
                messages.append(LLMMessage(role="user", content=_SYNTHESIZE))
                final = route_chat(
                    messages,
                    provider_name=response.provider,
                    model_id=response.model,
                )
                mode = self._mode_from_tools(used, extra_sources)
                return (
                    (final.content or "").strip() or "I could not produce an answer.",
                    mode,
                    list(dict.fromkeys(extra_sources)),
                    final.provider,
                    final.model,
                )
            if (response.content or "").strip():
                return (
                    response.content,
                    "chat",
                    [],
                    response.provider,
                    response.model,
                )
            break

        return "I could not produce an answer. Please try again.", "chat", [], last_provider, last_model

    def _stream_with_tools(
        self,
        *,
        conversation: Conversation,
        content: str,
    ) -> Iterator[str]:
        messages, _ = self._build_contextual_messages(
            conversation=conversation,
            content=content,
            mode="chat",
        )
        messages[0].content = messages[0].content.rstrip() + _TOOL_INSTRUCTIONS
        schemas = self._auto_tool_schemas(conversation.workspace_id)
        pin_provider = conversation.provider
        pin_model = conversation.model
        used: list[str] = []
        extra_sources: list[str] = []

        if schemas:
            response = route_chat(
                messages,
                provider_name=conversation.provider,
                model_id=conversation.model,
                tools=schemas,
            )
            pin_provider, pin_model = response.provider, response.model
            if response.tool_calls:
                messages.append(
                    LLMMessage(role="assistant", content="", tool_calls=response.tool_calls)
                )
                for call in response.tool_calls:
                    name = call.get("name") or ""
                    used.append(name)
                    result, rag_sources = self._run_chat_tool(
                        name,
                        call.get("arguments"),
                        conversation.workspace_id,
                        user_content=content,
                    )
                    extra_sources.extend(self._collect_tool_sources(name, result, rag_sources))
                    messages.append(
                        LLMMessage(
                            role="tool",
                            content=str(result),
                            tool_call_id=call.get("id"),
                            name=name,
                        )
                    )
                messages.append(LLMMessage(role="user", content=_SYNTHESIZE))
            elif (response.content or "").strip():
                self._auto_stream_state = ("chat", [], response.provider, response.model)
                yield response.content
                return

        full = ""
        for chunk in route_stream(
            messages, provider_name=pin_provider, model_id=pin_model
        ):
            full += chunk
            yield chunk
        mode = self._mode_from_tools(used, extra_sources)
        self._auto_stream_state = (
            mode,
            list(dict.fromkeys(extra_sources)),
            pin_provider,
            pin_model,
        )

    def _build_contextual_messages(
        self,
        *,
        conversation: Conversation,
        content: str,
        mode: str,
        knowledge_base_id: UUID | None = None,
        grounding_strict: bool = True,
        search_query: str | None = None,
    ) -> tuple[list[LLMMessage], list[str]]:
        llm_messages: list[LLMMessage] = []
        llm_messages.append(
            LLMMessage(
                role="system",
                content=(
                    "You are Suvyon. Reply in GitHub-flavored Markdown: headings, lists, "
                    "tables, fenced code blocks with a language tag, and markdown links. "
                    "Never emit HTML tags such as <p>, <div>, or <br>."
                ),
            )
        )

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
            query = (search_query or content).strip()
            wiki = wikipedia(query)
            search_results = web_search(query, max_results=6)
            encyclopedia = ""
            if wiki and not wiki.startswith("Tool error") and not wiki.startswith("No Wikipedia"):
                encyclopedia = f"Preferred encyclopedia source (trust this over random blogs):\n{wiki}\n\n"
            user_message = LLMMessage(
                role="user",
                content=(
                    "Answer ONLY from the sources below. Do not use training memory or earlier "
                    "chat replies if they disagree with these sources. Prefer the encyclopedia "
                    "source when it names a current office-holder. Ignore SEO listicles that "
                    "invent elections, vote counts, or inauguration dates not also in the "
                    "encyclopedia source. Never invent names, dates, or URLs. Cite only URLs "
                    "that appear below, as Markdown links [title](url). If sources conflict, "
                    "say so and quote the encyclopedia. Do not use HTML.\n\n"
                    f"{encyclopedia}"
                    f"Other web results:\n{search_results}\n\n"
                    f"User message: {content}\n"
                    f"Look up: {query}"
                ),
            )
            combined = f"{encyclopedia}{search_results}"
            return [
                llm_messages[0],
                user_message,
            ], self._source_links_from_search(combined)
        elif mode == "rag":
            rag_context, rag_sources = self._build_rag_context(
                conversation.workspace_id,
                content,
                knowledge_base_id=knowledge_base_id,
            )
            if rag_context:
                user_message = LLMMessage(
                    role="user",
                    content=build_rag_prompt(
                        rag_context, content, strict=grounding_strict
                    ),
                )
                return [*llm_messages, user_message], rag_sources
            return [*llm_messages, user_message], []

        return [*llm_messages, user_message], []

    def _source_links_from_search(self, search_results: str) -> list[str]:
        links: list[str] = []
        title = "Source"
        for raw in search_results.splitlines():
            if raw.startswith("Title:"):
                title = raw[6:].strip() or "Source"
            elif raw.startswith("URL:"):
                url = raw[4:].strip()
                if url.startswith("http"):
                    links.append(f"[{title}]({url})")
        return list(dict.fromkeys(links))

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
            if sources:
                return "Sources:\n" + "\n".join(f"- {item}" for item in sources)
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

        user_mode = (mode or "").lower() or None
        if not user_mode:
            assistant_content, selected_mode, extra_sources, used_provider, used_model = (
                self._answer_with_tools(conversation=conversation, content=content)
            )
            provenance_note = self._build_provenance_note(
                selected_mode,
                used_provider,
                used_model,
                sources=extra_sources if selected_mode in {"rag", "web"} else None,
            )
            if provenance_note:
                assistant_content = f"{assistant_content}\n\n---\n{provenance_note}"
            assistant_msg = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT.value,
                content=assistant_content,
                provider=used_provider,
                model=used_model,
            )
            try:
                self._messages.create(assistant_msg)
                self._messages.commit()
                return assistant_msg
            except SQLAlchemyError:
                self._messages.rollback()
                raise

        selected_mode = user_mode
        llm_messages, extra_sources = self._build_contextual_messages(
            conversation=conversation,
            content=content,
            mode=selected_mode,
            knowledge_base_id=knowledge_base_id,
            grounding_strict=user_mode == "rag",
        )
        if selected_mode == "rag" and not extra_sources:
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
            sources=extra_sources if selected_mode in {"rag", "web"} else None,
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

        user_mode = (mode or "").lower() or None
        if not user_mode:
            full_content = ""
            self._auto_stream_state = ("chat", [], conversation.provider, conversation.model)
            for chunk in self._stream_with_tools(conversation=conversation, content=content):
                full_content += chunk
                yield chunk
            selected_mode, extra_sources, used_provider, used_model = self._auto_stream_state
            provenance_note = self._build_provenance_note(
                selected_mode,
                used_provider,
                used_model,
                sources=extra_sources if selected_mode in {"rag", "web"} else None,
            )
            if provenance_note:
                full_content = f"{full_content}\n\n---\n{provenance_note}"
            assistant_msg = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT.value,
                content=full_content,
                provider=used_provider,
                model=used_model,
            )
            try:
                self._messages.create(assistant_msg)
                self._messages.commit()
            except SQLAlchemyError:
                self._messages.rollback()
                raise
            return

        selected_mode = user_mode
        llm_messages, extra_sources = self._build_contextual_messages(
            conversation=conversation,
            content=content,
            mode=selected_mode,
            knowledge_base_id=knowledge_base_id,
            grounding_strict=user_mode == "rag",
        )
        if selected_mode == "rag" and not extra_sources:
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
            sources=extra_sources if selected_mode in {"rag", "web"} else None,
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
