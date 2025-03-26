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

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
