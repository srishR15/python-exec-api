FROM python:3.10-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    make \
    g++ \
    flex \
    bison \
    pkg-config \
    protobuf-compiler \
    libprotobuf-dev \
    libnl-3-dev \
    libnl-route-3-dev \
    libcap-dev \
    libseccomp-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install nsjail
RUN git clone https://github.com/google/nsjail.git /tmp/nsjail \
    && cd /tmp/nsjail \
    && git checkout 3.1 \
    && make \
    && mv nsjail /usr/local/bin/nsjail \
    && rm -rf /tmp/nsjail

# Create sandbox and working directory
RUN mkdir -p /sandbox /etc/nsjail
WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY app.py .
COPY nsjail.cfg /etc/nsjail/

# Set proper permissions
RUN chmod 777 /sandbox \
    && chmod 644 /etc/nsjail/nsjail.cfg

# Drop to non-root user
USER nobody

EXPOSE 8080

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 8 --timeout 0 app:app"]