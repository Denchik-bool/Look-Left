import os
import requests
from dash import Dash, dcc, html
import plotly.graph_objs as go
from threading import Thread
import time

def get_zabbix_token():
    """Retrieve Zabbix API token"""
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": os.getenv("ZABBIX_USER", "Admin"),
            "password": os.getenv("ZABBIX_PASSWORD", "zabbix")
        },
        "id": 1
    }
    response = requests.post(os.getenv("ZABBIX_URL", "http://localhost:8080/api_jsonrpc.php"), json=payload)
    return response.json()["result"]

def get_host_metrics(token, host):
    """Fetch metrics for a specific host"""
    payload = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "output": ["name", "lastvalue"],
            "host": host
        },
        "auth": token,
        "id": 1
    }
    response = requests.post(os.getenv("ZABBIX_URL", "http://localhost:8080/api_jsonrpc.php"), json=payload)
    return response.json().get("result", [])

def fetch_metrics_periodically():
    """Periodically fetch metrics from Zabbix and store them for the dashboard"""
    global metrics_data
    token = get_zabbix_token()
    host = os.getenv("ZABBIX_HOST", "Simulated Host")

    while True:
        try:
            metrics = get_host_metrics(token, host)
            cpu_usage = next((float(m["lastvalue"]) for m in metrics if "CPU" in m["name"]), None)
            memory_usage = next((float(m["lastvalue"]) for m in metrics if "Memory" in m["name"]), None)

            if cpu_usage is not None and memory_usage is not None:
                metrics_data["CPU Usage"].append(cpu_usage)
                metrics_data["Memory Usage"].append(memory_usage)

                # Keep only the last 10 points
                metrics_data["CPU Usage"] = metrics_data["CPU Usage"][-10:]
                metrics_data["Memory Usage"] = metrics_data["Memory Usage"][-10:]

        except Exception as e:
            print(f"Error fetching metrics: {e}")

        time.sleep(5)  # Fetch every 5 seconds

# Initialize Dash app
app = Dash(__name__)
metrics_data = {"CPU Usage": [], "Memory Usage": []}

# Start thread to fetch metrics
fetch_thread = Thread(target=fetch_metrics_periodically, daemon=True)
fetch_thread.start()

# Layout for the dashboard
app.layout = html.Div([
    html.H1("Server Metrics Dashboard"),
    dcc.Graph(
        id='server-metrics',
        style={'height': '65vh'},
        config={'displayModeBar': False}
    ),
    dcc.Interval(
        id='update-interval',
        interval=5000,  # in milliseconds
        n_intervals=0
    )
])

# Callback to update the graph dynamically
@app.callback(
    dcc.Output('server-metrics', 'figure'),
    [dcc.Input('update-interval', 'n_intervals')]
)
def update_graph(n):
    return {
        'data': [
            go.Scatter(
                x=list(range(len(metrics_data["CPU Usage"]))),
                y=metrics_data["CPU Usage"],
                mode='lines+markers',
                name='CPU Usage'
            ),
            go.Scatter(
                x=list(range(len(metrics_data["Memory Usage"]))),
                y=metrics_data["Memory Usage"],
                mode='lines+markers',
                name='Memory Usage'
            )
        ],
        'layout': go.Layout(
            title='Server Metrics Over Time',
            xaxis={'title': 'Time (Last 10 Points)'},
            yaxis={'title': 'Usage (%)'},
            margin={'l': 40, 'r': 40, 't': 40, 'b': 40},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
