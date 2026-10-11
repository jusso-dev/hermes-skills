---
name: oakattest
description: "Run IRAP assessments in OakAttest, or develop it."
version: 0.1.0
author: Justin Middler (jusso-dev)
license: MIT
metadata:
  hermes:
    tags: [OakAttest, IRAP, ISM, Essential Eight, GRC, MCP, Next.js]
    category: products
    related_skills: [crownguard]
---

# OakAttest

OakAttest is an open-source, self-hosted IRAP assessment workspace for ASD-registered assessor firms and the client organisations they assess. It covers the assessment from organisation setup through scoping, ISM applicability, evidence, fieldwork, findings, residual risk, certification and ongoing monitoring. It also has Essential Eight assessments, ISO/IEC 27001 Stage 1 and SOC 2 readiness, a trust portal, questionnaires and an AI helper called Burl. Source: [jusso-dev/OakAttest](https://github.com/jusso-dev/OakAttest), licensed AGPL-3.0-or-later. (It moved from the `yumaitau` organisation; the old path redirects. It is active, not archived.)

OakAttest does not certify systems, and ASD does not endorse it. It helps assessors and clients build the artefacts that inform an authorisation decision.

## When to Use

- The user wants an agent to run or support an IRAP, Essential Eight, ISO 27001 or SOC 2 readiness engagement in their OakAttest deployment.
- The user wants to connect an MCP client to OakAttest.
- The user wants to change, test or self-host the OakAttest code.
- Not for giving a certification opinion. Assessor judgement stays with the human assessor.

## Part A: using OakAttest over MCP

### Connect

1. A tenant owner opens **Tenant admin**, then **Agent automation (MCP)**, and creates a named token. It is shown once and stored only as a SHA-256 digest.
2. Configure the client with `https://<your-oakattest-host>/api/mcp` (Streamable HTTP) and `Authorization: Bearer <token>`. Keep the token in the client's secret store or an environment variable, never in chat or a repo.
3. Call `get_capabilities` first. It returns the authoritative tool order and the upload protocol.

A token acts as the person who created it, with their current tenant and engagement permissions. Every tool call is written to the audit log.

### Tools

`get_capabilities`, `list_frameworks`, `list_clients`, `create_client`, `list_assessments`, `create_assessment`, `get_assessment`, `update_assessment_state`, `list_controls`, `decide_control_applicability`, `record_control_assessment`, `create_evidence_request`, `list_evidence`, `start_evidence_upload`, `finalize_evidence_upload`, `review_evidence`, `download_evidence`, `create_finding`, `update_finding_status`, `record_finding_retest`, `configure_audit_readiness`, `get_audit_readiness`, `update_audit_requirement`, `invite_engagement_member`, `invite_auditor`, `generate_audit_package`, `download_audit_package`.

### Evidence upload

1. `start_evidence_upload` with the exact filename, MIME type, byte length and the related request or control ids.
2. `PUT` the raw bytes to the returned `uploadUrl` with every returned header. The URL lasts ten minutes.
3. Compute SHA-256 over exactly those bytes.
4. `finalize_evidence_upload` with the evidence id and digest. OakAttest re-hashes the stored bytes before the item becomes usable.

### Rules for agents

- Respect role boundaries. An assessor token can request and review evidence but cannot write client implementation statements or upload client evidence. Do not look for a way around this; independence is the point.
- Draft, do not decide. Suggest applicability, control outcomes and findings, then let the assessor confirm. Burl works the same way.
- Confirm before inviting anyone (`invite_engagement_member`, `invite_auditor`), changing assessment state, closing findings or generating audit packages.
- Evidence and findings describe a client's weaknesses and may be classified up to PROTECTED. Do not copy them outside OakAttest or into chat beyond what the user asked for.
- Only upload material the deployment is authorised to store.

## Part B: developing and self-hosting

### Stack and layout

- Next.js (App Router), TypeScript, Drizzle ORM on PostgreSQL, Better Auth, React Email, Vitest, Playwright. Object storage is S3-compatible (Cloudflare R2 or AWS S3).
- `app/`: routes, server actions, auth and admin. `app/api/mcp` is the MCP endpoint.
- `lib/`: `mcp/` (server and token auth), `rbac/`, `audit/`, `irap/`, `evidence/`, `findings/`, `certification/`, `frameworks/`, `connectors/`, `burl/`, `pdf/`, `xlsx/`, `storage/`.
- `db/schema`, `db/migrations`, `db/seed`: schema, migrations and seed data.
- `docs/`: `ARCHITECTURE.md`, `RBAC.md`, `MCP.md`, `FRAMEWORK_PACKS.md`, `ASSURANCE_LIFECYCLE.md`, `TRUST_PORTAL.md`, `INFRASTRUCTURE.md` and others.

### Commands

```bash
cp .env.example .env
npm install
docker compose up -d postgres
npm run db:migrate
npm run db:seed
npm run dev          # http://localhost:3000
npm run lint
npm run typecheck
npm test
npm run build
```

Key settings: `DATABASE_URL`, `BETTER_AUTH_URL`, `NEXT_PUBLIC_BETTER_AUTH_URL`, `BETTER_AUTH_SECRET`, storage (`R2_*` or `S3_*`), email, `CRON_SECRET`, and for MCP in production `MCP_ALLOWED_HOSTS` and `MCP_ALLOWED_ORIGINS`. Burl uses `OAK_AI_PROVIDER`: `bedrock` with a Bedrock model id, or `hermes` with `OAK_AI_HERMES_BASE_URL`, `OAK_AI_HERMES_API_KEY` and `OAK_AI_HERMES_MODEL` to use a Hermes Agent gateway. See `.env.example` for the full list.

### Pitfalls

- `AGENTS.md` warns that this Next.js version differs from older docs. Read the guide in `node_modules/next/dist/docs/` before changing framework code.
- The README lists `npm run ism:import`, but `package.json` has `framework:import`. Check `package.json` before running a script.
- Apply all migrations (MCP tokens need `0018_mcp_api_tokens`) before issuing MCP tokens.
- Every mutating action must keep its audit event and RBAC check. Add tests under `__tests__/rbac` when you touch permissions.
- AGPL-3.0: modified versions offered over a network must make their source available.

### Safety rules

- Use disposable accounts and fictional clients for local work and screenshots (`npm run screenshots:readme` already does this).
- Never commit `.env`, signing secrets, AWS or R2 keys, or real assessment material.
- Do not run migrations or seeds against a production database unless the user asks for that exact step.

## Verification

- Part A: read back what changed (`get_assessment`, `list_evidence`, `get_audit_readiness`) and report it.
- Part B: lint, typecheck, `npm test` and build pass.
