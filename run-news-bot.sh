#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create necessary directories if they don't exist
mkdir -p ~/.news-bot/cache ~/.news-bot/digests

# Check if OpenAI API key exists
API_KEY_FILE="$HOME/.news-bot/openai-api.key"
if [ ! -f "$API_KEY_FILE" ]; then
    echo "Error: OpenAI API key not found at $API_KEY_FILE"
    echo "Please create the file with your API key"
    exit 1
fi

# Determine which image to use
if [ "$LOCAL" = "1" ]; then
    echo "Building and using local image..."
    docker build -t news-bot .
    IMAGE_NAME="news-bot"
else
    # Default to GHCR image, fallback to local build
    REPO_OWNER=$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\)\/.*/\1/')
    IMAGE_NAME="ghcr.io/${REPO_OWNER}/news-bot:latest"
    if ! docker pull "$IMAGE_NAME" 2>/dev/null; then
        echo "GHCR image not found, building locally..."
        docker build -t news-bot .
        IMAGE_NAME="news-bot"
    fi
fi

# Run the container with mounted volumes
echo "Running news-bot..."
docker run --rm \
    -v ~/.news-bot/cache:/app/.news-bot/cache \
    -v ~/.news-bot/digests:/app/.news-bot/digests \
    -v ~/.news-bot/openai-api.key:/root/.news-bot/openai-api.key \
    "$IMAGE_NAME" "$@"

echo "Done! Check ~/.news-bot/digests for the results." 