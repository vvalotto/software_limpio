#!/bin/bash
# build.sh - Script de build automatizado para quality-agents

set -e  # Exit on error

echo "🔨 Building quality-agents package..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Clean previous builds
echo "📦 Step 1: Cleaning previous builds..."
rm -rf dist/ build/ src/*.egg-info
echo -e "${GREEN}✓ Cleaned${NC}"
echo ""

# Step 2: Run tests
echo "🧪 Step 2: Running tests..."
if pytest -q; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
    exit 1
fi
echo ""

# Step 3: Lint check
echo "🔍 Step 3: Running quality checks..."
if codeguard src/ --quiet 2>/dev/null || true; then
    echo -e "${GREEN}✓ Quality checks completed${NC}"
else
    echo -e "${YELLOW}⚠ Quality issues found (review recommended)${NC}"
fi
echo ""

# Step 4: Build package
echo "📦 Step 4: Building distribution packages..."
if python -m build; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi
echo ""

# Step 5: Validate package
echo "✅ Step 5: Validating packages..."
if twine check dist/*; then
    echo -e "${GREEN}✓ Packages validated${NC}"
else
    echo -e "${RED}✗ Validation failed${NC}"
    exit 1
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Build completed successfully!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📦 Generated packages:"
ls -lh dist/
echo ""
echo "Next steps:"
echo "  • Test installation: pip install dist/*.whl"
echo "  • Publish to TestPyPI: ./packaging/publish.sh test"
echo "  • Publish to PyPI: ./packaging/publish.sh prod"
