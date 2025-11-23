# Wildfire Streamlit Dashboard

This project is a Streamlit application that visualizes wildfire data processed by a Flink job. It provides an interactive dashboard to monitor and analyze wildfire events based on temperature metrics.

## Project Structure

```
streamlit-dashboard/
├── src/
│   ├── streamlit_app.py          # Main entry point for the Streamlit dashboard
│   ├── components/
│   │   ├── charts.py             # Functions for creating visualizations
│   │   └── controls.py           # UI controls for user interaction
│   ├── services/
│   │   └── flink_client.py        # Handles communication with the Flink job
│   ├── metrics/
│   │   └── compute_metrics.py     # Functions to compute metrics from data
│   └── utils/
│       └── helpers.py            # Utility functions for data processing
├── requirements.txt               # Project dependencies
├── Dockerfile                     # Instructions to build the Docker image
├── .streamlit/
│   └── config.toml               # Configuration settings for the Streamlit app
└── README.md                      # dashboard documentation
```

## Setup Instructions

1. **Navigate to the streamlit directory**
   ```bash
   cd streamlit-dashboard
   ```

2. **Install Dependencies**
   ```bash
   source ../.venv/bin/activate  # Activate the parent directory virtual environment
   pip install -r requirements.txt  # Install additional packages for streamlit
   ```

3. **Run the Streamlit Application**
   ```bash
   streamlit run src/streamlit_app.py
   ```

4. **Access the Dashboard**
   Open your web browser and go to `http://localhost:8501` to view the dashboard.

## Usage Guidelines

- Use the controls on the dashboard to filter and visualize wildfire events based on temperature metrics.
- The dashboard displays various charts that represent the data processed by the Flink job, allowing for real-time monitoring of wildfire events.

## Overview of Components

- **streamlit_app.py**: Initializes the Streamlit application and sets up the layout.
- **charts.py**: Contains functions for generating visualizations such as temperature distributions.
- **controls.py**: Provides interactive controls like sliders and filters.
- **flink_client.py**: Manages the connection to the Flink job.
- **compute_metrics.py**: Computes metrics such as average temperature and counts of high-temperature events.
- **helpers.py**: Includes utility functions for data formatting.

## Specifications

Requires specifications for the dashboard, as discussed in the project proposal and milestone goals:

- Provide an interactive interface
- Display historical wildfire events and summaries
- Display spatial statistics
- Visualize geospatial wildfire maps
- Display real-time updates
- Display predictive model output with prediction overlays

<!-- ## Docker

To build and run the Docker container, use the following commands:
```
docker build -t streamlit-dashboard .
docker run -p 8501:8501 streamlit-dashboard
``` -->

