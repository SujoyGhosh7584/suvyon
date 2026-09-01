# Resend migration runbook

Use this runbook **before the SendGrid trial ends** to keep Suvyon authentication and agent email working. No application-code change is required: Suvyon already supports Resend over HTTPS.

Official references:

- [Resend API-key setup](https://resend.com/docs/dashboard/api-keys/introduction)
- [Resend domain verification](https://resend.com/docs/dashboard/domains/introduction)
- [Resend domain troubleshooting](https://resend.com/docs/knowledge-base/what-if-my-domain-is-not-verifying)
- [Resend sender-address rules](https://resend.com/docs/knowledge-base/how-do-I-create-an-email-address-or-sender-in-resend)
- [Resend pricing and current free limits](https://resend.com/pricing)

## What changes in Suvyon

Both authentication OTPs and confirmed agent emails call the shared selector in [`backend/app/tools/email_tool.py`](../backend/app/tools/email_tool.py#L248):

```text
RESEND_API_KEY configured  -> Resend
otherwise SENDGRID_API_KEY -> SendGrid
otherwise                  -> SMTP
```

Adding `RESEND_API_KEY` therefore switches registration verification, resend-verification, forgot-password, and confirmed `send_email` agent actions immediately. Drafting an agent email still does not send anything, and its explicit-confirmation safety check remains unchanged.

Suvyon does not automatically fall back after Resend rejects a request. Keep the SendGrid key temporarily for manual rollback, but understand that it remains dormant while `RESEND_API_KEY` is populated.

## Schedule

Do not wait until the final SendGrid day.

| Time | Action |
|---|---|
| 7–14 days before expiry | Create Resend account, add domain, and copy DNS records |
| 3–7 days before expiry | Wait for verified domain; create restricted API key |
| 2–3 days before expiry | Configure Render and run every smoke test |
| 1 day before expiry | Confirm Resend logs and real inbox delivery |
| After stable operation | Remove the unused SendGrid key |

DNS verification often completes quickly but can take up to 72 hours, so domain setup is the step that needs advance time.

## Prerequisites

You need:

- Access to the Resend dashboard
- Access to the DNS settings for a domain you own
- Access to the Suvyon Render service's Environment page
- A fresh email address or alias for registration testing
- The current SendGrid integration still working during migration

For real users, do not depend on Resend's shared `resend.dev` testing domain. It can send only to the email address associated with your Resend account. To send OTPs or agent emails to arbitrary users, verify a domain you own.

## Phase 1 — Add and verify a sending domain

1. Sign in to [Resend](https://resend.com/).
2. Open **Domains**.
3. Select **Add Domain**.
4. Prefer a sending subdomain such as:

   ```text
   notify.yourdomain.com
   ```

   A subdomain isolates transactional-email reputation from your main website domain.

5. Resend displays DNS records for SPF and DKIM, plus the required return-path/MX information.
6. Open your domain provider's DNS dashboard.
7. Copy each record exactly: type, host/name, value/content, priority when supplied, and TTL.
8. Return to Resend and select **Verify DNS Records**.
9. Do not continue until the domain status is **Verified** for sending.

### DNS verification problems

- Your DNS provider may automatically append the domain name. Do not create names such as `send.example.com.example.com`.
- Do not add extra quotation marks or spaces to DKIM values.
- Do not truncate long DKIM records.
- Ensure MX records use the region Resend supplied.
- Use **Restart verification** after correcting records.
- Allow up to 72 hours for global DNS propagation.

## Phase 2 — Choose the From address

After the domain is verified, Resend allows any address under that domain; it does not require creating each mailbox in Resend.

Recommended value:

```text
Suvyon <noreply@notify.yourdomain.com>
```

If users might reply, use a monitored mailbox such as `support@notify.yourdomain.com`. The address after `@` must match the domain or subdomain verified in Resend.

Suvyon reads this value from `SMTP_FROM_EMAIL`. The name is historical: this variable supplies the sender for Resend and SendGrid as well as SMTP.

## Phase 3 — Create the production API key

1. In Resend, open **API Keys**.
2. Select **Create API Key**.
3. Name it `Suvyon Production Render`.
4. Select **Sending access**, not Full access.
5. Restrict the key to your verified sending domain when offered.
6. Create the key.
7. Copy the `re_...` value immediately. Resend shows the secret only once.
8. Store a backup in a password manager. Never put it in Git, screenshots, frontend code, chat messages, or documentation.

Resend keys do not currently expire automatically. Rotate them periodically and immediately after suspected exposure.

## Phase 4 — Configure the Render backend

1. Open the [Render dashboard](https://dashboard.render.com/).
2. Select the `suvyon-backend` web service.
3. Open **Environment**.
4. Add or update:

   ```text
   RESEND_API_KEY=re_your_real_secret
   SMTP_FROM_EMAIL=Suvyon <noreply@notify.yourdomain.com>
   ```

5. Leave `SENDGRID_API_KEY` present temporarily. It is a manual rollback option, not an automatic fallback.
6. Save changes and allow Render to redeploy/restart the service.
7. Do not put either variable on Vercel. Vercel hosts the browser frontend; Render sends email.

The current [`backend/render.yaml`](../backend/render.yaml) declares `RESEND_API_KEY` as an external secret but does not declare `SMTP_FROM_EMAIL`. Add the From value manually in Render unless the blueprint is updated later.

## Phase 5 — Confirm the backend is healthy

After Render finishes deploying:

1. Open `https://suvyonbackend.onrender.com/api/v1/health` and confirm it reports healthy.
2. Open the Render logs and keep them visible during testing.
3. Open the Resend **Emails** or **Logs** page in another tab.

## Phase 6 — Test every Suvyon email flow

One successful email does not prove every application path works.

### Test A — Registration OTP

1. Register with a fresh test email or alias.
2. Confirm the API request succeeds and a message appears in Resend logs.
3. Confirm the inbox receives **Your Suvyon verification code**.
4. Enter the six-digit code and confirm the workspace opens.

This proves registration, OTP creation, system-email delivery, and OTP verification.

### Test B — Resend verification

1. Use an unverified test account.
2. Wait at least 60 seconds after the previous code request.
3. Select resend verification.
4. Confirm a new Resend log entry and inbox message.
5. Confirm the older code no longer works and the newest code works.

### Test C — Forgot password

1. Select **Forgot password?** and enter an active test-account email.
2. Confirm receipt of **Your Suvyon password reset code**.
3. Complete the reset.
4. Confirm login succeeds with the new password and fails with the old password.

### Test D — Agent draft safety

1. Open an agent configured with `draft_email,send_email`.
2. Ask it to compose an email.
3. Confirm a draft appears and no new entry appears in Resend logs.

This proves drafting does not send.

### Test E — Confirmed agent send

1. After reviewing the draft, reply with `send it`.
2. Confirm the UI reports success.
3. Confirm a Resend log entry appears.
4. Confirm the recipient receives the exact subject and body you approved.

## Phase 7 — Observe for one day

Before removing SendGrid:

- Check Resend logs for rejected, bounced, or delayed messages.
- Test more than one receiving provider if possible, such as Gmail and Outlook.
- Confirm messages are not consistently entering spam.
- Confirm the daily volume remains below your Resend plan limit.
- Confirm Render logs have no `Resend rejected the send` errors.

Resend's pricing page currently lists a free-plan daily limit of 100 messages. Recheck [current pricing](https://resend.com/pricing) when you migrate because provider limits can change.

## Phase 8 — Retire SendGrid

After Resend has been stable:

1. Remove or clear `SENDGRID_API_KEY` in Render.
2. Save and redeploy.
3. Repeat at least registration OTP and confirmed-agent-send tests.
4. Revoke the old SendGrid API key in SendGrid.
5. Cancel or allow the trial to end according to your plan.

## Rollback procedure

Use this only while the SendGrid key/account can still send:

1. In Render, clear or remove `RESEND_API_KEY`.
2. Confirm `SENDGRID_API_KEY` and `SMTP_FROM_EMAIL` are still populated.
3. Save and redeploy.
4. Test one registration OTP.

Removing the Resend key makes Suvyon select SendGrid. A failing Resend key does not trigger automatic SendGrid fallback.

After the SendGrid trial expires, this rollback will not work. Render free also blocks SMTP ports, so the remaining options are to repair Resend, pay for SendGrid, add another HTTPS provider in code, or upgrade Render and use SMTP.

## Error guide

| Symptom | Likely cause | Action |
|---|---|---|
| `RESEND_API_KEY is set but SMTP_FROM_EMAIL ... is empty` | Sender variable missing on Render | Add `SMTP_FROM_EMAIL`, save, redeploy |
| Resend HTTP 401 | Invalid, revoked, or incorrectly copied API key | Create/copy a new Sending-access key |
| Resend HTTP 403 | Unverified domain, mismatched From domain, or `resend.dev` used for another recipient | Verify your domain and correct `SMTP_FROM_EMAIL` |
| Resend HTTP 422 | Invalid sender, recipient, or message field | Check the provider response in Render and Resend logs |
| Resend HTTP 429 | Daily or rate limit reached | Reduce test volume or upgrade the plan |
| OTP request fails but agent draft works | Draft never sends; delivery configuration is broken | Check key, sender, and domain verification |
| Email appears in Resend but not inbox | Delayed, bounced, suppressed, or spam-filtered | Inspect delivery status and recipient spam folder |
| SendGrid still receives requests | `RESEND_API_KEY` is absent in the running Render service | Correct the Render environment and redeploy |

## Security rules

- Use a Sending-access, domain-restricted key.
- Keep keys only in backend environment variables.
- Never expose the key through `VITE_*` variables.
- Never commit `.env`.
- Rotate by creating a new key, deploying it, verifying logs, and only then deleting the old key.

## Current implementation limitations

The integration sends plain-text email through `POST https://api.resend.com/emails`. It does not yet persist Resend message IDs, add idempotency keys, consume delivery webhooks, automatically fail over to SendGrid, maintain an email-history table, or queue email in a durable outbox.

These limitations do not prevent normal low-volume delivery, but they are important interview and production-design discussion points.

## Completion checklist

- [ ] Owned domain or sending subdomain added to Resend
- [ ] SPF/DKIM/required DNS records copied exactly
- [ ] Resend status shows Verified
- [ ] Sending-access, domain-restricted key created
- [ ] Key stored securely
- [ ] `RESEND_API_KEY` added to Render
- [ ] `SMTP_FROM_EMAIL` uses the verified domain
- [ ] Render redeployed and health endpoint is healthy
- [ ] Registration OTP received and accepted
- [ ] Resend-verification flow tested
- [ ] Forgot-password flow tested
- [ ] Agent draft confirmed not to send
- [ ] Explicitly confirmed agent email delivered
- [ ] Resend logs checked for delivery/bounces
- [ ] One day of stable operation observed
- [ ] SendGrid key removed only after stability

Related documentation: [Email delivery](EMAIL_DELIVERY.md), [Environment variables](ENVIRONMENT.md), [Deployment](DEPLOYMENT.md), and [Troubleshooting](TROUBLESHOOTING.md).
