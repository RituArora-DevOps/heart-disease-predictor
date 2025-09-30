# ---------------------------------------------------------------------
# STAGE 1: Build Environment
# Used to install dependencies into a clean environment (faster build, smaller final image)
# ---------------------------------------------------------------------
FROM python:3.11-slim AS builder

# Install system dependencies necessary for compiling complex packages (like numpy, pandas)
# If using a version without -slim, this might be needed:
# RUN apt-get update && apt-get install -y build-essential

# Set working directory
WORKDIR /app

# Ensure we use a persistent virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------
# STAGE 2: Runtime Environment
# This is the final, minimalist image for production deployment
# ---------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Copy the virtual environment from the builder stage
ENV VIRTUAL_ENV=/opt/venv
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set working directory for the application
WORKDIR /app

# Copy application code and ML artifacts
# Note: Assuming 'artifacts', 'database', and 'services' directories are siblings to app.py
COPY app.py .
COPY database ./database
COPY services ./services
COPY artifacts ./artifacts 

# Expose port (FastAPI default)
EXPOSE 8000

# Run FastAPI with Uvicorn (ensures the application starts correctly)
# We set CMD here; the docker-compose environment variable PYTHONUNBUFFERED=1 handles logging
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
