# Workflows to enable

These GitHub Actions workflows are ready but not yet active. GitHub only runs workflows in `.github/workflows/`, and the tool that published this repository was not allowed to write there.

To turn them on, from a clone with your own credentials:

```bash
git mv .github/workflows-to-enable .github/workflows
git rm .github/workflows/README.md
git commit -m "Enable workflows"
git push
```

- `validate-skills.yml` runs `scripts/validate_skills.py` on every push and pull request.
- `cyber-au-checks.yml` runs the hermes-cyber-au tests and eval when that plugin changes.
- `cyber-au-knowledge-refresh.yml` is the daily knowledge refresh for hermes-cyber-au. It opens a pull request when the snapshot changes and never pushes to main.
