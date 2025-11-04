#!/bin/bash
# Simple local testing script using proper OCB setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Simple Local Field Service Testing${NC}"

# Configuration
MODULE_NAME="${1:-fieldservice_stage_validation}"
OCB_PATH="${2:-/home/fsmw/dev/OCA/18/OCB}"
REPO_DIR="$(pwd)"

echo -e "${YELLOW}📦 Module: ${MODULE_NAME}${NC}"
echo -e "${YELLOW}📁 OCB Path: ${OCB_PATH}${NC}"
echo -e "${YELLOW}📁 Repo: ${REPO_DIR}${NC}"

# Check dependencies
if [ ! -d "${OCB_PATH}" ]; then
    echo -e "${RED}❌ OCB not found at ${OCB_PATH}${NC}"
    exit 1
fi

if [ ! -d "${MODULE_NAME}" ]; then
    echo -e "${RED}❌ Module ${MODULE_NAME} not found${NC}"
    echo -e "${YELLOW}💡 Available modules:"
    ls -d */ | grep -v "OCB" | head -10
    exit 1
fi

# Test the module
echo -e "${YELLOW}🧪 Running tests for ${MODULE_NAME}...${NC}"

cd "${OCB_PATH}"

python odoo-bin -d test_db --test-enable --stop-after-init \
  --addons-path="${REPO_DIR},${REPO_DIR}/OCB/addons" \
  --database=test_db \
  --log-level=info \
  -i "${MODULE_NAME}" 2>&1 | tee /tmp/test_output.log

# Check for errors in output
if grep -q "ERROR\|error\|failed\|failure" /tmp/test_output.log; then
    echo -e "${RED}❌ Tests failed! Check logs above.${NC}"
    grep -E "(ERROR|error|failed|failure)" /tmp/test_output.log | tail -10
    exit 1
else
    echo -e "${GREEN}✅ Tests passed!${NC}"
fi

# Cleanup
rm -f /tmp/test_output.log