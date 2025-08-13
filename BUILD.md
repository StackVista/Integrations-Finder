# Build Documentation

This document describes how to build cross-platform executables for the SUSE Observability Integrations Finder.

## Overview

The project uses PyInstaller to create standalone executables for multiple platforms and architectures:

- **Linux**: x86_64, aarch64
- **macOS**: x86_64, aarch64 (Apple Silicon)
- **Windows**: x86_64

## Prerequisites

### System Requirements

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Platform-Specific Requirements

#### Linux
- Standard build tools (gcc, g++, make)
- tar, gzip for packaging

#### macOS
- Xcode Command Line Tools
- tar, gzip for packaging

#### Windows
- Visual Studio Build Tools (for native builds)
- zip for packaging

## Quick Start

### 1. Install Build Dependencies

```bash
# Install Python dependencies
pip install -r build_requirements.txt

# Or use the Makefile
make install-deps
```

### 2. Build for Current Platform

```bash
# Using Python script
python build.py all

# Using Makefile
make build-all
```

### 3. Build for Specific Platform

```bash
# Linux x86_64
python build.py linux-x86_64
make build-linux-x86_64

# macOS aarch64
python build.py macos-aarch64
make build-macos-aarch64

# Windows x86_64
python build.py win-x86_64
make build-win-x86_64
```

## Build Methods

### Method 1: Direct Build (Recommended for Development)

Use this method when building on the target platform or when you have cross-compilation tools available.

```bash
# Install dependencies
pip install -r build_requirements.txt

# Build for specific target
python build.py <platform>-<arch>

# Examples:
python build.py linux-x86_64
python build.py macos-aarch64
python build.py win-x86_64
```

### Method 2: Docker Build (Recommended for CI/CD)

Use this method for cross-platform builds without requiring native toolchains.

```bash
# Make script executable
chmod +x build-docker.sh

# Build for all platforms
./build-docker.sh all

# Build for specific platform
./build-docker.sh linux-x86_64
./build-docker.sh macos-aarch64
./build-docker.sh win-x86_64
```

### Method 3: Makefile

Use the provided Makefile for convenient build targets.

```bash
# Show available targets
make help

# Build all platforms
make build-all

# Build specific platform
make build-linux-x86_64
make build-macos-aarch64
make build-win-x86_64

# Clean build artifacts
make clean
```

## Build Output

### Generated Files

After a successful build, you'll find:

- **Executables**: In `dist/suse-observability-integrations-finder/`
- **Packages**: In `packages/` directory
- **Build artifacts**: In `build/` directory

### Package Formats

- **Linux**: `.tar.gz` archives
- **macOS**: `.tar.gz` archives (with optional `.app` bundles)
- **Windows**: `.zip` archives

### File Structure

```
packages/
├── suse-observability-integrations-finder-linux-x86_64.tar.gz
├── suse-observability-integrations-finder-linux-aarch64.tar.gz
├── suse-observability-integrations-finder-macos-x86_64.tar.gz
├── suse-observability-integrations-finder-macos-aarch64.tar.gz
└── suse-observability-integrations-finder-win-x86_64.zip
```

## Configuration

### PyInstaller Spec File

The build script automatically generates a PyInstaller spec file with:

- **Icon**: Uses `assets/images/logo.png` as application icon
- **Data files**: Includes logo and other assets
- **Hidden imports**: All required PyQt6 and other dependencies
- **Platform-specific settings**: Optimized for each target

### Customization

You can modify the build configuration by editing:

1. **`build.py`**: Main build script
2. **`build_requirements.txt`**: Build dependencies
3. **`Makefile`**: Build targets and commands

## Continuous Integration

### GitHub Actions Workflows

The project includes two GitHub Actions workflows:

#### 1. Test Workflow (`.github/workflows/test.yml`)
- **Triggers**: Every push and pull request
- **Purpose**: Ensures code quality and functionality
- **Actions**:
  - Runs unit tests and integration tests
  - Verifies CLI and GUI functionality
  - Checks code formatting and linting
  - Validates imports and dependencies

#### 2. Build and Release Workflow (`.github/workflows/build.yml`)
- **Triggers**: Every push, PR, and git tag
- **Builds**: Always builds executables for all platforms
- **Publishes**: Only publishes releases for git tags
- **Platforms**: Linux (x86_64, aarch64), macOS (x86_64, aarch64), Windows (x86_64)

### Release Process

#### Automated Release
1. **Create a tag**: `git tag v1.0.0 && git push origin v1.0.0`
2. **Automatic build**: GitHub Actions builds all platform executables
3. **Automatic release**: Creates GitHub release with downloadable packages using GitHub CLI
4. **Release notes**: Automatically generated from commits using GitHub API

#### Using the Release Script
```bash
# Create a new release
./release.sh v1.0.0

# The script will:
# - Validate version format
# - Check working directory is clean
# - Create and push git tag
# - Trigger GitHub Actions release
```

### Local CI

To run the full build locally:

```bash
# Clean previous builds
make clean

# Build all platforms
make build-all

# Check results
ls -la packages/
```

### Artifacts

- **Build artifacts**: Available for 30 days on all builds
- **Build logs**: Available for 7 days for debugging
- **Release packages**: Permanently available in GitHub releases

## Troubleshooting

### Common Issues

#### 1. PyInstaller Import Errors

**Problem**: Missing hidden imports
**Solution**: Add missing modules to the `hiddenimports` list in `build.py`

#### 2. Icon Not Loading

**Problem**: Icon file not found or invalid format
**Solution**: Ensure `assets/images/logo.png` exists and is a valid PNG file

#### 3. Cross-Platform Build Failures

**Problem**: Architecture-specific build errors
**Solution**: Use Docker build method for cross-platform compilation

#### 4. Large Executable Size

**Problem**: Executable includes unnecessary dependencies
**Solution**: Review and optimize the `excludes` list in the spec file

### Platform-Specific Issues

#### Linux
- Ensure you have the required build tools: `sudo apt-get install build-essential`
- For aarch64 builds, ensure you have ARM64 toolchain

#### macOS
- Install Xcode Command Line Tools: `xcode-select --install`
- For Apple Silicon builds, ensure you're using the correct Python version

#### Windows
- Install Visual Studio Build Tools
- Ensure you have the Windows SDK installed

### Debug Builds

To create debug builds with more verbose output:

```bash
# Add debug flags to PyInstaller
python build.py --debug linux-x86_64
```

## Distribution

### Creating Releases

1. **Tag a release**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub Actions** will automatically:
   - Build all platforms
   - Create a GitHub release
   - Upload all artifacts

### Manual Distribution

For manual distribution:

```bash
# Build all platforms
make build-all

# Create distribution package
tar -czf suse-observability-integrations-finder-v1.0.0.tar.gz packages/
```

## Security Considerations

- Executables are not signed by default
- Consider code signing for production releases
- Verify checksums of distributed packages
- Use HTTPS for downloads

## Performance Optimization

### Executable Size

- Use UPX compression (enabled by default)
- Exclude unnecessary modules
- Optimize data file inclusion

### Build Speed

- Use parallel builds where possible
- Cache build dependencies
- Use incremental builds for development

## Support

For build-related issues:

1. Check the troubleshooting section above
2. Review PyInstaller documentation
3. Check GitHub Actions logs for CI/CD issues
4. Create an issue in the project repository
