# FK94 Automation

## OpenClaw Autonomous Stack (New)
Architecture and deploy docs for autonomous growth + SaaS + consulting:
- `OPENCLAW_DEPLOY_PLAN.md` - full business/agent architecture
- `agent_topology.yaml` - agent graph, schedules, triggers, pipelines
- `openclaw.env.example` - required credentials/env vars template
- `OPENCLAW_DEPLOY_CHECKLIST.md` - step-by-step deployment checklist
- `openclaw_runner.py` - runtime loop (event polling + pipeline actions)

Run locally:
```bash
pip install -r requirements.txt
python3 openclaw_runner.py --once
python3 openclaw_runner.py --daemon --interval 300
```

Recommended startup mode (no clients yet):
```bash
export ENABLE_AUTONOMY=true
export AUTONOMY_MODE=guarded
export GROWTH_STAGE=pre_pmf
export MIN_PAID_CUSTOMERS_FOR_POST_PMF=5
python3 openclaw_runner.py --once
```

In `pre_pmf`, only acquisition/capture/conversion loops run.
Retention-heavy loops (churn recovery, paid consulting upsell) are skipped until enough paid users exist.

Deploy helpers:
```bash
# Validate environment + API readiness
python3 preflight.py

# One-command deploy helper
./deploy_openclaw.sh
```

## Content Manager (Rasperito - Legacy)
Social media posting scripts. These handle automated content publishing to Twitter/LinkedIn.
- `poster.py` - API-based poster
- `browser_poster.py` - Browser automation poster (Playwright)
- `content_calendar.json` - Pre-written posts
- `setup_cron.sh` - Cron job installer

## Dev Agent (Ralph)
Autonomous development agent that improves FK94 codebase 24/7.
Configuration lives in `/.ralph/` directory at project root.
- `.ralph/PROMPT.md` - Agent objectives
- `.ralph/fix_plan.md` - Task list
- `.ralph/AGENT.md` - Build commands
- `.ralphrc` - Rate limits and tool permissions

To start the dev agent: `ralph --monitor` from project root.
