FROM ubuntu:latest
LABEL authors="Τζίνα"

ENTRYPOINT ["top", "-b"]


# Use Python 3.12 as the base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . .

# Expose the API listening port
EXPOSE 8080

# Command to run the application
CMD ["python", "main.py"]

