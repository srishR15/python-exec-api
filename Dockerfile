FROM python:3.10-slim

# dependencies
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

RUN git clone https://github.com/google/nsjail.git /tmp/nsjail \
    && cd /tmp/nsjail \
    && git checkout 3.1 \
    && make \
    && mv nsjail /usr/local/bin/nsjail \
    && rm -rf /tmp/nsjail

# Create sandbox environment here
RUN mkdir -p /sandbox /etc/nsjail
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY nsjail.cfg /etc/nsjail/

RUN ln -s $(which python3) /usr/bin/python3 && \
    mkdir -p /sandbox && \
    python3 -c "import sys; print(f'Python paths: {sys.path}')" && \
    chown nobody:nogroup /sandbox

# Verify if Python installation is done
RUN echo "Python location: $(which python3)" && \
    ls -la $(which python3) && \
    ls -la /usr/bin/python3

RUN ls -la /usr/local/bin/python* && \
    ls -la /usr/bin/python*

# Set permissions that are required
RUN chmod 755 /app && \
    chmod 644 /etc/nsjail/nsjail.cfg && \
    chown -R nobody:nogroup /sandbox

# Run as non-root user
USER nobody

EXPOSE 8080
CMD ["python3", "app.py"]