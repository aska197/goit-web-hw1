# Use the official Python image from Docker Hub with Python 3.11
FROM python:3.11

# Set the environment variable for the application home directory
ENV APP_HOME /app

# Set the working directory inside the container
WORKDIR $APP_HOME

# Copy the application file into the container at /app
COPY hw1.py /app

# Install any additional dependencies if needed
# RUN pip install -r requirements.txt

# Expose the port where the application runs inside the container
# EXPOSE 5000

# Specify the command to run your application
CMD ["python", "hw1.py"]

