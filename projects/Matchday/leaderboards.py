"""
Leaderboards - Team and Player Season Rankings
Players use FPL data only. Teams combine FPL aggregates with API-Football stats.
"""

import os
import pandas as pd
import requests
from dotenv import load_dotenv
from apifootball_fetcher import APIFootballLeaderboards

load_dotenv()


class LeaderboardsFetcher:
    """Fetches season-cumulative data from the FPL API"""

    # Fetch and cache the bootstrap data which contains all player and team info
    def get_bootstrap_data(self):
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()

    # Build a dataframe from the bootstrap data
    def build_player_season_df(self):
        """All players with season totals, filtered to 90+ minutes"""
        bootstrap = self.get_bootstrap_data()

        teams = {
            team['id']: {
                'name':       team['name'],
                'short_name': team['short_name'],
                'badge_url':  f"https://resources.premierleague.com/premierleague/badges/t{team['code']}.png"
            }
            for team in bootstrap['teams']
        }

        rows = []

        # Filter to 90+ minutes to avoid skewing per-90 stats 
        for player in bootstrap['elements']:
            photo_filename = player['photo'].replace('.jpg', '').replace('.png', '')
            minutes  = int(player['minutes'])      if player['minutes']      else 0
            goals    = int(player['goals_scored']) if player['goals_scored'] else 0
            assists  = int(player['assists'])      if player['assists']      else 0

            rows.append({
                'player_id':         player['id'],
                'player_name':       player['web_name'],
                'full_name':         f"{player['first_name']} {player['second_name']}",
                'team_id':           player['team'],
                'team_name':         teams[player['team']]['name'],
                'team_short':        teams[player['team']]['short_name'],
                'team_badge':        teams[player['team']]['badge_url'],
                'position':          player['element_type'],
                'photo_url':         f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{photo_filename}.png",
                'minutes':           minutes,
                'goals':             goals,
                'assists':           assists,
                'clean_sheets':      int(player['clean_sheets'])   if player['clean_sheets']   else 0,
                'goals_conceded':    int(player['goals_conceded']) if player['goals_conceded'] else 0,
                'saves':             int(player['saves'])          if player['saves']          else 0,
                'yellow_cards':      int(player['yellow_cards'])   if player['yellow_cards']   else 0,
                'red_cards':         int(player['red_cards'])      if player['red_cards']      else 0,
                'influence':         float(player['influence'])    if player['influence']      else 0.0,
                'creativity':        float(player['creativity'])   if player['creativity']     else 0.0,
                'threat':            float(player['threat'])       if player['threat']         else 0.0,
                'ict_index':         float(player['ict_index'])    if player['ict_index']      else 0.0,
                'expected_goals':    float(player['expected_goals'])   if player.get('expected_goals')   else 0.0,
                'expected_assists':  float(player['expected_assists']) if player.get('expected_assists') else 0.0,
            })

        df = pd.DataFrame(rows)

        # Add per-90 stats for a simple "impact rating" combining goals and assists, with a minimum 90 minutes played threshold
        minutes_safe = df['minutes'].replace(0, pd.NA)
        df['goals_p90']     = (df['goals']   / minutes_safe) * 90
        df['assists_p90']   = (df['assists'] / minutes_safe) * 90
        df['impact_rating'] = df['goals_p90'].fillna(0) + df['assists_p90'].fillna(0)

        return df[df['minutes'] >= 90].copy()

    def build_team_season_df(self):
        """Aggregate FPL player stats up to team level"""
        player_df = self.build_player_season_df()

         # Get clean sheets from fixtures
        clean_sheets_map = self.get_team_clean_sheets_from_fixtures()

        rows = []

        # Aggregate by team
        for team_id in player_df['team_id'].unique():
            tp = player_df[player_df['team_id'] == team_id]
            if tp.empty:
                continue
            first = tp.iloc[0]
            rows.append({
                'team_id':        team_id,
                'team_name':      first['team_name'],
                'team_short':     first['team_short'],
                'team_badge':     first['team_badge'],
                'goals_scored':   int(tp['goals'].sum()),
                'assists':        int(tp['assists'].sum()),
                'xG':             float(tp['expected_goals'].sum()),
                'clean_sheets':   clean_sheets_map.get(team_id, 0),
                'goals_conceded': int(tp[tp['position'] == 1]['goals_conceded'].sum()),
            })

        return pd.DataFrame(rows)
    
    def get_team_clean_sheets_from_fixtures(self):
        """Count clean sheets from finished fixtures"""
        url = "https://fantasy.premierleague.com/api/fixtures/"
        response = requests.get(url, timeout=30)
        fixtures = response.json()
        
        clean_sheets = {}
        
        for fixture in fixtures:
            if fixture.get('finished'):
                team_h = fixture['team_h']
                team_a = fixture['team_a']
                score_h = fixture.get('team_h_score', 0)
                score_a = fixture.get('team_a_score', 0)
                
                # Home team clean sheet (if away team scored 0)
                if score_a == 0:
                    clean_sheets[team_h] = clean_sheets.get(team_h, 0) + 1
                
                # Away team clean sheet (if home team scored 0)
                if score_h == 0:
                    clean_sheets[team_a] = clean_sheets.get(team_a, 0) + 1
        
        return clean_sheets


class LeaderboardsProcessor:
    """Builds leaderboard dicts ready for the front-end"""

    def __init__(self):
        self.fetcher = LeaderboardsFetcher()
        api_key = os.getenv("APIFOOTBALL_KEY")

        bootstrap = self.fetcher.get_bootstrap_data()
        fpl_badge_map = {
            team['name']: f"https://resources.premierleague.com/premierleague/badges/t{team['code']}.png"
            for team in bootstrap['teams']
        }

        # always create the object — if no key it will read from cache only,
        # and if there's no cache either it'll just return empty lists gracefully
        self.apifootball = APIFootballLeaderboards(api_key, fpl_badge_map=fpl_badge_map)
        if not api_key:
            print("No APIFOOTBALL_KEY — will use cached team data if available")

    def get_player_leaderboards(self):
        """Top 5 players per metric, FPL data only"""
        bootstrap = self.fetcher.get_bootstrap_data()

        # find last finished gameweek for the per-90 minutes threshold
        current_gw = 1
        for event in bootstrap['events']:
            if event['is_current']:
                current_gw = event['id']
                break
        if current_gw == 1:
            for event in reversed(bootstrap['events']):
                if event['finished']:
                    current_gw = event['id']
                    break

        min_minutes = current_gw * 45
        df = self.fetcher.build_player_season_df()
        leaderboards = {}

        # integer_keys: these get displayed as whole numbers
        integer_keys = {'goals', 'assists', 'clean_sheets', 'saves'}

        metrics = [
            {
                'key':         'goals',
                'label':       'Top Scorers',
                'unit':        'goals',
                'description': 'Most goals scored this season',
            },
            {
                'key':         'assists',
                'label':       'Top Assisters',
                'unit':        'assists',
                'description': 'Most assists provided this season',
            },
            {
                'key':         'expected_goals',
                'label':       'Top xG',
                'unit':        'xG',
                'description': 'Highest expected goals this season',
            },
            {
                'key':         'expected_assists',
                'label':       'Top xA',
                'unit':        'xA',
                'description': 'Highest expected assists this season',
            },
            {
                'key':         'clean_sheets',
                'label':       'Most Clean Sheets',
                'unit':        'clean sheets',
                'description': 'Most clean sheets (goalkeepers only)',
                'position_filter': [1],
            },
            {
                'key':         'saves',
                'label':       'Most Saves',
                'unit':        'saves',
                'description': 'Most saves made this season (goalkeepers only)',
                'position_filter': [1],
            },
            {
                'key':         'impact_rating',
                'label':       'Best Goal Contributions per 90',
                'unit':        'G+A per 90',
                'description': f'Goals + assists per 90 minutes (min {min_minutes} minutes)',
                'min_minutes': min_minutes,
            },
        ]

        for metric in metrics:
            key = metric['key']
            df_filtered = df.copy()

            # Ensure ranking metric is numeric so nlargest() works reliably
            if key in df_filtered.columns:
                df_filtered[key] = pd.to_numeric(df_filtered[key], errors='coerce').fillna(0)

            if 'position_filter' in metric:
                df_filtered = df_filtered[df_filtered['position'].isin(metric['position_filter'])]
            if 'min_minutes' in metric:
                df_filtered = df_filtered[df_filtered['minutes'] >= metric['min_minutes']]
            
            # Get top 5 players for this metric
            top5 = df_filtered.nlargest(5, key)
            players_list = []
            for idx, (_, player) in enumerate(top5.iterrows(), 1):
                raw = player[key] if pd.notna(player[key]) else 0
                value = int(raw) if key in integer_keys else round(float(raw), 2)
                players_list.append({
                    'rank':        idx,
                    'player_name': player['player_name'],
                    'team_short':  player['team_short'],
                    'photo_url':   player['photo_url'],
                    'value':       value,
                    'goals':       int(player['goals']),
                    'assists':     int(player['assists']),
                    'minutes':     int(player['minutes']),
                })

            leaderboards[key] = {
                'label':       metric['label'],
                'unit':        metric['unit'],
                'description': metric['description'],
                'players':     players_list,
            }

        return leaderboards

    def get_team_leaderboards(self):
        """Top 5 teams per metric — FPL for goals/defence, API-Football for everything else"""
        fpl_df = self.fetcher.build_team_season_df()
        leaderboards = {}

        fpl_int_keys = {'goals_scored', 'goals_conceded', 'clean_sheets'}

        # Get top 5 teams
        def fpl_top5(df, key, ascending=False):
            top = df.nsmallest(5, key) if ascending else df.nlargest(5, key)
            out = []
            for idx, (_, team) in enumerate(top.iterrows(), 1):
                raw = float(team[key])
                value = int(raw) if key in fpl_int_keys else round(raw, 2)
                out.append({
                    'rank':           idx,
                    'team_name':      team['team_name'],
                    'team_short':     team['team_short'],
                    'team_badge':     team['team_badge'],
                    'value':          value,
                    'goals_scored':   int(team['goals_scored']),
                    'goals_conceded': int(team['goals_conceded']),
                    'clean_sheets':   int(team['clean_sheets']),
                })
            return out

        # FPL-based team boards
        fpl_metrics = [
            ('goals_scored',   'Most Goals Scored',    'goals',       'Total goals scored this season',              False),
            ('goals_conceded', 'Best Defence',         'goals',       'Fewest goals conceded this season',           True),
            ('clean_sheets',   'Most Clean Sheets',    'clean sheets','Total clean sheets this season',              False),
            ('xG',             'Highest xG',           'xG',          'Total expected goals this season',            False),
        ]

        for key, label, unit, desc, asc in fpl_metrics:
            leaderboards[key] = {
                'label':       label,
                'unit':        unit,
                'description': desc,
                'teams':       fpl_top5(fpl_df, key, ascending=asc),
            }

        if self.apifootball:
            # API-Football team boards 
            try:
                api_metrics = [
                    ('goals_per_game',      'Goals per Game',        'goals/game',    'Average goals scored per match',                    self.apifootball.get_team_goals_per_game_leaders()),
                    ('scoring_consistency', 'Scoring Consistency',   '% of matches',  'Percentage of matches in which the team scored',    self.apifootball.get_team_scoring_consistency_leaders()),
                    ('goals_against',       'Goals Conceded per Game','goals/game',   'Average goals conceded per match',                  self.apifootball.get_team_goals_against_leaders()),
                    ('clean_sheet_pct',     'Clean Sheet Rate',      '% of matches',  'Percentage of matches without conceding',           self.apifootball.get_team_clean_sheet_pct_leaders()),
                    ('win_rate',            'Win Rate',              '% of matches',  'Percentage of matches won this season',             self.apifootball.get_team_win_rate_leaders()),
                    ('yellow_cards_pg',     'Fewest Yellow Cards',   'per game',      'Average yellow cards per match — lower is better',  self.apifootball.get_team_yellow_cards_leaders()),
                ]

                for key, label, unit, desc, data in api_metrics:
                    if data:
                        leaderboards[key] = {
                            'label':       label,
                            'unit':        unit,
                            'description': desc,
                            'teams':       data,
                        }
            except Exception as e:
                print(f"Could not load API-Football team data: {e}")

        return leaderboards