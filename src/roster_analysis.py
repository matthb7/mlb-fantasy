import pandas as pd
import logging
import requests
import time
from pybaseball import playerid_lookup
from mlb_api import get_player_id

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_player_data(player_id, season=2025, group='batting'):
    url = f'https://statsapi.mlb.com/api/v1/people?personIds={player_id}&hydrate=stats(group=[{group}],type=[season],season={season})'
    time.sleep(10)  # Sleep for 10 seconds before making the request
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f'Failed to fetch data for player ID {player_id}')
        return None

def analyze_roster(roster_df):
    """
    Analyze the roster DataFrame and log the results.
    """
    logging.info('Analyzing roster...')
    for index, row in roster_df.iterrows():
        player_name = row['name']  # Assuming 'name' is the column for player names
        player_id = get_player_id(player_name)
        if player_id:
            player_data = fetch_player_data(player_id)
            if player_data:
                logging.info(f'Data for {player_name}: {player_data}')
        else:
            logging.warning(f'No player ID found for {player_name}')

def fetch_single_player(player_name, season=2025, group='batting'):
    player_id = get_player_id(player_name, season)
    if player_id:
        player_data = fetch_player_data(player_id, season, group)
        if player_data:
            logging.info(f'Data for {player_name}: {player_data}')
        else:
            logging.warning(f'No data found for {player_name}')
    else:
        logging.warning(f'No player ID found for {player_name}')

def main():
    # Load the roster from roster.txt
    roster_df = pd.read_csv('roster.txt', sep='\t')  # Adjust separator if necessary
    analyze_roster(roster_df)

    # Example: Fetch data for a single player
    # fetch_single_player('G Perdomo')

if __name__ == '__main__':
    main() 