#!/bin/bash

# Docker-based cross-platform build script for SUSE Observability Integrations Finder
# This script uses Docker containers to build executables for different platforms

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Build Docker image for a specific platform
build_docker_image() {
    local platform=$1
    local arch=$2
    
    print_status "Building Docker image for $platform-$arch..."
    
    cat > "$PROJECT_ROOT/Dockerfile.$platform-$arch" << EOF
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    make \\
    zip \\
    tar \\
    gzip \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY build_requirements.txt .
RUN pip install --no-cache-dir -r build_requirements.txt

# Copy source code
COPY . .

# Build the executable
RUN python build.py $platform-$arch

# Create output directory
RUN mkdir -p /output

# Copy built executable to output
RUN cp -r dist/* /output/ 2>/dev/null || true
RUN cp -r packages/* /output/ 2>/dev/null || true

# Set output as volume
VOLUME /output
EOF

    docker build -f "Dockerfile.$platform-$arch" -t "suse-integrations-finder:$platform-$arch" .
}

# Build executable using Docker
build_executable() {
    local platform=$1
    local arch=$2
    
    print_status "Building executable for $platform-$arch..."
    
    # Create output directory
    mkdir -p "$PROJECT_ROOT/packages"
    
    # Run Docker container
    docker run --rm \
        -v "$PROJECT_ROOT/packages:/output" \
        "suse-integrations-finder:$platform-$arch" \
        sh -c "cp -r /output/* . 2>/dev/null || true"
    
    print_status "Build completed for $platform-$arch"
}

# Clean up Docker images
cleanup_docker() {
    print_status "Cleaning up Docker images..."
    docker rmi $(docker images -q "suse-integrations-finder:*") 2>/dev/null || true
    rm -f "$PROJECT_ROOT"/Dockerfile.*
}

# Main build function
main() {
    local target=${1:-all}
    
    print_status "Starting Docker-based build for target: $target"
    
    # Check Docker availability
    check_docker
    
    # Define targets
    declare -A targets=(
        ["linux-x86_64"]="linux x86_64"
        ["linux-aarch64"]="linux aarch64"
        ["macos-x86_64"]="macos x86_64"
        ["macos-aarch64"]="macos aarch64"
        ["win-x86_64"]="win x86_64"
    )
    
    # Build targets
    if [[ "$target" == "all" ]]; then
        for target_name in "${!targets[@]}"; do
            IFS=' ' read -r platform arch <<< "${targets[$target_name]}"
            build_docker_image "$platform" "$arch"
            build_executable "$platform" "$arch"
        done
    elif [[ -n "${targets[$target]}" ]]; then
        IFS=' ' read -r platform arch <<< "${targets[$target]}"
        build_docker_image "$platform" "$arch"
        build_executable "$platform" "$arch"
    else
        print_error "Unknown target: $target"
        echo "Available targets:"
        for target_name in "${!targets[@]}"; do
            echo "  $target_name"
        done
        echo "  all"
        exit 1
    fi
    
    # Cleanup
    cleanup_docker
    
    print_status "All builds completed successfully!"
    print_status "Packages are available in: $PROJECT_ROOT/packages/"
}

# Show help
show_help() {
    echo "Docker-based build script for SUSE Observability Integrations Finder"
    echo ""
    echo "Usage: $0 [TARGET]"
    echo ""
    echo "Targets:"
    echo "  linux-x86_64    - Build Linux x86_64 executable"
    echo "  linux-aarch64   - Build Linux aarch64 executable"
    echo "  macos-x86_64    - Build macOS x86_64 executable"
    echo "  macos-aarch64   - Build macOS aarch64 executable"
    echo "  win-x86_64      - Build Windows x86_64 executable"
    echo "  all             - Build for all platforms (default)"
    echo ""
    echo "Examples:"
    echo "  $0 linux-x86_64"
    echo "  $0 all"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
