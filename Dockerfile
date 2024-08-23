# Use the official Python image as a base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . /app/

# Expose the port that the app will run on
EXPOSE 8001

# Command to run the FastAPI application
CMD ["uvicorn", "main:zeorag", "--host", "0.0.0.0", "--port", "8001"]
