# Packaging System

The Agent Integrations Finder build system creates multiple package formats for different platforms and use cases.

## Package Formats

### Linux Packages

#### Archive Packages
- **`.tar.gz`**: Portable archive containing the executable and dependencies
  - `agent-integrations-finder-linux-x86_64.tar.gz`
  - `agent-integrations-finder-linux-aarch64.tar.gz`

#### System Packages
- **`.deb`**: Debian/Ubuntu package for easy installation
  - `agent-integrations-finder_1.0.0_amd64.deb`
  - `agent-integrations-finder_1.0.0_aarch64.deb`
  - Installs executable to `/usr/local/bin/agent-integrations-finder`
  - Dependencies in `/usr/local/bin/_internal/`

- **`.rpm`**: Red Hat/Fedora/CentOS package for easy installation
  - `agent-integrations-finder-1.0.0-1.x86_64.rpm`
  - `agent-integrations-finder-1.0.0-1.aarch64.rpm`
  - Installs executable to `/usr/local/bin/agent-integrations-finder`
  - Dependencies in `/usr/local/bin/_internal/`

### Windows Packages

#### Archive Packages
- **`.zip`**: Portable archive containing the executable and dependencies
  - `agent-integrations-finder-win-x86_64.zip`

#### System Packages
- **`.msi`**: Microsoft Installer package for easy installation
  - `agent-integrations-finder-1.0.0-x86_64.msi`
  - Installs to `C:\Program Files\agent-integrations-finder\`
  - Creates Start Menu shortcuts
  - Handles uninstallation

### macOS Packages

#### Archive Packages
- **`.tar.gz`**: Portable archive containing the executable and dependencies
  - `agent-integrations-finder-macos-x86_64.tar.gz`
  - `agent-integrations-finder-macos-aarch64.tar.gz`

#### System Packages
- **`.pkg`**: macOS Package Installer for easy installation
  - `agent-integrations-finder-1.0.0-x86_64.pkg`
  - `agent-integrations-finder-1.0.0-aarch64.pkg`
  - Installs executable to `/usr/local/bin/agent-integrations-finder`
  - Dependencies in `/usr/local/bin/_internal/`

## Installation Methods

### Linux

#### Using .deb package (Debian/Ubuntu)
```bash
sudo dpkg -i agent-integrations-finder_1.0.0_amd64.deb
```

#### Using .rpm package (Red Hat/Fedora/CentOS)
```bash
sudo rpm -i agent-integrations-finder-1.0.0-1.x86_64.rpm
```

#### Using .tar.gz archive
```bash
tar -xzf agent-integrations-finder-linux-x86_64.tar.gz
cd agent-integrations-finder
./agent-integrations-finder --help
```

### Windows

#### Using .msi package
1. Double-click the `.msi` file
2. Follow the installation wizard
3. Use from Start Menu or `C:\Program Files\agent-integrations-finder\`

#### Using .zip archive
1. Extract the `.zip` file
2. Run `agent-integrations-finder.exe` from the extracted folder

### macOS

#### Using .pkg package
1. Double-click the `.pkg` file
2. Follow the installation wizard
3. Use from Terminal: `agent-integrations-finder --help`

#### Using .tar.gz archive
```bash
tar -xzf agent-integrations-finder-macos-x86_64.tar.gz
cd agent-integrations-finder
./agent-integrations-finder --help
```

## Build Requirements

### Local Development (Linux)
- **Python 3.11+**
- **PyInstaller**: `pip install -r build_requirements.txt`
- **dpkg-dev**: For .deb package creation (Ubuntu/Debian)
- **rpm-build**: For .rpm package creation (Red Hat/Fedora)

### GitHub Actions
- **Linux runners**: Include dpkg-dev and rpm-build tools
- **Windows runners**: Would need WiX tools for .msi creation
- **macOS runners**: Include pkgbuild by default

## Package Contents

All packages include:
- **Executable**: `agent-integrations-finder` (or `.exe` on Windows)
- **Dependencies**: All required Python libraries and system dependencies
- **Assets**: Application icons and resources
- **Documentation**: Built-in help and usage information

## Version Management

Package versions are managed in the build script:
- **Version**: `1.0.0` (configurable in `build.py`)
- **Architecture**: `x86_64`, `aarch64` (automatically detected)
- **Platform**: `linux`, `win`, `macos` (automatically detected)

## Customization

To modify package contents or metadata:
1. Edit the package creation methods in `build.py`
2. Update version numbers in the build script
3. Modify package descriptions and metadata
4. Add additional files or dependencies as needed
