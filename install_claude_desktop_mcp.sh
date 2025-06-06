#!/bin/bash

# Source and destination paths
SOURCE_FILE="$(dirname "$0")/config/claude.json"
TARGET_DIR="$HOME/Library/Application Support/Claude"
TARGET_FILE="$TARGET_DIR/claude_desktop_config.json"
TEMP_FILE="${TARGET_FILE}.tmp"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed. Please install jq first."
    echo "You can install it using Homebrew: brew install jq"
    exit 1
fi

# Check if source file exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file not found at $SOURCE_FILE"
    exit 1
fi

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Create target file with empty mcpServers object if it doesn't exist
if [ ! -f "$TARGET_FILE" ]; then
    echo "Creating new configuration file at $TARGET_FILE"
    echo '{"mcpServers": {}}' > "$TARGET_FILE"
fi

# Read the source configuration
SOURCE_CONTENT=$(cat "$SOURCE_FILE")

# If the source content is not a complete JSON object, wrap it in {}
if ! echo "$SOURCE_CONTENT" | jq -e . >/dev/null 2>&1; then
    SOURCE_CONTENT="{ $SOURCE_CONTENT }"
fi

# Extract the service name and configuration
SERVICE_NAME=$(echo "$SOURCE_CONTENT" | jq -r 'keys_unsorted[0]' 2>/dev/null)
SERVICE_CONFIG=$(echo "$SOURCE_CONTENT" | jq ".$SERVICE_NAME" 2>/dev/null)

# Validate the service name and configuration
if [ -z "$SERVICE_NAME" ] || [ "$SERVICE_NAME" = "null" ] || [ "$SERVICE_CONFIG" = "null" ]; then
    echo "Error: Could not determine service name or invalid configuration in source file"
    exit 1
fi

echo "Updating service '$SERVICE_NAME' in $TARGET_FILE"

# Update the target file with the new service configuration
if ! jq --arg name "$SERVICE_NAME" --argjson config "$SERVICE_CONFIG" \
    '.mcpServers[$name] = $config' "$TARGET_FILE" > "$TEMP_FILE"; then
    echo "Error: Failed to update configuration"
    rm -f "$TEMP_FILE"
    exit 1
fi

# Replace the original file
mv "$TEMP_FILE" "$TARGET_FILE"

# Set appropriate permissions
chmod 600 "$TARGET_FILE"

echo "Installation complete. Service '$SERVICE_NAME' has been updated in the configuration."
