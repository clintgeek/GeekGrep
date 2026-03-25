# Multi-stage build for geekGrep

# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app:$PYTHONPATH \
    PYTHONUNBUFFERED=1 \
    GEEKGREP_DATA_DIR=/data \
    GEEKGREP_DOCUMENTS_DIR=/documents

# Create directories
RUN mkdir -p /data /documents

# Expose port for Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command: run Streamlit from app root
WORKDIR /app
CMD ["streamlit", "run", "src/ui/web.py", "--server.port=8501", "--server.address=0.0.0.0"]
