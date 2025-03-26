# Use Node.js base image with Python
FROM nikolaik/python-nodejs:python3.11-nodejs20-slim

# Set working directory
WORKDIR /app

# Copy package.json and install Node.js dependencies first
COPY package.json .
RUN npm install

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set permissions for the application directory
RUN chmod -R 755 /app \
    && chown -R nobody:nogroup /app

# Create directory for Node.js cache
RUN mkdir -p /app/.npm \
    && chown -R nobody:nogroup /app/.npm

# Switch to non-root user
USER nobody

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
