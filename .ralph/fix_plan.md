# FK94 Security Platform - Fix Plan

## PRIORITY 1: Testing ✅ DONE
All 49 tests passing. Run `cd backend && pytest tests/ -v` to verify.

- [x] Add pytest tests for osint_service.py (mock external APIs) → `tests/test_osint.py` (13 tests)
- [x] Add pytest tests for scoring_service.py → `tests/test_scoring.py` (15 tests)
- [x] Add pytest tests for stripe_service.py → `tests/test_stripe.py` (18 tests)
- [x] Add basic API integration tests for /api/v1/health → `tests/test_health.py` (3 tests)
- [x] Verify all tests pass: 49/49 ✅

## PRIORITY 2: Frontend Features (Ralph - after tests green)
- [x] Add loading spinners/skeletons for all async operations → dashboard skeleton UI
- [x] Add export audit results as PDF button in frontend (backend PDF service exists) → already implemented for email audits
- [x] Add audit history in user dashboard (show past audits) → already implemented in dashboard/page.tsx
- [ ] Add dark mode toggle (Tailwind dark: classes)
- [ ] Improve mobile responsiveness across all pages
- [x] Add custom 404 page → `frontend/src/app/not-found.tsx`
- [x] Add Terms of Service page → `frontend/src/app/terms/page.tsx`
- [x] Add Privacy Policy page → `frontend/src/app/privacy/page.tsx`

## PRIORITY 3: SEO & Marketing
- [ ] Add structured data (JSON-LD) for security service pages
- [ ] Improve meta descriptions for all pages
- [ ] Add Open Graph images for social sharing
- [ ] Add FAQ schema markup on pricing page

## PRIORITY 4: Performance
- [ ] Add caching for repeated HIBP lookups (same email within 24h)
- [ ] Optimize frontend bundle size (check for unnecessary imports)
- [ ] Add lazy loading for dashboard components
- [ ] Implement request deduplication in job worker

## PRIORITY 5: Infrastructure
- [ ] Add Dockerfile health check for backend
- [ ] Add error tracking setup (Sentry-compatible error boundaries in frontend)

---

## COMPLETED

### Security & Robustness
- [x] Add Stripe webhook signature validation in stripe_service.py
- [x] Add input sanitization for all user-facing API endpoints
- [x] Validate and sanitize email/username/phone inputs before passing to external APIs
- [x] Add CORS origin validation (restrict to actual frontend domain in production)

### Error Handling
- [x] Add proper try/except blocks in osint_service.py for each external API call
- [x] Add timeout handling for httpx calls (some external APIs may hang)
- [x] Improve error messages returned to frontend (user-friendly, not stack traces)
- [x] Add fallback behavior when DeepSeek/Kimi API is down
- [x] Handle Supabase auth token expiry gracefully in frontend

### Frontend UX
- [x] Add error toast notifications instead of console.log errors
- [x] Add form validation with user-friendly error messages
- [x] Add progress indicator for full audit (multi-step process)

### Code Quality
- [x] Fix any ESLint warnings in frontend
- [x] Remove unused imports and dead code
- [x] Add health check for all external API dependencies in /status/apis
- [x] Add API response time logging middleware in FastAPI

### Still TODO (lower priority)
- [ ] Add rate limiting per-user (not just per-IP) for authenticated routes
- [ ] Add more exchanges to wallet deep scan (currently limited)
- [ ] Implement dark web monitoring check (breach compilation search)
- [ ] Add social media account detection by username
- [ ] Add type hints to all Python service functions
- [x] Create GitHub Actions CI pipeline (lint + build check on PR) → `.github/workflows/ci.yml`
