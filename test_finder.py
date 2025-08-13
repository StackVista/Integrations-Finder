#!/usr/bin/env python3
"""
Test script for the Integrations Finder tool.
"""

from integrations_finder import IntegrationsFinder


def test_sha_extraction():
    """Test SHA extraction from various input formats."""
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


if __name__ == "__main__":
    test_sha_extraction()
    test_integrations_finder()
    test_branch_detection()
