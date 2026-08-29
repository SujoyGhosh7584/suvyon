# Environment variables

Suvyon does not hardcode secrets. Local values live in `backend/.env` and `frontend/.env`. Production values live in **Render** and **Vercel** dashboards. None of those files should be committed.

Templates: `backend/.env.example`, `frontend/.env.example`.

---

## Why values must be updated when you change hosts

### Frontend: `VITE_API_BASE_URL`

Vite **inlines** any `VITE_*` variable at **build time**. Changing the variable on Vercel does nothing until you **Redeploy**. A build that still has `http://127.0.0.1:8000` will never reach Render.

Use:

- Local: `http://127.0.0.1:8000/api/v1`
- Production: `https://suvyonbackend.onrender.com/api/v1`

No trailing slash.

### Backend: `BACKEND_CORS_ORIGINS`

Browsers send an `Origin` header. FastAPI only allows listed origins. If you deploy a new Vercel URL (or a Preview deployment with a different hostname), login will fail until CORS is updated and Render **redeploys**.

Use comma-separated origins, **no quotes**, **no JSON array** on Render (plain URL is enough):

```text
https://suvyon-ten.vercel.app
```

Optional local + production:

```text
https://suvyon-ten.vercel.app,http://localhost:3000
```

Do **not** put the Render API URL here. CORS is for the **page origin** (Vercel or localhost), not the API host.

### Backend: `DATABASE_URL`

Local Postgres and Supabase are different servers. Using the production URL on your laptop writes to production data. Using the local URL on Render has no database.

Supabase URLs often start with `postgres://`. The app rewrites that to `postgresql+psycopg://` and turns on SSL for Supabase hosts.

### Backend: `SECRET_KEY`

JWTs are signed with this key. Changing it in production **invalidates all sessions**. Do not reuse a weak example string. Do not share local and production keys if you want them isolated.

### `APP_ENV`

`development` locally, `production` on Render. Logging and mental model of “this is live.”

---

## Backend variables

| Variable | Required | Local | Production (Render) |
|----------|----------|-------|---------------------|
| `APP_NAME` | No | `Suvyon` | `Suvyon` |
| `APP_VERSION` | No | `1.0.0` | `1.0.0` |
| `APP_ENV` | No | `development` | `production` |
| `API_V1_PREFIX` | No | `/api/v1` | `/api/v1` |
| `SECRET_KEY` | **Yes** | Random, long | Different random, long |
| `JWT_ALGORITHM` | No | `HS256` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | `7` |
| `DATABASE_URL` | **Yes** | Local Postgres | Supabase pooler URI |
| `SUPABASE_URL` | No | Optional / unused by app code | Optional |
| `SUPABASE_KEY` | No | Optional / unused by app code | Optional |
| `BACKEND_CORS_ORIGINS` | No | `http://localhost:3000,...` | Vercel origin |
| `GROQ_API_KEY` | For chat | Your Groq key | Same or dedicated key |
| `GEMINI_API_KEY` | For RAG embeddings | Your Gemini key | Same or dedicated |
| `OPENROUTER_API_KEY` | Optional | If you use OpenRouter | Same |
| `TAVILY_API_KEY` | Optional | Web search | Same |
| `SERPER_API_KEY` | Optional | Web search | Same |
| `BRAVE_API_KEY` | Optional | Web search | Same |
| `SMTP_HOST` | Email tools | e.g. `smtp.gmail.com` | Same |
| `SMTP_PORT` | Email tools | `587` | `587` |
| `SMTP_USERNAME` | Email tools | Gmail address | Same |
| `SMTP_PASSWORD` | Email tools | **App password**, no spaces | Same |
| `SMTP_FROM_EMAIL` | Email tools | From address | Same |

Chat needs **at least one** of Groq, Gemini, or OpenRouter. Knowledge upload embeddings need **Gemini** (or OpenRouter nomic embed as fallback).

---

## Frontend variables

| Variable | Required | Where to set |
|----------|----------|----------------|
| `VITE_API_BASE_URL` | **Yes** | `frontend/.env` locally; Vercel **Environment Variables** in production |

Vercel: Production (and Preview if you use it) must both have the correct API URL **before** the build, then Redeploy.

---

## Current production mapping

These are the values this project used when first hosted. If you recreate services, update this table and the live URLs in [DEPLOYMENT.md](DEPLOYMENT.md).

| Role | Value |
|------|--------|
| Vercel origin | `https://suvyon-ten.vercel.app` |
| Render API | `https://suvyonbackend.onrender.com` |
| `VITE_API_BASE_URL` | `https://suvyonbackend.onrender.com/api/v1` |
| `BACKEND_CORS_ORIGINS` | `https://suvyon-ten.vercel.app` |

---

## Checklist after any URL change

1. Update `VITE_API_BASE_URL` on Vercel → **Redeploy frontend**.
2. Update `BACKEND_CORS_ORIGINS` on Render → wait for **backend** redeploy.
3. Open the **new** frontend origin and hard-refresh.
4. Confirm https://suvyonbackend.onrender.com/api/v1/health still returns healthy.
