import pandas as pd
import numpy as np
from pybaseball import cache, statcast, statcast_batter, statcast_pitcher
from pathlib import Path
from datetime import datetime, timedelta
import logging
from points_calculator import calculate_batting_points, calculate_pitching_points
import argparse
from mlb_api import get_player_id, get_batter_stats, get_pitcher_stats
# TODO: remove these imports if not needed after more testing
# import matplotlib.pyplot as plt
# import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable caching pybaseball
cache.purge()

def load_roster(file_path):
    """
    Load roster data from a text file with categories.
    Each line should be in the format: name,position,start_year
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        sections = content.split('#')
        roster = {'Batters': [], 'Pitchers': [], 'IL': []}
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split('\n')
            category = lines[0].strip()
            if category in roster:
                for line in lines[1:]:
                    if line.strip():
                        parts = line.strip().split(',')
                        if len(parts) >= 3:  # Now checking for at least 3 parts
                            name = parts[0].strip()
                            position = parts[1].strip()
                            start_year = int(parts[2].strip())  # Convert start year to integer
                            roster[category].append({
                                'name': name,
                                'position': position,
                                'start_year': start_year
                            })
        
        return {k: pd.DataFrame(v) for k, v in roster.items() if v}
    except FileNotFoundError:
        print(f"Error: Roster file not found at {file_path}")
        return None
    except ValueError as e:
        print(f"Error: Invalid start year format in roster file: {str(e)}")
        return None

def analyze_roster_fullSeason(roster_dict, player_name=None):
    """
    Analyze the fantasy roster and generate insights
    """
    if not roster_dict:
        return
    
    print("\n=== Roster Analysis ===")
    
    # Analyze batters
    if 'Batters' in roster_dict:
        batters_df = roster_dict['Batters']
        if player_name:
            batters_df = batters_df[batters_df['name'] == player_name]
            if batters_df.empty:
                print(f"\nNo batter found with name: {player_name}")
                return
                
        print("\n=== Batters ===")
        print(f"Total Batters: {len(batters_df)}")
        print("\nPosition Distribution:")
        print(batters_df['position'].value_counts())
        
        # Calculate points for each batter
        batter_points = []
        for _, player in batters_df.iterrows():
            stats = get_batter_stats(player['name'], player['start_year'])
            points = calculate_batting_points(stats)
            batter_points.append({
                'name': player['name'],
                'position': player['position'],
                'points': points
            })
        
        batter_points_df = pd.DataFrame(batter_points)
        print("\nBatter Fantasy Points (2025 Season):")
        print(batter_points_df.sort_values('points', ascending=False))
    
    # Analyze pitchers
    if 'Pitchers' in roster_dict:
        pitchers_df = roster_dict['Pitchers']
        if player_name:
            pitchers_df = pitchers_df[pitchers_df['name'] == player_name]
            if pitchers_df.empty:
                print(f"\nNo pitcher found with name: {player_name}")
                return
                
        print("\n=== Pitchers ===")
        print(f"Total Pitchers: {len(pitchers_df)}")
        print("\nPosition Distribution:")
        print(pitchers_df['position'].value_counts())
        
        # Calculate points for each pitcher
        pitcher_points = []
        for _, player in pitchers_df.iterrows():
            stats = get_pitcher_stats(player['name'], player['start_year'])
            points = calculate_pitching_points(stats)
            pitcher_points.append({
                'name': player['name'],
                'position': player['position'],
                'points': points
            })
        
        pitcher_points_df = pd.DataFrame(pitcher_points)
        print("\nPitcher Fantasy Points (2025 Season):")
        print(pitcher_points_df.sort_values('points', ascending=False))
    
    # Show IL players
    if 'IL' in roster_dict:
        il_df = roster_dict['IL']
        if player_name:
            il_df = il_df[il_df['name'] == player_name]
            if il_df.empty:
                print(f"\nNo IL player found with name: {player_name}")
                return
                
        print("\n=== Injured List ===")
        print(f"Total IL Players: {len(il_df)}")
        print("\nIL Players:")
        print(il_df[['name', 'position']])

def get_statcast_for_batters(roster_df, start_date, end_date, player_name=None):
    """Get statcast data for all batters in the roster, or for a specific batter if player_name is provided."""
    try:
        output_file = f"data/statcast_batters_analysis_{start_date}_to_{end_date}.txt"
        with open(output_file, 'w') as f:
            f.write(f"Statcast Batters Analysis for {start_date} to {end_date}\n")
            f.write("=" * 80 + "\n\n")
            if player_name:
                roster_df = roster_df[roster_df['name'].str.contains(player_name, case=False, na=False)]
                if roster_df.empty:
                    logging.warning(f"No batter found with name: {player_name}")
                    f.write(f"No batter found with name: {player_name}\n")
                    return pd.DataFrame()
            all_stats = []
            for _, player in roster_df.iterrows():
                player_name = player['name']
                start_year = str(player['start_year'])  # Convert to string
                player_id = get_player_id(player_name, start_year)
                if not player_id:
                    logging.warning(f"Could not find player ID for {player_name}")
                    f.write(f"Could not find player ID for {player_name}\n")
                    continue
                logging.info(f"Processing {player_name} (ID: {player_id})")
                f.write(f"\nProcessing {player_name} (ID: {player_id})\n")
                f.write("-" * 80 + "\n")
                # Get statcast data for this batter
                try:
                    matches = statcast_batter(start_dt=start_date, end_dt=end_date, player_id=player_id)
                except Exception as e:
                    logging.error(f"Error retrieving statcast data for {player_name}: {e}")
                    f.write(f"Error retrieving statcast data for {player_name}: {e}\n")
                    continue
                logging.info(f"Found {len(matches)} matching rows for {player_name}")
                f.write(f"Found {len(matches)} matching rows\n\n")
                f.write("All events for this player:\n")
                f.write(matches.to_string())
                f.write("\n\n")
                if len(matches) == 0:
                    continue
                stats = {
                    'Name': player_name,
                    'HR': len(matches[matches['events'] == 'home_run']),
                    'BB': len(matches[matches['events'] == 'walk']),
                    'R': len(matches[matches['events'] == 'run']),
                    'RBI': len(matches[matches['events'] == 'rbi']),
                    'SB': len(matches[matches['events'] == 'stolen_base']),
                    'SO': len(matches[matches['events'] == 'strikeout']),
                    'HBP': len(matches[matches['events'] == 'hit_by_pitch']),
                    'SH': len(matches[matches['events'] == 'sac_bunt']),
                    'CS': len(matches[matches['events'] == 'caught_stealing']),
                    'H': len(matches[matches['events'].isin(['single', 'double', 'triple', 'home_run'])]),
                    '2B': len(matches[matches['events'] == 'double']),
                    '3B': len(matches[matches['events'] == 'triple']),
                    'TB': (len(matches[matches['events'] == 'single']) + 
                           2 * len(matches[matches['events'] == 'double']) +
                           3 * len(matches[matches['events'] == 'triple']) +
                           4 * len(matches[matches['events'] == 'home_run'])),
                    'PO': 0,  # Default to 0 since not in statcast
                    'E': 0    # Default to 0 since not in statcast
                }
                stats_df = pd.DataFrame([stats])
                points = calculate_batting_points(stats_df)
                stats['Fantasy Points'] = points
                f.write(f"\nDetailed Stats for {player_name}:\n")
                f.write("-" * 80 + "\n")
                for stat, value in stats.items():
                    f.write(f"{stat}: {value}\n")
                f.write("\nPoints Breakdown:\n")
                f.write("-" * 80 + "\n")
                f.write(f"HR: {stats['HR']} × 2 = {stats['HR'] * 2}\n")
                f.write(f"BB: {stats['BB']} × 1 = {stats['BB']}\n")
                f.write(f"R: {stats['R']} × 1 = {stats['R']}\n")
                f.write(f"RBI: {stats['RBI']} × 1 = {stats['RBI']}\n")
                f.write(f"SB: {stats['SB']} × 1 = {stats['SB']}\n")
                f.write(f"SO: {stats['SO']} × -1 = {stats['SO'] * -1}\n")
                f.write(f"HBP: {stats['HBP']} × 1 = {stats['HBP']}\n")
                f.write(f"SH: {stats['SH']} × 1 = {stats['SH']}\n")
                f.write(f"CS: {stats['CS']} × -1 = {stats['CS'] * -1}\n")
                f.write(f"Total Bases: {stats['TB']} × 1 = {stats['TB']}\n")
                f.write(f"  Singles: {len(matches[matches['events'] == 'single'])}\n")
                f.write(f"  Doubles: {stats['2B']} × 2 = {stats['2B'] * 2}\n")
                f.write(f"  Triples: {stats['3B']} × 3 = {stats['3B'] * 3}\n")
                f.write(f"  Home Runs: {stats['HR']} × 4 = {stats['HR'] * 4}\n")
                f.write(f"Fielding:\n")
                f.write(f"  Put Outs: {stats['PO']} × 1 = {stats['PO']}\n")
                f.write(f"  Errors: {stats['E']} × -1 = {stats['E'] * -1}\n")
                f.write(f"Total Points: {points}\n")
                f.write("=" * 80 + "\n\n")
                all_stats.append(stats)
            logging.info(f"Batters analysis written to {output_file}")
            return pd.DataFrame(all_stats)
    except Exception as e:
        logging.error(f"Error getting statcast data for batters: {str(e)}")
        return pd.DataFrame()

def get_statcast_for_pitchers(roster_df, start_date, end_date, player_name=None):
    """Get statcast data for all pitchers in the roster, or for a specific pitcher if player_name is provided."""
    try:
        output_file = f"data/statcast_pitchers_analysis_{start_date}_to_{end_date}.txt"
        with open(output_file, 'w') as f:
            f.write(f"Statcast Pitchers Analysis for {start_date} to {end_date}\n")
            f.write("=" * 80 + "\n\n")
            if player_name:
                roster_df = roster_df[roster_df['name'].str.contains(player_name, case=False, na=False)]
                if roster_df.empty:
                    logging.warning(f"No pitcher found with name: {player_name}")
                    f.write(f"No pitcher found with name: {player_name}\n")
                    return pd.DataFrame()
            all_stats = []
            for _, player in roster_df.iterrows():
                player_name = player['name']
                start_year = str(player['start_year'])  # Convert to string
                player_id = get_player_id(player_name, start_year)
                if not player_id:
                    logging.warning(f"Could not find player ID for {player_name}")
                    f.write(f"Could not find player ID for {player_name}\n")
                    continue
                logging.info(f"Processing {player_name} (ID: {player_id})")
                f.write(f"\nProcessing {player_name} (ID: {player_id})\n")
                f.write("-" * 80 + "\n")
                # Get statcast data for this pitcher
                try:
                    matches = statcast_pitcher(start_dt=start_date, end_dt=end_date, player_id=player_id)
                except Exception as e:
                    logging.error(f"Error retrieving statcast data for {player_name}: {e}")
                    f.write(f"Error retrieving statcast data for {player_name}: {e}\n")
                    continue
                logging.info(f"Found {len(matches)} matching rows for {player_name}")
                f.write(f"Found {len(matches)} matching rows\n\n")
                f.write("All events for this player:\n")
                f.write(matches.to_string())
                f.write("\n\n")
                if len(matches) == 0:
                    continue
                stats = {
                    'Name': player_name,
                    'W': len(matches[matches['events'] == 'win']),
                    'L': len(matches[matches['events'] == 'loss']),
                    'SV': len(matches[matches['events'] == 'save']),
                    'BSV': len(matches[matches['events'] == 'blown_save']),
                    'IP': len(matches) / 3,  # Approximate innings pitched
                    'H': len(matches[matches['events'].isin(['single', 'double', 'triple', 'home_run'])]),
                    'ER': len(matches[matches['events'] == 'earned_run']),
                    'BB': len(matches[matches['events'] == 'walk']),
                    'SO': len(matches[matches['events'] == 'strikeout']),
                    'HBP': len(matches[matches['events'] == 'hit_by_pitch']),
                    'WP': len(matches[matches['events'] == 'wild_pitch']),
                    'BK': len(matches[matches['events'] == 'balk']),
                    'PO': 0,  # Default to 0 since not in statcast
                    'E': 0    # Default to 0 since not in statcast
                }
                stats_df = pd.DataFrame([stats])
                points = calculate_pitching_points(stats_df)
                stats['Fantasy Points'] = points
                f.write(f"\nDetailed Stats for {player_name}:\n")
                f.write("-" * 80 + "\n")
                for stat, value in stats.items():
                    f.write(f"{stat}: {value}\n")
                f.write("\nPoints Breakdown:\n")
                f.write("-" * 80 + "\n")
                f.write(f"W: {stats['W']} × 5 = {stats['W'] * 5}\n")
                f.write(f"L: {stats['L']} × -5 = {stats['L'] * -5}\n")
                f.write(f"SV: {stats['SV']} × 5 = {stats['SV'] * 5}\n")
                f.write(f"BSV: {stats['BSV']} × -5 = {stats['BSV'] * -5}\n")
                f.write(f"IP: {stats['IP']} × 3 = {stats['IP'] * 3}\n")
                f.write(f"H: {stats['H']} × -1 = {stats['H'] * -1}\n")
                f.write(f"ER: {stats['ER']} × -2 = {stats['ER'] * -2}\n")
                f.write(f"BB: {stats['BB']} × -1 = {stats['BB'] * -1}\n")
                f.write(f"SO: {stats['SO']} × 1 = {stats['SO']}\n")
                f.write(f"HBP: {stats['HBP']} × -1 = {stats['HBP'] * -1}\n")
                f.write(f"WP: {stats['WP']} × -1 = {stats['WP'] * -1}\n")
                f.write(f"BK: {stats['BK']} × -1 = {stats['BK'] * -1}\n")
                f.write(f"Fielding:\n")
                f.write(f"  Put Outs: {stats['PO']} × 1 = {stats['PO']}\n")
                f.write(f"  Errors: {stats['E']} × -1 = {stats['E'] * -1}\n")
                f.write(f"Total Points: {points}\n")
                f.write("=" * 80 + "\n\n")
                all_stats.append(stats)
            logging.info(f"Pitchers analysis written to {output_file}")
            return pd.DataFrame(all_stats)
    except Exception as e:
        logging.error(f"Error getting statcast data for pitchers: {str(e)}")
        return pd.DataFrame()

def main():
    parser = argparse.ArgumentParser(description='Analyze MLB fantasy roster')
    parser.add_argument('mode', choices=['fullSeason', 'byDate'], 
                      help='fullSeason: analyze entire season stats, byDate: analyze specific date range using statcast')
    parser.add_argument('--start-date', help='Start date for byDate analysis (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date for byDate analysis (YYYY-MM-DD)')
    parser.add_argument('--player', help='Optional: analyze only this specific player')
    
    args = parser.parse_args()
    
    # Load roster from file
    roster_file = Path('data/roster.txt')
    roster_dict = load_roster(roster_file)
    
    if not roster_dict:
        print("Please create a roster.txt file in the data directory with your team's players.")
        return
        
    if args.mode == 'fullSeason':
        analyze_roster_fullSeason(roster_dict, args.player)
    else:  # byDate mode
        if not args.start_date or not args.end_date:
            print("For byDate analysis, please provide both --start-date and --end-date")
            return
            
        logging.info(f"\nAnalyzing statcast data for {args.start_date} to {args.end_date}:")
        try:
            statcast_data = statcast(start_dt=args.start_date, end_dt=args.end_date)
            logging.info(f"Statcast data shape: {statcast_data.shape}")
            logging.info(f"Statcast data columns: {statcast_data.columns.tolist()}")
            logging.info(f"Unique game dates in data: {statcast_data['game_date'].unique()}")
            logging.info(f"First row of statcast data:\n{statcast_data.iloc[0].to_string()}")
            
            # Find statcast data for each player
            if 'Batters' in roster_dict:
                print("\nStatcast matches for Batters:")
                get_statcast_for_batters(roster_dict['Batters'], args.start_date, args.end_date, args.player)
            if 'Pitchers' in roster_dict:
                print("\nStatcast matches for Pitchers:")
                get_statcast_for_pitchers(roster_dict['Pitchers'], args.start_date, args.end_date, args.player)
                
        except Exception as e:
            logging.error(f"Error getting statcast data: {str(e)}")

if __name__ == "__main__":
    main() 