# finance-os-dashboard-mvp - Work Plan

## TL;DR (For humans)
**What you'll get:** A local Finance OS MVP that starts with one command, lets you search Korean stocks, and renders market cap plus the supply oscillator in an interactive chart. The backend will cache KRX-derived data, the Python service will own the finance calculation, and the UI will use the agreed Toss-style visual system.

**Why this approach:** The approved plan already chose the lowest-risk split: Python/polars for the Excel-derived oscillator, Bun/Elysia as a fast API gateway, Redis for daily cache, and React/ECharts for the dashboard. I tightened the plan by making fixture-first math verification, schema/type sharing, cache fallback behavior, and full-stack evidence mandatory instead of implied.

**What it will NOT do:** It will not implement OpenDART/dartlab features in the first MVP slice, add post-MVP cache pre-warming or per-day chunking, or replace the approved stack.

**Effort:** Large
**Risk:** High - live KRX scraping, cross-runtime contracts, and finance-formula correctness all need hard evidence.
**Decisions to sanity-check:** `ALL` means full PyKRX history, Redis TTL is 86,400 seconds, cache invalidation runs at 15:35 KST, and the Excel fixture is Samsung Electronics `005930` for `2025-06-02` through `2026-05-29`.

Your next move: run `$start-work` on this plan, or request the optional high-accuracy plan review first. Full execution detail follows below.

---

> TL;DR (machine): Large/high-risk greenfield MVP; deliver Docker Compose, Python data-service, Bun backend/cache, React/ECharts frontend, tests, evidence, and docs without OpenDART implementation in MVP.

## Scope
### Must have
- A clean greenfield project rooted at `/Users/burt/Documents/KimiProjects/steady-n-wise`; no product code from the accidental scaffold is part of this plan.
- `docker-compose.yml` with `backend`, `data-service`, `redis`, and `frontend` services, plus health checks and documented env values.
- Python FastAPI data-service using PyKRX and polars for KRX market-cap/net-buy fetching and supply oscillator computation.
- Data-service APIs:
  - `GET /health`
  - `GET /stocks/search?q=...`
  - `GET /stocks/{stock_code}/supply-analysis?start=...&end=...`
- Bun/Elysia backend gateway APIs:
  - `GET /health`
  - `GET /api/v1/stocks/search?q=...`
  - `GET /api/v1/stocks/:stock_code/supply-analysis?start=...&end=...`
- Redis cache with key `supply:{code}:{start}:{end}`, normalized empty strings for `ALL`, TTL 86,400 seconds, cached fallback on upstream failure, and cache invalidation at 15:35 KST.
- Single-flight protection in both backend and data-service so 10 identical concurrent cache-miss requests trigger exactly one upstream scrape/fetch path.
- React/Vite frontend with TDS/Pretendard tokens, top search bar, sidebars, ECharts dual-axis chart, tooltip, zoom/pan, and period buttons `1M`, `3M`, `6M`, `1Y`, `ALL`.
- Fixture-first oscillator regression against `t-dad` Excel-derived CSV before UI integration.
- Playwright E2E against the full Docker Compose stack.
- Documentation covering local dev, API contract, ADR, formula parameters, fixture extraction, and post-MVP exclusions.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do not implement OpenDART/dartlab endpoints in this MVP. Keep `OPENDART_API_KEY` only as a future-facing env placeholder if retained from the approved spec.
- Do not call live PyKRX in unit tests. Use fixtures, fakes, or integration tests with explicit evidence.
- Do not add auth, user accounts, settings UI, real-time market data, PER/PBR charts, cache pre-warming, per-day Redis chunks, Redis Streams, or a full circuit-breaker state machine.
- Do not compute oscillator in TypeScript or the browser.
- Do not hard-code ad-hoc colors, spacing, radius, or fonts outside centralized frontend tokens.
- Do not treat green tests alone as done; each todo has a real-surface or auxiliary evidence artifact.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: TDD for finance calculation, validation, cache behavior, single-flight, and UI interactions; tests-after only for pure scaffold/config files where no behavior exists yet.
- Python gates: `uv run ruff check .`, `uv run basedpyright`, `uv run pytest` from `data-service/`.
- TypeScript backend gates: `bunx biome check .`, `bunx tsc --noEmit`, `bun test` from `backend/`.
- Frontend gates: `bunx biome check .`, `bunx tsc --noEmit`, `bun test`, and `bunx playwright test` from `frontend/`.
- Stack gate: `docker compose up --build -d`, `docker compose ps`, `curl -i http://localhost:${BACKEND_PORT:-3000}/health`, API `curl` scenarios, Playwright scenario, then `docker compose down`.
- Evidence paths:
  - `.omo/evidence/task-1-foundation.txt`
  - `.omo/evidence/task-2-data-contract.txt`
  - `.omo/evidence/task-3-oscillator.txt`
  - `.omo/evidence/task-4-data-api.txt`
  - `.omo/evidence/task-5-backend-cache.txt`
  - `.omo/evidence/task-6-frontend-shell.txt`
  - `.omo/evidence/task-7-e2e.txt`
  - `.omo/evidence/task-8-docs.txt`
  - `.omo/evidence/final-qa.txt`

## Execution strategy
### Parallel execution waves
- Wave 1: Task 1 only. Establish the repo and commands so later work has stable surfaces.
- Wave 2: Tasks 2 and 3 can run in parallel after Task 1. One owns contracts/fixtures; the other owns the pure oscillator implementation and tests.
- Wave 3: Tasks 4 and 5 can overlap after Tasks 2 and 3 once the contract and calculation are stable.
- Wave 4: Task 6 after backend routes exist enough to mock or call; frontend may use checked-in fixture/mock payload first, then switch to backend.
- Wave 5: Tasks 7 and 8 after all runtime surfaces exist.
- Final wave: F1-F4 after all todos pass.

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. Foundation and local stack | None | 2, 3, 4, 5, 6, 7, 8 | None |
| 2. Contract, fixtures, and shared schemas | 1 | 3, 4, 5, 6, 7, 8 | 3 |
| 3. Oscillator calculation core | 1, 2 fixture format | 4, 5, 6, 7, 8 | 2 after fixture header is agreed |
| 4. Data-service APIs and scheduler | 2, 3 | 5, 6, 7, 8 | 5 only after API shape is stable |
| 5. Backend gateway, cache, retry, single-flight | 2, 3, 4 health/contract | 6, 7, 8 | 4 with a fake data-service contract |
| 6. Frontend search and chart | 2, 5 API route shape | 7, 8 | None |
| 7. Full-stack E2E and performance evidence | 1-6 | 8, final wave | 8 after E2E command names are known |
| 8. Docs, ADR, and handoff | 1-7 | final wave | 7 late-stage evidence capture |

## Todos
> Implementation + Test = ONE todo. Never separate.

- [ ] 1. Create the foundation and local stack
  What to do / Must NOT do: Create root `.env.example`, `.gitignore`, `docker-compose.yml`, root `Makefile` or `package.json` scripts, service directories `backend/`, `frontend/`, and `data-service/`, and minimal healthcheck-capable placeholders only. Configure Redis on the internal Compose network. Do not add business logic or real PyKRX calls in this task.
  Parallelization: Wave 1 | Blocked by: none | Blocks: all later todos
  References (executor has NO interview context - be exhaustive): `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/specs/deep-interview-finance-os-dashboard.md:187-214`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/specs/deep-interview-finance-os-dashboard.md:166-183`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:61-77`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:81-85`
  Acceptance criteria (agent-executable): `docker compose config` exits 0; `docker compose up --build -d redis backend data-service frontend` starts all services; `docker compose ps` reports running/healthy or starting services without fatal exits; root `make down` or equivalent stops the stack.
  QA scenarios (name the exact tool + invocation): happy: `docker compose up --build -d && docker compose ps` must show all four services present, evidence `.omo/evidence/task-1-foundation.txt`; failure: temporarily run `docker compose --env-file /tmp/missing-finance-os.env config` or unset a required env in a copied config and capture the expected validation/failure path without committing the broken config, evidence `.omo/evidence/task-1-foundation.txt`.
  Commit: Y | `chore(foundation): scaffold compose workspace`

- [ ] 2. Lock API contracts, fixtures, and cross-runtime schemas
  What to do / Must NOT do: Define the canonical supply-analysis and search response schemas in the Python Pydantic models, expose/generate an OpenAPI JSON artifact, and create matching TypeScript/Zod types used by backend and frontend. Add `data-service/tests/fixtures/tdad_reference_005930_20250602_20260529.csv` with the exact header from the approved fixture recipe, plus a small backend/frontend fixture payload for contract tests. Do not invent extra response fields outside the approved schema unless they are documented and validated in all runtimes.
  Parallelization: Wave 2 | Blocked by: 1 | Blocks: 3, 4, 5, 6, 7, 8
  References (executor has NO interview context - be exhaustive): `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/specs/deep-interview-finance-os-dashboard.md:109-137`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:97-100`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:253-259`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:220`
  Acceptance criteria (agent-executable): `uv run pytest tests/test_contracts.py` passes in `data-service/`; `bun test tests/contracts.test.ts` passes in `backend/`; TypeScript Zod schemas reject malformed stock codes, malformed dates, and missing oscillator fields.
  QA scenarios (name the exact tool + invocation): happy: `curl -s http://localhost:${PYTHON_SERVICE_PORT:-8000}/openapi.json | jq '.paths["/stocks/{stock_code}/supply-analysis"].get'` shows the supply-analysis contract after Task 4 wires the app, evidence `.omo/evidence/task-2-data-contract.txt`; failure: `bun test tests/contracts.test.ts --test-name-pattern invalid` must show invalid query/body cases rejected, evidence `.omo/evidence/task-2-data-contract.txt`.
  Commit: Y | `feat(contract): define supply analysis schemas`

- [ ] 3. Implement and prove the oscillator calculation core
  What to do / Must NOT do: Implement `data-service/src/indicators/supply_oscillator.py` as a pure calculation over typed rows/dataframes with polars EMA parameters `span=12`, `span=26`, `span=9`, `adjust=False`. Include raw `supply_ratio`, `ema12`, `ema26`, `macd`, `signal`, and `oscillator` values in the output. Write the failing fixture regression first, then make it pass. Do not call PyKRX, Redis, FastAPI, or live network from these tests.
  Parallelization: Wave 2 | Blocked by: 1 and fixture header from 2 | Blocks: 4, 5, 6, 7, 8
  References (executor has NO interview context - be exhaustive): `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/specs/deep-interview-finance-os-dashboard.md:29-37`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:5-15`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:91-97`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:248-252`
  Acceptance criteria (agent-executable): `uv run pytest tests/test_supply_oscillator.py` passes; the test asserts fixture output within `1e-12` and asserts `oscillator == macd - signal` for every output row; `uv run ruff check .` and `uv run basedpyright` pass in `data-service/`.
  QA scenarios (name the exact tool + invocation): happy: `uv run pytest tests/test_supply_oscillator.py -q` passes and logs the checked fixture row count, evidence `.omo/evidence/task-3-oscillator.txt`; failure: `uv run pytest tests/test_supply_oscillator.py -q -k rejects_unsorted_or_missing_columns` proves bad fixture/input is rejected with a typed error, evidence `.omo/evidence/task-3-oscillator.txt`.
  Commit: Y | `feat(data-service): compute supply oscillator`

- [ ] 4. Build data-service APIs, KRX adapter, search data, locks, and scheduler
  What to do / Must NOT do: Implement FastAPI app structure under `data-service/src/`, PyKRX adapter, in-memory `krx_listed_stocks.json` search, `GET /health`, `GET /stocks/search`, `GET /stocks/{stock_code}/supply-analysis`, per-key single-flight around fetch/compute, Redis interaction where required by the approved plan, and APScheduler invalidation of `supply:*` at `15:35` `Asia/Seoul`. Do not make unit tests depend on live PyKRX; isolate PyKRX behind an adapter fake. Do not pre-warm cache.
  Parallelization: Wave 3 | Blocked by: 2, 3 | Blocks: 5, 6, 7, 8
  References (executor has NO interview context - be exhaustive): `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/specs/deep-interview-finance-os-dashboard.md:57-67`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/specs/deep-interview-finance-os-dashboard.md:93-106`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:87-118`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:280-285`
  Acceptance criteria (agent-executable): `uv run pytest` passes in `data-service/`; a fake adapter test proves 10 concurrent identical requests invoke the adapter once; scheduler test proves `supply:*` keys are deleted and unrelated keys remain; `/stocks/search?q=삼성` returns `005930`.
  QA scenarios (name the exact tool + invocation): happy: with the service running, `curl -i "http://localhost:${PYTHON_SERVICE_PORT:-8000}/stocks/005930/supply-analysis?start=2025-12-01&end=2026-06-01"` returns 200 with schema-valid JSON, evidence `.omo/evidence/task-4-data-api.txt`; failure: `curl -i "http://localhost:${PYTHON_SERVICE_PORT:-8000}/stocks/ABC/supply-analysis"` returns 422 or 400 with a typed validation error, evidence `.omo/evidence/task-4-data-api.txt`.
  Commit: Y | `feat(data-service): expose supply APIs`

- [ ] 5. Build backend gateway, Redis cache, retry policy, fallback, and single-flight
  What to do / Must NOT do: Implement Bun/Elysia app under `backend/src/` with Redis client, data-service HTTP client, 10s timeout, exponential backoff `200 ms * 2^n`, 5s cap, max 5 retries, jitter, `/health` polling every 30s, fail-fast `503` when upstream is unhealthy, search proxy, supply-analysis proxy/cache, cached fallback on upstream failure, and TypeScript `Map<string, Promise<...>>` single-flight cleanup. Do not compute oscillator in TypeScript.
  Parallelization: Wave 3 | Blocked by: 2, 3, 4 contract/health | Blocks: 6, 7, 8
  References (executor has NO interview context - be exhaustive): `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/specs/deep-interview-finance-os-dashboard.md:41-48`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/specs/deep-interview-finance-os-dashboard.md:84-90`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:120-169`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:212-221`
  Acceptance criteria (agent-executable): `bun test` passes in `backend/`; tests cover validation, cache hit, cache miss, Redis unavailable direct path, upstream unhealthy fail-fast, cached fallback, search proxy, `/health`, and 10 concurrent identical cache misses calling the fake upstream exactly once; `bunx biome check .` and `bunx tsc --noEmit` pass.
  QA scenarios (name the exact tool + invocation): happy: `curl -i "http://localhost:${BACKEND_PORT:-3000}/api/v1/stocks/005930/supply-analysis?start=2025-12-01&end=2026-06-01"` returns 200 and a second identical call records server-side cache hit under 100ms, evidence `.omo/evidence/task-5-backend-cache.txt`; failure: stop or fake-fail data-service after priming Redis, then repeat the same curl and verify `UPSTREAM_UNAVAILABLE` plus last cached value behavior matches the implemented contract, evidence `.omo/evidence/task-5-backend-cache.txt`.
  Commit: Y | `feat(backend): proxy and cache supply analysis`

- [ ] 6. Build frontend shell, search, and chart integration
  What to do / Must NOT do: Implement React/Vite frontend under `frontend/src/` with centralized TDS tokens, Pretendard font stack, `TopBar`, `Sidebar`, `CollapsibleRightPanel`, `MainLayout`, `StockSearch`, `SupplyChart`, route/search state, period buttons, tooltip, `dataZoom`, and backend API integration. Use generated/shared types or Zod validation at the API boundary. Do not hard-code colors outside token files. Do not create a marketing landing page; first screen is the dashboard.
  Parallelization: Wave 4 | Blocked by: 2, 5 API shape | Blocks: 7, 8
  References (executor has NO interview context - be exhaustive): `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/specs/deep-interview-finance-os-dashboard.md:18-28`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/specs/deep-interview-finance-os-dashboard.md:141-163`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:171-181`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:198-205`
  Acceptance criteria (agent-executable): `bun test`, `bunx biome check .`, and `bunx tsc --noEmit` pass in `frontend/`; component tests prove search debounce/dropdown/keyboard selection, period button API params, chart option includes two y-axes, tooltip, and `dataZoom`.
  QA scenarios (name the exact tool + invocation): happy: Playwright `page.goto("http://localhost:${FRONTEND_PORT:-5173}")`, fill search with `삼성`, select `삼성전자`, assert chart canvas/SVG is nonblank and period buttons update visible range, evidence `.omo/evidence/task-6-frontend-shell.txt`; failure: mock backend 500 or invalid schema, assert user-facing error state appears and no stale chart silently claims success, evidence `.omo/evidence/task-6-frontend-shell.txt`.
  Commit: Y | `feat(frontend): render supply dashboard`

- [ ] 7. Prove the full stack, concurrency, latency, and E2E behavior
  What to do / Must NOT do: Add full-stack scripts/tests that boot Docker Compose, run health/API checks, run concurrency checks, run Playwright E2E, capture response-time evidence, and tear the stack down. Do not rely on manual browser inspection or unstored terminal output.
  Parallelization: Wave 5 | Blocked by: 1-6 | Blocks: 8 and final wave
  References (executor has NO interview context - be exhaustive): `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/specs/deep-interview-finance-os-dashboard.md:218-245`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:183-206`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:275-288`
  Acceptance criteria (agent-executable): `docker compose up --build` reaches healthy/running state within 60 seconds; backend `/health` returns 200 with `status`, `redis`, `dataService`; search `삼성` returns `005930` within 300ms; cache hit is under 100ms server-side; cold 6-month request is under 5s; 10 concurrent identical misses trigger one PyKRX/fake scrape; Playwright E2E passes against Compose.
  QA scenarios (name the exact tool + invocation): happy: `./scripts/qa/full-stack.sh` or equivalent runs Compose, curl health/search/supply, concurrency probe, and Playwright, evidence `.omo/evidence/task-7-e2e.txt`; failure: `./scripts/qa/full-stack.sh --simulate-upstream-down` proves health/fail-fast/cached fallback behavior, evidence `.omo/evidence/task-7-e2e.txt`.
  Commit: Y | `test(e2e): verify finance dashboard stack`

- [ ] 8. Document handoff, ADR, and post-MVP boundaries
  What to do / Must NOT do: Write `README.md`, `docs/api.md`, `docs/adr/0001-compute-and-cache-indicator.md`, `data-service/README.md`, and any setup notes needed for `.env.example`, formula parameters, fixture extraction, local dev, QA scripts, and known post-MVP items. Mark OpenDART/dartlab as future scope unless it is needed by the first feature. Do not claim unsupported production security hardening.
  Parallelization: Wave 5 | Blocked by: 1-7 | Blocks: final wave
  References (executor has NO interview context - be exhaustive): `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/specs/deep-interview-finance-os-dashboard.md:248-275`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:223-266`, `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md:267-303`
  Acceptance criteria (agent-executable): `README.md` contains exact dev/test/down commands; ADR preserves Option A and rejected alternatives; `data-service/README.md` documents EMA parameters and fixture recipe; docs list post-MVP exclusions; all docs links point to existing files.
  QA scenarios (name the exact tool + invocation): happy: `rg -n "span=12|adjust=False|docker compose|OpenDART|post-MVP|005930" README.md docs data-service/README.md` finds expected documentation, evidence `.omo/evidence/task-8-docs.txt`; failure: run a docs link check script or `python scripts/qa/check_docs_links.py` and verify it fails on a deliberately broken temporary link but passes committed docs, evidence `.omo/evidence/task-8-docs.txt`.
  Commit: Y | `docs: document finance dashboard handoff`

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit: compare implemented files and evidence against this plan; command `python scripts/qa/check_plan_compliance.py .omo/plans/finance-os-dashboard-mvp.md`; evidence `.omo/evidence/final-qa.txt`.
- [ ] F2. Code quality review: run `uv run ruff check . && uv run basedpyright && uv run pytest` in `data-service/`, `bunx biome check . && bunx tsc --noEmit && bun test` in `backend/` and `frontend/`; evidence `.omo/evidence/final-qa.txt`.
- [ ] F3. Real manual QA: run `docker compose up --build -d`, execute health/search/supply curl checks and Playwright dashboard flow, capture screenshots or trace paths, then `docker compose down`; evidence `.omo/evidence/final-qa.txt`.
- [ ] F4. Scope fidelity: verify no OpenDART/dartlab implementation, auth, settings UI, real-time data, pre-warm, per-day chunking, or extra chart families were added; evidence `.omo/evidence/final-qa.txt`.

## Commit strategy
- One commit per todo, in dependency order.
- Use Conventional Commits exactly as listed in each todo unless the final diff changes scope materially.
- Do not commit `.env`, live credentials, build artifacts, caches, Playwright binary downloads, or generated logs outside `.omo/evidence/`.
- Final branch handoff should include a draft summary listing all commits and evidence files.
- If a worker is asked to stage or commit, include footer `Plan: .omo/plans/finance-os-dashboard-mvp.md` in the final commit message.

## Success criteria
1. `docker compose up --build` starts `backend`, `data-service`, `redis`, and `frontend` without fatal errors within 60 seconds.
2. `GET /api/v1/stocks/005930/supply-analysis?start=2025-12-01&end=2026-06-01` returns HTTP 200 with schema-valid JSON and one `data` entry per KRX trading day in the requested range, omitting non-trading days.
3. Every returned row satisfies `oscillator == macd - signal` within `1e-12`, and the EMA parameters `span=12/26/9`, `adjust=False` are documented.
4. A second identical backend supply-analysis request is served from Redis and records server-side response time under 100ms on local hardware.
5. The first request after empty cache or 15:35 KST invalidation for `005930` default 6-month range completes end-to-end within 5 seconds on local hardware.
6. Ten concurrent identical cache-miss requests call the PyKRX/fake adapter exactly once and all callers receive equivalent results.
7. `GET /api/v1/stocks/search?q=삼성` returns an array containing `{ "code": "005930", "name": "삼성전자" }` within 300ms.
8. Backend `GET /health` returns HTTP 200 with `status`, `redis`, `dataService`, and `timestamp` when dependencies are healthy.
9. Frontend search displays a matching ticker/name dropdown within 300ms of typing `삼성`, and selecting `삼성전자` updates the chart.
10. The chart renders two Y-axes, hover tooltip, zoom/pan, and period buttons whose visible spans match the approved KRX trading-day ranges: `1M` 21-23, `3M` 64-66, `6M` 125-130, `1Y` 245-252, and `ALL` full available PyKRX history.
11. After the 15:35 KST scheduler invalidates `supply:*`, the next previously cached range fetches fresh data rather than returning stale Redis data.
12. Playwright E2E passes against the full Docker Compose stack.
13. Documentation states the first MVP excludes OpenDART/dartlab implementation, auth, settings UI, real-time market data, pre-warming, and per-day cache chunking.
