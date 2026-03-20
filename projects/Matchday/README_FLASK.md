# MATCHDAY Flask Developer Guide

This file is intentionally Flask-specific.

Use `README.md` for product overview, setup, features, and deployment.
Use this file when you are changing backend behavior in Flask code.

## Who This Is For

- Contributors editing routes, models, or Flask app wiring
- Anyone adding/maintaining JSON API endpoints
- Anyone debugging request/session/auth flows

## App Factory and Startup Flow

Primary entrypoint is `app.py`.

`create_app()` does the following in order:

1. Creates Flask app instance
2. Loads settings from `config.Config`
3. Initializes `Flask-Session`
4. Ensures key directories exist (`data/`, `static/images/`)
5. Registers all blueprints under `routes/`
6. Initializes SQLite schema via `models.user.init_db()`

When running directly (`python app.py`), app serves on `0.0.0.0:8080`.

## Blueprint Map

Blueprints are registered centrally in `app.py`.

- `routes/main.py` -> `main_bp` (`/`, `/about`)
- `routes/auth.py` -> `auth_bp` (`/auth/*`)
- `routes/dashboard.py` -> `dashboard_bp` (`/dashboard/*`)
- `routes/totw.py` -> `totw_bp` (`/totw/*`)
- `routes/create.py` -> `create_bp` (`/create/*`)
- `routes/leaderboards.py` -> `leaderboards_bp` (`/leaderboards/*`)
- `routes/watchlist.py` -> `watchlist_bp` (`/watchlist/*`)
- `routes/fixtures.py` -> `fixtures_bp` (`/fixtures/*`)
- `routes/optimize.py` -> `optimize_bp` (`/optimize/*`)
- `routes/help.py` -> `help_bp` (`/help/*`)

## Request and Auth Patterns

Session/auth helpers live in `utils/auth.py`.

- `@login_required` enforces authenticated access
- `get_current_user()` populates template context for navbar/account state
- APIs generally return `jsonify(...)` with explicit status codes on error

Conventions used in routes:

- Form pages render templates and use flash messages where appropriate
- API routes return JSON payloads and machine-readable error keys
- Missing dataset conditions usually return `404` with `{ "error": "..." }`

## Data Loading and Caching Conventions

### Master Dataset

Most analytics routes read `data/premier_league_master_{SEASON}.xlsx`.

Helpers used:

- `utils.charts.file_mtime(...)`
- `utils.charts.load_master_xlsx(...)`
- route-specific wrappers such as `_load_dashboard_dataframe()`

### External Data

- FPL endpoints are fetched directly via `requests`
- Understat merge logic is in `pipeline.py`
- API-Football logic and cache fallback is in `apifootball_fetcher.py`
- Fixture/FDR helper cache is in `utils/fixtures_data.py`

## Database Notes

Database is SQLite (`usersdb.db`) managed in `models/user.py`.

Current table includes:

- credentials (`name`, `password`)
- optional preference columns
- `watchlist` JSON blob

Model module exposes route-facing functions like:

- `authenticate_user`, `register_user`
- `get_user_by_id`, `get_user_by_username`
- watchlist CRUD helpers

## How To Add a New Flask Feature

1. Create or choose a blueprint in `routes/`
2. Add route functions with clear return type (`HTML` vs `JSON`)
3. Reuse `login_required` for protected pages/APIs
4. If route needs the master dataset, centralize loading in a helper
5. Add corresponding template and static JS/CSS hooks if needed
6. Add tests under `tests/` for both success and failure paths

## Testing Flask Changes

Run all tests:

```bash
pytest
```

Useful targeted runs:

```bash
pytest tests/test_routes_auth_main_totw.py -q
pytest tests/test_dashboard_compare.py -q
pytest tests/test_routes_misc_coverage.py -q
```

Coverage is enforced in `pytest.ini` (`--cov-fail-under=60`).

## API Design Checklist

Before merging route changes, verify:

- Validation errors return deterministic JSON + proper status code
- Auth-protected endpoints are decorated
- Empty/missing data states are handled gracefully
- Expensive fetches are cached or bounded
- New route behavior is covered by tests

## Non-Goals of This File

This file does not duplicate:

- Product feature walkthrough
- High-level setup for end users
- Deployment checklist

Those live in `README.md`.
