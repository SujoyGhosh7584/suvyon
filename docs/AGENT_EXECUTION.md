# Agent execution and model selection

Agents now run multiple tool rounds. The Agents screen on desktop and mobile
shows saved runs, actual tool activity, requested model, provider-reported model,
and a Stop task control. Choose a model per task without editing the saved agent.

## Model policy

An explicit provider/model must be available in the configured catalogue and
allowed by the existing zero-cost policy. Unavailable selections and provider
errors are surfaced; Suvyon never silently substitutes a model for an explicit
selection. Old saved aliases are not rewritten: select a current listed model.

Auto may fall back between available providers on the first model request. Once
an agent has a response it keeps that routing selection for subsequent turns.
`openrouter/free` and `*-latest` are routing/version aliases controlled by their
providers; choosing one does not pin a specific underlying model. Response
metadata is used for model labels when available; otherwise the requested ID is
reported. A model's self-description in answer text is not identity metadata.

## Execution limits and persistence

- At most eight model turns and twelve tool calls per task.
- Two-minute execution budget, checked between requests. An in-flight network
  request may take longer to return; Stop prevents subsequent model/tool calls.
- Successful identical calls are not repeated. Failed identical calls get at
  most two actual attempts; the model can correct arguments or try another tool.
- Tools are checked against the agent's allowlist and schema before execution.
- Each activity event is committed to `agent_runs.events`. Tool text is capped
  at 16,000 characters per result. Only one active saved run per agent is allowed.
- Email drafts end in `awaiting_approval`. Delivery still requires the editable
  approval card. A successful send clears the pending saved draft.
- Runs use FastAPI background tasks, not a durable external queue. They survive
  browser navigation while the API process remains alive. Expired active records
  become interrupted when queried; server restarts do not automatically replay
  tools. Saved results remain inspectable and users can start another task.
- Runs have completed, failed, limited, cancelled, interrupted, or awaiting
  approval outcomes. A completed model answer is not independent factual verification.

The legacy synchronous and streaming routes use the same bounded engine. The
legacy stream delivers the final result after execution; live activity is exposed
through saved runs, which the frontend polls while active.

## Database and testing

Apply `python -m alembic upgrade head` from `backend` before running the updated
API. Revision `e1f2a3b4c5d6` adds the run table and an index preventing concurrent
active runs for one agent. Existing conversations and agent history are retained.

Run `python -m pytest -q` from `backend` and `npm.cmd run build` from `frontend`.
Execution tests stub model/tool calls; database tests use isolated SQLite sessions.

Suggested manual test: enable web_search, read_page and calculator, then ask the
agent to compare three hosting options and calculate costs for a specified usage.
Inspect the actual activity, source URLs and model labels. Test Stop mid-run and
reload the page to inspect saved progress.
