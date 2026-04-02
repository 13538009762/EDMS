#!/bin/bash

# EDMS Docker Stop Script for Linux/macOS

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/docker/"
COMPOSE_FILE="$SCRIPT_DIR/../docker-compose.yml"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "============================================"
echo "   EDMS Docker Stop Script"
echo "============================================"
echo ""

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo -e "${RED}ERROR: docker-compose is not installed${NC}"
    exit 1
fi

# Stop and remove containers
echo "Stopping EDMS services..."
$COMPOSE_CMD -f "$COMPOSE_FILE" down
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}ERROR: Failed to stop services${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}[OK]${NC} Services stopped successfully"
