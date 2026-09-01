# Suvyon documentation

Practical guides for running and hosting Suvyon. Architecture decisions live under [`architecture/`](architecture/00_PROJECT_CHARTER.md).

| Document | Use it for |
|----------|------------|
| [Local development](LOCAL_DEVELOPMENT.md) | venv, Postgres, backend, frontend, first login |
| [Environment variables](ENVIRONMENT.md) | Every env key, local vs production, why values must change |
| [Email delivery](EMAIL_DELIVERY.md) | Authentication OTP and agent email flows, provider selection, confirmation, and failures |
| [Resend migration runbook](RESEND_MIGRATION_RUNBOOK.md) | Future checklist for replacing SendGrid without breaking OTP or agent email |
| [Deployment](DEPLOYMENT.md) | GitHub, Supabase, Render, Vercel, live URLs, CORS |
| [Troubleshooting](TROUBLESHOOTING.md) | CORS, Vercel `@/lib` ignore, Render sleep, migrations |

**Production (this project)**

| Layer | URL |
|-------|-----|
| App (Vercel) | https://suvyon-ten.vercel.app |
| API (Render) | https://suvyonbackend.onrender.com |
| Health | https://suvyonbackend.onrender.com/api/v1/health |
| Source | https://github.com/SujoyGhosh7584/suvyon |
