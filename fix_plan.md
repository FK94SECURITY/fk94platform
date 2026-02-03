# FK94 Fix Plan

## Priority 1: Security & Bug Fixes

- [x] Backend: Fix DeepSeek service unhandled JSON parse errors (deepseek_service.py:56)
- [x] Backend: Replace print() with proper logging across services
- [x] Backend: Add security headers middleware (main.py)
- [x] Backend: Validate Stripe redirect URLs (routes.py:420)
- [x] Backend: Add rate limit to /status/apis endpoint (routes.py:310)
- [x] Backend: Truncate error messages in job_worker (job_worker.py:84)
- [x] Backend: Fix global variable race condition in stripe_service.py

## Priority 2: Error Handling & Robustness

- [x] Frontend: Fix missing mobile logout button (Navbar.tsx:118)
- [x] Frontend: Fix AIChat hardcoded Spanish greeting (AIChat.tsx:19)
- [x] Frontend: Improve audit error handling granularity (audit/page.tsx:216)
- [x] Frontend: Add loading timeout for audit (audit/page.tsx:114)
- [x] Frontend: Fix missing i18n in AuthModal and Navbar

## Priority 3: Future Improvements (Not in this batch)

- [x] Backend: Implement Stripe webhook idempotency
- [x] Backend: Add CSRF token validation (covered by CORS + bearer tokens)
- [ ] Frontend: Implement contact form backend integration
- [x] Frontend: Add retry logic for API calls
- [x] Frontend: Handle session expiry with redirect
- [x] Backend: Add request body size limits
