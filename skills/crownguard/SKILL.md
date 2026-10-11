---
name: crownguard
description: "Run crown-jewel risk assessments with crownguard."
version: 0.1.0
author: Justin Middler (jusso-dev)
license: MIT
metadata:
  hermes:
    tags: [crownguard, crown jewels, risk assessment, Essential Eight, CIS, Microsoft 365, Google Workspace, AWS]
    category: products
    related_skills: [m365-secure]
---

# crownguard

crownguard is a guided crown-jewel risk assessment for Microsoft 365, Google Workspace and AWS, with optional Azure and Google Cloud modules. The user names the systems and data that would hurt most if compromised, answers plain-language control questions drawn from vendor guidance, and gets a branded PDF. Questions map to CIS Benchmarks, the ASD Essential Eight, NIST CSF 2.0, the ISM and the Home Affairs Industry Data Classification Framework. Optional parts cover SOC maturity and an AI use-case register based on DTA policy.

It runs entirely in the browser with no backend, account or analytics. Hosted at [jusso-dev.github.io/crownguard](https://jusso-dev.github.io/crownguard/). Source: [jusso-dev/crownguard](https://github.com/jusso-dev/crownguard) (MIT code; some content folders use CC licences, see its README).

## When to Use

- The user wants to run or help with a crown-jewel or cloud security risk assessment for an organisation.
- The user wants to pre-fill an assessment from M365-Secure, Prowler or ScubaGoggles results.
- The user wants to score an assessment, render the PDF or export the AI register without a browser.
- The user wants to change crownguard questions, content or code.
- Not an audit. It is a self-assessment that does not connect to the tenant. Say so in anything you produce.

## Headless use (for agents)

Run from a checkout of the repository. Pin a release tag when one exists, so results are reproducible.

```sh
git clone https://github.com/jusso-dev/crownguard.git && cd crownguard
pnpm install
pnpm cg catalogue --platform microsoft --out catalogue.json
pnpm cg new --org "Example Pty Ltd" --platforms microsoft,aws --out example.crownguard.json
pnpm cg import example.crownguard.json ./scan.json --tool auto --licence
pnpm cg score example.crownguard.json --format text
pnpm cg render example.crownguard.json report.pdf
pnpm cg render example.crownguard.json ai-register.pdf --kind ai-register
pnpm cg ai-register export example.crownguard.json --format xlsx --out register.xlsx
pnpm cg migrate old.crownguard.json --out current.crownguard.json
pnpm cg validate example.crownguard.json
```

JSON goes to stdout and messages to stderr. Exit codes: 0 ok, 1 invalid input, 2 content error, 3 unexpected. The `.crownguard.json` format is versioned and documented in `docs/file-format.md`, with a JSON Schema. `docs/cli.md` lists every option.

This CLI replaces the old `cg-bot` helper used by the Crown Jewel Risk Assessor profile in `jusso-dev/hermes-agent-profiles`. Do not copy helper scripts into the crownguard tree.

## Procedure for an assessment

1. Confirm the organisation, the platforms in scope and their licence tiers.
2. Work through crown jewels by category: identity plane, privileged access, business data, collaboration and email, endpoints, cloud, AI assistants. For each, record classification, confidentiality, integrity and availability ratings, and the exposures that apply.
3. Answer control questions with the user. Use Unknown when they do not know. Unknown scores 0, because uncertainty is not protection. N/A needs a written reason or it counts as unanswered.
4. If they have scanner output, import it. M365-Secure JSON, Prowler CSV or JSON-OCSF and ScubaGoggles results pre-fill only where the checks are decisive. Every pre-filled answer keeps its evidence and can be changed.
5. Score, review the top risks and the 30/60/90-day roadmap with the user, then render the PDF.

Scoring in brief: Yes 1, Partial 0.5, No, Unknown and unanswered 0; weights Critical 4, High 3, Medium 2, Low 1; impact times likelihood on a 5 by 5 matrix. Essential Eight maturity is indicative only. Never assign an IDCF Data Security Level for the user; the data owner chooses it.

## Developing

- Stack: Vite, React, TypeScript, Tailwind, Zustand, Zod, `@react-pdf/renderer`, Vitest, Playwright.
- `content/`: all questions, categories, framework mappings and sources as YAML. Most improvements happen here. See `docs/content-guide.md`.
- `src/engine` (scoring), `src/wizard` (UI steps), `src/report` (PDF), `src/imports` (scanner importers), `src/lib/index.ts` (stable library surface), `src/cli` (headless CLI).
- `scripts/watch` and `watch/state.json`: the nightly source watch that opens pull requests when cited pages break, move or change.

```sh
pnpm dev                 # http://localhost:5173
pnpm test
pnpm lint
pnpm typecheck
pnpm validate:content
pnpm build
pnpm test:e2e
```

## Pitfalls

- Content must cite its sources. `pnpm validate:content` rejects sources that nothing cites.
- CIS Benchmarks are referenced by number and title only. Do not paste benchmark text.
- `content/soc/` is CC BY-SA 4.0. Keep its NOTICE when editing.
- The PDF is not yet tagged for screen readers. Point users who need that to the on-screen Review step.

## Safety rules

- Assessment files can describe an organisation's weaknesses. Keep them out of git and out of public places. Suggest the passphrase option or no-persistence mode for sensitive work.
- Use fictional organisations in examples and tests.
- Do not present the output as an audit, certification or legal advice.

## Verification

- `pnpm cg validate` passes on the assessment file before rendering.
- For code: test, lint, typecheck, validate:content and build pass.
