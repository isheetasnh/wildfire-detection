import streamlit as st
import pandas as pd
from datetime import datetime
from services.flink_client import get_flink_data
from metrics.compute_metrics import (
    calculate_average_temperature, 
    calculate_median_temperature, 
    count_high_temp_events, 
    calculate_number_of_events
)
from components.charts import plot_temperature_distribution, plot_fire_events
from components.controls import create_temperature_slider, create_timestamp_slider

HIGH_TEMP_THRESHOLD = 400

def main():
    st.title("Wildfire Detection Dashboard")

    # Fetch data from Flink job
    data = get_flink_data()

    if data is not None:
        # Convert data to DataFrame
        df = pd.DataFrame(data)

        # Calculate metrics
        st.header("Metrics")
        avg_temp = calculate_average_temperature(df)
        median_temp = calculate_median_temperature(df)
        high_temp_count = count_high_temp_events(df, threshold=HIGH_TEMP_THRESHOLD)
        num_events = calculate_number_of_events(df)

        # Display metrics
        st.metric(f"Average Temperature (K)", avg_temp)
        st.metric(f"Median Temperature (K)", median_temp)
        st.metric(f"Count of High Temperature Events (> {HIGH_TEMP_THRESHOLD} K)", high_temp_count)
        st.metric("Number of Events", num_events)
        
        # Set up filters
        st.sidebar.header("Filters")

        # Build temperature slider 
        min_temp, max_temp = create_temperature_slider(df)

        # Build timestamp slider
        min_timestamp, max_timestamp = create_timestamp_slider(df)

        # Filter data based on user input
        filtered_data = df[(df['mean_temp_k'] >= min_temp) & (df['mean_temp_k'] <= max_temp) &
                           (pd.to_datetime(df['timestamp']).between(pd.to_datetime(min_timestamp), pd.to_datetime(max_timestamp)))]

        # Display charts
        st.header("Visualizations")
        plot_temperature_distribution(filtered_data)
        plot_fire_events(filtered_data)

    else:
        st.error("No data available from Flink job.")

if __name__ == "__main__":
    main()