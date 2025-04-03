# Build stage
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry --version

# Set Poetry to create virtualenvs in the project directory
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Copy only the files needed for dependency installation
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Final stage
FROM python:3.11-slim

# Copy the virtual environment from the builder stage
COPY --from=builder /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Copy the application code
COPY news_bot /app/news_bot
COPY news-bot /app/news-bot

# Set working directory
WORKDIR /app

# Create mount points for cache and digests
RUN mkdir -p /app/.news-bot/cache /app/.news-bot/digests

# Set the entrypoint
ENTRYPOINT ["python", "-m", "news_bot.main"] 