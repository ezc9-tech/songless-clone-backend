FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# No default CMD as scripts are run via 'docker compose run' or 'make'
# We can set a placeholder CMD to prevent immediate exit if someone runs 'docker compose up'
CMD ["python", "--version"]
