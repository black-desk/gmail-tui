#!/bin/bash
# Run E2E tests with smtp4dev server.
# SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
# SPDX-License-Identifier: GPL-3.0-or-later

set -e

# Container name
CONTAINER_NAME="gmail-tui-test-server"

# Timeout for tests (seconds)
TIMEOUT=30

# Global exit code
EXIT_CODE=0

# Cleanup function - stop container and print logs on failure
cleanup() {
    if [ "$EXIT_CODE" -ne 0 ]; then
        echo "=== Docker Logs ==="
        docker logs "$CONTAINER_NAME" 2>&1 | tail -50 || echo "Failed to get docker logs"
        echo "==================="
    fi
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    echo "Container stopped"
}

# Register cleanup on exit
trap cleanup EXIT

# Check if port 143 is available (server not running)
if ! nc -z localhost 143 2>/dev/null; then
    echo "Starting smtp4dev container..."
    docker run -d --rm --name "$CONTAINER_NAME" \
        -p 143:143 -p 2525:25 \
        rnwood/smtp4dev:latest \
        --smtpport 2525 --imapport 143
    echo "Waiting for server to start..."
    sleep 5
fi

# Set test config path (relative to project root)
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
export GMAIL_TUI_CONFIG="$PROJECT_ROOT/tests/fixtures/test_config.yaml"

# Run tests with timeout
echo "Running E2E tests..."

set +e
timeout $TIMEOUT uv run pytest tests/test_e2e.py -v
EXIT_CODE=$?
set -e

exit $EXIT_CODE
