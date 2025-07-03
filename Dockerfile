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

# Run the MCP server
CMD ["uv", "run", "main.py"] 