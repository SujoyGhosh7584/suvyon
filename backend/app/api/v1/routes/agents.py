from collections.abc import Iterator
import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_agent_service, get_workspace_service
from app.api.security import get_current_verified_user
from app.agents.runner import run_agent, stream_agent
from app.models.user import User
from app.schemas.agent import (
    AgentCreate,
    AgentEmailSendRequest,
    AgentEmailSendResponse,
    AgentMessageResponse,
    AgentResponse,
    AgentRunRequest,
    AgentRunResponse,
    AgentUpdate,
    PendingEmailDraft,
)
from app.services.agent_service import AgentService
from app.services.workspace_service import WorkspaceService
from app.tools.registry import list_tools
from app.tools.email_tool import send_approved_email

router = APIRouter(prefix="/workspaces/{workspace_id}/agents", tags=["Agents"])


def _get_workspace_or_404(workspace_id, current_user, workspace_service):
    ws = workspace_service.get_workspace(workspace_id=workspace_id, owner_id=current_user.id)
    if ws is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
    return ws


def _get_agent_or_404(agent_id, workspace_id, agent_service):
    agent = agent_service.get_agent(agent_id=agent_id, workspace_id=workspace_id)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found.")
    return agent


def _require_active_agent(agent):
    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This agent is paused. Activate it before running it.",
        )


@router.get("", response_model=list[AgentResponse])
def list_agents(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    return [AgentResponse.model_validate(a) for a in agent_service.list_agents(workspace_id=workspace_id)]


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    workspace_id: UUID,
    request: AgentCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    return AgentResponse.model_validate(agent_service.create_agent(workspace_id=workspace_id, data=request))


@router.get("/tools", response_model=list[str])
def get_available_tools(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    return list_tools()


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    workspace_id: UUID,
    agent_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    return AgentResponse.model_validate(_get_agent_or_404(agent_id, workspace_id, agent_service))


@router.patch("/{agent_id}", response_model=AgentResponse)
def update_agent(
    workspace_id: UUID,
    agent_id: UUID,
    request: AgentUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    agent = _get_agent_or_404(agent_id, workspace_id, agent_service)
    return AgentResponse.model_validate(agent_service.update_agent(agent=agent, data=request))


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(
    workspace_id: UUID,
    agent_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    agent = _get_agent_or_404(agent_id, workspace_id, agent_service)
    agent_service.delete_agent(agent=agent)


@router.get("/{agent_id}/messages", response_model=list[AgentMessageResponse])
def get_agent_messages(
    workspace_id: UUID,
    agent_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    agent = _get_agent_or_404(agent_id, workspace_id, agent_service)
    return [
        AgentMessageResponse.model_validate(message)
        for message in agent_service.get_history(agent_id=agent.id)
    ]


@router.delete("/{agent_id}/messages", status_code=status.HTTP_204_NO_CONTENT)
def clear_agent_messages(
    workspace_id: UUID,
    agent_id: UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
) -> None:
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    agent = _get_agent_or_404(agent_id, workspace_id, agent_service)
    agent_service.clear_history(agent_id=agent.id)


@router.post("/{agent_id}/run", response_model=AgentRunResponse)
def run(
    workspace_id: UUID,
    agent_id: UUID,
    request: AgentRunRequest,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    agent = _get_agent_or_404(agent_id, workspace_id, agent_service)
    _require_active_agent(agent)
    history = agent_service.get_recent_history(agent_id=agent.id)
    pending_email: list[dict] = []
    content = run_agent(
        agent,
        request.content,
        history,
        pending_email=pending_email,
    )
    agent_service.append_exchange(
        agent_id=agent.id,
        user_content=request.content,
        assistant_content=content,
    )
    draft = None
    if pending_email:
        try:
            draft = PendingEmailDraft.model_validate(pending_email[-1])
        except ValueError:
            draft = None
    return AgentRunResponse(content=content, pending_email=draft)


@router.post("/{agent_id}/email/send", response_model=AgentEmailSendResponse)
def send_agent_email(
    workspace_id: UUID,
    agent_id: UUID,
    request: AgentEmailSendRequest,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    agent = _get_agent_or_404(agent_id, workspace_id, agent_service)
    _require_active_agent(agent)
    enabled_tools = {item.strip() for item in (agent.tools or "").split(",")}
    if "send_email" not in enabled_tools:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email sending is not enabled for this agent.",
        )
    message = send_approved_email(
        to=str(request.to),
        subject=request.subject,
        body=request.body,
        regards=request.regards,
    )
    agent_service.append_assistant_message(agent_id=agent.id, content=f"✅ {message}")
    return AgentEmailSendResponse(message=message)


@router.post("/{agent_id}/run/stream")
def run_stream(
    workspace_id: UUID,
    agent_id: UUID,
    request: AgentRunRequest,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    agent = _get_agent_or_404(agent_id, workspace_id, agent_service)
    _require_active_agent(agent)
    history = agent_service.get_recent_history(agent_id=agent.id)

    def event_stream() -> Iterator[str]:
        chunks: list[str] = []
        for chunk in stream_agent(agent, request.content, history):
            chunks.append(chunk)
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        agent_service.append_exchange(
            agent_id=agent.id,
            user_content=request.content,
            assistant_content="".join(chunks),
        )
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
