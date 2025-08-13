#!/bin/bash

# Release script for SUSE Observability Integrations Finder
# This script helps create a new release by tagging and pushing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if version is provided
if [ $# -eq 0 ]; then
    print_error "Usage: $0 <version>"
    echo ""
    echo "Examples:"
    echo "  $0 v1.0.0"
    echo "  $0 v1.1.0"
    echo ""
    echo "This will:"
    echo "  1. Create a git tag with the specified version"
    echo "  2. Push the tag to trigger GitHub Actions release"
    echo "  3. GitHub Actions will build and publish executables"
    exit 1
fi

VERSION=$1

# Validate version format
if [[ ! $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format. Use format: vX.Y.Z (e.g., v1.0.0)"
    exit 1
fi

print_status "Creating release for version: $VERSION"

# Check if we're on main/master branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "master" ]]; then
    print_warning "You're not on main/master branch. Current branch: $CURRENT_BRANCH"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Release cancelled."
        exit 1
    fi
fi

# Check if working directory is clean
if [[ -n $(git status --porcelain) ]]; then
    print_error "Working directory is not clean. Please commit or stash changes first."
    git status --short
    exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^$VERSION$"; then
    print_error "Tag $VERSION already exists!"
    exit 1
fi

# Create and push tag
print_status "Creating git tag: $VERSION"
git tag "$VERSION"

print_status "Pushing tag to remote..."
git push origin "$VERSION"

print_status "✅ Release tag created and pushed!"
echo ""
print_status "GitHub Actions will now:"
echo "  1. Build executables for all platforms"
echo "  2. Create a GitHub release"
echo "  3. Upload downloadable packages"
echo ""
print_status "You can monitor the build progress at:"
echo "  https://github.com/StackVista/stackstate-agent-integrations/actions"
echo ""
print_status "Release will be available at:"
echo "  https://github.com/StackVista/stackstate-agent-integrations/releases/tag/$VERSION"
