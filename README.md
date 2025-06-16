# MLB Fantasy Analysis

This project analyzes MLB players and fantasy baseball rosters using Python. It provides tools to:
- Analyze player statistics
- Evaluate fantasy roster performance
- Compare players across different statistical categories

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Place your roster file in the `data` directory

## Usage

Run the main analysis script:
```bash
python src/analyze_roster.py
```

## Data Sources
- MLB statistics are pulled using the pybaseball library
- Roster data should be provided in a text file format 