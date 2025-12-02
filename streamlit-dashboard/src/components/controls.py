from streamlit import slider, selectbox, button
import streamlit as st
import pandas as pd

# Display a temperature range slider and the min and max values from the dataframe
def create_temperature_slider(df, min_value=250, max_value=350, default_value=300):
    temp_col = 'mean_temp_k'
    if df.empty or temp_col not in df.columns:
        min_val = min_value
        max_val = max_value
    else:
        min_val = int(df[temp_col].min())
        max_val = int(df[temp_col].max())
    st.sidebar.write(f"Total temperature range: {min_val} - {max_val} K")

    # CRASH FIX: If min and max are the same, disable the slider and return the value
    if min_val == max_val:
        st.sidebar.warning(f"Only one temperature found: {min_val} K")
        return min_val, max_val

    st.sidebar.slider(
        "Temperature (K)",
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val),
        key="temp_range",
    )
    min_temp, max_temp = st.session_state["temp_range"]
    return temp_col, min_temp, max_temp

# Display a timestamp range slider and the min and max values from the dataframe
def create_timestamp_slider(df):
    time_col = 's3_timestamp'
    if df.empty or time_col not in df.columns:
        min_val = pd.to_datetime("2025-01-01 00:00").to_pydatetime()
        max_val = pd.to_datetime("2025-12-01 00:00").to_pydatetime()
    else:
        min_val = pd.to_datetime(df[time_col], unit='s').min().to_pydatetime()
        max_val = pd.to_datetime(df[time_col], unit='s').max().to_pydatetime()
    
    # FIXED: Used single quotes inside f-string to prevent syntax error
    st.sidebar.write(f"Total timestamp range: {min_val.strftime('%Y-%m-%d %H:%M')} - {max_val.strftime('%Y-%m-%d %H:%M')}")

    # CRASH FIX: If min and max are the same, disable the slider and return the value
    if min_val == max_val:
        st.sidebar.info("All events have the same timestamp.")
        return time_col, min_val, max_val

    st.sidebar.slider(
        "Timestamp",
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val),
        key="timestamp_range",
    )
    min_timestamp, max_timestamp = st.session_state["timestamp_range"]
    return time_col, min_timestamp, max_timestamp

# Create a refresh button to enable reloading the site
def create_refresh_button(callback):
    return button("Refresh Data", on_click=callback)