import psutil
import socket
import time
from flask import Flask, jsonify
from pyzabbix import ZabbixMetric, ZabbixSender

app = Flask(__name__)

@app.route('/metrics')
def get_metrics():
    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # Get memory usage
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    
    # Get server name
    server_name = socket.gethostname()
    
    # Get uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    
    metrics = {
        "server_name": server_name,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "uptime": uptime
    }
    
    # Send metrics to Zabbix
    zabbix_server = 'zabbix'  # Zabbix server hostname or IP
    zabbix_metrics = [
        ZabbixMetric(server_name, 'cpu.usage', cpu_usage),
        ZabbixMetric(server_name, 'memory.usage', memory_usage),
        ZabbixMetric(server_name, 'uptime', uptime_seconds)
    ]
    ZabbixSender(zabbix_server).send(zabbix_metrics)
    
    return jsonify(metrics)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)