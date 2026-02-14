# FK94 Autonomous Growth Stack (OpenClaw)

## Goal
Build a mostly autonomous system that:
- Runs FK94 SaaS growth daily without manual intervention.
- Keeps OSS tools open and free (`/checklist`, `/harden`).
- Sells premium SaaS automatically.
- Escalates qualified users to consulting offers.

## Business Engines (3 in parallel)
1. OSS Engine (traffic + trust)
2. SaaS Engine (MRR)
3. Consulting Engine (high-ticket optional)

---

## Agent Topology

### A1. Orchestrator (Master Brain)
- Role: assign goals, budget, and task priority.
- Inputs: MRR, trials, churn, CAC, conversion rates.
- Outputs: daily execution plan + task queue for all agents.
- Cadence: every 6 hours.

### A2. Acquisition Agent
- Role: SEO pages, social distribution, partner/referral outreach.
- Inputs: content backlog, top converting pages, keywords.
- Outputs: published content + campaign tasks.
- Cadence: every 4 hours.

### A3. Content Agent (Kimi 2.5)
- Role: generate bilingual posts, emails, landing variants.
- Inputs: RSS/news, product updates, customer pain points.
- Outputs: scheduled posts + email sequences + A/B copy.
- Cadence: 2 batches/day.

### A4. Lead Qualification Agent
- Role: score every lead and route to SaaS or Consulting path.
- Inputs: form/chat events, profile data, behavior signals.
- Outputs: score (0-100), segment, next action.
- Cadence: event-driven.

### A5. Sales Closer Agent
- Role: automatic follow-up for high-intent leads.
- Inputs: lead score + objection profile.
- Outputs: call booking push, upgrade prompts, proposal drafts.
- Cadence: event-driven + daily digest.

### A6. Customer Success Agent
- Role: reduce churn and increase activation.
- Inputs: onboarding completion, feature usage, failed payments.
- Outputs: reminders, recovery emails, in-app nudges.
- Cadence: event-driven.

### A7. Finance/RevOps Agent
- Role: monitor unit economics and trigger budget rules.
- Inputs: Stripe + analytics + infra costs.
- Outputs: alerts, spend adjustments, weekly business report.
- Cadence: hourly + weekly review.

### A8. Product/Dev Agent
- Role: continuous product fixes and improvements.
- Inputs: bug reports, drop-off points, conversion data.
- Outputs: PR-ready changes in prioritized backlog.
- Cadence: continuous loop with guardrails.

---

## Core Automation Flows

### Flow 1: Free User -> Paid SaaS
1. User uses checklist/harden/audit.
2. Event captured (`tool_started`, `tool_completed`, `audit_result`).
3. Lead agent scores intent.
4. Content agent sends personalized 14-day sequence.
5. Sales agent triggers trial/upgrade CTA.
6. Finance agent verifies conversion and CAC.

### Flow 2: Paid SaaS -> Consulting Upsell
1. Detect high-risk results (critical score, repeated incidents, high-value wallet).
2. Auto-create "consulting recommended" flag.
3. Sales agent sends concierge invitation.
4. If accepted, create proposal draft and booking link.

### Flow 3: Churn Recovery
1. Stripe payment failure or cancellation event.
2. CS agent sends rescue sequence.
3. Offer downgrade/pause/annual discount.
4. Orchestrator tracks win-back rate.

---

## Minimum Event Schema (must exist)
- `signup_started`
- `signup_completed`
- `checkout_started`
- `checkout_success`
- `checkout_failed`
- `scan_started`
- `scan_completed`
- `report_downloaded`
- `consulting_interest`
- `subscription_canceled`
- `payment_failed`

These events are required for autonomous decisioning.

---

## Guardrails (Mandatory)
- Daily spending cap per channel.
- Auto-pause campaigns if conversion drops below threshold.
- Auto-stop social agents if account warning/ban signal appears.
- No outbound message without frequency limits.
- No credential logs in plaintext.
- Human approval mode can be toggled ON/OFF per agent.

---

## 4-Phase Implementation

### Phase 1 (Days 1-5): Foundation
- Create shared event bus and unified lead table.
- Enable agent runner schedules.
- Connect metrics sources (Stripe + app analytics).

### Phase 2 (Days 6-10): Revenue Loops
- Turn on onboarding and upgrade sequences.
- Route qualified leads to consulting lane.
- Add automated churn prevention.

### Phase 3 (Days 11-15): Optimization
- A/B testing for offer pages and emails.
- Dynamic pricing experiments (safe bounds).
- Add partner/referral automation.

### Phase 4 (Days 16-21): Full Autonomy
- Enable orchestrator budget controls.
- Activate daily and weekly business briefings.
- Enable auto-reprioritization of all agents.

---

## Definition of Ready for OpenClaw Deploy
- Env vars complete (see `openclaw.env.example`).
- Stripe webhook active and verified.
- Lead capture path tested end-to-end.
- At least one email provider and one analytics provider connected.
- Circuit breakers enabled.
- Dry-run completed for 48h with no critical errors.

---

## Definition of Done
- 80%+ of growth and follow-up actions are automated.
- Leads are auto-classified and routed.
- Paid conversions can happen without manual actions.
- Consulting upsell happens only for qualified profiles.
- Weekly report generated automatically with MRR/churn/CAC summary.
