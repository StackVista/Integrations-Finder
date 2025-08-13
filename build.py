#!/usr/bin/env python3
"""
Build script for SUSE Observability Integrations Finder
Creates cross-platform executables using PyInstaller

Note: Icons are now supported with automatic format detection:
- Windows: Uses .ico format (converted from PNG)
- macOS: Uses .icns format (when available)
- Linux: Uses .png format
- Pillow is included for automatic conversion
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


class Builder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.spec_file = self.project_root / "integrations_finder.spec"

    def get_platform_dist_dir(self, target_platform, target_arch):
        """Get platform-specific dist directory"""
        return self.dist_dir / target_platform / target_arch

    def clean(self):
        """Clean build artifacts"""
        print("Cleaning build artifacts...")
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.spec_file.exists():
            self.spec_file.unlink()
        print("Clean complete.")

    def create_spec_file(self, target_platform, target_arch):
        """Create PyInstaller spec file for the target platform"""
        print(f"Creating spec file for {target_platform}-{target_arch}...")

        # Determine target architecture for PyInstaller
        target_arch_value = "'arm64'" if target_arch == "aarch64" else "None"

        # Determine icon path and executable name based on platform
        icon_path = None
        exe_name = "agent-integrations-finder"

        if target_platform == "win":
            icon_path = "'assets/images/logo.ico'" if Path("assets/images/logo.ico").exists() else None
            exe_name = "agent-integrations-finder.exe"
        elif target_platform == "macos":
            icon_path = "'assets/images/logo.icns'" if Path("assets/images/logo.icns").exists() else None
        else:  # linux
            icon_path = "'assets/images/logo.png'" if Path("assets/images/logo.png").exists() else None

        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['integrations_finder.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/images/logo.png', 'assets/images'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        'requests',
        'click',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{exe_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch={target_arch_value},
    codesign_identity=None,
    entitlements_file=None,
    icon={icon_path},
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='agent-integrations-finder',
)

# For macOS, create .app bundle
if '{target_platform}' == 'macos':
    app = BUNDLE(
        coll,
        name='Agent Integrations Finder.app',
        icon={icon_path},
        bundle_identifier='com.suse.observability.agent-integrations-finder',
        info_plist={{
            'CFBundleName': 'Agent Integrations Finder',
            'CFBundleDisplayName': 'Agent Integrations Finder',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        }},
    )
"""

        with open(self.spec_file, "w") as f:
            f.write(spec_content)

        print(f"Spec file created: {self.spec_file}")

    def build(self, target_platform, target_arch):
        """Build executable for target platform and architecture"""
        print(f"Building for {target_platform}-{target_arch}...")

        # Create spec file
        self.create_spec_file(target_platform, target_arch)

        # Get platform-specific dist directory
        platform_dist_dir = self.get_platform_dist_dir(target_platform, target_arch)
        platform_dist_dir.mkdir(parents=True, exist_ok=True)

        # Build command with platform-specific dist directory
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            "--distpath",
            str(platform_dist_dir),
            str(self.spec_file),
        ]

        print(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("Build successful!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Build failed: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return False

    def package(self, target_platform, target_arch):
        """Package the built executable"""
        print(f"Packaging for {target_platform}-{target_arch}...")

        # Get platform-specific dist directory
        platform_dist_dir = self.get_platform_dist_dir(target_platform, target_arch)
        dir_name = "agent-integrations-finder"

        source_dir = platform_dist_dir / dir_name
        if not source_dir.exists():
            print(f"Error: Build directory not found: {source_dir}")
            return False

        # Create output directory
        output_dir = self.project_root / "packages"
        output_dir.mkdir(exist_ok=True)

        # Package based on platform
        if target_platform == "linux":
            # Create tar.gz
            archive_name = f"agent-integrations-finder-{target_platform}-{target_arch}.tar.gz"
            archive_path = output_dir / archive_name

            cmd = [
                "tar",
                "-czf",
                str(archive_path),
                "-C",
                str(platform_dist_dir),
                dir_name,
            ]
            subprocess.run(cmd, check=True)

        elif target_platform == "macos":
            # Create .dmg or .tar.gz
            archive_name = f"agent-integrations-finder-{target_platform}-{target_arch}.tar.gz"
            archive_path = output_dir / archive_name

            cmd = [
                "tar",
                "-czf",
                str(archive_path),
                "-C",
                str(platform_dist_dir),
                dir_name,
            ]
            subprocess.run(cmd, check=True)

        elif target_platform == "win":
            # Create zip using Python's zipfile module
            archive_name = f"agent-integrations-finder-{target_platform}-{target_arch}.zip"
            archive_path = output_dir / archive_name

            import os
            import zipfile

            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                source_dir = platform_dist_dir / dir_name
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(platform_dist_dir)
                        zipf.write(file_path, arcname)

        print(f"Package created: {archive_path}")
        return True


def main():
    """Main build function"""
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help", "help"]:
        print("Usage: python build.py <target>")
        print("Targets:")
        print("  linux-x86_64")
        print("  linux-aarch64")
        print("  macos-x86_64")
        print("  macos-aarch64")
        print("  win-x86_64")
        print("  all")
        print("")
        print("Examples:")
        print("  python build.py linux-x86_64")
        print("  python build.py all")
        sys.exit(1)

    target = sys.argv[1]
    builder = Builder()

    targets = {
        "linux-x86_64": ("linux", "x86_64"),
        "linux-aarch64": ("linux", "aarch64"),
        "macos-x86_64": ("macos", "x86_64"),
        "macos-aarch64": ("macos", "aarch64"),
        "win-x86_64": ("win", "x86_64"),
    }

    if target == "all":
        build_targets = targets.values()
    elif target in targets:
        build_targets = [targets[target]]
    else:
        print(f"Unknown target: {target}")
        sys.exit(1)

    # Clean first
    builder.clean()

    # Build each target
    for platform_name, arch in build_targets:
        print(f"\n{'=' * 50}")
        print(f"Building {platform_name}-{arch}")
        print(f"{'=' * 50}")

        if builder.build(platform_name, arch):
            builder.package(platform_name, arch)
        else:
            print(f"Failed to build {platform_name}-{arch}")
            sys.exit(1)

    print("\nAll builds completed successfully!")


if __name__ == "__main__":
    main()
