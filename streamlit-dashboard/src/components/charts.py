from typing import List
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st

# Plot temperature distribution histogram
def plot_temperature_distributions(data: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.histplot(data['mean_temp_k'], bins=30, kde=True, ax=axes[0], color='blue', label='Mean Temp (K)', alpha=0.5)
    axes[0].legend()
    axes[0].set_title('Mean Temperature Distribution')
    axes[0].set_xlabel('Temperature (K)')
    axes[0].set_ylabel('Frequency')
    axes[0].grid(True)

    sns.histplot(data['max_temp_k'], bins=30, kde=True, ax=axes[1], color='red', label='Max Temp (K)', alpha=0.5)
    axes[1].legend()
    axes[1].set_title('Max Temperature Distribution')
    axes[1].set_xlabel('Temperature (K)')
    axes[1].set_ylabel('Frequency')
    axes[1].grid(True)

    st.pyplot(fig)
    plt.close(fig)

def plot_temperature_scatter(data: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='total_pixels', y='max_temp_k', data=data, ax=ax, color='red', label='Max Temp (K)', alpha=0.6)
    sns.scatterplot(x='total_pixels', y='mean_temp_k', data=data, ax=ax, color='blue', label='Mean Temp (K)', alpha=0.6)
    ax.set_title('Scatter Plot of Total Pixels vs Max/Mean Temperature')
    ax.set_xlabel('Total Pixels Affected')
    ax.set_ylabel('Temperature (K)')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)

def plot_temperatures_box_whiskers(data: pd.DataFrame, threshold=None) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=data[['min_temp_k', 'mean_temp_k', 'max_temp_k']], ax=ax)
    ax.set_title('Box and Whisker Plot of Temperatures')
    ax.set_ylabel('Temperature (K)')
    ax.set_xticklabels(['Min Temp (K)', 'Mean Temp (K)', 'Max Temp (K)'])
    st.pyplot(fig)
    plt.close(fig)

def plot_temperatures_over_time(data: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    data['s3_timestamp'] = pd.to_datetime(data['s3_timestamp'], unit='s')
    sns.lineplot(x='s3_timestamp', y='mean_temp_k', data=data, ax=ax, label='Mean Temp (K)')
    sns.lineplot(x='s3_timestamp', y='max_temp_k', data=data, ax=ax, label='Max Temp (K)')
    sns.lineplot(x='s3_timestamp', y='min_temp_k', data=data, ax=ax, label='Min Temp (K)')
    ax.set_title('Temperature Over Time')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Temperature (K)')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)

# Plot wildfire event histogram by total pixels affected
def plot_fire_events(data: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data['total_pixels'], bins=30, kde=True, ax=ax)
    ax.set_title('Count of Wildfire Events by Total Pixels Affected')
    ax.set_xlabel('Total Pixels Affected')
    ax.set_ylabel('Frequency')
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)