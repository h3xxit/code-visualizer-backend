# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the rest of the application files to the container
COPY . .
RUN pip install -e .

# Expose port 8000
EXPOSE 8000

# Start the Flask application
CMD ["python", "api/server.py"]