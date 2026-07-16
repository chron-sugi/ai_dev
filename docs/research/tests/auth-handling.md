The pattern that works best for agents is: don't disable auth — make obtaining credentials completely deterministic and documented. Turning auth off creates a second code path that diverges from production (redirects, guards, and 401 handling never get exercised), and agents then "fix" bugs that only exist in the bypassed mode.

Three layers, from backend to browser:

**1. Seeded dev credentials + real login flow.** Your dev environment seeds a known test user on startup (`dev@local.test` / password from `.env`). Auth stays fully on; the credentials are just knowable. This is the baseline every other layer builds on.

**2. FastAPI dependency override for API-level testing.** For pytest, don't log in at all — swap the auth dependency:

```python
app.dependency_overrides[get_current_user] = lambda: User(id=1, email="dev@local.test")
```

This is the idiomatic FastAPI escape hatch: scoped to the test process, zero production code changes, no env flag that could leak.

**3. Playwright: authenticate once via API, reuse storageState.** Instead of scripting the login UI in every test, a global setup hits your login endpoint directly, captures the cookie/JWT, and saves it:

```ts
// global-setup: POST /auth/login → save state
await request.post('/api/auth/login', { data: { email, password } });
await request.storageState({ path: '.auth/state.json' });
```

Then every test/agent session starts pre-authenticated via `storageState: '.auth/state.json'`. Login UI itself gets one dedicated test; everything else skips it.

The agent-facing piece — and this is where your usual approach applies — is making the recipe discoverable rather than hoping the agent figures it out. A short section in `AGENTS.md` or a glob-scoped instruction file: "Test credentials are seeded from `.env.development`. For Playwright, run `npx playwright test` — auth state is handled by global setup. Never modify auth middleware to bypass login." That last sentence matters; without it, agents blocked by a 401 will happily comment out your auth dependency. You could even back it with a lint rule or hook denying edits to the auth module during agent sessions, consistent with your enforcement-over-prose stance.

One thing to avoid: the `X-Test-User` header-impersonation pattern (middleware that trusts a header when `ENV=dev`). It's convenient but it's a real contamination vector — one misconfigured env var in staging and it's an auth bypass vulnerability. The seeded-user + storageState combo gets you the same ergonomics with no dormant backdoor.