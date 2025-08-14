#!/bin/bash

# Docker build script for Agent Integrations Finder
# Supports multi-architecture builds and GitHub Container Registry

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Configuration
REGISTRY="ghcr.io"
REPO="stackvista/agent-integrations-finder"
IMAGE_NAME="${REGISTRY}/${REPO}"

# Get git information
GIT_SHA=$(git rev-parse --short=8 HEAD)
GIT_TAG=$(git describe --tags --exact-match 2>/dev/null || echo "")

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running or you don't have permissions"
        exit 1
    fi
}

# Check if docker buildx is available
check_buildx() {
    if ! docker buildx version &> /dev/null; then
        print_error "Docker buildx is not available"
        exit 1
    fi
}

# Create and use buildx builder
setup_builder() {
    print_step "Setting up Docker buildx builder..."
    
    # Create a new builder if it doesn't exist
    if ! docker buildx inspect multiarch-builder &> /dev/null; then
        docker buildx create --name multiarch-builder --use
    else
        docker buildx use multiarch-builder
    fi
    
    # Bootstrap the builder
    docker buildx inspect --bootstrap
}

# Build for a specific architecture
build_architecture() {
    local arch=$1
    local platform="linux/${arch}"
    
    print_step "Building for ${arch}..."
    
    # Build the executable first
    print_status "Building executable for ${arch}..."
    # Convert architecture names for build.py
    build_arch=${arch}
    if [[ "${arch}" == "amd64" ]]; then
        build_arch="x86_64"
    elif [[ "${arch}" == "arm64" ]]; then
        build_arch="aarch64"
    fi
    python3 build.py linux-${build_arch}
    
    # Build Docker image
    print_status "Building Docker image for ${arch}..."
    docker buildx build \
        --platform ${platform} \
        --tag ${IMAGE_NAME}:${GIT_SHA}-${arch} \
        --file Dockerfile \
        --load \
        .
    
    # Tag with version if this is a release
    if [[ -n "${GIT_TAG}" ]]; then
        print_status "Tagging release image for ${arch}..."
        docker tag ${IMAGE_NAME}:${GIT_SHA}-${arch} ${IMAGE_NAME}:${GIT_TAG}-${arch}
    fi
}

# Create multi-architecture manifest
create_manifest() {
    print_step "Creating multi-architecture manifest..."
    
    # Build for both architectures
    build_architecture "amd64"
    build_architecture "arm64"
    
    # Create manifest with git SHA
    print_status "Creating manifest with tag: ${GIT_SHA}"
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        --tag ${IMAGE_NAME}:${GIT_SHA} \
        --file Dockerfile \
        --push \
        .
    
    # Create manifest with version tag if this is a release
    if [[ -n "${GIT_TAG}" ]]; then
        print_status "Creating release manifest with tag: ${GIT_TAG}"
        docker buildx build \
            --platform linux/amd64,linux/arm64 \
            --tag ${IMAGE_NAME}:${GIT_TAG} \
            --file Dockerfile \
            --push \
            .
    fi
}

# Push individual architecture images
push_architectures() {
    print_step "Pushing individual architecture images..."
    
    # Push amd64 image
    print_status "Pushing amd64 image..."
    docker push ${IMAGE_NAME}:${GIT_SHA}-amd64
    
    # Push arm64 image
    print_status "Pushing arm64 image..."
    docker push ${IMAGE_NAME}:${GIT_SHA}-arm64
    
    # Push versioned images if this is a release
    if [[ -n "${GIT_TAG}" ]]; then
        print_status "Pushing versioned images..."
        docker push ${IMAGE_NAME}:${GIT_TAG}-amd64
        docker push ${IMAGE_NAME}:${GIT_TAG}-arm64
    fi
}

# Build and push all images
build_and_push() {
    print_step "Building and pushing all images..."
    
    # Build for both architectures and create manifest
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        --tag ${IMAGE_NAME}:${GIT_SHA} \
        --tag ${IMAGE_NAME}:${GIT_SHA}-amd64 \
        --tag ${IMAGE_NAME}:${GIT_SHA}-arm64 \
        --file Dockerfile \
        --push \
        .
    
    # Add version tags if this is a release
    if [[ -n "${GIT_TAG}" ]]; then
        print_status "Adding version tags..."
        docker buildx build \
            --platform linux/amd64,linux/arm64 \
            --tag ${IMAGE_NAME}:${GIT_TAG} \
            --tag ${IMAGE_NAME}:${GIT_TAG}-amd64 \
            --tag ${IMAGE_NAME}:${GIT_TAG}-arm64 \
            --file Dockerfile \
            --push \
            .
    fi
}

# Build only (no push)
build_only() {
    print_step "Building images (no push)..."
    
    # Build for both architectures
    build_architecture "amd64"
    build_architecture "arm64"
    
    # Create local manifest
    print_status "Creating local manifest..."
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        --tag ${IMAGE_NAME}:${GIT_SHA} \
        --file Dockerfile \
        --load \
        .
}

# Clean up Docker images
cleanup() {
    print_step "Cleaning up Docker images..."
    
    # Remove local images
    docker rmi ${IMAGE_NAME}:${GIT_SHA}-amd64 2>/dev/null || true
    docker rmi ${IMAGE_NAME}:${GIT_SHA}-arm64 2>/dev/null || true
    docker rmi ${IMAGE_NAME}:${GIT_SHA} 2>/dev/null || true
    
    if [[ -n "${GIT_TAG}" ]]; then
        docker rmi ${IMAGE_NAME}:${GIT_TAG}-amd64 2>/dev/null || true
        docker rmi ${IMAGE_NAME}:${GIT_TAG}-arm64 2>/dev/null || true
        docker rmi ${IMAGE_NAME}:${GIT_TAG} 2>/dev/null || true
    fi
}

# Show help
show_help() {
    echo "Docker build script for Agent Integrations Finder"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build          - Build images for all architectures (no push)"
    echo "  push           - Build and push all images to registry"
    echo "  manifest       - Create multi-architecture manifest"
    echo "  amd64          - Build only for amd64 architecture"
    echo "  arm64          - Build only for arm64 architecture"
    echo "  cleanup        - Clean up local Docker images"
    echo "  help           - Show this help message"
    echo ""
    echo "Environment:"
    echo "  GITHUB_TOKEN   - GitHub token for pushing to registry"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 push"
    echo "  GITHUB_TOKEN=xxx $0 push"
}

# Main function
main() {
    local command=${1:-help}
    
    print_status "Starting Docker build for Agent Integrations Finder"
    print_status "Git SHA: ${GIT_SHA}"
    if [[ -n "${GIT_TAG}" ]]; then
        print_status "Git Tag: ${GIT_TAG}"
    fi
    print_status "Registry: ${REGISTRY}"
    print_status "Repository: ${REPO}"
    
    # Check prerequisites
    check_docker
    check_buildx
    setup_builder
    
    # Execute command
    case "$command" in
        build)
            build_only
            ;;
        push)
            if [[ -z "${GITHUB_TOKEN}" ]]; then
                print_error "GITHUB_TOKEN environment variable is required for pushing"
                exit 1
            fi
            # Login to GitHub Container Registry
            echo "${GITHUB_TOKEN}" | docker login ${REGISTRY} -u USERNAME --password-stdin
            build_and_push
            ;;
        manifest)
            create_manifest
            push_architectures
            ;;
        amd64)
            build_architecture "amd64"
            ;;
        arm64)
            build_architecture "arm64"
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
    
    print_status "Docker build completed successfully!"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help|help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
