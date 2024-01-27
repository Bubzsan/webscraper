# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Install utilities
RUN apt-get update && apt-get install -y wget gnupg2 curl unzip 

# Install Node.js and npm
RUN apt-get install -y nodejs npm

# Install Chrome dependencies
RUN apt-get install -y libnss3 libxss1 libasound2 libatk-bridge2.0-0 libgtk-3-0 libgbm1

# Download a specific Chrome for Testing version.
RUN npx @puppeteer/browsers install chrome@120.0.6099.109

# Set display port as an environment variable
ENV DISPLAY=:99

# Provide write permissions for the root user to the /.cache directory
RUN mkdir -p /.cache && chmod -R 777 /.cache

# Set the path to the Chrome binary
ENV CHROME_BINARY_PATH="/chrome/linux-120.0.6099.109/chrome-linux64/chrome"

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the dependencies file to the working directory
COPY requirements.txt ./

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy and download the English model
RUN pip install spacy && python -m spacy download en_core_web_sm

# Copy the content of the local src directory to the working directory
COPY web_scraper.py .

# Command to run the script
# ENTRYPOINT ["python", "./web_scraper.py"]
ENTRYPOINT [ "/bin/bash" ]
