# Use Python 3.12.5
FROM python:3.12.5

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container
COPY ./requirements.txt /code/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code into the container
COPY ./app /code/app

# Command to run the FastAPI application
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
