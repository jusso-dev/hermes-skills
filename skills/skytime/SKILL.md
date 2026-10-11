---
name: skytime
description: "Log and report time in SkyTime, or work on its code."
version: 0.1.0
author: Justin Middler (jusso-dev)
license: MIT
metadata:
  hermes:
    tags: [SkyTime, timesheets, time tracking, MCP, Next.js, Cloudflare]
    category: products
    related_skills: []
---

# SkyTime

SkyTime is a multi-tenant time tracking app: timers and manual time entries, clients, projects, task boards, weekly timesheet approvals, reports with PDF and CSV export, expenses and invoices, capacity planning and time off. The hosted instance is at `https://skytime.yarndigi.com.au`. The source is public at [jusso-dev/SkyTime](https://github.com/jusso-dev/SkyTime) (MIT).

This skill has two parts. Part A is for using SkyTime through its MCP server or REST API. Part B is for developing on the codebase.

## When to Use

- The user asks you to start or stop a timer, log time, fix an entry, submit a week, or summarise hours for a period, project or client.
- The user asks you to set up an MCP client or script against SkyTime.
- The user asks you to change, test or deploy the SkyTime code.
- Not for other time trackers (Toggl, Harvest, Clockify).

## Part A: using SkyTime

### Connect

1. The user signs in to SkyTime in a browser and opens **API & MCP**.
2. They create a personal access token: a name, **read only** or **read and write**, and an expiry of 1 to 365 days. The token is shown once.
3. The token goes into the MCP client's secret configuration or an environment variable. Never ask the user to paste it into chat, and never write it into a file you commit.
4. MCP settings: endpoint `<SKYTIME_URL>/api/mcp`, transport **Streamable HTTP**, header `Authorization: Bearer <token>`. OAuth and legacy SSE are not supported. GET and DELETE on the endpoint return 405 by design.

```json
{
  "mcpServers": {
    "skytime": {
      "url": "https://skytime.yarndigi.com.au/api/mcp",
      "headers": { "Authorization": "Bearer ${SKYTIME_TOKEN}" }
    }
  }
}
```

The `${SKYTIME_TOKEN}` placeholder only works if your client expands environment variables in its config. Otherwise use the client's own secret store.

For REST, set `SKYTIME_URL` and `SKYTIME_TOKEN` in the environment and call `$SKYTIME_URL/api/v1/...` with the same bearer header.

A token belongs to one user in one organisation. A read-only token cannot change anything. Bearer tokens cannot create more tokens. Role changes and revocation apply immediately.

### Discover before you act

- MCP `tools/list`, or `GET /api/v1/actions`, returns every action with its JSON Schema. `GET /api/v1/openapi.json` is the OpenAPI 3.1 spec.
- Tool annotations say whether an action reads, writes, is destructive or sends invitation email. Check them before calling.
- Main tools: `timer_get`, `timer_start`, `timer_stop`, `time_entries_list`, `time_entries_create`, `time_entries_update`, `time_entries_duplicate`, `time_entries_resume`, `time_entries_bulk_update`, `time_entries_import`, `time_entries_delete`, `projects_list`, `clients_list`, `tasks_list`, `tags_list`, `timesheets_create`, `timesheets_transition`, `reports_summary`, `reports_export`, `saved_reports_create`, `expenses_create`, `invoices_create`, `invoices_export`, `allocations_create`, `workload_report`, `time_off_create`, `time_off_review`.

### Workflows

- **Start and stop a timer**: `projects_list` to find the project id, `timer_get` to make sure nothing is already running, `timer_start`, later `timer_stop` with the timer id.
- **Log a day after the fact**: `projects_list` (and `tasks_list` if the user names a task), then one `time_entries_create` per block, or `time_entries_import` for up to 100 entries in one atomic call. Read back with `time_entries_list` for that day and show the user the totals.
- **Weekly summary**: `reports_summary` for Monday to Sunday, grouped by project or client. Dates are inclusive and use the organisation's time zone. Offer `reports_export` with `pdf` or `csv` if they want a file.
- **Submit a week**: `timesheets_create` with any date in the week (weeks are UTC), then `timesheets_transition` with `submit`. Admins can `approve`, `reject` or `reopen`.
- **Invoice**: `expenses_create` as needed, then (admin) `invoices_create`, `invoices_export`, `invoices_update`.
- **Plan capacity**: (admin) `members_update` for weekly capacity, `allocations_create`, then `workload_report`.

### Rules for agents

- Durations are integer milliseconds. Timestamps are ISO 8601 with an offset. Convert the user's local times carefully and say which time zone you used.
- Do not retry a write blindly after a timeout. Read the current state first. Only `timer_stop` is safe to retry. Other creates take no idempotency key and can duplicate.
- Approved weeks and invoiced entries are locked. If an edit is refused, explain the lock rather than working around it.
- Confirm before deleting entries, bulk edits, submitting or approving timesheets, creating invoices, or inviting members (invites send email).
- Exports come back over MCP as an embedded resource with base64 content. Save the file rather than printing the bytes.
- Amounts are kept separate by currency. Do not add different currencies together.

## Part B: developing SkyTime

### Stack and layout

- Next.js app in `src/client/next-landing-page`, run on Cloudflare Workers in production through vinext. React, Tailwind, Better Auth (passkeys, two-factor), Zod, pdfkit, `@modelcontextprotocol/sdk`.
- Database: SQLite file locally (`data/skytime.sqlite`, override with `SKYTIME_SQLITE`) through `node:sqlite`; Cloudflare D1 in production. Logos go to `data/attachments/` locally and R2 in production.
- `lib/automation/actions.ts`, `schemas.ts`, `services.ts`, `planning.ts`: the action registry. REST `/api/v1/*` and MCP `/api/mcp` are both generated from it, so a new action belongs here.
- `db/schema.sql` and `db/schema-sql.ts`: schema, including the SQLite triggers that enforce approval and invoice locks. `scripts/migrate.mjs` applies it.
- `lib/tenant.ts`, `lib/audit.ts`, `lib/errors.ts`, `lib/reports/*`: tenancy checks, audit log, error capture and PDF/CSV reports.
- `app/api/*`: legacy unversioned routes used by the UI, plus `app/api/v1` and `app/api/mcp`.
- `e2e/*.spec.ts`: Playwright suites. `docs/api.md` and `docs/mcp.md` document the API.
- `workers/d1-backup`: a separate Worker for D1 backups.

### Commands

From `src/client/next-landing-page`:

```bash
npm ci
npm run auth:migrate     # Better Auth tables
npm run db:migrate       # SkyTime schema
npm run dev              # http://localhost:3000
npm run type-check
npm run build
npx playwright install chromium
npm run test:integration # API, MCP and browser tests on data/skytime-test.sqlite
npm run dev:vinext       # Workers runtime locally on port 3001
```

Set `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL` and `NEXT_PUBLIC_APP_URL` before building. To match CI, point the URLs at `http://127.0.0.1:3100`, build, then run `CI=1 npm run test:integration`.

### Pitfalls

- D1 has no interactive transactions. Each statement commits on its own, so business rules live in SQLite triggers and guarded updates (for example invoice creation only claims rows whose `invoice_id` is still null). Keep it that way.
- Both migrations are required after schema changes, and they must stay additive and repeatable. CI runs them twice.
- Add new behaviour to the action registry, not as a one-off route, so REST, MCP and audit stay in step.
- The README and `.env.example` mention a Postgres `DATABASE_URL` and Resend settings. The app itself uses SQLite or D1, and the Postgres scripts in `docker/` are not the app database. Check `lib/db.ts` and `lib/email.ts` for current behaviour.
- `AGENTS.md` in the app folder warns that this Next.js version differs from older docs. Read the guide in `node_modules/next/dist/docs/` before changing framework code.

### Safety rules

- Use fictional users and organisations in tests. Never point tests or scripts at the production instance.
- Do not run `npm run deploy:vinext` or touch production D1 or R2 unless the user asks for that exact step.
- Never commit tokens, `BETTER_AUTH_SECRET` or Cloudflare credentials.

## Verification

- Part A: read back what you changed (`timer_get`, `time_entries_list`, `reports_summary`) and report totals in hours and minutes.
- Part B: `npm run type-check`, `npm run build` and `npm run test:integration` pass.
