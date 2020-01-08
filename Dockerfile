# Dockerfile to be used to build the HireRight program

# Using Python 3.8.0
FROM python:3.8.0

COPY . /usr/src/hireright
WORKDIR /usr/src/hireright

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the program
CMD ["python", "./main.py"]
