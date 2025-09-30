# ---------------------------------------------------------
# STAGE 1: Builder (For compiling wheels & installing deps)
# ---------------------------------------------------------
FROM python:3.11-slim AS builder

# Avoid Python writing .pyc files & enable real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Use a virtual environment for isolation and better control
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install only build dependencies required for compiling packages like psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*  # CLEANUP: Saves space

# Install Python packages without pip cache
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------
# STAGE 2: Runtime (Final minimal image)
# ---------------------------------------------------------
FROM python:3.11-slim AS runtime

# Reuse the same virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Only install runtime libraries needed by psycopg2 at runtime (not dev tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*  # CLEANUP: Save space

# Copy only the virtual environment from the builder stage
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

# Set application workdir
WORKDIR /app

# Copy only necessary files to reduce size
COPY app.py .
COPY requirements.txt .
COPY database ./database
COPY services ./services
COPY src ./src

# Only copy essential artifacts — omit unused CSVs or extras
RUN mkdir -p /app/artifacts
COPY artifacts/model.pkl artifacts/preprocessor.pkl artifacts/optimal_threshold.txt ./artifacts/

# Optional: remove tests, data files, logs, or notebooks if not used in production
# RUN rm -rf tests/ data/ notebooks/

# Expose FastAPI's port
EXPOSE 8000

# Use Uvicorn to serve the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
