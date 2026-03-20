"""
Team of the Week
"""

import requests
import pandas as pd

class GameweekFetcher:
    """
    Fetches data from FPL API
    """
    
    def get_bootstrap_data(self):
        """
        Get general player/team data
        Returns: dictionary with 'elements', 'teams', 'events'
        """
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_gameweek_data(self, gameweek):
        """
        Get performance data for a specific gameweek
        
        Args:
            gameweek: int (1-38)
        Returns: dictionary with 'elements' (player performances)
        """
        url = f"https://fantasy.premierleague.com/api/event/{gameweek}/live/"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_current_gameweek(self):
        """
        Find which gameweek is current or most recent
        Returns: int (gameweek number)
        """
        bootstrap = self.get_bootstrap_data()
        
        # First check for current gameweek
        for event in bootstrap['events']:
            if event['is_current']:
                return event['id']
        
        # If no current, find most recent finished
        for event in reversed(bootstrap['events']):
            if event['finished']:
                return event['id']
        
        return 1


class DataProcessor:
    """
    Combines bootstrap data with gameweek data into a clean DataFrame
    """
    
    def __init__(self):
        self.fetcher = GameweekFetcher()
    
    def build_gameweek_dataframe(self, gameweek):
        """
        Create a DataFrame with player info + gameweek stats
        
        Args:
            gameweek: int
            
        Returns:
            pandas DataFrame with columns:
            - player_id
            - player_name
            - team_name
            - position (1=GK, 2=DEF, 3=MID, 4=FWD)
            - minutes
            - goals
            - assists
            - clean_sheets
            - saves
            - goals_conceded
            - yellow_cards
            - red_cards
            - bonus
            - bps
            - influence
            - creativity
            - threat
        """
        # Get data
        bootstrap = self.fetcher.get_bootstrap_data()
        gw_data = self.fetcher.get_gameweek_data(gameweek)
        
        # Create team lookup
        teams = {}
        for team in bootstrap['teams']:
            teams[team['id']] = {
                'name': team['name'],
                'short_name': team['short_name'],
                'badge_url': f"https://resources.premierleague.com/premierleague/badges/t{team['code']}.png"
            }
        
        # Create player lookup: {player_id: player_info}
        players = {}
        for player in bootstrap['elements']:
            players[player['id']] = {
                'player_name': player['web_name'],
                'full_name': f"{player['first_name']} {player['second_name']}",
                'team_id': player['team'],
                'team_name': teams[player['team']]['name'],
                'team_short': teams[player['team']]['short_name'],
                'team_badge': teams[player['team']]['badge_url'],
                'position': player['element_type'],
                'photo_url': f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player['photo'].replace('.jpg', '').replace('.png', '')}.png"
            }
        
        # Build rows by combining player info + gameweek stats
        rows = []
        for player_perf in gw_data['elements']:
            player_id = player_perf['id']
            stats = player_perf['stats']
            
            # Only include players who actually played
            if stats['minutes'] == 0:
                continue
            
            # Combine player info with their gameweek stats
            row = {
                'player_id': player_id,
                'player_name': players[player_id]['player_name'],
                'full_name': players[player_id]['full_name'],
                'team_name': players[player_id]['team_name'],
                'team_short': players[player_id]['team_short'],
                'photo_url': players[player_id]['photo_url'],
                'team_badge': players[player_id]['team_badge'],
                'position': players[player_id]['position'],
                'minutes': stats['minutes'],
                'goals': stats['goals_scored'],
                'assists': stats['assists'],
                'clean_sheets': stats['clean_sheets'],
                'goals_conceded': stats['goals_conceded'],
                'saves': stats['saves'],
                'yellow_cards': stats['yellow_cards'],
                'red_cards': stats['red_cards'],
                'bonus': stats['bonus'],
                'bps': stats['bps'],
                'influence': float(stats['influence']),
                'creativity': float(stats['creativity']),
                'threat': float(stats['threat']),
                'ict_index': float(stats['ict_index']),
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Sort by team and position
        df = df.sort_values(['team_short', 'position', 'player_name'])
        
        return df

class TOTWScorer:
    """
    Custom scoring algorithm
    """
    
    def calculate_scores(self, df):
        """
        Calculate TOTW score for each player based on position + universal factors
        """
        df = df.copy()
        df['totw_score'] = 0.0
        
        # Position specific scoring
        
        # Goalkeepers (position 1)
        gk = df['position'] == 1
        df.loc[gk, 'totw_score'] = (
            df.loc[gk, 'saves'] * 0.3 +              
            df.loc[gk, 'clean_sheets'] * 15 +        
            df.loc[gk, 'goals_conceded'] * -2        
        )
        
        # Defenders (position 2)
        def_mask = df['position'] == 2
        df.loc[def_mask, 'totw_score'] = (
            df.loc[def_mask, 'clean_sheets'] * 12 +   
            df.loc[def_mask, 'goals'] * 15 +         
            df.loc[def_mask, 'assists'] * 8 +         
            df.loc[def_mask, 'goals_conceded'] * -1.5 
        )
        
        # Midfielders (position 3)
        mid = df['position'] == 3
        df.loc[mid, 'totw_score'] = (
            df.loc[mid, 'goals'] * 12 +              
            df.loc[mid, 'assists'] * 10 +             
            df.loc[mid, 'creativity'] * 0.05 +       
            df.loc[mid, 'threat'] * 0.03             
        )
        
        # Forwards (position 4)
        fwd = df['position'] == 4
        df.loc[fwd, 'totw_score'] = (
            df.loc[fwd, 'goals'] * 15 +               
            df.loc[fwd, 'assists'] * 8 +         
            df.loc[fwd, 'threat'] * 0.05              
        )
        
        # Universal scoring

        # Bonus points
        df['totw_score'] += df['bonus'] * 2
        df['totw_score'] += df['bps'] * 0.1
        
        # ICT Index (overall performance metric)
        df['totw_score'] += df['ict_index'] * 0.02
        
        
        # Disciplinary penalties
        df['totw_score'] -= df['yellow_cards'] * 1    
        df['totw_score'] -= df['red_cards'] * 15     
        
        # Minutes requirement 
        df.loc[df['minutes'] < 60, 'totw_score'] *= 0.5
        
        # Elite performance bonuses (top 11 in each category)
        
        # Bonus for being in top 11 most creative players
        top_creative = df.nlargest(11, 'creativity').index
        df.loc[top_creative, 'totw_score'] += 5
        
        # Bonus for being in top 11 most influential players
        top_influence = df.nlargest(11, 'influence').index
        df.loc[top_influence, 'totw_score'] += 5
        
        # Bonus for being in top 11 most threatening players
        top_threat = df.nlargest(11, 'threat').index
        df.loc[top_threat, 'totw_score'] += 5
        
        return df
    
    def calculate_rating(self, df):
        """
        Calculate a 0-10 rating based on actual performance
        """
        df = df.copy()
        
        if len(df) == 0:
            return df
        
        max_score = df['totw_score'].max()
        min_score = df['totw_score'].min()
        
        if max_score <= 0:
            df['rating'] = 8.0
            return df
        
        score_range = max_score - min_score
        
        if score_range > 0:
            # Scale to 7.8-9.2 range
            df['rating'] = 7.8 + ((df['totw_score'] - min_score) / (max_score - min_score)) * 1.4
            
            # Significant outlier bonus
            sorted_scores = df['totw_score'].nlargest(2).values
            if len(sorted_scores) >= 2:
                if sorted_scores[0] > sorted_scores[1] * 1.3:  # 30% better
                    # Check for exceptional stats
                    top_player = df[df['totw_score'] == max_score].iloc[0]
                    if top_player['goals'] >= 3:  # Hattrick or more
                        df.loc[df['totw_score'] == max_score, 'rating'] = 10.0
                    elif top_player['goals'] >= 2 or (top_player['goals'] >= 1 and top_player['assists'] >= 2):
                        df.loc[df['totw_score'] == max_score, 'rating'] = 9.5
                    else:
                        df.loc[df['totw_score'] == max_score, 'rating'] = 9.2
            
            df['rating'] = df['rating'].round(1)
        else:
            # All same score
            df['rating'] = 8.2
        
        return df


class FormationSelector:

    def select_best_xi(self, df, formation='4-3-3'):
        """
        Select best XI with a fixed formation
        """
        # Parse formation
        def_count, mid_count, fwd_count = map(int, formation.split('-'))
        
        # Pick best at each position
        gk = df[df['position'] == 1].nlargest(1, 'totw_score')
        defenders = df[df['position'] == 2].nlargest(def_count, 'totw_score')
        midfielders = df[df['position'] == 3].nlargest(mid_count, 'totw_score')
        forwards = df[df['position'] == 4].nlargest(fwd_count, 'totw_score')
        
        return pd.concat([gk, defenders, midfielders, forwards])
    
    def select_best_xi_dynamic(self, df):
        """
        Selects best XI with a flexible formation
        Tries multiple formations and picks the one with highest total score
        """
        # Try different valid formations
        formations_to_try = [
            (3, 4, 3),  # 3-4-3
            (3, 5, 2),  # 3-5-2
            (4, 3, 3),  # 4-3-3
            (4, 4, 2),  # 4-4-2
            (4, 5, 1),  # 4-5-1
            (5, 3, 2),  # 5-3-2
            (5, 4, 1),  # 5-4-1
        ]
        
        best_team = None
        best_formation = None
        best_total_score = -1
        
        # Always need 1 GK
        gk = df[df['position'] == 1].nlargest(1, 'totw_score')
        
        # Try each formation
        for def_count, mid_count, fwd_count in formations_to_try:
            defenders = df[df['position'] == 2].nlargest(def_count, 'totw_score')
            midfielders = df[df['position'] == 3].nlargest(mid_count, 'totw_score')
            forwards = df[df['position'] == 4].nlargest(fwd_count, 'totw_score')
            
            # Make sure we have enough players in each position
            if len(defenders) < def_count or len(midfielders) < mid_count or len(forwards) < fwd_count:
                continue
            
            team = pd.concat([gk, defenders, midfielders, forwards])
            total_score = team['totw_score'].sum()
            
            if total_score > best_total_score:
                best_total_score = total_score
                best_team = team
                best_formation = f"{def_count}-{mid_count}-{fwd_count}"
        
        # Fallback if nothing worked
        if best_team is None:
            return self.select_best_xi(df, '4-3-3'), '4-3-3'
        
        return best_team, best_formation
        

        