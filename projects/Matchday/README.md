# MATCHDAY - Premier League Analytics Platform

MATCHDAY is a Flask-based Premier League analytics app that combines Fantasy Premier League (FPL), Understat, and API-Football data.

It includes player and team dashboards, Team of the Week, fixtures/FDR tools, leaderboards, a budget optimizer, and account-based watchlists.

## Documentation Split

- `README.md`: product overview, setup, feature map, and deployment
- `README_FLASK.md`: Flask internals (app factory, blueprints, request/auth patterns, and backend development workflow)

## Features

- Merged FPL + Understat dataset with per-90 metrics
- Team of the Week selection and dynamic formation logic
- Leaderboards for players and teams (including xG/value views)
- Fixtures Difficulty Rating (FDR) matrix and simple match predictor
- Best XI optimizer with formation and budget constraints
- Authenticated watchlist support (SQLite + Flask sessions)
- Player compare APIs and radial percentile charts
- Excel export and local caching for fetched datasets

## Requirements

- Python 3.10+
- Internet connection (required on first run to fetch FPL and Understat data)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/CSEN174-W2026/EPL-App.git
cd EPL-App
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

On macOS/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python3 app.py
```

> On some systems `python` works instead of `python3`. Use whichever points to Python 3.10+.

The first time you run the app, it will automatically fetch and cache player and team data from the FPL and Understat APIs. This may take 30–60 seconds. Subsequent runs load from the cached file in `data/` and start faster.

### 5. Open in your browser

```
http://127.0.0.1:8080
```

or equivalently `http://localhost:8080` — both point to the same local server. In most terminals you can hold **Shift** and click the URL printed in the console to open it directly.

You can register a new account or browse most features without logging in.

## Configuration

Key settings live in `config.py` and environment variables:

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Flask session secret (set this in production) | hardcoded fallback |
| `FLASK_DEBUG` | Enable debug mode (`true`/`1`/`t`) | `false` |
| `DATABASE_URI` | Database path | SQLite (`usersdb.db`) |
| `SEASON` | EPL season string (e.g. `2425`) | auto-derived from date |
| `APIFOOTBALL_KEY` | API-Football key (optional, for team stats) | none |

To set environment variables on macOS/Linux:

```bash
export SECRET_KEY=your-secret-key
export FLASK_DEBUG=true
python app.py
```

## Tests and Coverage

Run the full test suite:

```bash
pytest
```

`pytest.ini` is configured to collect coverage for core modules and enforce a minimum total coverage threshold of `60%`.

Generate the HTML coverage report:

```bash
pytest --cov-report=html
```

The report is written to `htmlcov/`.

## Key Routes

| Route | Description |
|---|---|
| `/` | Home page |
| `/about` | About page |
| `/auth/*` | Login / register / logout |
| `/dashboard/*` | Player analytics, compare, charts, form and timeline APIs |
| `/totw` | Team of the Week |
| `/leaderboards` | Player and team leaderboard views |
| `/fixtures` | Fixture difficulty matrix and match predictor |
| `/optimize` | Budget-based Best XI optimizer |
| `/create` | Custom team creation |
| `/watchlist` | User watchlist UI and APIs |
| `/help` | FAQ and contact form |

## Data Notes

- Data files are written to `data/` and cached after the first fetch.
- API-Football team stats are cached in `data/apifootball_cache/`.
- User and account data is stored in `usersdb.db` (created automatically on first run).

Current `users` table shape:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    favorite_team TEXT,
    favorite_player TEXT,
    friends TEXT,
    watchlist TEXT
);
```

## Project Structure

```text
EPL-App/
├── app.py                  # App entry point and factory
├── config.py               # Configuration and environment variables
├── pipeline.py             # Data pipeline (FPL + Understat merge)
├── totw.py                 # Team of the Week logic
├── apifootball_fetcher.py  # API-Football integration
├── leaderboards.py         # Leaderboard computation helpers
├── models/                 # Database models (SQLite)
├── routes/                 # Flask blueprints
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS, JS, images
├── utils/                  # Shared helpers (charts, auth, fixtures)
├── tests/                  # pytest test suite
└── data/                   # Cached data files (auto-generated)
```

## Deployment

For production:

1. Set secure environment variables (`SECRET_KEY`, etc.)
2. Disable debug mode
3. Run behind a production WSGI server (for example Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 'app:create_app()'
```
