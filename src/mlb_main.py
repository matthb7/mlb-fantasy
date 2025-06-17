import pandas as pd
import argparse
# import json
# import statsapi
# import time
from datetime import datetime, timedelta

from pathlib import Path
from service.file_service import load_roster, write_batter_metrics, write_starting_pitcher_metrics, write_relief_pitcher_metrics
from service.rating_service import rate_all_batters, rate_all_pitchers
from service.logging_service import get_logger

# from pybaseball import cache, statcast, statcast_batter, statcast_pitcher
# from api.pybaseball_api import get_player_id, get_batter_stats, get_pitcher_stats
# import matplotlib.pyplot as plt
# import seaborn as sns

# Set up logging
logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Analyze MLB fantasy roster')
    parser.add_argument('mode', choices=['fullSeason', 'byDate'], 
                      help='fullSeason: analyze entire season stats, byDate: analyze specific date range using statcast')
    parser.add_argument('--start-date', help='Start date for byDate analysis (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date for byDate analysis (YYYY-MM-DD)')
    parser.add_argument('--player', help='Optional: analyze only this specific player')

    args = parser.parse_args()
    # Load the roster from roster.txt
    roster_file = Path('data/input/roster.txt')
    roster_dict = load_roster(roster_file)

    batters_df = roster_dict['Batters']
    pitchers_df = roster_dict['Pitchers']
    starting_pitchers_df = pitchers_df[pitchers_df['position'] == 'SP']
    relief_pitchers_df = pitchers_df[pitchers_df['position'] == 'RP']

    batters_output_file = f"data/output/analysis_B_{args.mode}.txt"
    starting_pitchers_output_file = f"data/output/analysis_SP_{args.mode}.txt"
    relief_pitchers_output_file = f"data/output/analysis_RP_{args.mode}.txt"
    if args.player:
        player_name = args.player
        if player_name in batters_df['name'].values:
            batters_df = batters_df[batters_df['name'] == player_name]
            batters_output_file = f"data/output/analysis_B_{args.mode}_{player_name}.txt"
        else:
            batters_df = pd.DataFrame()
        if player_name in starting_pitchers_df['name'].values:
            starting_pitchers_df = starting_pitchers_df[pitchers_df['name'] == player_name]
            starting_pitchers_output_file = f"data/output/analysis_SP_{args.mode}_{player_name}.txt"
        else:
            starting_pitchers_df = pd.DataFrame()
        if player_name in relief_pitchers_df['name'].values:
            relief_pitchers_df = relief_pitchers_df[pitchers_df['name'] == player_name]
            relief_pitchers_output_file = f"data/output/analysis_RP_{args.mode}_{player_name}.txt"
        else:
            relief_pitchers_df = pd.DataFrame()

    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')

    if not batters_df.empty:
        with open(batters_output_file, 'w') as fileB:
            fileB.write(f"Statcast Batters Analysis...\n")
            fileB.write("=" * 80 + "\n\n")
            
            fileB.write("One Week Ago Analysis:\n")
            fileB.write("-" * 40 + "\n")
            logger.info(f'START batters one week analysis...\n--------------------------------')
            one_week_ago_batters_df = rate_all_batters(batters_df, one_week_ago, today)
            one_week_ago_batters_df = one_week_ago_batters_df.sort_values(by='RATING', ascending=False)
            fileB.write(one_week_ago_batters_df.to_string())
            fileB.write("\n\n")
            write_batter_metrics(fileB, one_week_ago_batters_df, 7)
            logger.info(f'STOP batters one week analysis...\n--------------------------------')

            fileB.write("Two Weeks Ago Analysis:\n")
            fileB.write("-" * 40 + "\n")
            logger.info(f'START batters two week analysis...\n--------------------------------')
            two_weeks_ago_batters_df = rate_all_batters(batters_df, two_weeks_ago, today)
            two_weeks_ago_batters_df = two_weeks_ago_batters_df.sort_values(by='RATING', ascending=False)
            fileB.write(two_weeks_ago_batters_df.to_string())
            fileB.write("\n\n")
            write_batter_metrics(fileB, two_weeks_ago_batters_df, 14)
            logger.info(f'STOP batters two week analysis...\n--------------------------------')

            fileB.write("All Season Analysis:\n")
            fileB.write("-" * 40 + "\n")
            logger.info(f'START batters all season analysis...\n--------------------------------')
            all_season_batters_df = rate_all_batters(batters_df, None, None)
            all_season_batters_df = all_season_batters_df.sort_values(by='RATING', ascending=False)
            fileB.write(all_season_batters_df.to_string())
            fileB.write("\n\n")
            write_batter_metrics(fileB, all_season_batters_df, 365)
            logger.info(f'STOP batters all season analysis...\n--------------------------------')

    if not starting_pitchers_df.empty:
        with open(starting_pitchers_output_file, 'w') as fileSP:
            fileSP.write(f"Statcast STARTING Pitchers Analysis...\n")
            fileSP.write("=" * 80 + "\n\n")

            fileSP.write("One Week Ago Analysis:\n")
            fileSP.write("-" * 40 + "\n")
            logger.info(f'START pitchers one week analysis...\n--------------------------------')
            one_week_ago_pitchers_df = rate_all_pitchers(starting_pitchers_df, one_week_ago, today)
            one_week_ago_pitchers_df = one_week_ago_pitchers_df.sort_values(by='RATING', ascending=False)
            fileSP.write(one_week_ago_pitchers_df.to_string())
            fileSP.write("\n\n")
            write_starting_pitcher_metrics(fileSP, one_week_ago_pitchers_df, 7)
            logger.info(f'STOP pitchers one week analysis...\n--------------------------------')

            fileSP.write("Two Weeks Ago Analysis:\n")
            fileSP.write("-" * 40 + "\n")
            logger.info(f'START pitchers two week analysis...\n--------------------------------')
            two_weeks_ago_pitchers_df = rate_all_pitchers(starting_pitchers_df, two_weeks_ago, today)
            two_weeks_ago_pitchers_df = two_weeks_ago_pitchers_df.sort_values(by='RATING', ascending=False)
            fileSP.write(two_weeks_ago_pitchers_df.to_string())
            fileSP.write("\n\n")
            write_starting_pitcher_metrics(fileSP, two_weeks_ago_pitchers_df, 14)
            logger.info(f'STOP pitchers two week analysis...\n--------------------------------')

            fileSP.write("All Season Analysis:\n")
            fileSP.write("-" * 40 + "\n")
            logger.info(f'START pitchers all season analysis...\n--------------------------------')
            all_season_pitchers_df = rate_all_pitchers(starting_pitchers_df, None, None)
            all_season_pitchers_df = all_season_pitchers_df.sort_values(by='RATING', ascending=False)
            fileSP.write(all_season_pitchers_df.to_string())
            fileSP.write("\n\n")
            write_starting_pitcher_metrics(fileSP, all_season_pitchers_df, 365)
            logger.info(f'STOP pitchers all season analysis...\n--------------------------------')
    
    if not relief_pitchers_df.empty:
        with open(relief_pitchers_output_file, 'w') as fileRP:
            fileRP.write(f"Statcast RELIEF Pitchers Analysis...\n")
            fileRP.write("=" * 80 + "\n\n")

            fileRP.write("One Week Ago Analysis:\n")
            fileRP.write("-" * 40 + "\n")
            logger.info(f'START pitchers one week analysis...\n--------------------------------')
            one_week_ago_pitchers_df = rate_all_pitchers(relief_pitchers_df, one_week_ago, today)
            one_week_ago_pitchers_df = one_week_ago_pitchers_df.sort_values(by='RATING', ascending=False)
            fileRP.write(one_week_ago_pitchers_df.to_string())
            fileRP.write("\n\n")
            write_relief_pitcher_metrics(fileRP, one_week_ago_pitchers_df, 7)
            logger.info(f'STOP pitchers one week analysis...\n--------------------------------')

            fileRP.write("Two Weeks Ago Analysis:\n")
            fileRP.write("-" * 40 + "\n")
            logger.info(f'START pitchers two week analysis...\n--------------------------------')
            two_weeks_ago_pitchers_df = rate_all_pitchers(relief_pitchers_df, two_weeks_ago, today)
            two_weeks_ago_pitchers_df = two_weeks_ago_pitchers_df.sort_values(by='RATING', ascending=False)
            fileRP.write(two_weeks_ago_pitchers_df.to_string())
            fileRP.write("\n\n")
            write_relief_pitcher_metrics(fileRP, two_weeks_ago_pitchers_df, 14)
            logger.info(f'STOP pitchers two week analysis...\n--------------------------------')

            fileRP.write("All Season Analysis:\n")
            fileRP.write("-" * 40 + "\n")
            logger.info(f'START pitchers all season analysis...\n--------------------------------')
            all_season_pitchers_df = rate_all_pitchers(relief_pitchers_df, None, None)
            all_season_pitchers_df = all_season_pitchers_df.sort_values(by='RATING', ascending=False)
            fileRP.write(all_season_pitchers_df.to_string())
            fileRP.write("\n\n")
            write_relief_pitcher_metrics(fileRP, all_season_pitchers_df, 365)
            logger.info(f'STOP pitchers all season analysis...\n--------------------------------')

if __name__ == '__main__':
    main() 