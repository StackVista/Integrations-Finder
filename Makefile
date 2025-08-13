# Makefile for SUSE Observability Integrations Finder
# Cross-platform build targets

.PHONY: help clean install-deps build-all build-linux-x86_64 build-linux-aarch64 build-macos-x86_64 build-macos-aarch64 build-win-x86_64

# Default target
help:
	@echo "SUSE Observability Integrations Finder - Build Targets"
	@echo ""
	@echo "Available targets:"
	@echo "  install-deps      - Install build dependencies"
	@echo "  clean            - Clean build artifacts"
	@echo "  build-all        - Build for all platforms"
	@echo "  build-linux-x86_64    - Build Linux x86_64 executable"
	@echo "  build-linux-aarch64   - Build Linux aarch64 executable"
	@echo "  build-macos-x86_64    - Build macOS x86_64 executable"
	@echo "  build-macos-aarch64   - Build macOS aarch64 executable"
	@echo "  build-win-x86_64      - Build Windows x86_64 executable"
	@echo ""
	@echo "Examples:"
	@echo "  make build-linux-x86_64"
	@echo "  make build-all"

# Install build dependencies
install-deps:
	@echo "Installing build dependencies..."
	pip install -r build_requirements.txt
	@echo "Build dependencies installed."

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf packages/
	rm -f *.spec
	@echo "Clean complete."

# Build all platforms
build-all: build-linux-x86_64 build-linux-aarch64 build-macos-x86_64 build-macos-aarch64 build-win-x86_64
	@echo "All builds completed!"

# Linux x86_64
build-linux-x86_64:
	@echo "Building Linux x86_64..."
	python3 build.py linux-x86_64

# Linux aarch64
build-linux-aarch64:
	@echo "Building Linux aarch64..."
	python3 build.py linux-aarch64

# macOS x86_64
build-macos-x86_64:
	@echo "Building macOS x86_64..."
	python3 build.py macos-x86_64

# macOS aarch64
build-macos-aarch64:
	@echo "Building macOS aarch64..."
	python3 build.py macos-aarch64

# Windows x86_64
build-win-x86_64:
	@echo "Building Windows x86_64..."
	python3 build.py win-x86_64

# Quick build for current platform
build-current:
	@echo "Building for current platform..."
	python3 build.py all
