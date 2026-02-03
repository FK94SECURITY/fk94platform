# FK94 Automation

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
