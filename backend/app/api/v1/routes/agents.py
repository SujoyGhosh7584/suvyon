from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_agent_service, get_workspace_service
from app.api.security import get_current_active_user
from app.agents.runner import run_agent, stream_agent
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentResponse, AgentRunRequest, AgentRunResponse, AgentUpdate
from app.services.agent_service import AgentService
from app.services.workspace_service import WorkspaceService
from app.tools.registry import list_tools

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


@router.get("", response_model=list[AgentResponse])
def list_agents(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    return [AgentResponse.model_validate(a) for a in agent_service.list_agents(workspace_id=workspace_id)]


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    workspace_id: UUID,
    request: AgentCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    return AgentResponse.model_validate(agent_service.create_agent(workspace_id=workspace_id, data=request))


@router.get("/tools", response_model=list[str])
def get_available_tools(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    return list_tools()


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    workspace_id: UUID,
    agent_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
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
    current_user: Annotated[User, Depends(get_current_active_user)],
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
    current_user: Annotated[User, Depends(get_current_active_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    agent = _get_agent_or_404(agent_id, workspace_id, agent_service)
    agent_service.delete_agent(agent=agent)


@router.post("/{agent_id}/run", response_model=AgentRunResponse)
def run(
    workspace_id: UUID,
    agent_id: UUID,
    request: AgentRunRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    agent = _get_agent_or_404(agent_id, workspace_id, agent_service)
    content = run_agent(agent, request.content, request.history)
    return AgentRunResponse(content=content)


@router.post("/{agent_id}/run/stream")
def run_stream(
    workspace_id: UUID,
    agent_id: UUID,
    request: AgentRunRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    workspace_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    _get_workspace_or_404(workspace_id, current_user, workspace_service)
    agent = _get_agent_or_404(agent_id, workspace_id, agent_service)

    def event_stream() -> Iterator[str]:
        for chunk in stream_agent(agent, request.content, request.history):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
