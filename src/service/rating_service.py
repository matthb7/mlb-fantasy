import pandas as pd

from api.pybaseball_api import get_player_id
from util import copy_dict_to_df
from api.mlb_api import fetch_batter_data, fetch_fielder_data, fetch_batter_data_by_range, fetch_fielder_data_by_range, fetch_pitcher_data, fetch_pitcher_data_by_range
from service.calculator_service import calculate_batter_rating, calculate_starting_pitcher_rating, calculate_relief_pitcher_rating, calculate_batting_points_from_dict, calculate_pitching_points_from_dict
from service.logging_service import get_logger

# Set up logging
logger = get_logger(__name__)

def write_mlb_api_data_to_dict(data_dict, batting_season_stats, fielding_season_stats, pitching_season_stats):
    # batting stats
    data_dict['HR'] = batting_season_stats.get('homeRuns', 0)
    data_dict['TB'] = batting_season_stats.get('totalBases', 0)
    data_dict['BB'] = batting_season_stats.get('baseOnBalls', 0)
    data_dict['R'] = batting_season_stats.get('runs', 0)
    data_dict['RBI'] = batting_season_stats.get('rbi', 0)
    data_dict['SB'] = batting_season_stats.get('stolenBases', 0)
    data_dict['SO'] = batting_season_stats.get('strikeOuts', 0)
    data_dict['HBP'] = batting_season_stats.get('hitByPitch', 0)
    data_dict['SH'] = batting_season_stats.get('sacBunts', 0)
    data_dict['SF'] = batting_season_stats.get('sacFlies', 0)
    data_dict['CS'] = batting_season_stats.get('caughtStealing', 0)
    # fielding stats
    data_dict['E'] = fielding_season_stats.get('errors', 0)
    data_dict['PO'] = fielding_season_stats.get('putOuts', 0)
    # pitching stats
    data_dict['IP'] = pitching_season_stats.get('inningsPitched', 0)
    data_dict['ER'] = pitching_season_stats.get('earnedRuns', 0)
    data_dict['SV'] = pitching_season_stats.get('saves', 0)
    data_dict['SO'] = pitching_season_stats.get('strikeOuts', 0)
    data_dict['H'] = pitching_season_stats.get('hits', 0)
    data_dict['BB'] = pitching_season_stats.get('baseOnBalls', 0)
    data_dict['HB'] = pitching_season_stats.get('hitBatsmen', 0)
    data_dict['PG'] = pitching_season_stats.get('perfectGame', 0)
    data_dict['HD'] = pitching_season_stats.get('holds', 0)
    # extra stats
    data_dict['GP'] = batting_season_stats.get('gamesPlayed', 0) or pitching_season_stats.get('gamesPlayed', 0)
    data_dict['AB'] = batting_season_stats.get('atBats', 0) or pitching_season_stats.get('atBats', 0)
    data_dict['BA'] = batting_season_stats.get('avg', 0) or pitching_season_stats.get('avg', 0)
    data_dict['OBP'] = batting_season_stats.get('obp', 0) or pitching_season_stats.get('obp', 0)
    data_dict['SLG'] = batting_season_stats.get('slg', 0) or pitching_season_stats.get('slg', 0)
    data_dict['OPS'] = batting_season_stats.get('ops', 0) or pitching_season_stats.get('ops', 0)
    data_dict['GS'] = pitching_season_stats.get('gamesStarted', 0)
    data_dict['SOP'] = pitching_season_stats.get('saveOpportunities', 0)
    data_dict['W'] = pitching_season_stats.get('wins', 0)
    data_dict['L'] = pitching_season_stats.get('losses', 0)
    return data_dict

def fetch_single_player_data(player_id, startDate=None, endDate=None, type='batter'):
    logger.info(f'fetching player data for {player_id}...')
    player_id = int(player_id)
    data_dict = {}
    batting_season_stats = {}
    fielding_season_stats = {}
    pitching_season_stats = {}

    if type == 'pitcher':
        if startDate and endDate:
            pitching_data = fetch_pitcher_data_by_range(player_id, startDate, endDate)
        else:
            pitching_data = fetch_pitcher_data(player_id, 2025)['people'][0]
        if not pitching_data:
            logger.warning(f'No batting data found for {player_id}')
            return None
        pitching_season_stats = pitching_data['stats'][0]['splits'][0]['stat']
    elif type == 'batter':
        if startDate and endDate:
            batting_data = fetch_batter_data_by_range(player_id, startDate, endDate)
        else:
            batting_data = fetch_batter_data(player_id, 2025)['people'][0]
        if not batting_data:
            logger.warning(f'No batting data found for {player_id}')
            return None
        batting_season_stats = batting_data['stats'][0]['splits'][0]['stat']
    
    if startDate and endDate:
        fielding_data = fetch_fielder_data_by_range(player_id, startDate, endDate)
    else:
        fielding_data = fetch_fielder_data(player_id, 2025)['people'][0]
    if not fielding_data:
        logger.warning(f'No batting data found for {player_id}')
        return None
    fielding_season_stats = fielding_data['stats'][0]['splits'][0]['stat']

    write_mlb_api_data_to_dict(data_dict, batting_season_stats, fielding_season_stats, pitching_season_stats)
    return data_dict

def rate_single_batter(batters_df, index, start_date=None, end_date=None):
    name = batters_df.loc[index, 'name']
    player_id = batters_df.loc[index, 'mlbID']
    start_year = batters_df.loc[index, 'start_year']
    logger.info(f'Rating {name}...')
    if pd.isna(player_id):
        player_id = get_player_id(name, start_year)
        logger.warning(f'No MLB ID provided... Queried for name: {name}, ID is {player_id}')
    player_data = fetch_single_player_data(player_id, start_date, end_date)
    if not player_data:
        logger.error(f'No player data found for {name}')
    player_data['POINTS'] = calculate_batting_points_from_dict(player_data)
    copy_dict_to_df(player_data, batters_df, index)
    rating = calculate_batter_rating(player_data)
    logger.info(f'Complete: {rating}')
    return rating

def rate_all_batters(batters_df, start_date=None, end_date=None):
    if isinstance(batters_df, pd.Series):
        batters_df = pd.DataFrame([batters_df])
    for index, row in batters_df.iterrows():
        rating = rate_single_batter(batters_df, index, start_date, end_date)
        batters_df.loc[index, 'RATING'] = rating
    return batters_df

def rate_single_pitcher(pitchers_df, index, start_date=None, end_date=None):
    name = pitchers_df.loc[index, 'name']
    player_id = pitchers_df.loc[index, 'mlbID']
    start_year = pitchers_df.loc[index, 'start_year']
    position = pitchers_df.loc[index, 'position']
    logger.info(f'Rating {name}...')
    if pd.isna(player_id):
        player_id = get_player_id(name, start_year)
        logger.warning(f'No MLB ID provided... Queried for name: {name}, ID is {player_id}')
    player_data = fetch_single_player_data(player_id, start_date, end_date, type='pitcher')
    player_data['POINTS'] = calculate_pitching_points_from_dict(player_data)
    copy_dict_to_df(player_data, pitchers_df, index)
    if not player_data:
        logger.error(f'No player data found for {name}')
        return None
    rating = 0  # Initialize rating
    if position == 'SP':
        rating = calculate_starting_pitcher_rating(player_data)
    elif position == 'RP':
        rating = calculate_relief_pitcher_rating(player_data)
    logger.info(f'Complete: {rating}')
    return rating

def rate_all_pitchers(pitchers_df, start_date=None, end_date=None):
    if isinstance(pitchers_df, pd.Series):
        pitchers_df = pd.DataFrame([pitchers_df])
    for index, row in pitchers_df.iterrows():
        rating = rate_single_pitcher(pitchers_df, index, start_date, end_date)  
        pitchers_df.loc[index, 'RATING'] = rating
    return pitchers_df