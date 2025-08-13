# SUSE Observability Integrations Finder - Usage Guide

## Quick Start

1. **Install the tool:**
   ```bash
   ./install.sh
   ```

2. **Use CLI mode:**
   ```bash
   python3 integrations_finder.py find <agent_sha_or_container_path>
   ```

3. **Use GUI mode:**
   ```bash
   python3 integrations_finder.py gui
   ```

## Supported Input Formats

The tool can extract 8-character git SHAs from various formats:

### Direct SHA
```bash
python3 integrations_finder.py find a1b2c3d4
```

### Container Tags
```bash
python3 integrations_finder.py find stackstate/agent:7.51.1-a1b2c3d4
```

### Full Container Paths
```bash
python3 integrations_finder.py find registry.example.com/stackstate/agent:7.51.1-a1b2c3d4
```

### Quay.io Container Format
```bash
python3 integrations_finder.py find quay.io/stackstate/stackstate-k8s-agent:a1b2c3d4
```

### SHA Embedded in Text
```bash
python3 integrations_finder.py find "some-text-a1b2c3d4-more-text"
```

## How It Works

1. **SHA Extraction**: The tool extracts the 8-character git SHA from your input
2. **Agent Commit Lookup**: Fetches the SUSE Observability agent commit from GitHub using the SHA
3. **Dependencies File**: Reads `stackstate-deps.json` to get the integrations version
4. **URL Generation**: Creates a clickable GitHub URL to the integrations source code

## Example Workflow

```bash
$ python3 integrations_finder.py find quay.io/stackstate/stackstate-k8s-agent:8be54df8

Extracted SHA: 8be54df8
Found SUSE Observability agent commit: https://github.com/StackVista/stackstate-agent/commit/8be54df8bcabf8b535012341084d4a35ccbd04e7
Found integrations version: 7.51.1-3

Success! Found integrations source code:

SUSE Observability Agent Commit:
  SHA: 8be54df8
  URL: https://github.com/StackVista/stackstate-agent/commit/8be54df8bcabf8b535012341084d4a35ccbd04e7
  Date: 2025-06-19T09:30:45Z
  Committer: Louis Parkin

Integrations Commit:
  Version: 7.51.1-3
  SHA: 07b9828b
  URL: https://github.com/StackVista/stackstate-agent-integrations/tree/7.51.1-3
  Date: 2024-11-20T15:49:28Z
  Committer: Louis Parkin

Click the integrations URL above to view the source code.

Quick access URL: https://github.com/StackVista/stackstate-agent-integrations/tree/7.51.1-3

Open URL in browser? (y/N): y
```

## GUI Mode

The GUI provides a user-friendly interface:

1. Launch: `python3 integrations_finder.py gui`
2. Enter the SUSE Observability agent SHA or container path
3. Click "Find Integrations"
4. Click "Open URL in Browser" to view the source code

## Troubleshooting

### Common Issues

1. **"Could not extract 8-character SHA"**
   - Make sure your input contains a valid 8-character hex string
   - Check that the container tag format is correct

2. **"Could not find agent commit"**
   - The SHA might not exist in the SUSE Observability agent repository
   - Check if the SHA is correct
   - Verify network connectivity to GitHub

3. **"Could not find integrations version"**
   - The `stackstate-deps.json` file might not exist for that commit
   - The file format might have changed

### Network Issues

The tool requires internet access to:
- GitHub API (for commit information)
- GitHub raw content (for stackstate-deps.json)
- GitHub web pages (fallback for commit verification)

### Rate Limiting

GitHub API has rate limits. If you encounter issues:
- Wait a few minutes before trying again
- Consider using the GUI mode which provides better error handling

## Development

### Running Tests
```bash
python3 test_finder.py
```

### Installing for Development
```bash
pip3 install -e .
```

### Project Structure
```
integrations-finder/
├── integrations_finder.py    # Main application
├── test_finder.py           # Test script
├── requirements.txt         # Python dependencies
├── setup.py                # Installation script
├── install.sh              # Quick install script
├── README.md               # Project documentation
└── USAGE.md               # This usage guide
```
