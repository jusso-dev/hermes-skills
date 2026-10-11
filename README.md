# hermes-skills

Skills and plugins for [Hermes Agent](https://hermes-agent.nousresearch.com/) by Justin Middler. Each skill teaches a Hermes agent how to use, or work on, one tool.

## Install

Add this repository as a skills tap once, then install the skills you want:

```bash
hermes skills tap add jusso-dev/hermes-skills
hermes skills tap list
hermes skills install jusso-dev/hermes-skills/skills/skytime
```

Hermes scans each skill when it installs it. These are community skills, so you can read each `SKILL.md` here first.

To install one skill without adding the tap, use the same full path:

```bash
hermes skills install jusso-dev/hermes-skills/skills/<skill-name>
```

## Skills

| Skill | What it helps with | Install path |
| --- | --- | --- |
| `crownguard` | Crown-jewel risk assessments for Microsoft 365, Google Workspace and AWS with crownguard, including the headless CLI | `skills/crownguard` |
| `happie-parent` | Helping a parent run their HappiE kids video library at home: children, videos, imports, updates, backups and fixes | `skills/happie-parent` |
| `junction` | Finding and calling Microsoft Graph, Azure, Defender and other Microsoft APIs through Junction, and developing it | `skills/junction` |
| `m365-secure` | Running the M365-Secure tenant assessment CLI, reading its reports, and adding checks | `skills/m365-secure` |
| `oakattest` | Running IRAP and readiness engagements in OakAttest over MCP, and developing or self-hosting it | `skills/oakattest` |
| `servicesnap` | Working on the ServiceSnap vehicle logbook apps for iOS and Android and their Firebase backend | `skills/servicesnap` |
| `skytime` | Logging and reporting time in SkyTime through its MCP server or API, and developing it | `skills/skytime` |

## Plugins

### hermes-cyber-au

Australian cyber security guidance for Hermes: retrieval over ASD, ACSC and other Australian sources, an offline query checker, and seven skills (`sentinel-expert`, `aws-cloudwatch-expert`, `ism-control-lookup`, `detection-engineering`, `essential-eight-assessor`, `threat-intel-check`, `incident-response-au`).

```bash
hermes plugins install jusso-dev/hermes-skills/plugins/hermes-cyber-au
```

The plugin registers its skills when it loads. Details, configuration and the knowledge refresh are in [plugins/hermes-cyber-au/README.md](plugins/hermes-cyber-au/README.md). This pack used to live at `jusso-dev/hermes-cyber-au` and moved here with its git history.

## Layout

```text
skills/<skill-name>/SKILL.md          skills served by the tap
plugins/hermes-cyber-au/              Hermes plugin with its own skills/, tests and knowledge snapshot
skills.sh.json                        categories shown in Hermes skill search
scripts/validate_skills.py            checks every SKILL.md against the Hermes format
.github/workflows-to-enable/          skill validation and the cyber plugin's checks and refresh (see its README)
```

## Safety

Skills here never contain credentials, private endpoints or customer data. Where a skill needs a token, it names the environment variable or settings page and leaves the value to you. Skills that can change things tell the agent to confirm with you first.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

MIT. See [LICENSE](LICENSE). The cyber plugin keeps its own [LICENSE](plugins/hermes-cyber-au/LICENSE) and [NOTICE](plugins/hermes-cyber-au/NOTICE). Each skill describes a separate project that has its own licence.
