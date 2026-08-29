# Troubleshooting

## Render: `error parsing value for field "BACKEND_CORS_ORIGINS"`

Pydantic used to JSON-decode list env vars. A plain URL or empty string crashed Alembic on boot.

**Fix (in code):** CORS accepts a comma-separated string. On Render set:

```text
https://suvyon-ten.vercel.app
```

No `["..."]` unless it is valid JSON. Redeploy after changing env.

---

## Vercel: `Cannot find module '@/lib/...'`

Root `.gitignore` contained `lib/`, which ignored **`frontend/src/lib`**. Those files never reached GitHub.

**Fix:** ignore only `/lib/` at the repo root. Commit and push `frontend/src/lib/` (`api.ts`, `services.ts`, `utils.ts`, `themes.ts`, `keyboard.ts`, `messageFormat.ts`). Redeploy Vercel.

Also confirm Vercel builds the branch that contains that commit. A log line `Branch: main, Commit: …` means that commit, not a different feature branch.

---

## Login works locally, fails on https://suvyon-ten.vercel.app

1. Browser DevTools → Network → failed request. If CORS: update Render `BACKEND_CORS_ORIGINS` to `https://suvyon-ten.vercel.app` (no trailing slash) and wait for Render deploy.  
2. If requests go to `127.0.0.1:8000`: Vercel `VITE_API_BASE_URL` was missing at **build** time. Set it and **Redeploy**.  
3. First hit after Render sleep: wait up to a minute; do not assume the API is down.

---

## Render deploy fails on `CREATE EXTENSION vector`

Enable **vector** in the Supabase dashboard (Database → Extensions), then Manual Deploy.

---

## Render deploy fails on database connection

- Password special characters must be URL-encoded in `DATABASE_URL`.  
- Use the pooler URI from Supabase, not a stale host.  
- Confirm the project is not paused.

---

## Chat works, knowledge upload vanishes

Expected on Render free: files in `uploads/` are not durable. Embeddings in Postgres may remain while the original file path is gone.

---

## Alembic vs app disagree locally

Always run commands from `backend` with the venv active:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
alembic upgrade head
```

---

## Port already in use

- API: change `--port 8000` or stop the other process.  
- UI: Vite uses **3000** (`frontend/vite.config.ts`).

---

## SMTP / Gmail “authentication failed”

Use a Google **App Password** (16 characters, no spaces). Unquoted spaces in `.env` truncate the value.
