# -----------------------------
# Stage 1: Builder
# -----------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy requirements and install dependencies (cached)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# -----------------------------
# Stage 2: Runtime
# -----------------------------
FROM python:3.11-slim

# Set timezone to UTC
ENV TZ=UTC

WORKDIR /app

# Install cron + timezone tools
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Configure timezone to UTC
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone

# Copy installed python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Create volume mount folders
RUN mkdir -p /data /cron && chmod 755 /data /cron

# -----------------------------
# Step 10: Cron job for logging 2FA
# -----------------------------
# Copy Python script for cron
COPY scripts/log_2fa_cron.py /app/scripts/log_2fa_cron.py

# Copy cron configuration
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# Set correct permissions and install cron job
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron

# Ensure log folder/file exists
RUN mkdir -p /cron && chmod 755 /cron && \
    touch /cron/last_code.txt && chmod 666 /cron/last_code.txt

# Expose backend port
EXPOSE 8080

# Start cron + FastAPI server
CMD service cron start && uvicorn app:app --host 0.0.0.0 --port 8080
