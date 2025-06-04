# SC-Esport-Stats

## Overview
SC-Esport-Stats is a web application built with Streamlit that allows users to view and analyze esports statistics. The application provides a user-friendly interface for displaying various statistics related to esports matches.

## Project Structure
```
sc-esport-stats
├── src
│   ├── app.py                # Main entry point of the Streamlit application
│   ├── components
│   │   └── stats_display.py   # Functions for rendering statistics
│   ├── data_processing
│   │   └── stats_analyzer.py  # Functions for processing and analyzing data
│   └── utils
│       └── helpers.py         # Utility functions for various tasks
├── data
│   └── raw                    # Directory for storing raw data files
├── requirements.txt           # Python dependencies for the project
├── .streamlit
│   └── config.toml           # Streamlit configuration settings
└── README.md                  # Documentation for the project
```

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
To run the Streamlit application, execute the following command in your terminal:
```
streamlit run src/app.py
```

### Features
- Display various esports statistics in a visually appealing format.
- Analyze raw data and generate insights.
- User-friendly interface for easy navigation and interaction.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.