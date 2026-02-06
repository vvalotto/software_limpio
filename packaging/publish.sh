#!/bin/bash
# publish.sh - Script de publicación para PyPI/TestPyPI

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check argument
if [ "$#" -ne 1 ]; then
    echo -e "${RED}Error: Missing argument${NC}"
    echo ""
    echo "Usage:"
    echo "  $0 test    # Publish to TestPyPI"
    echo "  $0 prod    # Publish to PyPI (production)"
    exit 1
fi

MODE=$1

# Validate dist/ exists
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo -e "${RED}✗ No packages found in dist/${NC}"
    echo "Run ./packaging/build.sh first"
    exit 1
fi

# Function to publish to TestPyPI
publish_test() {
    echo -e "${BLUE}📦 Publishing to TestPyPI...${NC}"
    echo ""
    echo "This will upload to: https://test.pypi.org/project/quality-agents/"
    echo ""
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled"
        exit 0
    fi

    twine upload --repository testpypi dist/*

    echo ""
    echo -e "${GREEN}✓ Published to TestPyPI${NC}"
    echo ""
    echo "Test installation:"
    echo "  pip install --index-url https://test.pypi.org/simple/ quality-agents"
    echo ""
    echo "View at: https://test.pypi.org/project/quality-agents/"
}

# Function to publish to PyPI
publish_prod() {
    echo -e "${RED}⚠️  WARNING: Publishing to PyPI (PRODUCTION)${NC}"
    echo ""
    echo "This action:"
    echo "  • CANNOT be undone"
    echo "  • Makes the package publicly available"
    echo "  • Version numbers cannot be reused"
    echo ""
    echo "Version to publish: $(grep '^version' pyproject.toml | cut -d'"' -f2)"
    echo ""
    read -p "Are you ABSOLUTELY sure? (yes/NO) " -r
    echo
    if [[ ! $REPLY == "yes" ]]; then
        echo "Cancelled (safety first!)"
        exit 0
    fi

    twine upload dist/*

    echo ""
    echo -e "${GREEN}🎉 Published to PyPI!${NC}"
    echo ""
    echo "Installation:"
    echo "  pip install quality-agents"
    echo ""
    echo "View at: https://pypi.org/project/quality-agents/"
}

# Execute based on mode
case $MODE in
    test)
        publish_test
        ;;
    prod)
        publish_prod
        ;;
    *)
        echo -e "${RED}Invalid mode: $MODE${NC}"
        echo "Use 'test' or 'prod'"
        exit 1
        ;;
esac
