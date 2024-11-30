# Use the official Ubuntu base image
FROM ubuntu:20.04

# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages and dependencies
RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    curl \
    gnupg2 \
    lsb-release \
    wget \
    apt-transport-https && \
    # Add GlusterFS 10 repository
    add-apt-repository ppa:gluster/glusterfs-10 && \
    apt-get update && \
    # Install GlusterFS server and necessary utilities
    apt-get install -y \
    glusterfs-server \
    iputils-ping \
    net-tools && \
    apt-get clean

# Expose the necessary ports for GlusterFS communication
EXPOSE 24007 24008 24009 49152

# Create necessary directories for GlusterFS brick data storage
RUN mkdir -p /gluster/brick

# Start GlusterFS daemon in the foreground when the container runs
CMD ["glusterd", "-N", "--no-daemon"]
