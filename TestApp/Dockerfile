# Use the official Python image from the Docker Hub
FROM arm64v8/python:3.12.6-bookworm
# Set environment variables to prevent Python from writing .pyc files and to ensure output is sent straight to the terminal
#ENV PYTHONDONTWRITEBYTECODE=1
#ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Command to run the application
CMD ["python", "test_2.py"]
