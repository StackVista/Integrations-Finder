# Makefile for Agent Integrations Finder
# Cross-platform build and packaging targets

.PHONY: help clean install-deps install-system-deps build-all package-all \
        build-linux-x86_64 build-linux-aarch64 build-macos-x86_64 build-macos-aarch64 build-win-x86_64 \
        package-linux-x86_64 package-linux-aarch64 package-macos-x86_64 package-macos-aarch64 package-win-x86_64 \
        deb-linux-x86_64 deb-linux-aarch64 \
        msi-win-x86_64 pkg-macos-x86_64 pkg-macos-aarch64 \
        docker-build docker-push docker-amd64 docker-arm64 docker-cleanup \
        test run-gui run-cli

# Default target
help:
	@echo "Agent Integrations Finder - Build and Packaging Targets"
	@echo ""
	@echo "Dependencies:"
	@echo "  install-deps         - Install Python build dependencies"
	@echo "  install-system-deps  - Install system packaging tools (Linux)"
	@echo ""
	@echo "Build Targets:"
	@echo "  build-all            - Build executables for all platforms"
	@echo "  build-linux-x86_64   - Build Linux x86_64 executable"
	@echo "  build-linux-aarch64  - Build Linux aarch64 executable"
	@echo "  build-macos-x86_64   - Build macOS x86_64 executable"
	@echo "  build-macos-aarch64  - Build macOS aarch64 executable"
	@echo "  build-win-x86_64     - Build Windows x86_64 executable"
	@echo ""
	@echo "Package Targets:"
	@echo "  package-all          - Build and package for all platforms"
	@echo "  package-linux-x86_64 - Build and package Linux x86_64 (.tar.gz, .deb)"
	@echo "  package-linux-aarch64- Build and package Linux aarch64 (.tar.gz, .deb)"
	@echo "  package-macos-x86_64 - Build and package macOS x86_64 (.tar.gz, .pkg)"
	@echo "  package-macos-aarch64- Build and package macOS aarch64 (.tar.gz, .pkg)"
	@echo "  package-win-x86_64   - Build and package Windows x86_64 (.zip, .msi)"
	@echo ""
	@echo "Docker Targets:"
	@echo "  docker-build          - Build Docker images for all architectures"
	@echo "  docker-push           - Build and push Docker images to registry"
	@echo "  docker-amd64          - Build Docker image for amd64 only"
	@echo "  docker-arm64          - Build Docker image for arm64 only"
	@echo "  docker-cleanup        - Clean up local Docker images"
	@echo ""
	@echo "Individual Package Targets:"
	@echo "  deb-linux-x86_64     - Create .deb package for Linux x86_64"
	@echo "  deb-linux-aarch64    - Create .deb package for Linux aarch64"
	@echo "  msi-win-x86_64       - Create .msi package for Windows x86_64"
	@echo "  pkg-macos-x86_64     - Create .pkg package for macOS x86_64"
	@echo "  pkg-macos-aarch64    - Create .pkg package for macOS aarch64"
	@echo ""
	@echo "Development Targets:"
	@echo "  test                 - Run tests"
	@echo "  run-gui              - Run GUI application"
	@echo "  run-cli              - Run CLI application with demo"
	@echo "  clean                - Clean build artifacts"
	@echo ""
	@echo "Examples:"
	@echo "  make install-deps install-system-deps"
	@echo "  make package-linux-x86_64"
	@echo "  make deb-linux-x86_64"
	@echo "  make docker-build"
	@echo "  make docker-push"
	@echo "  make package-all"
	@echo "  make test"

# Install Python build dependencies
install-deps:
	@echo "Installing Python build dependencies..."
	pip install -r build_requirements.txt
	@echo "Python build dependencies installed."

# Install system packaging tools (Linux only)
install-system-deps:
	@echo "Installing system packaging tools..."
	@if [ "$$(uname)" = "Linux" ]; then \
		sudo apt-get update && sudo apt-get install -y dpkg-dev; \
		echo "System packaging tools installed."; \
	else \
		echo "System packaging tools installation skipped (not on Linux)"; \
	fi

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf packages/
	rm -rf temp_*/
	rm -f *.spec
	@echo "Clean complete."

# Build all platforms (executables only)
build-all: build-linux-x86_64 build-linux-aarch64 build-macos-x86_64 build-macos-aarch64 build-win-x86_64
	@echo "All builds completed!"

# Package all platforms (executables + system packages)
package-all: package-linux-x86_64 package-linux-aarch64 package-macos-x86_64 package-macos-aarch64 package-win-x86_64
	@echo "All packages created!"
	@echo "Available packages:"
	@ls -la packages/ 2>/dev/null || echo "No packages found"

# Linux x86_64
build-linux-x86_64:
	@echo "Building Linux x86_64..."
	python3 build.py linux-x86_64

package-linux-x86_64: build-linux-x86_64
	@echo "Packaging Linux x86_64 completed"

# Linux aarch64
build-linux-aarch64:
	@echo "Building Linux aarch64..."
	python3 build.py linux-aarch64

package-linux-aarch64: build-linux-aarch64
	@echo "Packaging Linux aarch64 completed"

# macOS x86_64
build-macos-x86_64:
	@echo "Building macOS x86_64..."
	python3 build.py macos-x86_64

package-macos-x86_64: build-macos-x86_64
	@echo "Packaging macOS x86_64 completed"

# macOS aarch64
build-macos-aarch64:
	@echo "Building macOS aarch64..."
	python3 build.py macos-aarch64

package-macos-aarch64: build-macos-aarch64
	@echo "Packaging macOS aarch64 completed"

# Windows x86_64
build-win-x86_64:
	@echo "Building Windows x86_64..."
	python3 build.py win-x86_64

package-win-x86_64: build-win-x86_64
	@echo "Packaging Windows x86_64 completed"

# Individual package format targets
# Linux .deb packages
deb-linux-x86_64: build-linux-x86_64
	@echo "Creating .deb package for Linux x86_64..."
	@python3 build.py linux-x86_64 --create-deb-only

deb-linux-aarch64: build-linux-aarch64
	@echo "Creating .deb package for Linux aarch64..."
	@python3 build.py linux-aarch64 --create-deb-only



# Windows .msi package
msi-win-x86_64: build-win-x86_64
	@echo "Creating .msi package for Windows x86_64..."
	@python3 build.py win-x86_64 --create-msi-only

# macOS .pkg packages
pkg-macos-x86_64: build-macos-x86_64
	@echo "Creating .pkg package for macOS x86_64..."
	@python3 build.py macos-x86_64 --create-pkg-only

pkg-macos-aarch64: build-macos-aarch64
	@echo "Creating .pkg package for macOS aarch64..."
	@python3 build.py macos-aarch64 --create-pkg-only

# Docker targets
docker-build:
	@echo "Building Docker images for all architectures..."
	@./docker-build.sh build

docker-push:
	@echo "Building and pushing Docker images to registry..."
	@./docker-build.sh push

docker-amd64:
	@echo "Building Docker image for amd64..."
	@./docker-build.sh amd64

docker-arm64:
	@echo "Building Docker image for arm64..."
	@./docker-build.sh arm64

docker-cleanup:
	@echo "Cleaning up Docker images..."
	@./docker-build.sh cleanup

# Development targets
test:
	@echo "Running tests..."
	python3 test_finder.py
	@echo "Tests completed."

run-gui:
	@echo "Starting GUI application..."
	python3 integrations_finder.py gui

run-cli:
	@echo "Running CLI demo..."
	python3 integrations_finder.py find a1b2c3d4

# Quick build for current platform
build-current:
	@echo "Building for current platform..."
	python3 build.py all

# Show package information
list-packages:
	@echo "Available packages:"
	@if [ -d packages ]; then \
		ls -la packages/; \
	else \
		echo "No packages directory found. Run 'make package-all' first."; \
	fi

# Show build information
info:
	@echo "Agent Integrations Finder Build Information"
	@echo "=========================================="
	@echo "Python version: $$(python3 --version)"
	@echo "Platform: $$(uname -s) $$(uname -m)"
	@echo "Build directory: $$(pwd)"
	@echo ""
	@echo "Available build tools:"
	@command -v dpkg-deb >/dev/null 2>&1 && echo "✓ dpkg-deb (for .deb packages)" || echo "✗ dpkg-deb (for .deb packages)"
	@command -v pkgbuild >/dev/null 2>&1 && echo "✓ pkgbuild (for .pkg packages)" || echo "✗ pkgbuild (for .pkg packages)"
	@command -v candle >/dev/null 2>&1 && echo "✓ WiX candle (for .msi packages)" || echo "✗ WiX candle (for .msi packages)"
	@command -v light >/dev/null 2>&1 && echo "✓ WiX light (for .msi packages)" || echo "✗ WiX light (for .msi packages)"
