---
slug: finance-os-dashboard-mvp
status: plan-written
intent: clear
pending-action: write .omo/plans/finance-os-dashboard-mvp.md
approach: Convert the provided Finance OS Dashboard MVP consensus into one decision-complete execution plan for a Docker Compose local stack: Python FastAPI data-service computes the supply oscillator with PyKRX/polars, Bun/Elysia backend proxies and caches via Redis with single-flight, React/ECharts frontend renders search and chart UX, and verification covers formula regression, cache/single-flight behavior, health checks, and Playwright E2E.
---

# Draft: finance-os-dashboard-mvp

## Components (topology ledger)
<!-- Lock the SHAPE before depth. One row per top-level component that can succeed or fail independently. -->
<!-- id | outcome (one line) | status: active|deferred | evidence path -->
| id | outcome (one line) | status | evidence path |
| --- | --- | --- | --- |
| foundation | One-command Docker Compose local stack with env docs, service health checks, and dev/test commands. | active | `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md` |
| data-service | Python service fetches KRX data, computes audited oscillator values, serves search and supply-analysis APIs, and invalidates Redis cache after market close. | active | `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md` |
| backend | Bun/Elysia gateway validates requests, proxies data-service, retries/fails fast on upstream health, caches in Redis, and coalesces identical cache misses. | active | `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md` |
| frontend | React/ECharts UI implements TDS/Pretendard shell, stock search, period controls, dual-axis chart, tooltip, and zoom/pan. | active | `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md` |
| verification | Unit, integration, real-surface API, Docker Compose, and Playwright evidence prove formula correctness and end-to-end behavior. | active | `.gjc/_session-019f112a-2128-7000-aa5f-5680ddfc6476/plans/ralplan/019f112a-2128-7000-aa5f-5680ddfc6476/pending-approval.md` |

## Open assumptions (announced defaults)
<!-- Record any default you adopt instead of asking, so the user can veto it at the gate. -->
<!-- assumption | adopted default | rationale | reversible? -->
| assumption | adopted default | rationale | reversible? |
| --- | --- | --- | --- |
| Existing accidental scaffold | Removed from scope; the executable plan starts from the empty `steady-n-wise` project plus `.gjc` state. | The user requested a plan file workflow, and the Finance OS plan requires a multi-runtime app, not the minimal Python scaffold created earlier. | Yes |
| Intent route | CLEAR. | The supplied file already defines the desired MVP, architecture option, tasks, acceptance criteria, risks, and ADR. | Yes |
| Plan slug | `finance-os-dashboard-mvp`. | Matches the supplied consensus title and is lowercase/kebab-case for the ulw-plan scaffold. | Yes |
| High-accuracy plan review | Offered after plan generation, not automatic. | CLEAR intent path makes dual Momus review optional at delivery. | Yes |

## Findings (cited - path:lines)
- The supplied consensus chooses Option A: Python FastAPI data service computes oscillator with PyKRX/polars, Redis caches, ElysiaJS acts as gateway, and ECharts renders the chart.
- The accepted sequencing is vertical slices: foundation, data service, backend gateway/cache, frontend shell, search, chart integration, verification, hardening/handoff.
- The locked oscillator formula is `supply_ratio`, EMA12, EMA26, MACD, Signal, Oscillator using polars `ewm_mean(span=12/26/9, adjust=False)`.
- The acceptance criteria include Docker Compose boot, API schema/trading-day coverage, oscillator arithmetic tolerance, Redis cache hit latency, cold-start latency, single-flight scrape count, search latency, backend health, frontend search/chart UX, scheduler invalidation, and Playwright E2E.
- Current `steady-n-wise` contains no product code after cleanup; `.omo` now contains the ulw-plan scaffold for this slug.
- Evaluation improvement: the executable plan makes OpenDART/dartlab explicitly out of scope for the first MVP slice, because the first feature only needs PyKRX market-cap/net-buy data and the original deep-interview spec lists OpenDART/dartlab as broader data-service capability.
- Evaluation improvement: the executable plan requires fixture/fake-based tests before live PyKRX behavior, so finance logic and concurrency can be proven without network flake.
- Evaluation improvement: the executable plan adds cross-runtime schema/type sharing and Zod validation to reduce Python/TypeScript contract drift.
- Evaluation improvement: the executable plan turns cache fallback, latency, scheduler invalidation, and single-flight behavior into concrete QA artifacts instead of informal acceptance notes.

## Decisions (with rationale)
- Preserve the supplied Option A architecture because it is the consensus recommendation and keeps finance-critical time-series calculation in the Python/polars service.
- Keep range-keyed Redis cache for MVP because the supplied ADR explicitly accepts duplicate overlapping ranges as a simplicity tradeoff.
- Treat `ALL` as empty `start`/`end` or omitted params because the supplied ADR locks that contract.
- Defer pre-warming and per-day cache chunking because the supplied consensus names them as post-MVP optimizations.
- Generate one execution plan with waves aligned to independently verifiable vertical slices, not a monolithic backend-first build.

## Scope IN
- Create a decision-complete `.omo/plans/finance-os-dashboard-mvp.md` from the supplied consensus after explicit approval.
- Include exact file paths, implementation waves, acceptance criteria, happy/failure QA scenarios, evidence paths, and commit strategy.
- Include guardrails for formula correctness, Redis cache/single-flight behavior, health checks, Docker Compose startup, frontend chart behavior, and Playwright E2E.
- Preserve the supplied architecture and ADR decisions unless the user changes scope before approval.

## Scope OUT (Must NOT have)
- Do not implement product code while in ulw-plan mode.
- Do not replace the consensus architecture with a different stack.
- Do not add speculative post-MVP optimizations such as pre-warming, per-day Redis chunks, pagination, or alternate charting libraries.
- Do not keep the accidental minimal Python scaffold as part of the Finance OS plan.

## Open questions
- None blocking. The supplied consensus plan is specific enough to convert into a decision-complete work plan.

## Approval gate
status: approved-and-written
completed action: wrote `.omo/plans/finance-os-dashboard-mvp.md`
approval source: user said "승인. 기존 계획 평가한 후 개선항목이 있다면 개선하고 .omo 계획으로 작성해."
implementation authorization: not granted; this remains a planning handoff only.
<!-- When exploration is exhausted and unknowns are answered, set status: awaiting-approval. -->
<!-- That durable record is the loop guard: on a later turn read it and resume at the gate instead of re-running exploration. -->
