#!/usr/bin/env python3
"""
Demo script for SUSE Observability Integrations Finder
"""

from integrations_finder import IntegrationsFinder


def demo_sha_extraction():
    """Demonstrate SHA extraction from various input formats."""
    print("=== SHA Extraction Demo ===\n")
    
    finder = IntegrationsFinder()
    
    test_inputs = [
        "a1b2c3d4",
        "stackstate/agent:7.51.1-a1b2c3d4",
        "registry.example.com/stackstate/agent:7.51.1-a1b2c3d4",
        "quay.io/stackstate/stackstate-k8s-agent:a1b2c3d4",
        "some-text-a1b2c3d4-more-text",
        "invalid-input",
    ]
    
    for input_str in test_inputs:
        sha = finder.extract_sha(input_str)
        status = "✓" if sha else "✗"
        print(f"{status} Input: '{input_str}'")
        print(f"   Extracted SHA: '{sha}'")
        print()


def demo_workflow():
    """Demonstrate the complete workflow (with a dummy SHA)."""
    print("=== Complete Workflow Demo ===\n")
    
    # This will fail because a1b2c3d4 is not a real commit
    # but it shows the workflow steps
    test_input = "stackstate/agent:7.51.1-a1b2c3d4"
    
    print(f"Input: {test_input}")
    print("Expected workflow:")
    print("1. Extract SHA: a1b2c3d4")
    print("2. Look up agent commit on GitHub")
    print("3. Read stackstate-deps.json")
    print("4. Generate integrations URL")
    print()
    
    finder = IntegrationsFinder()
    success, message = finder.find_integrations(test_input)
    
    print("Actual result:")
    print(message)
    print()


def main():
    """Run the demo."""
    print("SUSE Observability Integrations Finder - Demo\n")
    print("This demo shows how the tool works with various input formats.\n")
    
    demo_sha_extraction()
    demo_workflow()
    
    print("=== Usage Instructions ===")
    print("To use the tool with real data:")
    print("1. CLI: python3 integrations_finder.py find <agent_sha_or_container_path>")
    print("2. GUI: python3 integrations_finder.py gui")
    print()
    print("Example with real data:")
print("  python3 integrations_finder.py find quay.io/stackstate/stackstate-k8s-agent:8be54df8")


if __name__ == "__main__":
    main()
