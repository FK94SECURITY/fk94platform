# OpenClaw Deploy Checklist (FK94)

## 1) Before Deploy
- [ ] Backend API reachable and healthy (`/api/v1/health`).
- [ ] Stripe checkout and webhook configured.
- [ ] Supabase auth + schema applied.
- [ ] `openclaw.env.example` copied to real `.env` with values.
- [ ] Social sessions present if using browser bots.
- [ ] Alert webhook configured (Slack/Telegram/Discord).

## 2) Security
- [ ] No secrets in git.
- [ ] Service keys only in server env vars.
- [ ] Provider API keys scoped to minimum permissions.
- [ ] Webhook signature verification enabled.
- [ ] Rate limits enabled in production.

## 3) Dry Run (48h)
- [ ] Run all agents in guarded mode.
- [ ] Confirm events are ingested.
- [ ] Confirm no spam burst from outreach agents.
- [ ] Confirm budget cap and auto-pause are working.
- [ ] Validate lead scoring and routing logic.

## 4) Production Launch
- [ ] Set `ENABLE_AUTONOMY=true`.
- [ ] Keep `AUTONOMY_MODE=guarded` first week.
- [ ] Enable full mode only after stable KPIs for 7 days.
- [ ] Review daily executive report.

## 5) Success Criteria
- [ ] Leads routed automatically with no manual triage.
- [ ] Free users receive automated conversion flow.
- [ ] Stripe events trigger retention and rescue sequences.
- [ ] Consulting offers sent only to high-intent/high-risk segments.

## 6) Rollback Plan
- [ ] Disable orchestrator first.
- [ ] Keep customer success active.
- [ ] Pause acquisition and sales automations.
- [ ] Maintain support notifications until stability restored.
