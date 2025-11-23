from typing import List
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st

# Plot temperature distribution histogram
def plot_temperature_distribution(data: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data['mean_temp_k'], bins=30, kde=True, ax=ax)
    ax.set_title('Temperature Distribution of Wildfire Events')
    ax.set_xlabel('Mean Temperature (K)')
    ax.set_ylabel('Frequency')
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)

# Plot wildfire event histogram by total pixels affected
def plot_fire_events(data: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data['total_pixels'], bins=30, kde=True, ax=ax)
    ax.set_title('Count of Wildfire Events by Total Pixels Affected')
    ax.set_xlabel('Total Pixels Affected')
    ax.set_ylabel('Count of Events')
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)