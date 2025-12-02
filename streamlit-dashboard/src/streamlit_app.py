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
    # PART 1: ORIGINAL VISUALIZATIONS
    # ==========================================
    data = get_kafka_data()

    if data is not None and not data.empty:
        df = pd.DataFrame(data)

        # --- FIX: ADAPT NEW FLINK DATA TO OLD CHARTS ---
        if 'avg_temp_k' in df.columns:
            df = df.rename(columns={
                'avg_temp_k': 'mean_temp_k',      # Map Avg -> Mean
                'event_count': 'total_pixels',    # Map Count -> Total Pixels
                'window_start': 's3_timestamp'    # Map Window Start -> Timestamp
            })
            
            # 1. Fix Timestamp (String -> Number)
            try:
                df['s3_timestamp'] = pd.to_datetime(df['s3_timestamp']).astype('int64') // 10**9
            except Exception as e:
                pass # Already numeric or failed
            
            # 2. Fix Missing 'min_temp_k' (CRITICAL FIX)
            # The new job doesn't calculate Min, so we use Mean as a placeholder
            if 'min_temp_k' not in df.columns:
                df['min_temp_k'] = df['mean_temp_k']
        # -----------------------------------------------

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

        if time_col in df.columns and temp_col in df.columns:
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
            st.warning("Data loaded, but columns for filtering are missing.")

    else:
        st.error("No data available. (Is the Flink job running?)")

    # ==========================================
    # PART 2: NEW ADVANCED MONITORING
    # ==========================================
    st.divider()
    st.subheader("Live Wildfire Heatmap & Aggregates")
    
    live_data = get_kafka_data()
    
    if not live_data.empty and 'grid_latitude' in live_data.columns:
        
        latest_window = live_data['window_end'].max()
        current_view = live_data[live_data['window_end'] == latest_window]
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Latest Window Time", str(latest_window)[11:19])
        m2.metric("Active Hot Zones", len(current_view))
        m3.metric("Highest Detected Temp", f"{current_view['max_temp_k'].max():.1f} K")
        
        if 'max_end_to_end_delay_seconds' in current_view.columns:
             m4.metric("Max System Lag", f"{current_view['max_end_to_end_delay_seconds'].max()} s")

        st.write("### 📍 Active Fire Zones")
        st.map(current_view.rename(columns={'grid_latitude': 'latitude', 'grid_longitude': 'longitude'}), size='event_count', color='#FF4B4B')
        
        st.write("### Intensity Trends (Last 5 mins)")
        # Aggregate across all grids for the chart
        time_trends = live_data.groupby('window_start').agg({
            'event_count': 'sum',
            'max_temp_k': 'max',
            'avg_temp_k': 'mean'
        }).reset_index().sort_values('window_start')

        tab1, tab2 = st.tabs(["Event Volume", "Max Temperature"])
        with tab1:
            st.bar_chart(time_trends, x='window_start', y='event_count', color="#FF4B4B")
        with tab2:
            st.line_chart(time_trends, x='window_start', y='max_temp_k')

if __name__ == "__main__":
    main()