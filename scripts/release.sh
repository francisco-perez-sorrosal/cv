#!/bin/bash

# Release script for CV MCP Server MCPB bundles
# Usage: ./scripts/release.sh [version]
# Example: ./scripts/release.sh 0.0.1

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if version is provided
if [ -z "$1" ]; then
    error "Version is required. Usage: $0 <version>"
fi

VERSION="$1"
TAG="v$VERSION"

info "Preparing release for version: $VERSION"

# Validate version format (basic semver check)
if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$'; then
    error "Invalid version format. Use semantic versioning (e.g., 0.0.1, 0.1.0, 1.0.0-beta)"
fi

# Check if we're on the mcp branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "mcp" ]; then
    warning "Not on mcp branch (current: $CURRENT_BRANCH). Switching to mcp branch..."
    git checkout mcp || error "Failed to switch to mcp branch"
fi

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    error "Working directory is not clean. Please commit or stash changes before releasing."
fi

# Update manifest.json version
info "Updating manifest.json version to $VERSION..."
python3 -c "
import json
with open('manifest.json', 'r') as f:
    manifest = json.load(f)
manifest['version'] = '$VERSION'
with open('manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)
print('Updated manifest.json version')
"

# Update pyproject.toml version
info "Updating pyproject.toml version to $VERSION..."
python3 -c "
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
content = re.sub(r'^version = \".*\"', f'version = \"$VERSION\"', content, flags=re.MULTILINE)
with open('pyproject.toml', 'w') as f:
    f.write(content)
print('Updated pyproject.toml version')
"

# Check if tag already exists
if git tag -l | grep -q "^$TAG$"; then
    error "Tag $TAG already exists. Please use a different version."
fi

# Commit version updates
info "Committing version updates..."
git add manifest.json pyproject.toml
git commit -m "chore: bump version to $VERSION

- Update manifest.json version to $VERSION
- Update pyproject.toml version to $VERSION
- Prepare for release $TAG"

# Create and push tag
info "Creating and pushing tag $TAG..."
git tag -a "$TAG" -m "Release version $VERSION

This release includes:
- CV MCP Server MCPB bundle
- Python 3.13 compatibility
- All CV tools and summarization capabilities"

git push origin mcp
git push origin "$TAG"

success "Release $VERSION created successfully!"
info "GitHub Actions will now build and publish the MCPB bundle."
info "Check the workflow at: https://github.com/francisco-perez-sorrosal/cv/actions"
info "Release will be available at: https://github.com/francisco-perez-sorrosal/cv/releases/tag/$TAG"
