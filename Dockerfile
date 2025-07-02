# Use the official Astral uv image with Python 3.12 on Alpine
FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Install nodejs and npm for the npx command (runtime dependency for context7)
# Alpine's package manager is apk
RUN apk add --no-cache nodejs npm

# Set the working directory
WORKDIR /app

# Copy requirements and install Python dependencies using the pre-installed uv
COPY requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the app
CMD ["python", "mcp_proxy.py", "sse", "--host", "0.0.0.0", "--port", "8000"]