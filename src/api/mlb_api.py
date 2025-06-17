import requests
import logging
import time

def fetch_batter_data(player_id, season=2025):
    return get_mlb_player_stats(player_id, season, 'batting')

def fetch_fielder_data(player_id, season=2025):
    return get_mlb_player_stats(player_id, season, 'fielding')

def fetch_pitcher_data(player_id, season=2025):
    return get_mlb_player_stats(player_id, season, 'pitching')

def fetch_batter_data_by_range(player_id, startDate, endDate):
    return get_mlb_player_stats_by_range(player_id, startDate, endDate, 'batting')

def fetch_fielder_data_by_range(player_id, startDate, endDate):
    return get_mlb_player_stats_by_range(player_id, startDate, endDate, 'fielding')

def fetch_pitcher_data_by_range(player_id, startDate, endDate):
    return get_mlb_player_stats_by_range(player_id, startDate, endDate, 'pitching')


def get_mlb_player_stats(player_id, season, group):
    url = f'https://statsapi.mlb.com/api/v1/people?personIds={player_id}&hydrate=stats(group=[{group}],type=[season],season={season})'
    # time.sleep(1)  # Sleep for 5 seconds before making the request
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f'Failed to fetch data for player ID {player_id}')
        return None
    
def get_mlb_player_stats_by_range(player_id, startDate, endDate, group):
    url = f'https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=byDateRange&group={group}&startDate={startDate}&endDate={endDate}'
    # time.sleep(1)  # Sleep for 5 seconds before making the request
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f'Failed to fetch data for player ID {player_id}')
        return None
    

    