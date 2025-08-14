# SUSE Observability Integrations Finder

A tool to trace from SUSE Observability Agent container tags to the corresponding integrations source code.

## Features

- **CLI Interface**: Command-line tool for quick lookups
- **GUI Interface**: User-friendly graphical interface with SUSE branding
- **Container Tag Support**: Extract SHA from full container paths
- **GitHub Integration**: Automatically fetches data from GitHub repositories
- **Cross-Platform Executables**: Standalone executables for Linux, macOS, and Windows

## Quick Start

### Option 1: Run from Source

1. **Install dependencies:**
   ```bash
   # CLI only (recommended for servers/CI)
   pip install -r requirements.txt
   
   # CLI + GUI (requires PyQt6)
   pip install -r requirements-gui.txt
   ```

2. **Run the tool:**
   ```bash
   # CLI mode
   python integrations_finder.py find <agent_sha_or_container_path>
   
   # GUI mode (requires PyQt6)
   python integrations_finder.py gui
   ```

### Option 2: Use Pre-built Executables

Download the latest release from the [Releases page](https://github.com/StackVista/stackstate-agent-integrations/releases) and choose the appropriate package for your platform:

#### Archive Packages (Portable)
- **Linux**: `agent-integrations-finder-linux-x86_64.tar.gz` or `agent-integrations-finder-linux-aarch64.tar.gz`
- **Windows**: `agent-integrations-finder-win-x86_64.zip`
- **macOS**: `agent-integrations-finder-macos-x86_64.tar.gz` or `agent-integrations-finder-macos-aarch64.tar.gz`

#### System Packages (Easy Installation)
- **Linux (Debian/Ubuntu)**: `agent-integrations-finder_1.0.0_amd64.deb`
- **Linux (Red Hat/Fedora)**: `agent-integrations-finder-1.0.0-1.x86_64.rpm`
- **Windows**: `agent-integrations-finder-1.0.0-x86_64.msi`
- **macOS**: `agent-integrations-finder-1.0.0-x86_64.pkg`

For detailed installation instructions, see [PACKAGING.md](PACKAGING.md).

## Installation

### Using Docker (Recommended)
The easiest way to run Agent Integrations Finder is using Docker:

```bash
# Pull and run the latest version
docker run --rm ghcr.io/stackvista/agent-integrations-finder:latest --help

# Run with a specific version
docker run --rm ghcr.io/stackvista/agent-integrations-finder:v1.0.0 --help

# Run GUI (requires X11 forwarding on Linux/macOS)
docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
  ghcr.io/stackvista/agent-integrations-finder:latest gui

# Run CLI with specific SHA
docker run --rm ghcr.io/stackvista/agent-integrations-finder:latest find a1b2c3d4
```

**Available Docker Images:**
- `ghcr.io/stackvista/agent-integrations-finder:latest` - Latest stable version
- `ghcr.io/stackvista/agent-integrations-finder:v1.0.0` - Specific version
- `ghcr.io/stackvista/agent-integrations-finder:<git-sha>` - Specific commit
- `ghcr.io/stackvista/agent-integrations-finder:<git-sha>-amd64` - AMD64 architecture only
- `ghcr.io/stackvista/agent-integrations-finder:<git-sha>-arm64` - ARM64 architecture only

### From Source

```bash
# Clone the repository
git clone https://github.com/StackVista/stackstate-agent-integrations.git
cd stackstate-agent-integrations/integrations-finder

# Install dependencies
pip install -r requirements.txt

# Run
python integrations_finder.py gui
```

### Building Executables

The project includes a complete build system for creating cross-platform executables:

```bash
# Install build dependencies
pip install -r build_requirements.txt

# Build for current platform
python build.py all

# Or use Makefile
make build-all
```

For detailed build instructions, see [BUILD.md](BUILD.md).

## Usage Examples

### CLI Examples
```bash
# Using a short SHA
python integrations_finder.py find a1b2c3d4

# Using a full container path (SHA will be extracted)
python integrations_finder.py find stackstate/agent:7.51.1-a1b2c3d4

# Using a full container path with registry
python integrations_finder.py find registry.example.com/stackstate/agent:7.51.1-a1b2c3d4

# Using the new quay.io container format
python integrations_finder.py find quay.io/stackstate/stackstate-k8s-agent:a1b2c3d4
```

### GUI Usage
1. Launch the GUI: `python integrations_finder.py gui`
2. Enter the SUSE Observability agent SHA or container path in the input field
3. Click "Find Integrations" to get the GitHub URL
4. Click the generated URL to open it in your browser

## Supported Formats

The tool can extract 8-character git SHAs from various formats:

- **Direct SHA**: `a1b2c3d4`
- **Container tags**: `stackstate/agent:7.51.1-a1b2c3d4`
- **Full container paths**: `registry.example.com/stackstate/agent:7.51.1-a1b2c3d4`
- **Quay.io container format**: `quay.io/stackstate/stackstate-k8s-agent:a1b2c3d4`

## How It Works

1. **SHA Extraction**: The tool extracts the 8-character git SHA from your input
2. **Agent Commit Lookup**: Fetches the SUSE Observability agent commit from GitHub using the SHA
3. **Dependencies File**: Reads `stackstate-deps.json` to get the integrations version
4. **URL Generation**: Creates a clickable GitHub URL to the integrations source code

## Build System

### Supported Platforms

- **Linux**: x86_64, aarch64
- **macOS**: x86_64, aarch64 (Apple Silicon)
- **Windows**: x86_64

### Icon Support

The build system supports application icons for different platforms:
- **Linux**: PNG format (automatically handled)
- **Windows**: ICO format (automatically converted from PNG)
- **macOS**: ICNS format (when available)

Icons are automatically detected and used based on platform requirements. The `convert_icon.py` script can be used to manually convert formats if needed.

**Note**: Pillow is included in the main requirements to support icon conversion and potential future image processing features.

### Build Methods

1. **Direct Build**: `python build.py <platform>-<arch>`
2. **Docker Build**: `./build-docker.sh <platform>-<arch>`
3. **Makefile**: `make build-<platform>-<arch>`
4. **Docker Images**: `make docker-build` or `./docker-build.sh build`

### Docker Build System

The project includes a comprehensive Docker build system for creating multi-architecture container images:

```bash
# Build Docker images for all architectures (local)
make docker-build

# Build and push to GitHub Container Registry
make docker-push

# Build specific architecture
make docker-amd64
make docker-arm64

# Clean up Docker images
make docker-cleanup
```

**Docker Build Features:**
- Multi-architecture support (AMD64, ARM64)
- Automatic tagging with git SHA and version tags
- GitHub Container Registry integration
- Multi-architecture manifests
- Build caching for faster builds

**Note**: Windows builds use Python's built-in `zipfile` module for packaging, ensuring compatibility across all Windows environments.

### Quick Build Commands

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

## Development

### Running Tests
```bash
python test_finder.py
```

### Installing for Development
```bash
pip install -e .
```

### Project Structure
```
integrations-finder/
├── integrations_finder.py    # Main application (CLI + GUI)
├── test_finder.py           # Test script for SHA extraction
├── demo.py                  # Demo script showing functionality
├── build.py                 # Cross-platform build script
├── build-docker.sh          # Docker-based build script
├── Makefile                 # Build targets and commands
├── requirements.txt         # Python dependencies
├── build_requirements.txt   # Build dependencies
├── setup.py                # Installation script
├── install.sh              # Quick install script
├── assets/images/logo.png  # Application logo and icon
├── README.md               # Project documentation
├── USAGE.md               # Detailed usage guide
└── BUILD.md               # Build system documentation
```

## Continuous Integration

The project includes GitHub Actions workflows that automatically:

### **Test Workflow** (`.github/workflows/test.yml`)
- **Triggers**: Every push and pull request
- **Actions**:
  - Runs unit tests and integration tests
  - Verifies CLI and GUI functionality
  - Checks code formatting and linting
  - Validates imports and dependencies

### **Build and Release Workflow** (`.github/workflows/build.yml`)
- **Builds**: Always builds executables for all platforms
- **Publishes**: Only publishes releases for git tags
- **Platforms**: Linux (x86_64, aarch64), macOS (x86_64, aarch64), Windows (x86_64)

### **Release Process**
1. **Create a tag**: `git tag v1.0.0 && git push origin v1.0.0`
2. **Automatic build**: GitHub Actions builds all platform executables
3. **Automatic release**: Creates GitHub release with downloadable packages using GitHub CLI
4. **Release notes**: Automatically generated from commits using GitHub API

### **Artifacts**
- **Build artifacts**: Available for 30 days on all builds
- **Build logs**: Available for 7 days for debugging
- **Release packages**: Permanently available in GitHub releases

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the BSD-3-Clause license - see the [LICENSE](LICENSE) file for details.
