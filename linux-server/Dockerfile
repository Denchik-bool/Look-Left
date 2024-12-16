# Use an official Ubuntu as a parent image
FROM ubuntu:latest

# Install necessary packages
RUN apt-get update && apt-get install -y \
    sysstat \
    && rm -rf /var/lib/apt/lists/*

# Enable sysstat
RUN sed -i 's/ENABLED="false"/ENABLED="true"/' /etc/default/sysstat

# Start sysstat service and keep the container running
CMD ["sh", "-c", "service sysstat start && tail -f /dev/null"]