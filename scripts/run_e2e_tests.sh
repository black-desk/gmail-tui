#!/bin/bash
# Run E2E tests with GreenMail server.
# SPDX-FileCopyrightText: 2026 Chen Linxuan <me@black-desk.cn>
# SPDX-License-Identifier: GPL-3.0-or-later

# Container name
CONTAINER_NAME="gmail-tui-test-server"

# Timeout for tests (seconds)
TIMEOUT=120

# Global exit code
EXIT_CODE=0

# Set test config path (relative to project root)
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
export GMAIL_TUI_CONFIG="$PROJECT_ROOT/tests/fixtures/test_config.yaml"

# Preload directory path (relative to project root)
PRELOAD_DIR="$PROJECT_ROOT/tests/fixtures/greenmail_preload"

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

# Start GreenMail container (remove if exists first)
echo "Starting GreenMail container..."

# Use environment variables to create test users with authentication enabled
# Use preload directory to load test emails
docker run -d --rm --name "$CONTAINER_NAME" \
    -p 3143:3143 -p 3025:3025 \
    -v "$PRELOAD_DIR:/greenmail-preload:ro" \
    -e GREENMAIL_OPTS="-Dgreenmail.setup.test.all -Dgreenmail.auth.disabled=false -Dgreenmail.hostname=0.0.0.0 -Dgreenmail.users=test@localhost:secret -Dgreenmail.preload.dir=/greenmail-preload" \
    greenmail/standalone:2.1.8

# Wait for the server to be ready
echo "Waiting for GreenMail server to be ready..."
sleep 3

# Run tests with timeout
echo "Running E2E tests..."

set +e
timeout --foreground $TIMEOUT uv run pytest tests/test_e2e.py "$@"
EXIT_CODE=$?
set -e

exit $EXIT_CODE
