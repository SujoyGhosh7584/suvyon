# Suvyon

Suvyon is a **multi-LLM AI workspace**: one product for chat, retrieval-augmented answers over your files, web-grounded research, and tool-using agents. It is designed to ship on **free-tier** infrastructure (GitHub, Vercel, Render, Supabase) without locking you to a single model vendor.

The UI is a React workspace (themes, conversations, knowledge, agents, settings). The API is FastAPI: JWT auth, workspaces, conversations, RAG (PostgreSQL + pgvector), and a tool loop (search, Wikipedia, image URLs, email, and more).

---

## Live deployment

These URLs are the current production hosts for this repository. If you fork or recreate services, update this table and [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

| Layer | Host | URL |
|-------|------|-----|
| Web app | Vercel | [https://suvyon-ten.vercel.app](https://suvyon-ten.vercel.app) |
| API | Render | [https://suvyonbackend.onrender.com](https://suvyonbackend.onrender.com) |
| Health check | Render | [https://suvyonbackend.onrender.com/api/v1/health](https://suvyonbackend.onrender.com/api/v1/health) |
| OpenAPI | Render | [https://suvyonbackend.onrender.com/docs](https://suvyonbackend.onrender.com/docs) |
| Source | GitHub | [https://github.com/SujoyGhosh7584/suvyon](https://github.com/SujoyGhosh7584/suvyon) |

Render’s **free** web service sleeps when idle. The first request after sleep can take 30–60 seconds.

---

## What you can do in the product

- **Workspaces** — Isolated places for chats, agents, and knowledge bases.
- **Chat** — Auto mode can call tools (Wikipedia, web search, image generation URLs, knowledge search). You can also pin Chat / RAG / Web-style modes where the UI exposes them.
- **Knowledge (RAG)** — Upload documents, chunk + embed (Gemini embeddings when configured), retrieve with pgvector.
- **Agents** — Saved agent configs with tools (email, research, studio helpers).
- **Models** — Route across Groq, Gemini, and OpenRouter depending on which API keys are set.
- **Accounts** — Register, login, JWT access + refresh tokens (stored in the browser).

Image generation uses public Pollinations URLs (proxied by the API). It does **not** persist generated files on the server. Knowledge **file bodies** on Render live on an ephemeral disk; they do not survive restarts the way the database does.

---

## Architecture (runtime)

```text
  Browser (Vercel or localhost:3000)
           │  HTTPS / Axios  (VITE_API_BASE_URL)
           ▼
  FastAPI  (Render or localhost:8000)
           │
           ├─ PostgreSQL + pgvector  (local or Supabase)
           ├─ Groq / Gemini / OpenRouter
           └─ Optional: Tavily, SMTP, Pollinations (images)
```

CORS must list the **frontend origin** (Vercel or `http://localhost:3000`), not the API URL. The frontend API base URL is baked in at **Vite build time**, so changing Vercel env vars requires a **redeploy**.

---

## Repository layout

```text
suvyon/
├── backend/                 FastAPI application
│   ├── app/                 Routes, services, RAG, tools, agents
│   ├── alembic/             Database migrations
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── render.yaml
├── frontend/                Vite + React + TypeScript
│   ├── src/
│   ├── .env.example
│   └── vercel.json
├── docs/
│   ├── LOCAL_DEVELOPMENT.md
│   ├── ENVIRONMENT.md
│   ├── DEPLOYMENT.md
│   ├── TROUBLESHOOTING.md
│   └── architecture/        Product and system design
└── README.md                This file
```

---

## Tech stack

| Area | Choice |
|------|--------|
| UI | React 18, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query |
| API | Python 3.12, FastAPI, Uvicorn, Pydantic Settings |
| Data | PostgreSQL, SQLAlchemy 2, Alembic, pgvector |
| Auth | JWT (python-jose), bcrypt |
| Hosting | Vercel (static UI), Render (API), Supabase (managed Postgres) |

Longer rationale: [docs/architecture/04_TECH_STACK.md](docs/architecture/04_TECH_STACK.md).

---

## Prerequisites (local)

- **Python 3.12**
- **Node.js 20 or 22** and npm
- **PostgreSQL 15+** with extension `vector` (`CREATE EXTENSION IF NOT EXISTS vector;`)
- **Git**
- At least one LLM key for chat (**Groq** is the usual free starting point)
- **Gemini** key if you want knowledge embeddings

---

## Run locally (Windows / PowerShell)

Do this from the **repository root** (the folder that contains `backend` and `frontend`).

### 1. Virtual environment

Create once:

```powershell
python -m venv .venv
```

**Activate in every terminal** that runs Python:

```powershell
.\.venv\Scripts\Activate.ps1
```

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

You should see `(.venv)` in the prompt. Leave the venv with `deactivate`.

Linux/macOS: `python3 -m venv .venv` then `source .venv/bin/activate`.

### 2. Backend packages and env

```powershell
cd backend
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env` (never commit this file):

| Variable | What to put |
|----------|-------------|
| `SECRET_KEY` | Long random string (`python -c "import secrets; print(secrets.token_urlsafe(48))"`) |
| `DATABASE_URL` | `postgresql://USER:PASSWORD@127.0.0.1:5432/suvyon` |
| `BACKEND_CORS_ORIGINS` | `http://localhost:3000,https://localhost:3000` |
| `GROQ_API_KEY` | From [Groq Console](https://console.groq.com) |
| `GEMINI_API_KEY` | From [Google AI Studio](https://aistudio.google.com) (needed for RAG) |
| `APP_ENV` | `development` |

Full list and production differences: [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md).

### 3. Migrations then API

Still in `backend`, venv active:

```powershell
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Confirm:

- http://127.0.0.1:8000/ → `"status": "running"`
- http://127.0.0.1:8000/api/v1/health → `"status": "healthy"`

Keep this terminal running.

### 4. Frontend

**New terminal** (Node does not need the venv):

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

`frontend/.env` must contain:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

No trailing slash. Restart `npm run dev` after changing it.

Open **http://localhost:3000**, register, create a workspace, send a message.

Step-by-step with troubleshooting: [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md).

### Daily two-terminal habit

**A — API**

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**B — UI**

```powershell
cd frontend
npm run dev
```

---

## Tests

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m pytest -q
```

---

## Production environment (what is set where)

Do **not** copy `.env` to GitHub. Set secrets in the host dashboards.

**Vercel (frontend)** — must be present **before** `npm run build`:

| Name | Production value |
|------|------------------|
| `VITE_API_BASE_URL` | `https://suvyonbackend.onrender.com/api/v1` |

**Render (backend)** — typical production set:

| Name | Production value |
|------|------------------|
| `APP_ENV` | `production` |
| `SECRET_KEY` | Dedicated production secret |
| `DATABASE_URL` | Supabase connection URI |
| `BACKEND_CORS_ORIGINS` | `https://suvyon-ten.vercel.app` |
| `GROQ_API_KEY` | Groq |
| `GEMINI_API_KEY` | Gemini |
| `OPENROUTER_API_KEY` | Optional |

**Why you must update these when URLs change**

- **CORS** is an exact browser origin. A new Vercel domain without a Render env update = login/network failures.
- **`VITE_*` is compiled into JS.** Changing Vercel env without Redeploy leaves the old API host in the bundle.
- **`DATABASE_URL`** on Render must be Supabase, not your laptop Postgres.
- **`SECRET_KEY`** rotation logs everyone out.

How to recreate the stack: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Documentation index

| Document | Contents |
|----------|----------|
| [docs/README.md](docs/README.md) | Short index of operational docs |
| [docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md) | Local install in full |
| [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) | Every variable, local vs production |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Supabase, Render, Vercel, live URLs |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | CORS parse errors, `frontend/src/lib` gitignore, sleep, pgvector |
| [docs/architecture/00_PROJECT_CHARTER.md](docs/architecture/00_PROJECT_CHARTER.md) | Charter and principles |
| [docs/architecture/02_PRODUCT_REQUIREMENTS.md](docs/architecture/02_PRODUCT_REQUIREMENTS.md) | Product requirements |
| [docs/architecture/03_SYSTEM_ARCHITECTURE.md](docs/architecture/03_SYSTEM_ARCHITECTURE.md) | System architecture |
| [docs/architecture/09_API_SPECIFICATION.md](docs/architecture/09_API_SPECIFICATION.md) | API specification |

---

## License and status

Personal / portfolio project. Free-tier limits (Render sleep, Supabase quotas, LLM rate limits) apply in production.
