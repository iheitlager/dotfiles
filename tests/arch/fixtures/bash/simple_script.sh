#!/usr/bin/env bash
# Simple test script for extraction
# This script demonstrates function extraction

# Setup function
setup() {
    echo "Setting up"
}

# Cleanup function
cleanup() {
    echo "Cleaning up"
}

# Main function
main() {
    setup
    echo "Running main"
    cleanup
}

main "$@"
