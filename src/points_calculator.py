import pandas as pd
import logging

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
    'CS': -1, # Caught Stealing
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

FIELDING_POINTS = {
    'PO': 1,  # Put Out
    'E': -1,  # Error
} 

def calculate_batting_points(stats):
    """
    Calculate fantasy points for batting statistics
    """
    points = 0
    if stats is None or stats.empty:
        return 0
    
    player_name = stats['Name'].iloc[0]
    logging.info(f"\nPoints breakdown for {player_name}:")
    
    # Basic stats
    hr_points = stats['HR'].sum() * BATTING_POINTS['HR']
    bb_points = stats['BB'].sum() * BATTING_POINTS['BB']
    r_points = stats['R'].sum() * BATTING_POINTS['R']
    rbi_points = stats['RBI'].sum() * BATTING_POINTS['RBI']
    sb_points = stats['SB'].sum() * BATTING_POINTS['SB']
    so_points = stats['SO'].sum() * BATTING_POINTS['SO']
    hbp_points = stats['HBP'].sum() * BATTING_POINTS['HBP']
    sh_points = stats['SH'].sum() * BATTING_POINTS['SH']
    cs_points = stats['CS'].sum() * BATTING_POINTS['CS']
    
    logging.info(f"HR: {stats['HR'].sum()} × {BATTING_POINTS['HR']} = {hr_points}")
    logging.info(f"BB: {stats['BB'].sum()} × {BATTING_POINTS['BB']} = {bb_points}")
    logging.info(f"R: {stats['R'].sum()} × {BATTING_POINTS['R']} = {r_points}")
    logging.info(f"RBI: {stats['RBI'].sum()} × {BATTING_POINTS['RBI']} = {rbi_points}")
    logging.info(f"SB: {stats['SB'].sum()} × {BATTING_POINTS['SB']} = {sb_points}")
    logging.info(f"SO: {stats['SO'].sum()} × {BATTING_POINTS['SO']} = {so_points}")
    logging.info(f"HBP: {stats['HBP'].sum()} × {BATTING_POINTS['HBP']} = {hbp_points}")
    logging.info(f"SH: {stats['SH'].sum()} × {BATTING_POINTS['SH']} = {sh_points}")
    logging.info(f"CS: {stats['CS'].sum()} × {BATTING_POINTS['CS']} = {cs_points}")
    
    # Calculate singles (1B) from hits and other base hits
    total_hits = stats['H'].sum()
    doubles = stats['2B'].sum()
    triples = stats['3B'].sum()
    homers = stats['HR'].sum()
    singles = total_hits - (doubles + triples + homers)
    
    # Calculate total bases
    tb = (singles + 
          doubles * 2 + 
          triples * 3 + 
          homers * 4)
    tb_points = tb * BATTING_POINTS['TB']
    
    logging.info(f"Total Bases: {tb} × {BATTING_POINTS['TB']} = {tb_points}")
    logging.info(f"  Singles: {singles}")
    logging.info(f"  Doubles: {doubles} × 2 = {doubles * 2}")
    logging.info(f"  Triples: {triples} × 3 = {triples * 3}")
    logging.info(f"  Home Runs: {homers} × 4 = {homers * 4}")
    
    # Fielding points
    po_points = stats['PO'].sum() * FIELDING_POINTS['PO']
    e_points = stats['E'].sum() * FIELDING_POINTS['E']
    
    logging.info(f"Fielding:")
    logging.info(f"  Put Outs: {stats['PO'].sum()} × {FIELDING_POINTS['PO']} = {po_points}")
    logging.info(f"  Errors: {stats['E'].sum()} × {FIELDING_POINTS['E']} = {e_points}")
    
    points = (hr_points + bb_points + r_points + rbi_points + sb_points + 
              so_points + hbp_points + sh_points + cs_points + tb_points +
              po_points + e_points)
    
    logging.info(f"Total Points: {points}")
    logging.info("-" * 50)
    
    return points

def calculate_pitching_points(stats):
    """
    Calculate fantasy points for pitching statistics
    """
    points = 0
    if stats is None or stats.empty:
        return 0
    
    player_name = stats['Name'].iloc[0]
    logging.info(f"\nPoints breakdown for {player_name}:")
    
    # Basic stats
    ip_points = stats['IP'].sum() * PITCHING_POINTS['IP']
    er_points = stats['ER'].sum() * PITCHING_POINTS['ER']
    sv_points = stats['SV'].sum() * PITCHING_POINTS['SV']
    so_points = stats['SO'].sum() * PITCHING_POINTS['SO']
    h_points = stats['H'].sum() * PITCHING_POINTS['H']
    bb_points = stats['BB'].sum() * PITCHING_POINTS['BB']
    hb_points = stats['HBP'].sum() * PITCHING_POINTS['HB']
    
    logging.info(f"IP: {stats['IP'].sum()} × {PITCHING_POINTS['IP']} = {ip_points}")
    logging.info(f"ER: {stats['ER'].sum()} × {PITCHING_POINTS['ER']} = {er_points}")
    logging.info(f"SV: {stats['SV'].sum()} × {PITCHING_POINTS['SV']} = {sv_points}")
    logging.info(f"SO: {stats['SO'].sum()} × {PITCHING_POINTS['SO']} = {so_points}")
    logging.info(f"H: {stats['H'].sum()} × {PITCHING_POINTS['H']} = {h_points}")
    logging.info(f"BB: {stats['BB'].sum()} × {PITCHING_POINTS['BB']} = {bb_points}")
    logging.info(f"HB: {stats['HBP'].sum()} × {PITCHING_POINTS['HB']} = {hb_points}")
    
    # Fielding points
    po_points = stats['PO'].sum() * FIELDING_POINTS['PO']
    e_points = stats['E'].sum() * FIELDING_POINTS['E']
    
    logging.info(f"Fielding:")
    logging.info(f"  Put Outs: {stats['PO'].sum()} × {FIELDING_POINTS['PO']} = {po_points}")
    logging.info(f"  Errors: {stats['E'].sum()} × {FIELDING_POINTS['E']} = {e_points}")
    
    points = (ip_points + er_points + sv_points + so_points + h_points + 
              bb_points + hb_points + po_points + e_points)
    
    logging.info(f"Total Points: {points}")
    logging.info("-" * 50)
    
    return points 