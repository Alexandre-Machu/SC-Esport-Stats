# SC-Esport-Stats

## Overview
SC-Esport-Stats is a web application built with Streamlit that allows users to view and analyze League of Legends esports statistics for the SC-Esport team. The application provides a user-friendly interface for displaying various player and team statistics.

## Project Structure
```
sc-esport-stats
├── src
│   ├── app.py                # Main entry point of the Streamlit application
│   ├── components
│   │   ├── stats_display.py        # Global statistics display
│   │   └── player_stats_display.py # Player-specific statistics display
│   └── data_processing
│       └── stats_analyzer.py       # Data processing and analysis
├── data
│   └── *.json                # Match data files
├── requirements.txt          # Python dependencies
├── .streamlit
│   └── config.toml          # Streamlit configuration with custom theme
└── README.md
```

## Features
- **Role-based Navigation**: Easy access to player statistics by role (TOP, JUNGLE, MID, ADC, SUPPORT)
- **Player Statistics**:
  - Average KDA, kills, deaths, and assists
  - CS per minute statistics
  - Vision score tracking
  - Champion pool analysis
- **Match History**:
  - Detailed game history with champion icons
  - Win/Loss tracking
  - Performance metrics per game
  - Champion-specific statistics
- **Visual Analytics**:
  - Champion win/loss distribution
  - Performance trends
  - Interactive data visualizations

## Getting Started

### Prerequisites
- Python 3.7 or higher
- Streamlit

### Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd sc-esport-stats
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Running the Application
To run the Streamlit application:
```
streamlit run src/app.py
```

### Configuration
The application uses a custom theme defined in `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#0b9394"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"
```

## Data Sources
- Match data is stored in JSON format
- Champion icons are fetched from Riot Games Data Dragon API

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.