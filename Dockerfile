FROM python:3.10-slim-bookworm

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install system dependencies
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends awscli \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy full project
COPY . .

CMD ["python", "app.py"]
