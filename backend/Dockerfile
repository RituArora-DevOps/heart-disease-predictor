# ---------------------------------------------------------------------
# STAGE 1: Builder Environment
# Uses the full Python image to ensure robust installation of C extensions (like psycopg2)
# ---------------------------------------------------------------------
FROM python:3.11 AS builder

# Set working directory
WORKDIR /app

# Ensure we use a persistent virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install necessary system dependencies for building psycopg2 (libpq-dev)
# and immediately clean up the APT cache.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
# Ensure 'psycopg2' is listed in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    # CRITICAL CLEANUP: Remove the pip cache after installation to save space
    && rm -rf ~/.cache/pip

# ---------------------------------------------------------------------
# STAGE 2: Runtime Environment (Minimalist for production)
# Switches back to the smaller 'slim' image
# ---------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Install PostgreSQL client libraries needed at runtime (libpq5)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
ENV VIRTUAL_ENV=/opt/venv
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set working directory for the application
WORKDIR /app

# Copy application code and ML artifacts
COPY app.py .
COPY requirements.txt .
COPY database ./database
COPY services ./services
COPY artifacts ./artifacts 
COPY src ./src

# Expose port (FastAPI default)
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
