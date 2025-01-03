# Use a Python base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables (These should be passed securely at runtime, not hardcoded)
ENV GROQ_API_KEY=${GROQ_API_KEY}
ENV GITHUB_TOKEN=${GITHUB_TOKEN}

# Expose the application port
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "app.py"]
