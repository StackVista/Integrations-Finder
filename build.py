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

    def create_deb_package(self, target_platform, target_arch, source_dir, output_dir):
        """Create .deb package for Debian/Ubuntu"""
        print("Creating .deb package...")

        # Create package structure
        package_name = "agent-integrations-finder"
        package_version = "1.0.0"

        # Convert architecture names to Debian format
        deb_arch = target_arch.replace("x86_64", "amd64").replace("aarch64", "arm64")
        deb_name = f"{package_name}_{package_version}_{deb_arch}.deb"
        deb_path = output_dir / deb_name

        # Create temporary directory structure
        temp_dir = self.project_root / "temp_deb"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        # Create DEBIAN control file
        debian_dir = temp_dir / "DEBIAN"
        debian_dir.mkdir()

        control_content = f"""Package: {package_name}
Version: {package_version}
Architecture: {deb_arch}
Maintainer: SUSE Observability Team <observability@suse.com>
Description: Agent Integrations Finder
 A tool to trace from SUSE Observability Agent container tags to the corresponding integrations source code.
 Provides both CLI and GUI interfaces for finding integration source code.
 Installs executable to /usr/local/bin/agent-integrations-finder
"""

        with open(debian_dir / "control", "w") as f:
            f.write(control_content)

        # Create usr/local/bin directory and copy executable
        bin_dir = temp_dir / "usr" / "local" / "bin"
        bin_dir.mkdir(parents=True)

        # Copy the executable
        executable = source_dir / "agent-integrations-finder"
        if executable.exists():
            shutil.copy2(executable, bin_dir / "agent-integrations-finder")
            os.chmod(bin_dir / "agent-integrations-finder", 0o755)

        # Copy _internal directory to /usr/local/bin (where PyInstaller expects it)
        bin_internal_dir = temp_dir / "usr" / "local" / "bin" / "_internal"
        bin_internal_dir.mkdir(parents=True)

        internal_dir = source_dir / "_internal"
        if internal_dir.exists():
            shutil.copytree(internal_dir, bin_internal_dir, dirs_exist_ok=True)

        # Create .deb package using dpkg-deb
        try:
            cmd = ["dpkg-deb", "--build", str(temp_dir), str(deb_path)]
            subprocess.run(cmd, check=True)
            print(f"Created .deb package: {deb_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: dpkg-deb not available, skipping .deb package creation")
        finally:
            # Clean up
            shutil.rmtree(temp_dir)

    def create_rpm_package(self, target_platform, target_arch, source_dir, output_dir):
        """Create .rpm package for Red Hat/Fedora/CentOS"""
        print("Creating .rpm package...")

        # Create package structure
        package_name = "agent-integrations-finder"
        package_version = "1.0.0"
        rpm_name = f"{package_name}-{package_version}-1.{target_arch}.rpm"
        rpm_path = output_dir / rpm_name

        # Create temporary directory structure
        temp_dir = self.project_root / "temp_rpm"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        # Create RPM build structure
        rpm_build_dir = temp_dir / "rpmbuild"
        rpm_build_dir.mkdir()

        # Create SPEC file
        spec_content = f"""Name: {package_name}
Version: {package_version}
Release: 1
Summary: Agent Integrations Finder
License: BSD-3-Clause
URL: https://github.com/StackVista/Integrations-Finder
BuildArch: {target_arch}

%description
A tool to trace from SUSE Observability Agent container tags to the corresponding integrations source code.
Provides both CLI and GUI interfaces for finding integration source code.

%files
%defattr(-,root,root,-)
/usr/local/bin/agent-integrations-finder
/usr/local/lib/{package_name}/

%post
chmod +x /usr/local/bin/agent-integrations-finder

%clean
rm -rf $RPM_BUILD_ROOT
"""

        spec_file = temp_dir / f"{package_name}.spec"
        with open(spec_file, "w") as f:
            f.write(spec_content)

        # Create buildroot structure
        buildroot = rpm_build_dir / "BUILDROOT" / f"{package_name}-{package_version}-1.{target_arch}"
        buildroot.mkdir(parents=True)

        # Copy files to buildroot
        bin_dir = buildroot / "usr" / "local" / "bin"
        bin_dir.mkdir(parents=True)

        executable = source_dir / "agent-integrations-finder"
        if executable.exists():
            shutil.copy2(executable, bin_dir / "agent-integrations-finder")
            os.chmod(bin_dir / "agent-integrations-finder", 0o755)

        lib_dir = buildroot / "usr" / "local" / "lib" / package_name
        lib_dir.mkdir(parents=True)

        internal_dir = source_dir / "_internal"
        if internal_dir.exists():
            shutil.copytree(internal_dir, lib_dir / "_internal")

        # Try to build RPM using rpmbuild
        try:
            cmd = ["rpmbuild", "--define", f"_topdir {rpm_build_dir}", "-bb", str(spec_file)]
            subprocess.run(cmd, check=True)

            # Find and copy the built RPM
            rpm_dir = rpm_build_dir / "RPMS" / target_arch
            if rpm_dir.exists():
                for rpm_file in rpm_dir.glob("*.rpm"):
                    shutil.copy2(rpm_file, rpm_path)
                    print(f"Created .rpm package: {rpm_path}")
                    break
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: rpmbuild not available, skipping .rpm package creation")
        finally:
            # Clean up
            shutil.rmtree(temp_dir)

    def create_msi_package(self, target_platform, target_arch, source_dir, output_dir):
        """Create .msi package for Windows"""
        print("Creating .msi package...")

        # Create package structure
        package_name = "agent-integrations-finder"
        package_version = "1.0.0"
        msi_name = f"{package_name}-{package_version}-{target_arch}.msi"
        msi_path = output_dir / msi_name

        # Create temporary directory structure
        temp_dir = self.project_root / "temp_msi"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        # Copy files to temp directory
        program_files = temp_dir / "Program Files" / package_name
        program_files.mkdir(parents=True)

        # Copy the executable
        executable = source_dir / "agent-integrations-finder.exe"
        if executable.exists():
            shutil.copy2(executable, program_files / "agent-integrations-finder.exe")

        # Copy _internal directory
        internal_dir = source_dir / "_internal"
        if internal_dir.exists():
            shutil.copytree(internal_dir, program_files / "_internal")

        # Create WiX XML file for MSI
        wix_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product Id="*" Name="{package_name}" Language="1033" Version="{package_version}" 
             Manufacturer="SUSE Observability" UpgradeCode="PUT-GUID-HERE">
        <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" />
        <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
        <MediaTemplate EmbedCab="yes" />
        
        <Feature Id="ProductFeature" Title="{package_name}" Level="1">
            <ComponentGroupRef Id="ProductComponents" />
        </Feature>
    </Product>
    
    <Fragment>
        <Directory Id="TARGETDIR" Name="SourceDir">
            <Directory Id="ProgramFilesFolder">
                <Directory Id="INSTALLFOLDER" Name="{package_name}" />
            </Directory>
        </Directory>
    </Fragment>
    
    <Fragment>
        <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
            <Component Id="MainExecutable" Guid="*">
                <File Id="ExecutableFile" Source="Program Files/{package_name}/agent-integrations-finder.exe" KeyPath="yes" />
            </Component>
        </ComponentGroup>
    </Fragment>
</Wix>
"""

        wix_file = temp_dir / f"{package_name}.wxs"
        with open(wix_file, "w") as f:
            f.write(wix_content)

        # Try to build MSI using WiX
        try:
            cmd = ["candle", str(wix_file), "-out", str(temp_dir / f"{package_name}.wixobj")]
            subprocess.run(cmd, check=True)

            cmd = ["light", str(temp_dir / f"{package_name}.wixobj"), "-out", str(msi_path)]
            subprocess.run(cmd, check=True)

            print(f"Created .msi package: {msi_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: WiX tools not available, skipping .msi package creation")
        finally:
            # Clean up
            shutil.rmtree(temp_dir)

    def create_pkg_package(self, target_platform, target_arch, source_dir, output_dir):
        """Create .pkg package for macOS"""
        print("Creating .pkg package...")

        # Create package structure
        package_name = "agent-integrations-finder"
        package_version = "1.0.0"
        pkg_name = f"{package_name}-{package_version}-{target_arch}.pkg"
        pkg_path = output_dir / pkg_name

        # Create temporary directory structure
        temp_dir = self.project_root / "temp_pkg"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        # Create package structure
        pkg_root = temp_dir / "pkgroot"
        pkg_root.mkdir()

        # Copy files to /usr/local/bin and /usr/local/lib
        bin_dir = pkg_root / "usr" / "local" / "bin"
        bin_dir.mkdir(parents=True)

        executable = source_dir / "agent-integrations-finder"
        if executable.exists():
            shutil.copy2(executable, bin_dir / "agent-integrations-finder")
            os.chmod(bin_dir / "agent-integrations-finder", 0o755)

        lib_dir = pkg_root / "usr" / "local" / "lib" / package_name
        lib_dir.mkdir(parents=True)

        internal_dir = source_dir / "_internal"
        if internal_dir.exists():
            shutil.copytree(internal_dir, lib_dir / "_internal")

        # Create package info
        info_dir = temp_dir / "package_info"
        info_dir.mkdir()

        info_content = f"""<?xml version="1.0" encoding="utf-8"?>
<pkg-info format-version="2" identifier="com.suse.observability.{package_name}" version="{package_version}" install-location="/" auth="root">
    <payload installKBytes="0" numberOfFiles="0"/>
    <bundle-version/>
    <upgrade-bundle/>
    <update-bundle/>
    <atomic-update-bundle/>
    <strict-identifier/>
    <relocate/>
    <scripts>
        <postinstall file="./postinstall"/>
    </scripts>
</pkg-info>
"""

        with open(info_dir / "PackageInfo", "w") as f:
            f.write(info_content)

        # Create postinstall script
        postinstall_content = """#!/bin/bash
chmod +x /usr/local/bin/agent-integrations-finder
"""

        with open(info_dir / "postinstall", "w") as f:
            f.write(postinstall_content)
        os.chmod(info_dir / "postinstall", 0o755)

        # Try to build pkg using pkgbuild
        try:
            cmd = [
                "pkgbuild",
                "--root",
                str(pkg_root),
                "--identifier",
                f"com.suse.observability.{package_name}",
                "--version",
                package_version,
                "--install-location",
                "/",
                str(pkg_path),
            ]
            subprocess.run(cmd, check=True)
            print(f"Created .pkg package: {pkg_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: pkgbuild not available, skipping .pkg package creation")
        finally:
            # Clean up
            shutil.rmtree(temp_dir)

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

        # Create system packages first
        if target_platform == "linux":
            self.create_deb_package(target_platform, target_arch, source_dir, output_dir)
            self.create_rpm_package(target_platform, target_arch, source_dir, output_dir)
        elif target_platform == "win":
            self.create_msi_package(target_platform, target_arch, source_dir, output_dir)
        elif target_platform == "macos":
            self.create_pkg_package(target_platform, target_arch, source_dir, output_dir)

        # Package based on platform (original tar.gz/zip packages)
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

        pass


def main():
    """Main build function"""
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help", "help"]:
        print("Usage: python build.py <target> [options]")
        print("Targets:")
        print("  linux-x86_64")
        print("  linux-aarch64")
        print("  macos-x86_64")
        print("  macos-aarch64")
        print("  win-x86_64")
        print("  all")
        print("  docker-amd64")
        print("  docker-arm64")
        print("  docker-all")
        print("")
        print("Options:")
        print("  --create-deb-only    - Create only .deb package (Linux)")
        print("  --create-rpm-only    - Create only .rpm package (Linux)")
        print("  --create-msi-only    - Create only .msi package (Windows)")
        print("  --create-pkg-only    - Create only .pkg package (macOS)")
        print("")
        print("Examples:")
        print("  python build.py linux-x86_64")
        print("  python build.py linux-x86_64 --create-deb-only")
        print("  python build.py docker-all")
        print("  python build.py all")
        sys.exit(1)

    target = sys.argv[1]
    builder = Builder()

    # Check for package-only options
    create_deb_only = "--create-deb-only" in sys.argv
    create_rpm_only = "--create-rpm-only" in sys.argv
    create_msi_only = "--create-msi-only" in sys.argv
    create_pkg_only = "--create-pkg-only" in sys.argv

    targets = {
        "linux-x86_64": ("linux", "x86_64"),
        "linux-aarch64": ("linux", "aarch64"),
        "macos-x86_64": ("macos", "x86_64"),
        "macos-aarch64": ("macos", "aarch64"),
        "win-x86_64": ("win", "x86_64"),
        "docker-amd64": ("docker", "amd64"),
        "docker-arm64": ("docker", "arm64"),
    }

    if target == "all":
        build_targets = targets.values()
    elif target == "docker-all":
        build_targets = [("docker", "amd64"), ("docker", "arm64")]
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

        if platform_name == "docker":
            # Handle Docker builds
            print(f"Building Docker image for {arch}...")
            if builder.build("linux", arch.replace("amd64", "x86_64").replace("arm64", "aarch64")):
                print(f"Docker build preparation completed for {arch}")
            else:
                print(f"Failed to prepare Docker build for {arch}")
                sys.exit(1)
        elif builder.build(platform_name, arch):
            # Handle package-only options
            if create_deb_only and platform_name == "linux":
                builder.create_deb_package(
                    platform_name,
                    arch,
                    builder.get_platform_dist_dir(platform_name, arch) / "agent-integrations-finder",
                    builder.project_root / "packages",
                )
            elif create_rpm_only and platform_name == "linux":
                builder.create_rpm_package(
                    platform_name,
                    arch,
                    builder.get_platform_dist_dir(platform_name, arch) / "agent-integrations-finder",
                    builder.project_root / "packages",
                )
            elif create_msi_only and platform_name == "win":
                builder.create_msi_package(
                    platform_name,
                    arch,
                    builder.get_platform_dist_dir(platform_name, arch) / "agent-integrations-finder",
                    builder.project_root / "packages",
                )
            elif create_pkg_only and platform_name == "macos":
                builder.create_pkg_package(
                    platform_name,
                    arch,
                    builder.get_platform_dist_dir(platform_name, arch) / "agent-integrations-finder",
                    builder.project_root / "packages",
                )
            else:
                # Normal packaging (all formats)
                builder.package(platform_name, arch)
        else:
            print(f"Failed to build {platform_name}-{arch}")
            sys.exit(1)

    print("\nAll builds completed successfully!")


if __name__ == "__main__":
    main()
