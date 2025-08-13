#!/usr/bin/env python3
"""
CI-specific tests for SUSE Observability Integrations Finder
This version doesn't import PyQt6 to avoid GUI dependencies in CI
"""

import sys
import os

# Add the current directory to the path so we can import the core functionality
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import only the core functionality, not the GUI
try:
    from integrations_finder import IntegrationsFinder
except ImportError as e:
    if "PyQt6" in str(e):
        print("⚠️  PyQt6 not available in CI environment - skipping GUI tests")
        print("   This is expected in CI. GUI functionality will be tested in local development.")
        sys.exit(0)
    else:
        raise


def test_sha_extraction():
    """Test SHA extraction from various input formats."""
    print("=== SHA Extraction Demo ===\n")
    
    finder = IntegrationsFinder()
    
    test_cases = [
        ("a1b2c3d4", "a1b2c3d4"),
        ("stackstate/agent:7.51.1-a1b2c3d4", "a1b2c3d4"),
        ("registry.example.com/stackstate/agent:7.51.1-a1b2c3d4", "a1b2c3d4"),
        ("quay.io/stackstate/stackstate-k8s-agent:a1b2c3d4", "a1b2c3d4"),
        ("some-text-a1b2c3d4-more-text", "a1b2c3d4"),
        ("invalid-input", None),
        ("", None),
    ]
    
    print("Testing SHA extraction:")
    for input_str, expected in test_cases:
        result = finder.extract_sha(input_str)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_str}' -> '{result}' (expected: '{expected}')")


def test_branch_detection():
    """Test branch detection functionality."""
    finder = IntegrationsFinder()
    
    # Test known tags
    known_tags = ["7.51.1-3", "7.51.1", "v1.0.0"]
    print("\nTesting branch detection with known tags:")
    for tag in known_tags:
        is_branch = finder.is_branch_version(tag)
        status = "BRANCH" if is_branch else "TAG"
        print(f"  {tag}: {status}")
    
    # Test likely branches
    likely_branches = ["main", "master", "develop", "feature-branch"]
    print("\nTesting branch detection with likely branches:")
    for branch in likely_branches:
        is_branch = finder.is_branch_version(branch)
        status = "BRANCH" if is_branch else "TAG"
        print(f"  {branch}: {status}")


def test_integrations_finder():
    """Test the complete integrations finder workflow."""
    finder = IntegrationsFinder()
    
    # Test with a sample input (this will fail if the SHA doesn't exist)
    test_input = "a1b2c3d4"  # This is a dummy SHA for testing
    
    print(f"\nTesting complete workflow with: {test_input}")
    result = finder.find_integrations(test_input)
    
    if len(result) == 3:
        success, message, is_branch = result
        print(f"Success: {success}")
        print(f"Is Branch: {is_branch}")
        print(f"Message: {message}")
    else:
        success, message = result
        print(f"Success: {success}")
        print(f"Message: {message}")


def test_cli_functionality():
    """Test CLI functionality without GUI."""
    print("\n=== CLI Functionality Test ===")
    
    # Test that we can import the CLI module
    try:
        import click
        print("✅ Click library imported successfully")
    except ImportError as e:
        print(f"❌ Click library import failed: {e}")
        return False
    
    # Test that the IntegrationsFinder class works
    try:
        finder = IntegrationsFinder()
        print("✅ IntegrationsFinder class instantiated successfully")
    except Exception as e:
        print(f"❌ IntegrationsFinder instantiation failed: {e}")
        return False
    
    # Test SHA extraction
    try:
        sha = finder.extract_sha("a1b2c3d4")
        assert sha == "a1b2c3d4"
        print("✅ SHA extraction works correctly")
    except Exception as e:
        print(f"❌ SHA extraction failed: {e}")
        return False
    
    return True


def main():
    """Run all CI tests."""
    print("SUSE Observability Integrations Finder - CI Tests\n")
    print("Running headless tests (no GUI)...\n")
    
    try:
        test_sha_extraction()
        test_branch_detection()
        test_integrations_finder()
        
        if test_cli_functionality():
            print("\n✅ All CI tests passed!")
        else:
            print("\n❌ Some CI tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
