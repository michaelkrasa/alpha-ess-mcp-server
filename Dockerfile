# Use Python 3.12 as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies using uv
RUN uv sync

# Run the application
CMD ["uv", "run", "main.py"] 