# Use official Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy requirement files first for efficient caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY backend .

# Copy the env file of the project
COPY .env .

# Expose port for FastAPI
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
