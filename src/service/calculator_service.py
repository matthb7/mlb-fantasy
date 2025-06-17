import pandas as pd
import logging
from datetime import datetime, timedelta

BATTING_POINTS = {
    'HR': 2,  # Home Run
    'TB': 1,  # Total Bases
    'BB': 1,  # Base on Balls (Walk)
    'R': 1,   # Run
    'RBI': 1, # Run Batted In
    'SB': 1,  # Stolen Base
    'SO': -1, # Strike Out
    'HBP': 1, # Hit By Pitch
    'SH': 1,  # Sacrifice Hit
    'SF': 1,  # Sacrifice Fly
    'CS': -1, # Caught Stealing
    # NOT FOUND IN ANY API
    'CYC': 3, # Cycle (Single, Double, Triple, Home Run in one game)
    'GSHR': 4, # Grand Slam Home Run
}

PITCHING_POINTS = {
    'IP': 3,  # Innings Pitched
    'ER': -2, # Earned Run
    'SV': 5,  # Save
    'SO': 1,  # Strike Out
    'H': -1,  # Hit Allowed
    'BB': -1, # Base on Balls (Walk)
    'HB': -1, # Hit Batsman
    'PG': 5,  # Perfect Game
    'HD': 2,  # Hold
}

# NOT FOUND IN PYBASEBALL API
FIELDING_POINTS = {
    'PO': 1,  # Put Out
    'E': -1,  # Error
}

def calculate_batter_rating(player_data, days_ago=None):
    if days_ago is None:
        days_ago = (datetime.now() - datetime(2025, 3, 27)).days

    # Extract relevant stats
    points = player_data.get('POINTS', 0)
    at_bats = player_data.get('AB', 0)
    ops = player_data.get('OPS', 0)
    games = player_data.get('GP', 0)
    putouts = player_data.get('PO', 0)

    # Weights for each criterion
    points_weight = 0.5  # Increased from 0.4
    consistency_weight = 0.3  # Increased from 0.2
    power_weight = 0.1  # Decreased from 0.2
    value_weight = 0.1  # Decreased from 0.2

    # normalize stats with adjusted factors
    power_normalized = points / games / 5  # Reduced divisor from 10 to 5
    points_normalized = points / days_ago / 5  # Reduced divisor from 10 to 5
    at_bats_normalized = float(at_bats) / days_ago / 5  # Reduced divisor from 10 to 5
    
    # Add playing time consistency metric
    games_per_day = float(games) / days_ago
    consistency_bonus = min(games_per_day * 2, 1.0)  # Cap at 1.0, scale by 2

    # Calculate overall rating
    overall_rating = (points_normalized * points_weight) + \
                    (at_bats_normalized * consistency_weight) + \
                    (power_normalized * power_weight) + \
                    (float(ops) * value_weight) + \
                    (consistency_bonus * 0.2)  # Additional bonus for playing time consistency

    return overall_rating

def calculate_starting_pitcher_rating(player_data, days_ago=None):
    if days_ago is None:
        days_ago = (datetime.now() - datetime(2025, 3, 27)).days

    # Extract relevant stats
    points = calculate_pitching_points_from_dict(player_data)
    innings_pitched = player_data.get('IP', 0)
    games = player_data.get('GS', 0)
    strikeouts = player_data.get('SO', 0)
    earned_runs = player_data.get('ER', 0)

    # Weights for each criterion
    points_weight = 0.4
    consistency_weight = 0.2
    power_weight = 0.2
    efficiency_weight = 0.2

    # normalize stats with adjusted factors
    power_normalized = points / games / 5  # Reduced divisor from 10 to 5
    points_normalized = points / days_ago / 5  # Reduced divisor from 10 to 5
    innings_pitched_normalized = float(innings_pitched) / days_ago / 5  # Reduced divisor from 10 to 5
    
    # Add efficiency metric (K/ER ratio)
    efficiency = float(strikeouts) / float(earned_runs) if earned_runs > 0 else float(strikeouts)
    efficiency_normalized = min(efficiency / 10, 1.0)  # Cap at 1.0, scale by 10

    # Calculate overall rating
    overall_rating = (points_normalized * points_weight) + \
                    (innings_pitched_normalized * consistency_weight) + \
                    (power_normalized * power_weight) + \
                    (efficiency_normalized * efficiency_weight)

    return overall_rating

def calculate_relief_pitcher_rating(player_data, days_ago=None):
    if days_ago is None:
        days_ago = (datetime.now() - datetime(2025, 3, 27)).days

    # Extract relevant stats
    points = player_data.get('POINTS', 0)
    innings_pitched = player_data.get('IP', 0)
    saves = player_data.get('SV', 0)
    save_opportunities = player_data.get('SOP', 0)
    games = player_data.get('GP', 0)
    strikeouts = player_data.get('SO', 0)
    earned_runs = player_data.get('ER', 0)

    # Weights for each criterion
    points_weight = 0.35
    consistency_weight = 0.15
    power_weight = 0.2
    value_weight = 0.15
    efficiency_weight = 0.15

    # normalize stats with adjusted factors
    power_normalized = points / games / 5  # Reduced divisor from 10 to 5
    points_normalized = points / days_ago / 5  # Reduced divisor from 10 to 5
    innings_pitched_normalized = float(innings_pitched) / days_ago / 5  # Reduced divisor from 10 to 5
    saves_normalized = float(saves) / float(save_opportunities) if save_opportunities > 0 else 0
    
    # Add efficiency metric (K/ER ratio)
    efficiency = float(strikeouts) / float(earned_runs) if earned_runs > 0 else float(strikeouts)
    efficiency_normalized = min(efficiency / 10, 1.0)  # Cap at 1.0, scale by 10

    # Calculate overall rating
    overall_rating = (points_normalized * points_weight) + \
                    (innings_pitched_normalized * consistency_weight) + \
                    (power_normalized * power_weight) + \
                    (saves_normalized * value_weight) + \
                    (efficiency_normalized * efficiency_weight)

    return overall_rating

def calculate_batting_points_from_dict(stats):
    points = 0
    if not stats:
        return 0
    
    # Basic points
    points += float(stats.get('HR', 0)) * BATTING_POINTS['HR']
    points += float(stats.get('TB', 0)) * BATTING_POINTS['TB']
    points += float(stats.get('BB', 0)) * BATTING_POINTS['BB']
    points += float(stats.get('R', 0)) * BATTING_POINTS['R']
    points += float(stats.get('RBI', 0)) * BATTING_POINTS['RBI']
    points += float(stats.get('SB', 0)) * BATTING_POINTS['SB']
    points += float(stats.get('SO', 0)) * BATTING_POINTS['SO']
    points += float(stats.get('HBP', 0)) * BATTING_POINTS['HBP']
    points += float(stats.get('SH', 0)) * BATTING_POINTS['SH']
    points += float(stats.get('SF', 0)) * BATTING_POINTS['SF']
    points += float(stats.get('CS', 0)) * BATTING_POINTS['CS']
    
    # Fielding points
    points += float(stats.get('PO', 0)) * FIELDING_POINTS['PO']
    points += float(stats.get('E', 0)) * FIELDING_POINTS['E']
    
    return points

def calculate_pitching_points_from_dict(stats):
    points = 0
    if not stats:
        return 0
    
    # Basic points
    points += float(stats.get('IP', 0)) * PITCHING_POINTS['IP']
    points += float(stats.get('ER', 0)) * PITCHING_POINTS['ER']
    points += float(stats.get('SV', 0)) * PITCHING_POINTS['SV']
    points += float(stats.get('SO', 0)) * PITCHING_POINTS['SO']
    points += float(stats.get('H', 0)) * PITCHING_POINTS['H']
    points += float(stats.get('BB', 0)) * PITCHING_POINTS['BB']
    points += float(stats.get('HB', 0)) * PITCHING_POINTS['HB']
    points += float(stats.get('PG', 0)) * PITCHING_POINTS['PG']
    points += float(stats.get('HD', 0)) * PITCHING_POINTS['HD']

    # Fielding points
    points += float(stats.get('PO', 0)) * FIELDING_POINTS['PO']
    points += float(stats.get('E', 0)) * FIELDING_POINTS['E']

    return points
