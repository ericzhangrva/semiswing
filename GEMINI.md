# SemiSwing Repository Guidelines

## Snapshot Updates Protocol
When the user drops new screenshots under `snapshots/` or requests a portfolio snapshot update:
1. **Extract & Sync Holdings**: Inspect the new screenshots under `snapshots/` and update all relevant YAML configs in `config/portfolios/private/*.yaml` with the latest quantities, prices, cost bases, and snapshot date.
2. **Re-encrypt Vaults**: Run `.venv/bin/python -m semiswing.cli sync-secrets` to update `encrypted_family.json`, `encrypted_isabel.json`, and `encrypted_portfolios.json`.
3. **Refresh Market Data & Reports**: Run `.venv/bin/python -m semiswing.cli recommend --refresh` to pull latest market closes, evaluate regime and models, and regenerate daily HTML reports and index.
4. **Integrate Remote Commits**: Pull latest remote changes (e.g. from scheduled GitHub Actions) with `git pull --rebase origin main` or fetch & rebase.
5. **Auto Commit & Push**: Automatically stage all updated encrypted vaults, reports, and instructions, commit with a standard message (`chore(portfolios): update snapshot sync, encrypted vaults, and daily reports`), and push to GitHub `origin main` without waiting for manual confirmation.
