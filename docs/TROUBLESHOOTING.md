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

## Email agent: draft works on Vercel, send shows “Network Error”

The Vercel site is not sending mail. The **Render API** is. Drafts never contact any delivery provider, so they succeed. A confirmed send uses Resend when `RESEND_API_KEY` is set, otherwise SendGrid when `SENDGRID_API_KEY` is set, otherwise SMTP.

**Render’s free web service blocks outbound SMTP** (ports 25, 465, 587). The connection hangs, the HTTP request is dropped, and the browser reports Axios `Network Error` even though your Wi‑Fi is fine. The same `SMTP_*` values work on your laptop because that machine is not behind Render’s firewall.

**Fix (pick one):**

1. **Stay on Render free** — add **`RESEND_API_KEY`** or **`SENDGRID_API_KEY`** in the Render dashboard (not Vercel). Redeploy. Verify the sender on that provider. Keep `SMTP_FROM_EMAIL` as the From address.
2. **Keep Gmail SMTP as-is** — upgrade the Render instance off the free plan so ports 587/465 are allowed.

OTP sign-up mail has the same restriction on production.

If both HTTPS keys are set, Resend wins. The backend does not fall through to SendGrid or SMTP after Resend rejects a send. Also confirm `SMTP_FROM_EMAIL` exists in the Render dashboard: the current `render.yaml` declares the API keys but not this required sender value. Full behavior: [Email delivery](EMAIL_DELIVERY.md).

## Render: `Can't locate revision identified by 'f6a7b8c9d0e1'`

The **database** (shared Supabase) is already at Alembic revision `f6a7b8c9d0e1` because it was applied from your laptop. Render is deploying a Git commit that **does not contain** `backend/alembic/versions/f6a7b8c9d0e1_add_otp_codes.py`.

Alembic then refuses to start: it sees a version ID in `alembic_version` that is not in the cloned repo.

**Fix:** commit and **push** that migration file (and the rest of the OTP backend) to the **same branch Render builds**. Redeploy. `alembic upgrade head` will then match the database and start Uvicorn.

Do not stamp the version backward unless you also drop `otp_codes`; otherwise a later upgrade will try to create the table twice.

An email transport is required for new sign-ups. Locally, set `SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_FROM_EMAIL`. On Render free, prefer `RESEND_API_KEY` or `SENDGRID_API_KEY` plus `SMTP_FROM_EMAIL`. Check spam. Wait 60 seconds before resend. Codes expire in 10 minutes.

## Provider saved but no models appear

1. Confirm the latest API-key migration ran with `alembic upgrade head`.
2. Confirm the frontend points to the same backend where the key was saved.
3. Refresh `/api/v1/models` after saving; the UI invalidates this query automatically.
4. Check whether the provider retired the curated model or exhausted the account's free quota.
5. Confirm `ZERO_COST_MODE=true` is not filtering a model whose declared application price is nonzero.
6. Never paste the key into logs. Replace or revoke it from the provider dashboard if exposure is suspected.

## Existing user keys stopped decrypting

`CREDENTIAL_ENCRYPTION_KEY` or its fallback `SECRET_KEY` changed. Restore the previous encryption secret. If the previous value is unavailable, the ciphertext cannot be recovered; affected users must delete and save new provider keys.

## A collapsed drawer still consumes screen width

Confirm the latest frontend assets are deployed and clear the service-worker/browser cache if an old bundle is retained. The current drawer state uses zero width and removes the inter-panel gap. The workspace-navigation preference is stored under `suvyon-navigation-open` in local storage.

## Responses remain narrow on a wide screen

Confirm the response has the `message-bubble-assistant` class and its scroll container has `chat-transcript`. The fluid layout permits wide structured output while individual prose paragraphs remain intentionally constrained for readability. Tables should expand within the response and scroll horizontally only when their content exceeds the available canvas.
