import pandas as pd
import logging
import time
from pybaseball import playerid_lookup, batting_stats_bref, batting_stats, batting_stats_range, pitching_stats_bref
from util import PLAYER_NAME_MAPPING

# use mlbID for player reference
def get_season_stats_bref(season=2025):
    return batting_stats_bref(season)

# use mlbID for player reference
def get_season_stats(season=2025):
    return batting_stats(season)

def get_batting_states_range(start_date, end_date):
    return batting_stats_range(start_date, end_date)

def get_player_id(player_name, start_year):
    """Get player ID using playerid_lookup."""
    if player_name in PLAYER_NAME_MAPPING:
        full_name = PLAYER_NAME_MAPPING[player_name]
        # Split the full name into last name and first name
        name_parts = full_name.split()
        if len(name_parts) >= 2:
            last_name = name_parts[-1]  # Last part is the last name
            first_name = ' '.join(name_parts[:-1])  # Everything else is the first name
            
            # Try exact match first
            exact_matches = playerid_lookup(last_name, first_name)
            if not exact_matches.empty:
                # If multiple matches, use start year to find the correct one
                if len(exact_matches) > 1:
                    # Find the player whose career started in the roster's start year
                    year_match = exact_matches[exact_matches['mlb_played_first'] == start_year]
                    if not year_match.empty:
                        return year_match.iloc[0]['key_mlbam']
                return exact_matches.iloc[0]['key_mlbam']
                
            # If no exact match, try fuzzy match
            possible_matches = playerid_lookup(last_name, first_name, fuzzy=True)
            if not possible_matches.empty: 
                # If multiple fuzzy matches, use start year to find the correct one
                if len(possible_matches) > 1:
                    # Find the player whose career started in the roster's start year
                    year_match = possible_matches[possible_matches['mlb_played_first'] == start_year]
                    if not year_match.empty:
                        return year_match.iloc[0]['key_mlbam']
                return possible_matches.iloc[0]['key_mlbam']
            
    logging.error(f"Could not find player ID for {player_name}")
    return None

def get_batter_stats(player_name, start_year):
    """Get batting statistics using pybaseball."""
    try:
        # First get the player ID
        player_id = get_player_id(player_name, start_year)
        if player_id is None:
            logging.error(f"Could not find player ID for {player_name}")
            return None
            
        logging.info(f"Found player ID {player_id} for {player_name}")
        
        # Add sleep before getting stats
        time.sleep(10)
        
        logging.info(f"Getting batting stats for {player_name}")
        try:
            stats = batting_stats_bref(2025)  # Use 2025 season
            logging.info(f"Raw batting stats type: {type(stats)}")
            logging.info(f"Raw batting stats: {stats}")
            if stats is not None:
                logging.info(f"Batting stats DataFrame shape: {stats.shape}")
                logging.info(f"Batting stats columns: {stats.columns.tolist()}")
                if not stats.empty:
                    logging.info(f"Sample row from batting stats:\n{stats.iloc[0].to_string()}")
                # Filter for this player using mlbID
                player_stats = stats[stats['mlbID'] == player_id]
                logging.info(f"Found {len(player_stats)} rows of batting stats for {player_name}")
                if not player_stats.empty:
                    logging.info(f"First row of batting stats for {player_name}:")
                    for col in player_stats.columns:
                        logging.info(f"{col}: {player_stats.iloc[0][col]}")
                    return player_stats
        except Exception as e:
            logging.error(f"Error getting batting stats: {str(e)}")
            raise
                
    except Exception as e:
        logging.error(f"Error getting stats for {player_name}: {str(e)}")
    return None

def get_pitcher_stats(player_name, start_year):
    """Get pitching statistics using pybaseball."""
    try:
        # First get the player ID
        player_id = get_player_id(player_name, start_year)
        if player_id is None:
            logging.error(f"Could not find player ID for {player_name}")
            return None
            
        logging.info(f"Found player ID {player_id} for {player_name}")
        
        # Add sleep before getting stats
        time.sleep(10)
        
        logging.info(f"Getting pitching stats for {player_name}")
        try:
            stats = pitching_stats_bref(2025)  # Use 2025 season
            logging.info(f"Raw pitching stats type: {type(stats)}")
            logging.info(f"Raw pitching stats: {stats}")
            if stats is not None:
                logging.info(f"Pitching stats DataFrame shape: {stats.shape}")
                logging.info(f"Pitching stats columns: {stats.columns.tolist()}")
                if not stats.empty:
                    logging.info(f"Sample row from pitching stats:\n{stats.iloc[0].to_string()}")
                # Filter for this player using mlbID
                player_stats = stats[stats['mlbID'] == player_id]
                logging.info(f"Found {len(player_stats)} rows of pitching stats for {player_name}")
                if not player_stats.empty:
                    logging.info(f"First row of pitching stats for {player_name}:")
                    for col in player_stats.columns:
                        logging.info(f"{col}: {player_stats.iloc[0][col]}")
                    return player_stats
        except Exception as e:
            logging.error(f"Error getting pitching stats: {str(e)}")
            raise
                
    except Exception as e:
        logging.error(f"Error getting stats for {player_name}: {str(e)}")
    return None