# Use an official Python runtime as a parent image
FROM python:alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install required Python packages
RUN pip install flask

# Expose port 80
EXPOSE 80

# Run the Flask application
CMD ["python", "app.py"]
