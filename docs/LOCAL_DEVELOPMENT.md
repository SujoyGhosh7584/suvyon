# Local development

This guide is for running Suvyon on a Windows PC (PowerShell). A short Linux/macOS section is at the end.

You need:

- Python 3.12
- Node.js 20 or 22 (npm)
- PostgreSQL 15+ with the **pgvector** extension available
- Git

The repo layout:

```text
suvyon/
  backend/     FastAPI API (port 8000)
  frontend/    Vite + React (port 3000)
  docs/
```

---

## 1. Clone and enter the repo

```powershell
cd "F:\AI Projects\suvyon\suvyon"
```

Use your real path if it differs.

---

## 2. Python virtual environment

Create once (from the **repo root**):

```powershell
python -m venv .venv
```

**Activate** (you must do this in every new terminal before backend work):

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again. The prompt should show `(.venv)`.

**Deactivate** when you are done:

```powershell
deactivate
```

Install backend packages (venv must be active):

```powershell
cd backend
pip install -r requirements.txt
cd ..
```

---

## 3. PostgreSQL

Create a database, for example `suvyon`. Enable pgvector in that database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Note the connection URL:

```text
postgresql://USER:PASSWORD@127.0.0.1:5432/suvyon
```

If the password contains `@`, `#`, or `%`, URL-encode it.

---

## 4. Backend environment file

```powershell
copy backend\.env.example backend\.env
```

Edit `backend\.env`. At minimum set:

| Variable | Local value |
|----------|-------------|
| `SECRET_KEY` | Long random string (not the example placeholder) |
| `DATABASE_URL` | Your local Postgres URL |
| `BACKEND_CORS_ORIGINS` | `http://localhost:3000,https://localhost:3000` |
| `APP_ENV` | `development` |
| `GROQ_API_KEY` | From [console.groq.com](https://console.groq.com) (chat) |
| `GEMINI_API_KEY` | From [Google AI Studio](https://aistudio.google.com) (RAG embeddings) |
| `SMTP_*` | Required for **register OTP** and **forgot password**. Same Gmail App Password as agent email. |

Optional: `OPENROUTER_API_KEY`, Tavily/Brave/Serper for search.

Never commit `backend/.env`.

Generate a secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## 5. Database migrations

Venv active, from **`backend`**:

```powershell
cd backend
alembic upgrade head
```

This creates tables (users, workspaces, conversations, document chunks, OTP codes, and so on). After pulling OTP work, always run `alembic upgrade head` again so `otp_codes` exists. Existing users are marked verified so they are not locked out.

---

## 6. Start the API

Venv active, from **`backend`**:

```powershell
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Check:

- http://127.0.0.1:8000/ → `status: running`
- http://127.0.0.1:8000/api/v1/health → `status: healthy`
- http://127.0.0.1:8000/docs → Swagger UI

Leave this terminal open.

---

## 7. Frontend environment and install

New terminal (venv is **not** required for Node):

```powershell
cd frontend
copy .env.example .env
npm install
```

`frontend/.env` should contain:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

No trailing slash. Vite reads this only at **dev server start** and **production build**. After you change it, restart `npm run dev`.

---

## 8. Start the UI

```powershell
cd frontend
npm run dev
```

Open **http://localhost:3000**. Vite proxies `/api` to port 8000 as well; the app still uses `VITE_API_BASE_URL` for Axios.

Register a user, create a workspace, send a chat.

---

## 9. Typical daily workflow

**Terminal A — API**

```powershell
cd "F:\AI Projects\suvyon\suvyon"
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal B — UI**

```powershell
cd "F:\AI Projects\suvyon\suvyon\frontend"
npm run dev
```

---

## 10. Tests (optional)

Venv active:

```powershell
cd backend
python -m pytest -q
```

---

## Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
cd backend
pip install -r requirements.txt
cp .env.example .env
# edit .env
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

---

## What not to mix up

| Local | Production |
|-------|------------|
| `http://127.0.0.1:8000/api/v1` | `https://suvyonbackend.onrender.com/api/v1` |
| `http://localhost:3000` | `https://suvyon-ten.vercel.app` |
| Local Postgres | Supabase `DATABASE_URL` on Render |

Pointing the local UI at the Render API (or the Vercel app at localhost) without matching CORS will fail. See [ENVIRONMENT.md](ENVIRONMENT.md) and [DEPLOYMENT.md](DEPLOYMENT.md).
