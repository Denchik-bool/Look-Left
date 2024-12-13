# Use an official Ubuntu as a parent image
FROM ubuntu:latest

# Install necessary packages
RUN apt-get update && apt-get install -y \
    sysstat \
    && rm -rf /var/lib/apt/lists/*

# Start the sysstat service
CMD ["sar", "-u", "1", "3"]