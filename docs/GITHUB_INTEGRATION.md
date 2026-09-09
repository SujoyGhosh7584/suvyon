# Social login and GitHub projects

Suvyon uses OAuth only for identity and a GitHub App for repository access. No
Google or GitHub OAuth access token is stored. GitHub repository calls use
short-lived installation tokens generated when needed.

## Google login

Create a Web OAuth client in Google Cloud and configure:

- Authorized redirect URI: `https://YOUR_API/api/v1/auth/oauth/google/callback`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI` with the same callback URI

Only `openid email profile` is requested.

## GitHub login

Create a GitHub OAuth App and configure:

- Authorization callback URL: `https://YOUR_API/api/v1/auth/oauth/github/callback`
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`
- `GITHUB_REDIRECT_URI` with the same callback URI

Only `read:user user:email` is requested. Repository access is deliberately
not requested by the login application.

## GitHub repository access

Create a GitHub App with setup URL:

`https://YOUR_API/api/v1/github/install/callback`

Repository permissions:

- Metadata: Read-only
- Contents: Read and write
- Pull requests: Read and write

Do not grant administration, secrets, workflows, or organization permissions.
Set:

- `GITHUB_APP_ID`
- `GITHUB_APP_SLUG`
- `GITHUB_APP_PRIVATE_KEY` (PEM; use literal `\n` in a one-line host variable)
- `GITHUB_APP_SETUP_URL`

Set `FRONTEND_URL` to the exact frontend origin. Users install the app on only
the repositories they choose. Suvyon blocks changes to workflow files, secrets,
private keys, lockfiles, binaries, generated folders, and stale proposals.

## Database

Apply migrations before enabling either integration:

```powershell
cd backend
alembic upgrade head
```

`ZERO_COST_MODE=true` filters out every model with a declared non-zero input or
output price. Free provider rate limits still apply.
