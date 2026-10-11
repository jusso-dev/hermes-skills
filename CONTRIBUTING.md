# Contributing

Thanks for helping. A few rules keep this repository useful and safe to publish.

## Adding or changing a skill

- One skill per folder: `skills/<skill-name>/SKILL.md`. The folder name is the install name, and it must match `name` in the frontmatter.
- Frontmatter needs `name` and `description`. Keep the description to one short sentence of 60 characters or fewer, because Hermes cuts longer ones in its skill index. Add `version`, `author`, `license` and `metadata.hermes.tags` as the existing skills do.
- Follow the existing shape: what the tool is, When to Use, the procedure, pitfalls, safety rules and how to verify the work.
- Put long reference material in `references/` next to `SKILL.md` and point to it from the skill.
- Add the skill to a grouping in `skills.sh.json` and to the table in `README.md`.
- Run `python scripts/validate_skills.py` before opening a pull request. CI runs it too once the workflows are enabled.

## What must never go in

This repository is public. Do not add secrets, tokens, keys, passwords, private or internal URLs, project or account identifiers, customer or client data, tenant data, or personal information about anyone, including children. Use placeholders such as `<your-host>` and environment variable names instead.

If a skill describes a private codebase, keep it at the level of architecture and developer workflow.

## Writing style

Australian English, plain language, short sentences. No em dashes, no emojis and no marketing language.

## The cyber plugin

`plugins/hermes-cyber-au` is a full Hermes plugin with its own tests and contributing notes. See its `CONTRIBUTING.md`.
