from typing import Literal
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema


class GitHubRepositoryOption(BaseSchema):
    installation_id: UUID
    github_repo_id: int
    full_name: str
    default_branch: str
    is_private: bool


class GitHubProjectConnect(BaseSchema):
    installation_id: UUID
    github_repo_id: int


class GitHubProjectResponse(BaseSchema):
    id: UUID
    full_name: str
    default_branch: str
    is_private: bool


class RepositoryQuestion(BaseSchema):
    question: str = Field(..., min_length=2, max_length=4000)


class RepositoryDocumentationRequest(BaseSchema):
    instructions: str = Field(default="Create comprehensive project documentation.", max_length=4000)


class RepositoryAnswer(BaseSchema):
    content: str
    files: list[str]


class ChangeProposalRequest(BaseSchema):
    instruction: str = Field(..., min_length=5, max_length=4000)


class ProposedChange(BaseSchema):
    path: str
    content: str
    reason: str = ""


class ChangeProposalResponse(BaseSchema):
    id: UUID
    instruction: str
    title: str
    description: str
    changes: list[ProposedChange]
    status: str
    pull_request_url: str | None


class ApproveProposalRequest(BaseSchema):
    confirmed: Literal[True]

