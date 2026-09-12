# UI, BYOK, and Responsive Behavior

This document records the currently implemented workspace interface and per-user model-provider behavior. It supplements the architecture documents; it does not replace their requirements.

## Modern workspace layout

- Desktop workspace navigation is an expanded drawer, not a permanent miniature rail.
- The three-line menu button closes the drawer to zero width so the selected page receives the released space.
- The open/closed workspace-navigation preference is stored in browser local storage.
- Chat history and the agent list are independent collapsible drawers. They also close to zero width.
- Chat and agent pages use the remaining viewport height and width instead of a fixed page-sized panel.
- The shared toolbar remains available for workspace switching and starting a new chat.
- Mobile uses a compact header and floating bottom navigation. A focused chat or agent task removes surrounding navigation.
- Authentication, landing, workspace directory, overview, knowledge, GitHub, settings, chat, and agent screens share the same surface, input, button, radius, shadow, and theme tokens.

## Fluid response layout

Response width depends on the available content container rather than a fixed `max-w-3xl` value:

- assistant output uses up to 96% of a normal desktop canvas;
- wide screens with a landscape aspect ratio allow up to 98%, capped at 1800 px;
- tables, code blocks, and generated images can consume the full assistant-response width;
- prose remains constrained to a readable character measure;
- user messages remain compact and right-aligned;
- portrait phones use full-width assistant responses and up to 90% for user messages;
- short landscape phones use the mobile interface through 1024 px viewport width;
- container queries adapt bubbles when a sidebar, split view, or narrow browser window reduces the actual content area.

Keyboard behavior still supports Enter to send and Shift+Enter for a line break, but the interface does not display redundant instructional copy above the composer.

## Themes

The selected theme is applied through `data-theme` on the document root. Themes control:

- application chrome;
- accent and primary colors;
- focus rings;
- navigation highlights;
- branded gradients;
- buttons and interactive state.

Content surfaces intentionally remain high-contrast and readable while theme accents change. Theme choice is stored locally and restored during application startup.

## Per-user API keys

Authenticated users can manage provider credentials under Settings. The backend:

1. validates the provider name and minimum key length;
2. encrypts the value before database storage;
3. stores only an encrypted value and a four-character hint;
4. never returns the complete credential to the browser;
5. decrypts keys only for the authenticated user's model request;
6. prioritizes that user's configured providers before shared server credentials;
7. uses shared environment credentials only as fallbacks.

Encryption derives a Fernet key from `CREDENTIAL_ENCRYPTION_KEY`, falling back to `SECRET_KEY`. Production must set a dedicated, stable `CREDENTIAL_ENCRYPTION_KEY`; rotating it without re-encrypting rows makes existing saved credentials unreadable.

## Supported BYOK providers

| Provider | Credential | Access represented in Suvyon |
|---|---|---|
| Groq | API key | Free rate-limited hosted models |
| Google Gemini | Google AI Studio key | Free-tier Gemini models |
| OpenRouter | API key | Explicit free models and free automatic routing |
| Cerebras | API key | Free inference tier |
| SambaNova | SambaCloud key | Free SambaCloud account models |
| Hugging Face | Fine-grained token | Monthly Inference Providers credits |
| Mistral | API key | Free mode with limited usage |
| Cohere | Trial key | Free, rate-limited trial usage |
| NVIDIA NIM | API Catalog key | Hosted trial access |

Free tiers, quotas, model identifiers, and terms can change. The model registry is a curated application catalogue, not a promise that a provider will keep a model or quota indefinitely.

GitHub Models is not registered because GitHub retired its playground, catalogue, inference API, and BYOK service on July 30, 2026. Cloudflare Workers AI is not in the one-key settings flow because its REST API requires both an Account ID and an API token.

## Provider adapter and routing

Groq, Gemini, and OpenRouter retain their specialized adapters. Additional providers share an OpenAI Chat Completions-compatible adapter supporting:

- normal chat completions;
- server-sent-event streaming;
- system, user, assistant, and tool messages;
- function tool schemas and returned tool calls;
- token usage when supplied by the provider;
- per-request user credential overrides;
- provider-specific error details.

An explicit provider or model is never silently substituted. Auto routing tries configured providers sequentially and can continue after a provider error. This is failover, not predictive latency-, health-, or cost-based load balancing.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/users/me/api-keys` | Return configuration status and masked hints for supported providers |
| `PUT` | `/api/v1/users/me/api-keys/{provider}` | Encrypt and save or replace the authenticated user's key |
| `DELETE` | `/api/v1/users/me/api-keys/{provider}` | Remove the authenticated user's saved key |
| `GET` | `/api/v1/models` | List policy-allowed models available through user or shared credentials |

## Deployment and validation

Apply the user-key migration before enabling the Settings interface:

```bash
alembic upgrade head
```

Keep `CREDENTIAL_ENCRYPTION_KEY` identical across restarts and replicas. Optional shared fallback variables are listed in [Environment variables](ENVIRONMENT.md).

The completed implementation is covered by backend API-key tests, the full backend test suite, TypeScript compilation, and the Vite production build. Live provider calls still depend on each supplied credential, account entitlement, quota, model availability, and network access.

## Primary references

- [Cerebras inference rate limits](https://inference-docs.cerebras.ai/support/rate-limits)
- [SambaNova API keys and URLs](https://docs.sambanova.ai/docs/en/get-started/api-keys-urls)
- [Hugging Face Inference Providers pricing](https://huggingface.co/docs/inference-providers/pricing)
- [Mistral usage and Free mode](https://docs.mistral.ai/admin/billing-usage/usage-limits)
- [Cohere trial-key limits](https://docs.cohere.com/v1/docs/cohere-faqs)
- [NVIDIA NIM API reference](https://docs.nvidia.com/nim/large-language-models/latest/api-reference.html)
- [GitHub Models retirement](https://docs.github.com/en/github-models)
- [Cloudflare Workers AI REST prerequisites](https://developers.cloudflare.com/workers-ai/get-started/rest-api/)
