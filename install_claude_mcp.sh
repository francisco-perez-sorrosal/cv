#!/bin/bash

# Function to display usage
show_usage() {
    echo "Usage: $0 [desktop|code] [optional_project_path]"
    echo "  desktop: Install for Claude Desktop"
    echo "  code: Install for Claude Code (in current directory or specified path)"
    echo "  optional_project_path: Custom directory path for Claude Code installation"
    echo ""
    echo "Examples:"
    echo "  $0 desktop"
    echo "  $0 code"
    echo "  $0 code /path/to/my/project"
    exit 1
}

# Validate arguments
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    show_usage
fi

MODE="$1"
if [ "$MODE" != "desktop" ] && [ "$MODE" != "code" ]; then
    echo "Error: First argument must be 'desktop' or 'code'"
    show_usage
fi

# Function to get target file path based on mode
get_target_file() {
    if [ "$MODE" = "desktop" ]; then
        echo "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
    else
        # Code mode
        if [ $# -eq 2 ] && [ -n "$2" ]; then
            # Custom path provided
            CUSTOM_PATH="$2"
            if [ ! -d "$CUSTOM_PATH" ]; then
                echo "Error: Directory $CUSTOM_PATH does not exist"
                exit 1
            fi
            echo "$CUSTOM_PATH/.mcp.json"
        else
            # Default to current directory
            echo "./.mcp.json"
        fi
    fi
}

# Source and destination paths
SOURCE_FILE="$(dirname "$0")/config/claude.json"
TARGET_FILE=$(get_target_file "$@")
TARGET_DIR=$(dirname "$TARGET_FILE")
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

# Create target file with empty mcpServers object if it doesn't exist or is empty/invalid JSON
if [ ! -f "$TARGET_FILE" ] || ! jq -e . "$TARGET_FILE" >/dev/null 2>&1; then
    if [ -f "$TARGET_FILE" ]; then
        echo "Configuration file exists but is empty or invalid JSON. Resetting $TARGET_FILE"
    else
        echo "Creating new configuration file at $TARGET_FILE"
    fi
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

if [ "$MODE" = "desktop" ]; then
    echo "Updating service '$SERVICE_NAME' in Claude Desktop configuration: $TARGET_FILE"
else
    echo "Updating service '$SERVICE_NAME' in Claude Code configuration: $TARGET_FILE"
fi

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

if [ "$MODE" = "desktop" ]; then
    echo "Installation complete. Service '$SERVICE_NAME' has been updated in Claude Desktop configuration."
    echo "Please restart Claude Desktop for the changes to take effect."
else
    echo "Installation complete. Service '$SERVICE_NAME' has been updated in Claude Code configuration."
    echo "Please restart your Claude Code instance for the changes to take effect."
fi
