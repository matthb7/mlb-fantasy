import pandas as pd

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
                        if len(parts) == 4:  # name, position, start_year, mlbID
                            name = parts[0].strip()
                            position = parts[1].strip()
                            start_year = int(parts[2].strip())
                            player_id = int(parts[3].strip())
                            roster[category].append({
                                'name': name,
                                'position': position,
                                'start_year': start_year,
                                'mlbID': player_id
                            })
                        elif len(parts) == 3:  # name, position, start_year
                            name = parts[0].strip()
                            position = parts[1].strip()
                            start_year = int(parts[2].strip())
                            roster[category].append({
                                'name': name,
                                'position': position,
                                'start_year': start_year,
                                'mlbID': None
                            })
                        
        
        return {k: pd.DataFrame(v) for k, v in roster.items() if v}
    except FileNotFoundError:
        print(f"Error: Roster file not found at {file_path}")
        return None
    except ValueError as e:
        print(f"Error: Invalid start year format in roster file: {str(e)}")
        return None
    
def write_batter_metrics(fileB, df, days_ago):
    fileB.write("Points per Game (GP):\n")
    points_per_game = pd.to_numeric(df['POINTS'], errors='coerce') / pd.to_numeric(df['GP'].replace(0, 1), errors='coerce')
    result_df = pd.DataFrame({
        'Name': df['name'],
        'Position': df['position'],
        'Points/Game': points_per_game
    })
    fileB.write(result_df.to_string())
    fileB.write("\n\n")

    fileB.write("Points per Day:\n")
    points_per_day = pd.to_numeric(df['POINTS'], errors='coerce') / days_ago
    result_df = pd.DataFrame({
        'Name': df['name'],
        'Position': df['position'],
        'Points/Day': points_per_day
    })
    fileB.write(result_df.to_string())
    fileB.write("\n\n")

    fileB.write("At Bats (AB) per Day:\n")
    ab_per_day = pd.to_numeric(df['AB'], errors='coerce') / days_ago
    result_df = pd.DataFrame({
        'Name': df['name'],
        'Position': df['position'],
        'AB/Day': ab_per_day
    })
    fileB.write(result_df.to_string())
    fileB.write("\n\n")

def write_starting_pitcher_metrics(fileP, df, days_ago):
    fileP.write("Points per Game (GS):\n")
    points_per_game = pd.to_numeric(df['POINTS'], errors='coerce') / pd.to_numeric(df['GS'].replace(0, 1), errors='coerce')
    result_df = pd.DataFrame({
        'Name': df['name'],
        'Position': df['position'],
        'Points/Game': points_per_game
    })
    fileP.write(result_df.to_string())
    fileP.write("\n\n")

    fileP.write("Points per Day:\n")
    points_per_day = pd.to_numeric(df['POINTS'], errors='coerce') / days_ago
    result_df = pd.DataFrame({
        'Name': df['name'],
        'Position': df['position'],
        'Points/Day': points_per_day
    })
    fileP.write(result_df.to_string())
    fileP.write("\n\n")

    fileP.write("Innings Pitched per Game:\n")
    ip_per_game = pd.to_numeric(df['IP'], errors='coerce') / pd.to_numeric(df['GS'].replace(0, 1), errors='coerce')
    result_df = pd.DataFrame({
        'Name': df['name'],
        'Position': df['position'],
        'IP/Game': ip_per_game
    })
    fileP.write(result_df.to_string())
    fileP.write("\n\n")

def write_relief_pitcher_metrics(fileP, df, days_ago):
    fileP.write("Points per Game (GP):\n")
    points_per_game = pd.to_numeric(df['POINTS'], errors='coerce') / pd.to_numeric(df['GP'].replace(0, 1), errors='coerce')
    result_df = pd.DataFrame({
        'Name': df['name'],
        'Position': df['position'],
        'Points/Game': points_per_game
    })
    fileP.write(result_df.to_string())
    fileP.write("\n\n")

    fileP.write("Points per Day:\n")
    points_per_day = pd.to_numeric(df['POINTS'], errors='coerce') / days_ago
    result_df = pd.DataFrame({
        'Name': df['name'],
        'Position': df['position'],
        'Points/Day': points_per_day
    })
    fileP.write(result_df.to_string())
    fileP.write("\n\n")

    fileP.write("Innings Pitched per Game:\n")
    ip_per_game = pd.to_numeric(df['IP'], errors='coerce') / pd.to_numeric(df['GP'].replace(0, 1), errors='coerce')
    result_df = pd.DataFrame({
        'Name': df['name'],
        'Position': df['position'],
        'IP/Game': ip_per_game
    })
    fileP.write(result_df.to_string())
    fileP.write("\n\n")

    fileP.write("Save (SV) / Save Opp (SOP):\n")
    sv_per_opp = pd.to_numeric(df['SV'], errors='coerce') / pd.to_numeric(df['SOP'].replace(0, 1), errors='coerce')
    result_df = pd.DataFrame({
        'Name': df['name'],
        'Position': df['position'],
        'SV/SOP': sv_per_opp
    })
    fileP.write(result_df.to_string())
    fileP.write("\n\n")