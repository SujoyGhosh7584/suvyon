# Parallel Universe Chat

Open an existing chat and choose **Parallel universes** (desktop or mobile).

- **Branch & explore:** name an alternative and choose a message to branch from,
  or keep the full history. The new conversation has independent message IDs,
  the saved model settings, and a link to its source. Ask a new question to
  explore that direction. Branching does not call a model.
- **Compare & merge:** choose two to four conversations from the workspace,
  preview their latest answers, and describe what the synthesis should optimize
  for. Suvyon uses the currently selected model to create a new chat containing
  the synthesis and collapsible snapshots of its sources. Original chats remain
  available.

Branches copy text, not attached files or private knowledge bases. Reattach files
in the new chat when needed. Shared workspace knowledge remains available through
the normal knowledge picker. Deleting a source chat keeps its branches and clears
their source link.

Merges compare proposals; they do not independently verify claims or run tools.
Empty sources, duplicate selections, sources outside the workspace, and source
transcripts exceeding 60,000 characters are rejected before model generation.
Model or database failures do not leave a partially created merge.

## Setup

Apply the database migration before running the updated API:

```powershell
cd backend
python -m alembic upgrade head
```

Then restart the API and rebuild/restart the frontend. No new API key or service
is required; merges use the existing model router and its zero-cost restrictions.

## Validation

```powershell
python -m pytest tests/test_conversation_universes.py tests/test_chat_knowledge_scope.py -q
```

The tests use an isolated SQLite database and stub model responses. They cover
snapshot independence, branch ordering, rollback, source deletion, workspace
authorization, merge provenance, model selection, and invalid/oversized input.
