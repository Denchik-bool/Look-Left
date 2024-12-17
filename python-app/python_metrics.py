import psutil
import socket
import time
import subprocess
from flask import Flask, jsonify
from threading import Thread

app = Flask(__name__)

def collect_and_send_metrics():
    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # Get memory usage
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    
    # Get server name
    server_name = socket.gethostname()

    # Get network traffic
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv
    
    # Get uptime
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    
    metrics = {
        "server_name": server_name,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "uptime": uptime_seconds,
        "bytes_sent": bytes_sent,
        "bytes_recv": bytes_recv
    }
    
    # Send metrics to Zabbix using zabbix-sender
    zabbix_server = 'zabbix'  # Zabbix server hostname
    try:
        subprocess.run(
            f'zabbix_sender -z {zabbix_server} -s {server_name} -k cpu.usage -o {cpu_usage}',
            shell=True,
            check=True
        )
        subprocess.run(
            f'zabbix_sender -z {zabbix_server} -s {server_name} -k memory.usage -o {memory_usage}',
            shell=True,
            check=True
        )
        subprocess.run(
            f'zabbix_sender -z {zabbix_server} -s {server_name} -k uptime -o {uptime_seconds}',
            shell=True,
            check=True
        )
        subprocess.run(
            f'zabbix_sender -z {zabbix_server} -s {server_name} -k net.bytes_recv -o {bytes_recv}',
            shell=True,
            check=True
        )
        subprocess.run(
            f'zabbix_sender -z {zabbix_server} -s {server_name} -k net.bytes_sent -o {bytes_sent}',
            shell=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error sending metrics to Zabbix: {e}")
    
    return metrics

@app.route('/metrics')
def get_metrics():
    metrics = collect_and_send_metrics()
    return jsonify(metrics)

def send_metrics_periodically():
    while True:
        collect_and_send_metrics()
        time.sleep(20)  # Send metrics every 20 seconds

if __name__ == '__main__':
    # Start Flask app in a separate thread with threaded=True
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, threaded=True))
    flask_thread.start()
    
    # Start sending metrics periodically
    send_metrics_periodically()
