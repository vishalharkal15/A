# Use Python 3.11 as base image
FROM python:3.11-slim

# Install Node.js 20
RUN apt-get update && apt-get install -y \
    curl \
    libgl1 \
    libglib2.0-0 \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Node.js dependencies
RUN npm install

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build frontend
RUN npm run build

# Expose port
EXPOSE 5000

# Start application
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
