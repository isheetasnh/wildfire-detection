# monitor.py
import json
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output

LOG_FILE = "producer_metrics_log.jsonl"

def load_metrics():
    """Load the JSONL metrics into a pandas DataFrame."""
    rows = []
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
    except FileNotFoundError:
        return pd.DataFrame()

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    return df

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H2("Kafka Producer: Real-Time Metrics"),
        dcc.Graph(id="metrics-graph"),
        dcc.Interval(
            id="interval-component",
            interval=1000,
            n_intervals=0
        ),
    ]
)

@app.callback(
    Output("metrics-graph", "figure"),
    Input("interval-component", "n_intervals"),
)
def update_graph(n):
    df = load_metrics()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Waiting for metrics...",
            xaxis_title="Time",
            yaxis_title="Value",
        )
        return fig

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Throughput (msg/s)", "Latency (seconds)"),
    )

    # Throughput trace
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["throughput_msgs_per_sec"],
            mode="lines+markers",
            name="Throughput (msg/s)",
        ),
        row=1,
        col=1,
    )

    # Latency trace
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["last_latency_sec"],
            mode="lines+markers",
            name="Latency (s)",
        ),
        row=2,
        col=1,
    )

    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="msg/s", row=1, col=1)
    fig.update_yaxes(title_text="seconds", row=2, col=1)

    fig.update_layout(
        height=600,
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
