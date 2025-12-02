import streamlit as st
import pandas as pd
from services.flink_client import get_synthetic_data, get_kafka_data
from metrics.compute_metrics import (
    calculate_average_temperature, 
    calculate_median_temperature, 
    count_high_temp_events, 
    calculate_number_of_events
)
from components.charts import (
    plot_temperature_distributions, 
    plot_temperature_scatter, 
    plot_fire_events, 
    plot_temperatures_box_whiskers, 
    plot_temperatures_over_time
)
from components.controls import create_temperature_slider, create_timestamp_slider

HIGH_TEMP_THRESHOLD = 2000

def main():
    st.set_page_config(page_title="Wildfire Dashboard", layout="wide")
    st.title("Wildfire Detection Dashboard")

    if st.sidebar.button("Refresh Data"):
        st.rerun()

    # ==========================================
    # PART 1: ORIGINAL VISUALIZATIONS (Git Style)
    # ==========================================
    # This uses the synthetic data to preserve the "Demo" look
    data = get_kafka_data()

    if data is not None:
        df = pd.DataFrame(data)

        # --- Metrics ---
        st.header("Summary Statistics")
        avg_temp = calculate_average_temperature(df)
        median_temp = calculate_median_temperature(df)
        high_temp_count = count_high_temp_events(df, threshold=HIGH_TEMP_THRESHOLD)
        num_events = calculate_number_of_events(df)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Average Temperature (K)", avg_temp)
        col2.metric("Median Temperature (K)", median_temp)
        col3.metric(f"High Temp Events (> {HIGH_TEMP_THRESHOLD} K)", high_temp_count)
        col4.metric("Number of Events", num_events)
        
        # --- Filters ---
        st.sidebar.header("Filters")
        temp_col, min_temp, max_temp = create_temperature_slider(df)
        time_col, min_timestamp, max_timestamp = create_timestamp_slider(df)

        filtered_data = df[(df[temp_col] >= min_temp) & (df[temp_col] <= max_temp) &
                           (pd.to_datetime(df[time_col], unit='s').between(pd.to_datetime(min_timestamp), pd.to_datetime(max_timestamp)))]

        # --- Charts ---
        st.header("📊 Visualizations")
        plot_temperatures_over_time(filtered_data)
        plot_temperature_distributions(filtered_data)
        plot_temperature_scatter(filtered_data)
        plot_temperatures_box_whiskers(filtered_data, threshold=HIGH_TEMP_THRESHOLD)
        plot_fire_events(filtered_data)

    else:
        st.error("No simulation data available.")

    # ==========================================
    # PART 2: NEW DYNAMIC TABLE (Real Data)
    # ==========================================
    st.divider()
    st.subheader("🔥 Live Critical Alerts (> 2000 K)")
    st.caption("Real-time high-intensity events detected by Flink")

    live_data = get_kafka_data()

    if not live_data.empty:
        # Sort by newest first
        live_data = live_data.sort_values(by="s3_timestamp", ascending=False)
        
        st.dataframe(
            live_data,
            use_container_width=True,
            column_config={
                "timestamp": "Time Detected",
                "max_temp_k": st.column_config.NumberColumn("Max Temp", format="%.2f K"),
                "total_pixels": "Size (Pixels)"
            },
            hide_index=True
        )
    else:
        st.info("No critical fires detected yet (Max Temp > 2000 K). Check Producer.")

if __name__ == "__main__":
    main()