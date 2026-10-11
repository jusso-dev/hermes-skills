---
name: junction
description: "Call Microsoft APIs safely with Junction, or develop it."
version: 0.1.0
author: Justin Middler (jusso-dev)
license: MIT
metadata:
  hermes:
    tags: [Junction, Microsoft Graph, Azure, Defender, Sentinel, MCP, Rust]
    category: products
    related_skills: [m365-secure]
---

# Junction

Junction is a Rust runtime for Microsoft's public APIs. It turns official Microsoft specifications (Graph, Azure Resource Manager, Sentinel, Defender, Purview, Power Platform, Power BI, Fabric and the Office 365 Management Activity API) into one versioned catalogue of about 20,000 operations, then runs them through a CLI, a terminal UI, a stdio MCP server and a local HTTP API. Policy is read-only by default. Source: [jusso-dev/junction](https://github.com/jusso-dev/junction) (MIT).

Junction is independent and not affiliated with or endorsed by Microsoft. It is a prerelease. Representative read-only calls have been tested against a live tenant; most write operations and many credential flows have not. Keep the [disclaimer](https://github.com/jusso-dev/junction/blob/main/DISCLAIMER.md) in mind and say so when it matters.

## When to Use

- The user wants to find, describe or call a Microsoft Graph, Azure, Defender, Sentinel, Fabric or Power Platform operation.
- The user wants to wire Junction into an agent as an MCP server, or run its local HTTP API.
- The user wants to change or test the Junction code, catalogues or generators.
- Not for granting permissions or bypassing licensing. Junction only sends requests the credentials already allow.

## Install

Prebuilt binaries for Linux x86_64, macOS Apple Silicon and Windows x86_64 are published as GitHub prereleases with a `.sha256` file next to each archive. Download the archive for the platform, check the checksum, then extract it. Or build from source with Rust 1.89 or newer:

```sh
cargo build --release   # target/release/junction
```

## Find and inspect operations (no credentials needed)

```sh
junction search "list users" --product graph --limit 5
junction describe graph.users.list          # metadata plus input JSON Schema
junction permissions graph.users.list --json
junction api products
junction api aliases                        # intune.*, entra.*, purview.* names that map to Graph
junction tui                                # browse the catalogue
```

Always `describe` before `execute`. The input envelope is `{"parameters": {...}, "body": {...}}` and unknown fields are rejected.

## Run operations

1. Set up a context: copy an example from `examples/` (for example `execution-context.json`), set the tenant and cloud, then `junction context add <name> --file <file>`. Context files hold configuration only, never credentials. They live under `.junction/contexts` in the working directory.
2. Supply credentials through the environment or the OS credential store, never in a context file or chat:
   - App credentials: `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` (the tenant must match the context).
   - Interactive: `junction --context <name> auth login --client-id <app-id>` (device code or browser).
   - Existing Azure CLI login, managed identity, certificates and workload identity are also supported. See `docs/AUTHENTICATION.md`.
3. Execute:

```sh
junction --context <name> execute graph.users.list --input '{}'
junction --context <name> execute graph.users.list --input '{}' --all   # bounded paging
junction --context <name> batch --input-file batch.json
```

Policy modes are `read-only` (default), `safe-write` and `full`. A policy file can deny operations and pin tenants (see `examples/policy.toml`). Destructive and privileged operations always return `approval_required`. Only a person at the terminal can approve them, with `--approve` or `junction approvals issue`.

## Use from an agent (MCP)

Configure the MCP client to run `junction` over stdio, for example with arguments `["--context", "<name>", "mcp", "serve", "--policy", "read-only"]`.

The server exposes `junction_search`, `junction_describe`, `junction_permissions`, `junction_context`, `junction_execute` and `junction_batch`. Context and policy are fixed when the server starts. Tool arguments cannot change tenant, endpoint, credentials or policy.

For HTTP instead, set `JUNCTION_SERVER_TOKEN` to a random value and run `junction --context <name> serve --policy read-only`. It listens on loopback only unless `--allow-external` is given. Every route needs `Authorization: Bearer <server token>`.

## Agent rules

- Start in `read-only`. Ask before switching a server to `safe-write` or `full`, and explain which operations that unlocks.
- Never try to approve your own `approval_required` result. Show the user the operation and input, and let them approve it at the terminal.
- Keep tenant data out of chat beyond what the user asked for. Results can contain personal information.
- A `response_too_large` or timeout error may mean the request already ran. Read state before retrying a write.
- If a call returns `authorization_failed`, report the permission Junction names. Do not suggest broader roles than needed.
- `credential_required` means a key or login is missing. Tell the user which command to run themselves.

## Developing Junction

- Workspace crates in `crates/`: `junction` (CLI), `junction-core`, `junction-registry`, `junction-schema`, `junction-generator`, `junction-discovery`, `junction-auth`, `junction-policy`, `junction-runtime`, `junction-http`, `junction-mcp`, `junction-server`, `junction-tui`, `junction-types`.
- Catalogue sources are in `sources/*.toml`, overrides in `overrides/`, generators in `generators/`, receipts in `generated/manifests/`. Generated registry JSON is not committed; the daily release workflow rebuilds it from upstream.
- Design and status: `docs/SPECIFICATION.md`, `docs/IMPLEMENTATION.md`, `docs/STATUS.md`, `docs/RELEASING.md`.
- Before a pull request:

```sh
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo test --workspace --locked
```

- Imports must come from official Microsoft sources and keep their revision and digest receipts.
- Use synthetic data in tests. Keep credentials, tokens, tenant data and API responses out of issues, fixtures and logs.
- Release versions are assigned by the workflow. Do not reuse or hand-create tags.
- Keep the disclaimer intact and do not imply Microsoft endorsement.

## Verification

- For calls: show the operation id, the API version used and a short summary of the result.
- For code: fmt, clippy and tests pass. `scripts/live-smoke.sh` is for read-only checks against a tenant the user owns, and only when they ask.
