# Multi-stage Dockerfile for Agent Integrations Finder
# Stage 1: Build stage
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    zip \
    tar \
    gzip \
    dpkg-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt build_requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r build_requirements.txt

# Copy source code
COPY . .

# Build the executable for the target architecture
ARG TARGETARCH
RUN if [ "$TARGETARCH" = "amd64" ]; then \
        python build.py linux-x86_64; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
        python build.py linux-aarch64; \
    else \
        echo "Unsupported architecture: $TARGETARCH"; \
        exit 1; \
    fi

# Stage 2: Runtime stage
FROM python:3.11-slim AS runtime

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages/

# Copy the application source
COPY --from=builder /app/integrations_finder.py /app/

# Switch to non-root user
USER app

# Set environment variables
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages
ENV PATH=/usr/local/bin:$PATH

# Default command
ENTRYPOINT ["python", "/app/integrations_finder.py"]
CMD ["--help"]
