# SemiSwing Repository Guidelines

## Snapshot Updates Protocol
When the user drops new screenshots under `snapshots/` or requests a portfolio snapshot update:
1. **Extract & Sync Holdings**: Inspect the new screenshots under `snapshots/` and update all relevant YAML configs in `config/portfolios/private/*.yaml` with the latest quantities, prices, cost bases, and snapshot date.
2. **Re-encrypt Vaults**: Run `.venv/bin/python -m semiswing.cli sync-secrets` to update `encrypted_family.json`, `encrypted_isabel.json`, and `encrypted_portfolios.json`.
3. **Refresh Market Data & Reports**: Run `.venv/bin/python -m semiswing.cli recommend --refresh` to pull latest market closes, evaluate regime and models, and regenerate daily HTML reports and index.
4. **Update Backtest Audit Manifest**: Run `.venv/bin/python -m semiswing.cli backtest` to regenerate `reports/backtests/audit_manifest.json` and backtest tearsheets.
5. **Verify CI Gates**: Run `.venv/bin/pytest tests/ -v` to ensure 100% test pass.
6. **Integrate Remote Commits**: Pull latest remote changes with `git pull --rebase origin main` or fetch & rebase.
7. **Auto Commit & Push**: Automatically stage all updated encrypted vaults, reports, and instructions, commit with a standard message (`chore(portfolios): update snapshot sync, encrypted vaults, and daily reports`), and push to GitHub `origin main` without waiting for manual confirmation.

## Quality Control & CI Invariant
- **Mandatory Pre-Push Test Verification**: NEVER execute `git push` in this repository without first running `.venv/bin/pytest tests/ -v` locally and verifying a 100% pass rate. If any test or institutional gate fails, diagnose and resolve it before pushing.
