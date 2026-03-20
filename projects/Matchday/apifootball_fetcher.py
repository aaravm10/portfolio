"""
API-Football Data Fetcher
Fetches EPL team stats from /teams/statistics — the only endpoint that works on the free plan.
Players and possession are handled by FPL instead.
"""

import os
import requests
import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

load_dotenv()

# Utility functions for safe parsing and scaling
def _safe_int(val, default=0):
    try:
        return int(val or default)
    except (TypeError, ValueError):
        return default

# Safely convert to float, treating None or invalid strings as default
def _safe_float(val, default=0.0):
    try:
        return float(val or default)
    except (TypeError, ValueError):
        return default


def _pct_str_to_float(val):
    """Convert '78%' or '78' or 78 to 78.0"""
    if val is None:
        return 0.0
    if isinstance(val, str):
        return _safe_float(val.replace('%', '').strip())
    return _safe_float(val)

# Min-max scale a pandas Series to a specified range (default 0-100), handling constant series gracefully
def _minmax_scale(series, lo=0, hi=100):
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series([50.0] * len(series), index=series.index)
    return ((series - mn) / (mx - mn)) * (hi - lo) + lo


class APIFootballFetcher:
    """Fetches /teams/statistics for all EPL teams with pickle caching.
    Falls back to stale cache if the API is unavailable (e.g. daily quota hit).
    api_key can be None if you just want to read from existing cache.
    """

    def __init__(self, api_key, cache_dir="data/apifootball_cache"):
        self.api_key   = api_key
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.base_url  = "https://v3.football.api-sports.io"
        self.headers   = {"x-apisports-key": self.api_key} if api_key else {}
        self.league_id = 39
        self.season    = 2024
        self.cache_ttl = timedelta(hours=6)

    # Cache path for a given key
    def _cache_path(self, key):
        return self.cache_dir / f"{key}.pkl"

    # Checking if cache is fresh based on modification time
    def _cache_fresh(self, path):
        if not path.exists():
            return False
        return datetime.now() - datetime.fromtimestamp(path.stat().st_mtime) < self.cache_ttl

    # Save data to cache
    def _save(self, data, key):
        with open(self._cache_path(key), 'wb') as f:
            pickle.dump(data, f)

    # Load data from cache
    def _load(self, key):
        with open(self._cache_path(key), 'rb') as f:
            return pickle.load(f)

    def _cache_exists(self, key):
        return self._cache_path(key).exists()

    # Fetch data from API
    def _get(self, endpoint, params):
        if not self.api_key:
            raise RuntimeError("No API key — cannot fetch from API")
        url = f"{self.base_url}/{endpoint}"
        # Retry up to 3 times on rate limit (429), with a 60s wait in between
        for _ in range(3):
            r = requests.get(url, headers=self.headers, params=params, timeout=30)
            if r.status_code == 429:
                print("  Rate-limited, waiting 60s...")
                time.sleep(60)
                continue
            r.raise_for_status()
            return r.json()
        raise RuntimeError(f"Failed after retries: {endpoint}")

    # Fallback to cache on failure
    def _fetch_with_fallback(self, cache_key, fetch_fn):
        cp = self._cache_path(cache_key)
        if self._cache_fresh(cp):
            return self._load(cache_key)
        # If cache is stale or missing, try fetching from API
        try:
            data = fetch_fn()
            self._save(data, cache_key)
            return data
        except Exception as e:
            if self._cache_exists(cache_key):
                print(f"  API unavailable ({e}), using stale cache for {cache_key}")
                return self._load(cache_key)
            raise

    # Fetch team list for the league and season
    def get_teams(self):
        def fetch():
            data = self._get("teams", {"league": self.league_id, "season": self.season})
            return [item['team'] for item in data.get('response', [])]
        return self._fetch_with_fallback(f"teams_{self.season}", fetch)

    # Fetch stats for a single team
    def get_team_stats_raw(self, team_id):
        def fetch():
            data = self._get("teams/statistics", {
                "league": self.league_id,
                "season": self.season,
                "team":   team_id,
            })
            return data.get('response', {})
        return self._fetch_with_fallback(f"team_stats_{self.season}_{team_id}", fetch)


class TeamStatsBuilder:
    """Parses /teams/statistics into a DataFrame with derived stats and composite scores"""

    def __init__(self, fetcher: APIFootballFetcher):
        self.fetcher = fetcher

    # Build df for all teams with derived stats and composite scores
    def build(self) -> pd.DataFrame:
        teams = self.fetcher.get_teams()
        print(f"  Fetching stats for {len(teams)} teams...")
        rows = []
        for team in teams:
            stats = self.fetcher.get_team_stats_raw(team['id'])
            if stats:
                rows.append(self._parse(team, stats))
            time.sleep(0.15)
        df = pd.DataFrame(rows)
        df = self._add_derived(df)
        df = self._add_composite_scores(df)
        return df

    # Parse stats for a single team
    def _parse(self, team, s):
        fix     = s.get('fixtures',        {})
        goals_s = s.get('goals',           {})
        cards   = s.get('cards',           {})
        penalty = s.get('penalty',         {})
        cs      = s.get('clean_sheet',     {})
        fts     = s.get('failed_to_score', {})
        lineups = s.get('lineups',         [])

        played = _safe_int(fix.get('played', {}).get('total'))
        wins   = _safe_int(fix.get('wins',   {}).get('total'))
        draws  = _safe_int(fix.get('draws',  {}).get('total'))
        losses = _safe_int(fix.get('loses',  {}).get('total'))

        goals_for     = _safe_int(goals_s.get('for',     {}).get('total', {}).get('total'))
        goals_against = _safe_int(goals_s.get('against', {}).get('total', {}).get('total'))

        # cards come back as time-interval buckets, so sum across all intervals
        def sum_card_intervals(card_dict):
            if not isinstance(card_dict, dict):
                return 0
            if 'total' in card_dict and not isinstance(card_dict.get('total'), dict):
                return _safe_int(card_dict.get('total'))
            return sum(_safe_int(v.get('total')) for v in card_dict.values() if isinstance(v, dict))

        # Handle both total cards and interval buckets, with safe parsing
        yellow_cards    = sum_card_intervals(cards.get('yellow', {}))
        red_cards       = sum_card_intervals(cards.get('red',    {}))
        clean_sheets    = _safe_int(cs.get('total'))
        failed_to_score = _safe_int(fts.get('total'))
        pen_scored      = _safe_int(penalty.get('scored', {}).get('total'))
        pen_missed      = _safe_int(penalty.get('missed', {}).get('total'))

        top_formation = ''
        if lineups:
            top_formation = sorted(lineups, key=lambda x: x.get('played', 0), reverse=True)[0].get('formation', '')

        return {
            'team_id':          team['id'],
            'team_name':        team['name'],
            'team_logo':        team.get('logo', ''),
            'top_formation':    top_formation,
            'games_played':     played,
            'wins':             wins,
            'draws':            draws,
            'losses':           losses,
            'goals_for':        goals_for,
            'goals_against':    goals_against,
            'yellow_cards':     yellow_cards,
            'red_cards':        red_cards,
            'clean_sheets':     clean_sheets,
            'failed_to_score':  failed_to_score,
            'penalties_scored': pen_scored,
            'penalties_missed': pen_missed,
        }

    # Add derived stats like win rate, goal difference, goals per game, etc.
    def _add_derived(self, df: pd.DataFrame) -> pd.DataFrame:
        gp = df['games_played'].replace(0, np.nan)

        df['win_rate']               = (df['wins']          / gp * 100).round(1).fillna(0)
        df['goal_difference']        = df['goals_for'] - df['goals_against']
        df['goals_per_game']         = (df['goals_for']     / gp).round(2).fillna(0)
        df['goals_against_per_game'] = (df['goals_against'] / gp).round(2).fillna(0)
        df['clean_sheet_pct']        = (df['clean_sheets']  / gp * 100).round(1).fillna(0)
        df['scoring_consistency']    = ((gp - df['failed_to_score']) / gp * 100).round(1).fillna(0)
        df['cards_per_game']         = ((df['yellow_cards'] + df['red_cards'] * 3) / gp).round(2).fillna(0)

        pen_att = (df['penalties_scored'] + df['penalties_missed']).replace(0, np.nan)
        df['penalty_conversion'] = (df['penalties_scored'] / pen_att * 100).round(1).fillna(np.nan)

        return df

    # Add composite scores like defensive solidity and overall team score based on weighted metrics
    def _add_composite_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        df['defensive_solidity'] = _minmax_scale(df['clean_sheet_pct'] - df['goals_against_per_game'] * 10).round(1)
        df['discipline_index']   = _minmax_scale(-df['cards_per_game']).round(1)
        df['team_score'] = (
            df['defensive_solidity']              * 0.50 +
            df['discipline_index']                * 0.25 +
            _minmax_scale(df['goals_per_game'])   * 0.25
        ).round(1)
        return df


class APIFootballLeaderboards:
    """Used by leaderboards.py — returns top-5 team lists ready for the front-end"""

    def __init__(self, api_key, fpl_badge_map=None):
        self._builder      = TeamStatsBuilder(APIFootballFetcher(api_key))
        self._teams_df     = None
        self._fpl_badge_map = fpl_badge_map or {}

    # load and cache teams stats DataFrame
    def _teams(self) -> pd.DataFrame:
        if self._teams_df is None:
            self._teams_df = self._builder.build()
        return self._teams_df

    # map team name to badge
    def _badge(self, team_name, fallback):
        return self._fpl_badge_map.get(team_name) or fallback

    # get top-5 teams
    def _top(self, col, n=5, ascending=False):
        df  = self._teams().copy().dropna(subset=[col])
        top = df.nsmallest(n, col) if ascending else df.nlargest(n, col)
        out = []
        for rank, (_, row) in enumerate(top.iterrows(), 1):
            out.append({
                'rank':           rank,
                'team_name':      row['team_name'],
                'team_short':     row['team_name'][:3].upper(),
                'team_badge':     self._badge(row['team_name'], row.get('team_logo', '')),
                'value':          round(float(row[col]), 2) if pd.notna(row[col]) else 0,
                'goals_scored':   int(row.get('goals_for', 0)),
                'goals_conceded': int(row.get('goals_against', 0)),
                'clean_sheets':   int(row.get('clean_sheets', 0)),
                'win_rate':       float(row.get('win_rate', 0)),
            })
        return out

    # team leaderboards
    def get_team_goals_per_game_leaders(self):
        return self._top('goals_per_game')

    def get_team_scoring_consistency_leaders(self):
        return self._top('scoring_consistency')

    def get_team_goals_against_leaders(self):
        return self._top('goals_against_per_game', ascending=True)

    def get_team_clean_sheet_pct_leaders(self):
        return self._top('clean_sheet_pct')

    def get_team_defensive_solidity_leaders(self):
        return self._top('defensive_solidity')

    def get_team_discipline_leaders(self):
        return self._top('discipline_index')

    def get_team_overall_score_leaders(self):
        return self._top('team_score')

    def get_team_win_rate_leaders(self):
        return self._top('win_rate')

    def get_team_yellow_cards_leaders(self):
        return self._top('cards_per_game', ascending=True)

if __name__ == "__main__":
    api_key = os.getenv("APIFOOTBALL_KEY")
    if not api_key:
        raise EnvironmentError("APIFOOTBALL_KEY not set — add it to your .env file")

    lb = APIFootballLeaderboards(api_key)

    team_tests = {
        "Goals per Game":        lb.get_team_goals_per_game_leaders,
        "Scoring Consistency":   lb.get_team_scoring_consistency_leaders,
        "Fewest Goals Conceded": lb.get_team_goals_against_leaders,
        "Clean Sheet %":         lb.get_team_clean_sheet_pct_leaders,
        "Defensive Solidity":    lb.get_team_defensive_solidity_leaders,
        "Discipline":            lb.get_team_discipline_leaders,
        "Overall Score":         lb.get_team_overall_score_leaders,
    }

    for title, fn in team_tests.items():
        data = fn()
        print(f"\n{title}:")
        for t in data:
            print(f"  {t['rank']}. {t['team_name']} – {t['value']}")