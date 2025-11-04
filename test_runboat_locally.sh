#!/bin/bash
# Field Service Runboat Local Testing Script
# This replicates the OCA Runboat CI environment locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Field Service Runboat Testing Environment${NC}"

# Configuration
CONTAINER="ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest"
REPO_DIR="$(pwd)"
MODULE_NAME="${1:-fieldservice_stage_validation}"

echo -e "${YELLOW}📦 Using container: ${CONTAINER}${NC}"
echo -e "${YELLOW}📁 Repository: ${REPO_DIR}${NC}"
echo -e "${YELLOW}📦 Module: ${MODULE_NAME}${NC}"

# Check if we're in the right directory
if [ ! -d "${MODULE_NAME}" ]; then
    echo -e "${RED}❌ Error: Module ${MODULE_NAME} not found in current directory${NC}"
    echo -e "${YELLOW}💡 Available modules:"
    ls -d */ | grep -E "(fieldservice|.*)" | head -10
    exit 1
fi

# Create a Docker network for communication between containers
echo -e "${YELLOW}🌐 Creating Docker network...${NC}"
docker network create test-network 2>/dev/null || true

# Start PostgreSQL container
echo -e "${YELLOW}🐘 Starting PostgreSQL container...${NC}"
docker run -d --name test-postgres \
  --network test-network \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=odoo \
  postgres:12.0

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
sleep 15

# Test PostgreSQL connection
echo -e "${YELLOW}🔍 Testing PostgreSQL connection...${NC}"
docker run --rm --network test-network ${CONTAINER} \
  bash -c "pg_isready -h test-postgres -U odoo -d odoo" || {
    echo -e "${RED}❌ PostgreSQL connection failed${NC}"
    docker stop test-postges 2>/dev/null || true
    docker rm test-postges 2>/dev/null || true
    docker network rm test-network 2>/dev/null || true
    exit 1
  }

echo -e "${YELLOW}🧪 Running tests for ${MODULE_NAME}...${NC}"
docker run --rm \
  --network test-network \
  -v "${REPO_DIR}:/opt/odoo/addons/field-service" \
  -v "${REPO_DIR}/OCB:/opt/odoo/addons/OCB" \
  -e OCA_ENABLE_CHECKLOG_ODOO=1 \
  -e PGHOST=test-postgres \
  -e PGUSER=odoo \
  -e PGPASSWORD=odoo \
  -e PGDATABASE=odoo \
  ${CONTAINER} \
  bash -c "
    set -e
    export PYTHONPATH=/opt/odoo/addons/field-service/OCB
    cd /opt/odoo/addons/OCB
    
    echo 'Creating database...'
    createdb --host=test-postgres --username=odoo odoo_test
    
    echo 'Installing field-service modules...'
    python odoo-bin -d odoo_test --init --without-demo --stop-after-init \
      --addons-path=/opt/odoo/addons/field-service,/opt/odoo/addons/OCB/addons \
      --database=odoo_test \
      fieldservice
    
    echo 'Installing ${MODULE_NAME}...'
    python odoo-bin -d odoo_test --init --without-demo --stop-after-init \
      --addons-path=/opt/odoo/addons/field-service,/opt/odoo/addons/OCB/addons \
      --database=odoo_test \
      ${MODULE_NAME}
    
    echo 'Running tests for ${MODULE_NAME}...'
    python odoo-bin -d odoo_test --test-enable --stop-after-init \
      --addons-path=/opt/odoo/addons/field-service,/opt/odoo/addons/OCB/addons \
      --database=odoo_test \
      -i ${MODULE_NAME}
  "

TEST_EXIT_CODE=$?

# Cleanup
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
docker stop test-postgres 2>/dev/null || true
docker rm test-postgres 2>/dev/null || true
docker network rm test-network 2>/dev/null || true

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Tests failed with exit code ${TEST_EXIT_CODE}${NC}"
    echo -e "${YELLOW}💡 Check the logs above for details${NC}"
    exit $TEST_EXIT_CODE
fi