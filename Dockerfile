# FOR UBUNTU SERVER
FROM ubuntu:20.04

# Set timezone:
ENV TZ=Asia/Ho_Chi_Minh
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && apt-get update && apt-get install -y tzdata

# Install dependencies:
RUN apt-get update && apt-get install -y --no-install-recommends \
    keyboard-configuration \
    sudo \
    software-properties-common \
    python3.8 \
    python3-distutils \
    python3.8-dev \
    python3-pip \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    fonts-liberation \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install requirements
COPY requirements.txt /tmp/
RUN python3.8 -m pip install --upgrade pip && \
    python3.8 -m pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Copy the rest of the application files
COPY . /app

# Create a non-root user to run the application
RUN groupadd -r app && useradd -r -g app appuser && \
    chown -R appuser:app /app && \
    chmod 755 /app && \
    usermod -a -G sudo appuser && \
    echo 'appuser ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# Use the non-root user to run the application
USER appuser

# Command to run on container start    
ENTRYPOINT ["python3.8"]
CMD ["app.py"]
