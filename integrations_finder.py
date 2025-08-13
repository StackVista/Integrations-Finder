#!/usr/bin/env python3
"""
SUSE Observability Integrations Finder

A tool to trace from SUSE Observability Agent container tags to the corresponding integrations source code.
"""

import json
import re
import sys
import webbrowser
from typing import Optional, Tuple

import click
import requests
from PyQt6.QtCore import Qt, QThread, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QFont, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class IntegrationsFinder:
    """Main class for finding integrations source code from SUSE Observability agent container tags."""

    AGENT_REPO = "https://github.com/StackVista/stackstate-agent"
    INTEGRATIONS_REPO = "https://github.com/StackVista/stackstate-agent-integrations"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "SUSE-Observability-Integrations-Finder/1.0"})

    def extract_sha(self, input_string: str) -> Optional[str]:
        """
        Extract 8-character git SHA from various input formats.

        Args:
            input_string: Input string that may contain a SHA

        Returns:
            8-character SHA if found, None otherwise
        """
        # Pattern to match 8-character hex strings (git short SHA)
        sha_pattern = r"[a-fA-F0-9]{8}"

        # If input is already 8 characters and looks like a SHA, return it
        if len(input_string) == 8 and re.match(sha_pattern, input_string):
            return input_string

        # Look for SHA in container tag format (e.g., 7.51.1-a1b2c3d4 or quay.io/stackstate/stackstate-k8s-agent:a1b2c3d4)
        container_pattern = r"[0-9]+\.[0-9]+\.[0-9]+-([a-fA-F0-9]{8})"
        match = re.search(container_pattern, input_string)
        if match:
            return match.group(1)

        # Look for SHA in quay.io format (e.g., quay.io/stackstate/stackstate-k8s-agent:a1b2c3d4)
        quay_pattern = r"quay\.io/stackstate/stackstate-k8s-agent:([a-fA-F0-9]{8})"
        match = re.search(quay_pattern, input_string)
        if match:
            return match.group(1)

        # Look for any 8-character hex string in the input
        match = re.search(sha_pattern, input_string)
        if match:
            return match.group(0)

        return None

    def get_agent_commit(self, sha: str) -> Optional[dict]:
        """
        Fetch agent commit information from GitHub.

        Args:
            sha: 8-character git SHA

        Returns:
            Commit information dict or None if not found
        """
        try:
            # Try GitHub API first
            api_url = f"https://api.github.com/repos/StackVista/stackstate-agent/commits/{sha}"
            response = self.session.get(api_url)

            if response.status_code == 200:
                return response.json()

            # If API fails, try to fetch the commit page
            commit_url = f"{self.AGENT_REPO}/commit/{sha}"
            response = self.session.get(commit_url)

            if response.status_code == 200:
                # This is a fallback - we can't easily parse the HTML
                # but we can confirm the commit exists
                return {"sha": sha, "html_url": commit_url}

        except Exception as e:
            print(f"Error fetching agent commit: {e}")

        return None

    def get_integrations_commit(self, version: str) -> Optional[dict]:
        """
        Fetch integrations commit information from GitHub.

        Args:
            version: Integrations version (branch or tag)

        Returns:
            Commit information dict or None if not found
        """
        try:
            # Try GitHub API to get the latest commit for this version
            api_url = "https://api.github.com/repos/StackVista/stackstate-agent-integrations/commits"
            params = {"sha": version, "per_page": 1}
            response = self.session.get(api_url, params=params)

            if response.status_code == 200:
                commits = response.json()
                if commits:
                    return commits[0]

            # Fallback: try to get commit info for the version directly
            api_url = "https://api.github.com/repos/StackVista/stackstate-agent-integrations/commits/{}".format(version)
            response = self.session.get(api_url)

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            print(f"Error fetching integrations commit: {e}")

        return None

    def is_branch_version(self, version: str) -> bool:
        """
        Check if the integrations version is a branch (not a tag).

        Args:
            version: Integrations version string

        Returns:
            True if it's a branch, False if it's a tag
        """
        try:
            # Check if it's a tag by trying to get tag info
            api_url = "https://api.github.com/repos/StackVista/stackstate-agent-integrations/tags"
            response = self.session.get(api_url)

            if response.status_code == 200:
                tags = response.json()
                # Check if version matches any tag name
                for tag in tags:
                    if tag.get("name") == version:
                        return False  # It's a tag

            # If not found in tags, it's likely a branch
            return True

        except Exception as e:
            print(f"Error checking if version is branch: {e}")
            # Default to assuming it's a branch if we can't determine
            return True

    def get_stackstate_deps(self, sha: str) -> Optional[str]:
        """
        Fetch stackstate-deps.json file content from the agent repository.

        Args:
            sha: 8-character git SHA

        Returns:
            Integrations version string or None if not found
        """
        try:
            # Try GitHub API to get file content
            api_url = "https://api.github.com/repos/StackVista/stackstate-agent/contents/stackstate-deps.json"
            params = {"ref": sha}
            response = self.session.get(api_url, params=params)

            if response.status_code == 200:
                content = response.json()
                if content.get("type") == "file":
                    # Decode base64 content
                    import base64

                    file_content = base64.b64decode(content["content"]).decode("utf-8")
                    deps_data = json.loads(file_content)
                    return deps_data.get("STACKSTATE_INTEGRATIONS_VERSION")

            # Fallback: try raw GitHub URL
            raw_url = "https://raw.githubusercontent.com/StackVista/stackstate-agent/{}/stackstate-deps.json".format(sha)
            response = self.session.get(raw_url)

            if response.status_code == 200:
                deps_data = response.json()
                return deps_data.get("STACKSTATE_INTEGRATIONS_VERSION")

        except Exception as e:
            print(f"Error fetching stackstate-deps.json: {e}")

        return None

    def build_integrations_url(self, integrations_version: str) -> str:
        """
        Build GitHub URL for the integrations repository at the specified version.

        Args:
            integrations_version: Version string (branch or tag)

        Returns:
            GitHub URL for the integrations repository
        """
        return f"{self.INTEGRATIONS_REPO}/tree/{integrations_version}"

    def find_integrations(self, input_string: str) -> Tuple[bool, str]:
        """
        Main method to find integrations source code from input.

        Args:
            input_string: Input string containing SHA or container path

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Extract SHA from input
        sha = self.extract_sha(input_string)
        if not sha:
            return False, f"Could not extract 8-character SHA from: {input_string}"

        print(f"Extracted SHA: {sha}")

        # Get agent commit
        commit_info = self.get_agent_commit(sha)
        if not commit_info:
            return False, f"Could not find agent commit with SHA: {sha}"

        print("Found SUSE Observability agent commit: {}".format(commit_info.get("html_url", "N/A")))

        # Get integrations version from stackstate-deps.json
        integrations_version = self.get_stackstate_deps(sha)
        if not integrations_version:
            return (
                False,
                f"Could not find integrations version in stackstate-deps.json for SHA: {sha}",
            )

        print("Found integrations version: {}".format(integrations_version))

        # Get integrations commit information
        integrations_commit_info = self.get_integrations_commit(integrations_version)

        # Check if this is a branch version (development/unreleased)
        is_branch = self.is_branch_version(integrations_version)

        # Build integrations URL
        integrations_url = self.build_integrations_url(integrations_version)

        # Format commit information
        agent_commit_date = "N/A"
        agent_committer = "N/A"
        if commit_info.get("commit"):
            commit_data = commit_info["commit"]
            if commit_data.get("author"):
                agent_commit_date = commit_data["author"]["date"]
                agent_committer = commit_data["author"]["name"]

        integrations_commit_date = "N/A"
        integrations_committer = "N/A"
        integrations_commit_sha = "N/A"
        if integrations_commit_info:
            if integrations_commit_info.get("commit"):
                commit_data = integrations_commit_info["commit"]
                if commit_data.get("author"):
                    integrations_commit_date = commit_data["author"]["date"]
                    integrations_committer = commit_data["author"]["name"]
            integrations_commit_sha = integrations_commit_info.get("sha", "N/A")[:8]

        # Add warning if it's a branch version
        branch_warning = ""
        if is_branch:
            branch_warning = """
⚠️  WARNING: This integrations version ({}) appears to be a development branch, not a released tag.
   This means you're working with an unofficial/unreleased development version of the integrations.""".format(
                integrations_version
            )

        success_message = f"""Success! Found integrations source code:{branch_warning}

SUSE Observability Agent Commit:
  SHA: {sha}
  URL: {commit_info.get('html_url', 'N/A')}
  Date: {agent_commit_date}
  Committer: {agent_committer}

Integrations Commit:
  Version: {integrations_version} {'(DEVELOPMENT BRANCH)' if is_branch else '(RELEASED TAG)'}
  SHA: {integrations_commit_sha}
  URL: {integrations_url}
  Date: {integrations_commit_date}
  Committer: {integrations_committer}

Click the integrations URL above to view the source code."""

        return True, success_message, is_branch


class WorkerThread(QThread):
    """Worker thread for GUI to prevent blocking."""

    finished = pyqtSignal(bool, str)

    def __init__(self, finder: IntegrationsFinder, input_string: str):
        super().__init__()
        self.finder = finder
        self.input_string = input_string

    def run(self):
        result = self.finder.find_integrations(self.input_string)
        if len(result) == 3:
            success, message, is_branch = result
        else:
            # Backward compatibility
            success, message = result
            is_branch = False

        # Add branch indicator to message for GUI detection
        if is_branch:
            message += "\n[BRANCH_VERSION_DETECTED]"

        self.finished.emit(success, message)


class IntegrationsFinderGUI(QMainWindow):
    """GUI for the Agent Integrations Finder tool."""

    def __init__(self):
        super().__init__()
        self.finder = IntegrationsFinder()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Agent Integrations Finder")
        self.setGeometry(600, 400, 800, 500)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header with title and logo
        header_layout = QHBoxLayout()

        # Title (left side)
        title = QLabel("Agent Integrations Finder")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(title)

        # Add stretch to push logo to the right
        header_layout.addStretch()

        # Logo (right side)
        try:
            logo_label = QLabel()
            logo_pixmap = QPixmap("assets/images/logo.png")
            if not logo_pixmap.isNull():
                # Scale the logo to a reasonable size (e.g., 100px height)
                scaled_pixmap = logo_pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            else:
                logo_label.setText("")  # Empty if image fails to load
        except Exception:
            logo_label.setText("")  # Empty if image fails to load

        header_layout.addWidget(logo_label)
        layout.addLayout(header_layout)

        # Description
        desc = QLabel(
            "Enter a SUSE Observability agent container tag or SHA to find the corresponding integrations source code"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Warning label for development versions (initially hidden)
        self.warning_label = QLabel(
            "⚠️ WARNING: You are working with an unofficial/unreleased development version of the integrations"
        )
        self.warning_label.setStyleSheet(
            "color: red; font-weight: bold; background-color: #ffe6e6; "
            "padding: 8px; border: 2px solid red; border-radius: 4px;"
        )
        self.warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.warning_label.setWordWrap(True)
        self.warning_label.setVisible(False)
        layout.addWidget(self.warning_label)

        # Input section
        input_layout = QHBoxLayout()
        input_label = QLabel("SUSE Observability Agent SHA or Container Path:")
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("e.g., a1b2c3d4 or quay.io/stackstate/stackstate-k8s-agent:a1b2c3d4")
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_field)
        layout.addLayout(input_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()
        self.find_button = QPushButton("Find Integrations")
        self.find_button.clicked.connect(self.find_integrations)
        self.open_url_button = QPushButton("Open URL in Browser")
        self.open_url_button.clicked.connect(self.open_url)
        self.open_url_button.setEnabled(False)
        button_layout.addWidget(self.find_button)
        button_layout.addWidget(self.open_url_button)
        layout.addLayout(button_layout)

        # Results
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Results will appear here...")
        layout.addWidget(self.results_text)

        # Store URL for opening in browser
        self.current_url = None

    def find_integrations(self):
        """Find integrations source code."""
        input_string = self.input_field.text().strip()
        if not input_string:
            QMessageBox.warning(
                self,
                "Input Required",
                "Please enter a SUSE Observability agent SHA or container path.",
            )
            return

        # Disable UI during search
        self.find_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.results_text.clear()

        # Start worker thread
        self.worker = WorkerThread(self.finder, input_string)
        self.worker.finished.connect(self.on_search_finished)
        self.worker.start()

    def on_search_finished(self, success: bool, message: str):
        """Handle search completion."""
        # Re-enable UI
        self.find_button.setEnabled(True)
        self.progress_bar.setVisible(False)

        # Check if this is a branch version and show/hide warning
        is_branch = "DEVELOPMENT BRANCH" in message or "[BRANCH_VERSION_DETECTED]" in message
        self.warning_label.setVisible(is_branch)

        # Reset button styling
        self.open_url_button.setStyleSheet("")

        # Display results
        self.results_text.setPlainText(message)

        # Extract URL if successful
        self.current_url = None
        if success:
            # Extract URL from message - look for the integrations URL
            url_match = re.search(r"URL: (https://[^\s]+)", message)
            if url_match:
                # Find the integrations URL specifically
                lines = message.split("\n")
                for line in lines:
                    if "Integrations Commit:" in line or "URL:" in line:
                        url_match = re.search(r"URL: (https://[^\s]+)", line)
                        if url_match and "stackstate-agent-integrations" in url_match.group(1):
                            self.current_url = url_match.group(1)
                            self.open_url_button.setEnabled(True)

                            # Add red border if it's a branch version
                            if is_branch:
                                self.open_url_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        border: 3px solid red;
                                        border-radius: 5px;
                                        background-color: #ffe6e6;
                                        color: red;
                                        font-weight: bold;
                                    }
                                    QPushButton:hover {
                                        background-color: #ffcccc;
                                    }
                                """
                                )
                            break

    def open_url(self):
        """Open the integrations URL in the default browser."""
        if self.current_url:
            QDesktopServices.openUrl(QUrl(self.current_url))
        else:
            QMessageBox.warning(self, "No URL", "No URL available to open.")


@click.group()
def cli():
    """Agent Integrations Finder - Trace from agent container tags to integrations source code."""
    pass


@cli.command()
@click.argument("input_string")
def find(input_string):
    """Find integrations source code from SUSE Observability agent SHA or container path."""
    finder = IntegrationsFinder()
    result = finder.find_integrations(input_string)

    if len(result) == 3:
        success, message, is_branch = result
    else:
        # Backward compatibility
        success, message = result
        is_branch = False

    if success:
        # Extract URL for easy copying
        url_match = re.search(r"URL: (https://[^\s]+)", message)
        if url_match:
            # Find the integrations URL specifically
            lines = message.split("\n")
            for line in lines:
                if "Integrations Commit:" in line and "URL:" in line:
                    url_match = re.search(r"URL: (https://[^\s]+)", line)
                    if url_match and "stackstate-agent-integrations" in url_match.group(1):
                        url = url_match.group(1)
                        print(f"\nQuick access URL: {url}")

                        # Add warning if it's a branch version
                        if is_branch:
                            print("\n⚠️  WARNING: This integrations version appears to be a development branch!")
                            print("   You are working with an unofficial/unreleased development version.")

                        # Ask if user wants to open in browser
                        try:
                            open_browser = input("\nOpen URL in browser? (y/N): ").strip().lower()
                            if open_browser in ["y", "yes"]:
                                webbrowser.open(url)
                        except KeyboardInterrupt:
                            pass
                        break

    print(f"\n{message}")


@cli.command()
def gui():
    """Launch the graphical user interface."""
    app = QApplication(sys.argv)
    window = IntegrationsFinderGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    cli()
