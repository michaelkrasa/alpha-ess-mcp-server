FROM python:3.12-slim

# Install uv
RUN pip install uv

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy the rest of the application
COPY . .

# Expose port for HTTP server
EXPOSE 8000

# Run the MCP server in HTTP mode
CMD ["uv", "run", "main.py", "--http"] 