from streamlit import slider, selectbox, button
import streamlit as st
import pandas as pd

# Display a temperature range slider and the min and max values from the dataframe
def create_temperature_slider(df, min_value=250, max_value=350, default_value=300):
    min_val = int(df['mean_temp_k'].min())
    max_val = int(df['mean_temp_k'].max())
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
    return min_temp, max_temp

# Display a timestamp range slider and the min and max values from the dataframe
def create_timestamp_slider(df):
    min_val = pd.to_datetime(df['timestamp']).min().to_pydatetime()
    max_val = pd.to_datetime(df['timestamp']).max().to_pydatetime()
    
    # FIXED: Used single quotes inside f-string to prevent syntax error
    st.sidebar.write(f"Total timestamp range: {min_val.strftime('%Y-%m-%d %H:%M')} - {max_val.strftime('%Y-%m-%d %H:%M')}")

    # CRASH FIX: If min and max are the same, disable the slider and return the value
    if min_val == max_val:
        st.sidebar.info("All events have the same timestamp.")
        return min_val, max_val

    st.sidebar.slider(
        "Timestamp",
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val),
        key="timestamp_range",
    )
    min_timestamp, max_timestamp = st.session_state["timestamp_range"]
    return min_timestamp, max_timestamp

# Create a refresh button to enable reloading the site
def create_refresh_button(callback):
    return button("Refresh Data", on_click=callback)