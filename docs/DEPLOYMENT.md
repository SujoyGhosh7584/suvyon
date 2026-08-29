# Deployment

Suvyon is split so the UI and API can sit on free tiers:

```text
Browser  →  Vercel (React static site)
                │  HTTPS
                ▼
         Render (FastAPI)
                │
                ▼
         Supabase (PostgreSQL + pgvector)
```

Architecture background: [architecture/11_DEPLOYMENT_ARCHITECTURE.md](architecture/11_DEPLOYMENT_ARCHITECTURE.md).

---

## Live services (this repository)

Update this section if you recreate projects.

| Service | Provider | URL |
|---------|----------|-----|
| Frontend | [Vercel](https://vercel.com) | https://suvyon-ten.vercel.app |
| Backend | [Render](https://render.com) | https://suvyonbackend.onrender.com |
| API health | Render | https://suvyonbackend.onrender.com/api/v1/health |
| API root | Render | https://suvyonbackend.onrender.com/ |
| Git remote | GitHub | https://github.com/SujoyGhosh7584/suvyon |

OpenAPI (when the API is awake): https://suvyonbackend.onrender.com/docs

---

## What you must keep in sync

| If you change… | Also update… | Why |
|----------------|--------------|-----|
| Vercel production domain | Render `BACKEND_CORS_ORIGINS` | Browser Origin must match exactly |
| Render service URL | Vercel `VITE_API_BASE_URL` then **rebuild** | Vite bakes the API URL into JS |
| Supabase password or pooler host | Render `DATABASE_URL` | API cannot start without a valid DB |
| Groq/Gemini keys | Render env | Chat and RAG stop without keys |
| Git default branch | Vercel + Render branch settings | Wrong branch = old or broken build |

Preview deployments on Vercel use **different hostnames**. They will CORS-fail unless you add those origins or only test Production.

---

## 1. GitHub

1. Push the branch you want to host.
2. Confirm `frontend/src/lib/` is in the repo (see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)). A root `.gitignore` entry `lib/` used to hide that folder from Git.
3. Point Render and Vercel at the **same** branch you actually deploy (for example `main` or `Dev_Cursor_29_08_26_Fourth_Deployment`). A Vercel log that says `Branch: main` while your work is on another branch is a misconfiguration.

---

## 2. Supabase (database)

1. Create a free project at https://supabase.com
2. **Database → Extensions** → enable **vector**
3. **Project Settings → Database** → copy the connection **URI** (session pooler port **5432** or transaction pooler **6543**)
4. URL-encode special characters in the password

You do not need `SUPABASE_URL` / `SUPABASE_KEY` for the current app; SQLAlchemy uses `DATABASE_URL` only.

---

## 3. Render (backend)

1. **New → Web Service** → connect https://github.com/SujoyGhosh7584/suvyon
2. Settings:

| Field | Value |
|--------|--------|
| Root Directory | `backend` |
| Runtime | Python 3.12 |
| Instance | Free |
| Build | `pip install -r requirements.txt` |
| Start | `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check | `/api/v1/health` |

3. Environment (see [ENVIRONMENT.md](ENVIRONMENT.md)):

| Key | Production example |
|-----|-------------------|
| `APP_ENV` | `production` |
| `SECRET_KEY` | Generated random string |
| `DATABASE_URL` | Supabase URI |
| `BACKEND_CORS_ORIGINS` | `https://suvyon-ten.vercel.app` |
| `GROQ_API_KEY` | Groq key |
| `GEMINI_API_KEY` | Gemini key |
| `OPENROUTER_API_KEY` | Optional |

Blueprint file in repo: `backend/render.yaml` (you can still configure the service in the dashboard).

4. After deploy, confirm https://suvyonbackend.onrender.com/api/v1/health

**Free tier:** the service **sleeps** after idle time. The first request can take 30–60 seconds.

**Knowledge files:** uploads are stored on the Render disk (`uploads/`). That disk is **ephemeral**. Files disappear on restart/sleep. Chat still works; durable RAG storage is future work.

---

## 4. Vercel (frontend)

1. **Add New → Project** → same GitHub repo
2. **Root Directory:** `frontend`
3. Framework preset: **Vite** if listed, otherwise **Other** with:

| Field | Value |
|--------|--------|
| Install | `npm install` |
| Build | `npm run build` |
| Output | `dist` |

4. Environment variable:

| Name | Value |
|------|--------|
| `VITE_API_BASE_URL` | `https://suvyonbackend.onrender.com/api/v1` |

5. Deploy. Production URL for this project: https://suvyon-ten.vercel.app

`frontend/vercel.json` rewrites all routes to `index.html` so React Router works.

---

## 5. Order of operations (first-time)

1. Supabase + vector  
2. Render API (CORS can be localhost until Vercel exists)  
3. Vercel with `VITE_API_BASE_URL` pointing at Render  
4. Set `BACKEND_CORS_ORIGINS` to the Vercel origin → Render redeploy  
5. Register a user on the **Vercel** URL (empty production database)

---

## 6. Smoke test

1. https://suvyonbackend.onrender.com/api/v1/health → `"healthy"`  
2. https://suvyon-ten.vercel.app → landing page  
3. Register / log in  
4. Create workspace → send a chat message  

If the UI loads but login fails, CORS or `VITE_API_BASE_URL` is wrong. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
