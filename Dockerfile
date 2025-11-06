# Pull base image
FROM python:3.14.0-slim

# Install git
RUN apt-get update && \
    apt-get clean

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /opt/umd-handle

# Install dependencies
COPY pyproject.toml .
RUN pip install -e .[prod]

# Copy project
COPY src ./src
RUN pip install -e .[prod]
RUN src/manage.py collectstatic

# PORT
EXPOSE 3000

# Commands to run migration and start the server
CMD sh -c "src/manage.py migrate && umd-handle"
