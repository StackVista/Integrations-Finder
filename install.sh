#!/bin/bash

# SUSE Observability Integrations Finder Installation Script

echo "Installing SUSE Observability Integrations Finder..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "Python version: $python_version ✓"

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

echo "Dependencies installed successfully ✓"

# Make the main script executable
chmod +x integrations_finder.py

echo ""
echo "Installation completed successfully!"
echo ""
echo "Usage:"
echo "  CLI mode:   python3 integrations_finder.py find <agent_sha_or_container_path>"
echo "  GUI mode:   python3 integrations_finder.py gui"
echo ""
echo "Examples:"
echo "  python3 integrations_finder.py find a1b2c3d4"
echo "  python3 integrations_finder.py find quay.io/stackstate/stackstate-k8s-agent:a1b2c3d4"
echo "  python3 integrations_finder.py gui"
