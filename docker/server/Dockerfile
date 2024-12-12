# Use Alpine Linux as the base image
FROM alpine:latest

# Install Zabbix agent and other required utilities
RUN apk update && apk add --no-cache \
    bash \
    curl \
    zabbix-agent \
    && rm -rf /var/cache/apk/*

# Copy custom Zabbix agent configuration into the container
COPY zabbix_agent_config.conf /etc/zabbix/zabbix_agentd.conf

# Expose the Zabbix Agent port to allow communication
EXPOSE 10050

# Start the Zabbix agent on container startup
CMD ["zabbix_agentd", "-f"]
