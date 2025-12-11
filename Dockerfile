# Stage 1: Build the frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy frontend files
COPY components/web/package.json components/web/pnpm-lock.yaml ./components/web/
RUN cd components/web && pnpm install --frozen-lockfile

COPY components/web ./components/web
RUN cd components/web && pnpm build

# Stage 2: Python server
FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy Python project files
COPY components/python/pyproject.toml ./components/python/

# Install Python dependencies
WORKDIR /app/components/python
RUN uv sync --no-dev

# Copy Python source code
COPY components/python/src ./src

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/components/web/dist /app/components/web/dist

# Expose port
EXPOSE 8000

# Set environment variables (can be overridden in docker-compose)
ENV PYTHONUNBUFFERED=1
# Ensure local src is on module path for imports like assemblyai_stt
ENV PYTHONPATH="/app/components/python/src"

# Run the server with uvicorn (production mode)
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

