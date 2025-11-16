# Multi-Tasker — Render-ready (Dual-mode DB) Project (Final Release)

This build uses a dual-mode DB connection:
1. **Manual**: provide MANUAL_DATABASE_URL (.env or env var) — preferred for the external DB you supply.
2. **Automatic**: falls back to Render's DATABASE_URL / RENDER_DATABASE_URL when manual connection is absent or fails.
If both fail, app falls back to sqlite for best-effort local mode.

Default admin credentials in backup_auth.json (if DB seed fails):
- username: admin
- password: Admin@12345

**Setup bootstrap**: visit `/?page=setup` and provide your setup secret to create the initial admin. Set env var `SETUP_SECRET` in Render to override `DEFAULT_SETUP_SECRET`.

## How to use MANUAL mode locally
Create a `.env` file at project root with:
```
MANUAL_DATABASE_URL=postgresql://user:pass@host:port/dbname
```
When you run locally, db_connection will try MANUAL first (from .env) then Render DB.

## CI / Auto-deploy
Included `.github/workflows/ci-and-deploy.yml` runs tests on push to `main` and can optionally trigger a Render Deploy Hook if you add the `RENDER_DEPLOY_HOOK` secret in GitHub.

## Pages
Add new pages by creating a `.py` file under `/pages` with a `Page` class containing `title` and `run(self, app)` method. The app auto-discovers pages and registers them for permission management.
