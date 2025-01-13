# Use an official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the project files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Default command for the app service
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]