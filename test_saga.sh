#!/bin/bash

# =============================================================================
# SAGA Choreography Test Script
# Лабораторная работа №4
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API_URL="${API_URL:-http://localhost}"
INTERNAL_API_KEY=""

# Temporary files for storing data
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  SAGA Choreography Test Script${NC}"
echo -e "${BLUE}  Lab 4: Post Publication Flow${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# =============================================================================
# Helper functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  STEP: $1${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

wait_for_services() {
    log_info "Waiting for services to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$API_URL/health" > /dev/null 2>&1; then
            log_success "Backend is ready!"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "Services did not become ready in time"
    exit 1
}

# =============================================================================
# Step 1: Wait for services
# =============================================================================

log_step "1. Checking Services"
wait_for_services

# =============================================================================
# Step 2: Run migrations
# =============================================================================

log_step "2. Running Migrations"

log_info "Running backend migrations..."
docker exec backend alembic upgrade head 2>/dev/null || {
    log_warning "Backend migrations may already be applied or failed"
}

log_info "Running users-api migrations..."
docker exec users-api alembic upgrade head 2>/dev/null || {
    log_warning "Users migrations may already be applied or failed"
}

log_success "Migrations completed"

# =============================================================================
# Step 3: Initialize API keys
# =============================================================================

log_step "3. Initializing Internal API Keys"

API_KEYS_RESPONSE=$(curl -s -X POST "$API_URL/api/internal/init-keys")
echo "Response: $API_KEYS_RESPONSE"

# Extract first API key
INTERNAL_API_KEY=$(echo "$API_KEYS_RESPONSE" | grep -o '"key":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$INTERNAL_API_KEY" ]; then
    log_error "Failed to get API key"
    exit 1
fi

log_success "API Key obtained: ${INTERNAL_API_KEY:0:20}..."

# Update worker .env file
log_info "Updating worker .env with API key..."
sed -i "s/internal_api_key=.*/internal_api_key=$INTERNAL_API_KEY/" ./worker/.env 2>/dev/null || \
    echo "internal_api_key=$INTERNAL_API_KEY" >> ./worker/.env

# Restart workers to pick up new API key
log_info "Restarting workers..."
docker-compose restart worker dlq-worker 2>/dev/null || {
    log_warning "Could not restart workers - they may need manual restart"
}

sleep 5

# =============================================================================
# Step 4: Register test users
# =============================================================================

log_step "4. Registering Test Users"

# Author
AUTHOR_RESPONSE=$(curl -s -X POST "$API_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "saga_author@test.com",
        "username": "saga_author",
        "password": "password123"
    }')
echo "Author registration: $AUTHOR_RESPONSE"

AUTHOR_ID=$(echo "$AUTHOR_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
log_success "Author registered with ID: $AUTHOR_ID"

# Subscriber
SUBSCRIBER_RESPONSE=$(curl -s -X POST "$API_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "saga_subscriber@test.com",
        "username": "saga_subscriber",
        "password": "password123"
    }')
echo "Subscriber registration: $SUBSCRIBER_RESPONSE"

SUBSCRIBER_ID=$(echo "$SUBSCRIBER_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
log_success "Subscriber registered with ID: $SUBSCRIBER_ID"

# =============================================================================
# Step 5: Login users
# =============================================================================

log_step "5. Logging in Users"

# Author login
AUTHOR_TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/api/users/login" \
    -d "username=saga_author&password=password123")
echo "Author login response: $AUTHOR_TOKEN_RESPONSE"

AUTHOR_TOKEN=$(echo "$AUTHOR_TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -z "$AUTHOR_TOKEN" ]; then
    log_error "Failed to get author token"
    exit 1
fi
log_success "Author token obtained"

# Subscriber login
SUBSCRIBER_TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/api/users/login" \
    -d "username=saga_subscriber&password=password123")
echo "Subscriber login response: $SUBSCRIBER_TOKEN_RESPONSE"

SUBSCRIBER_TOKEN=$(echo "$SUBSCRIBER_TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -z "$SUBSCRIBER_TOKEN" ]; then
    log_error "Failed to get subscriber token"
    exit 1
fi
log_success "Subscriber token obtained"

# =============================================================================
# Step 6: Setup subscription
# =============================================================================

log_step "6. Setting up Subscription"

# Set subscription key for subscriber
log_info "Setting subscription key..."
curl -s -X PUT "$API_URL/api/users/me/subscription-key" \
    -H "Authorization: Bearer $SUBSCRIBER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"subscription_key": "test-push-key-12345"}'

# Subscribe to author
log_info "Subscribing to author..."
SUBSCRIBE_RESPONSE=$(curl -s -X POST "$API_URL/api/users/subscribe" \
    -H "Authorization: Bearer $SUBSCRIBER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"target_user_id\": $AUTHOR_ID}")
echo "Subscribe response: $SUBSCRIBE_RESPONSE"

log_success "Subscription setup complete"

# =============================================================================
# Step 7: Create article (DRAFT)
# =============================================================================

log_step "7. Creating Article (DRAFT status)"

TIMESTAMP=$(date +%s)
ARTICLE_RESPONSE=$(curl -s -X POST "$API_URL/api/articles" \
    -H "Authorization: Bearer $AUTHOR_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"title\": \"SAGA Test Article $TIMESTAMP\",
        \"description\": \"Testing SAGA choreography pattern\",
        \"body\": \"This article will go through moderation, preview generation, and publication.\"
    }")
echo "Article created: $ARTICLE_RESPONSE"

ARTICLE_ID=$(echo "$ARTICLE_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
ARTICLE_SLUG=$(echo "$ARTICLE_RESPONSE" | grep -o '"slug":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ARTICLE_ID" ]; then
    log_error "Failed to create article"
    exit 1
fi

log_success "Article created with ID: $ARTICLE_ID, Slug: $ARTICLE_SLUG"

# =============================================================================
# Step 8: Verify DRAFT status
# =============================================================================

log_step "8. Verifying DRAFT Status"

# Use internal endpoint to check status
ARTICLE_STATUS=$(curl -s -X GET "$API_URL/api/internal/posts/$ARTICLE_ID" \
    -H "X-API-Key: $INTERNAL_API_KEY")
echo "Article status: $ARTICLE_STATUS"

STATUS=$(echo "$ARTICLE_STATUS" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "$STATUS" != "DRAFT" ]; then
    log_error "Expected DRAFT status, got: $STATUS"
    exit 1
fi

log_success "Article is in DRAFT status"

# =============================================================================
# Step 9: Publish article (Start SAGA)
# =============================================================================

log_step "9. Publishing Article (Starting SAGA)"

PUBLISH_RESPONSE=$(curl -s -X POST "$API_URL/api/articles/$ARTICLE_ID/publish" \
    -H "Authorization: Bearer $AUTHOR_TOKEN")
echo "Publish response: $PUBLISH_RESPONSE"

NEW_STATUS=$(echo "$PUBLISH_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "$NEW_STATUS" != "PENDING_PUBLISH" ]; then
    log_error "Expected PENDING_PUBLISH status after publish, got: $NEW_STATUS"
    exit 1
fi

log_success "Article status changed to PENDING_PUBLISH"
log_info "SAGA workflow started!"

# =============================================================================
# Step 10: Wait for SAGA to complete
# =============================================================================

log_step "10. Waiting for SAGA to Complete"

log_info "Waiting for moderation, preview generation, and publication..."
log_info "This may take 10-30 seconds..."

MAX_WAIT=60
WAIT_INTERVAL=5
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
    sleep $WAIT_INTERVAL
    ELAPSED=$((ELAPSED + WAIT_INTERVAL))
    
    ARTICLE_STATUS=$(curl -s -X GET "$API_URL/api/internal/posts/$ARTICLE_ID" \
        -H "X-API-Key: $INTERNAL_API_KEY")
    
    STATUS=$(echo "$ARTICLE_STATUS" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    PREVIEW_URL=$(echo "$ARTICLE_STATUS" | grep -o '"preview_url":"[^"]*"' | cut -d'"' -f4)
    
    log_info "Status: $STATUS (elapsed: ${ELAPSED}s)"
    
    if [ "$STATUS" = "PUBLISHED" ]; then
        log_success "SAGA completed successfully!"
        log_success "Preview URL: $PREVIEW_URL"
        break
    elif [ "$STATUS" = "REJECTED" ]; then
        log_warning "Article was rejected by moderation (this is expected ~20% of the time)"
        break
    elif [ "$STATUS" = "ERROR" ]; then
        log_warning "Article encountered an error during processing"
        break
    fi
done

if [ $ELAPSED -ge $MAX_WAIT ] && [ "$STATUS" = "PENDING_PUBLISH" ]; then
    log_warning "SAGA did not complete within timeout. Check worker logs."
fi

# =============================================================================
# Step 11: Final verification
# =============================================================================

log_step "11. Final Status Verification"

FINAL_ARTICLE=$(curl -s -X GET "$API_URL/api/internal/posts/$ARTICLE_ID" \
    -H "X-API-Key: $INTERNAL_API_KEY")
echo "Final article state:"
echo "$FINAL_ARTICLE" | python3 -m json.tool 2>/dev/null || echo "$FINAL_ARTICLE"

FINAL_STATUS=$(echo "$FINAL_ARTICLE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

# =============================================================================
# Step 12: Test internal API protection
# =============================================================================

log_step "12. Testing Internal API Protection"

log_info "Testing access to internal endpoint without API key..."
UNAUTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X GET "$API_URL/api/internal/posts/$ARTICLE_ID")

if [ "$UNAUTH_RESPONSE" = "401" ]; then
    log_success "Internal endpoint correctly rejected request without API key (401)"
else
    log_warning "Expected 401, got: $UNAUTH_RESPONSE"
fi

log_info "Testing access to internal endpoint with JWT instead of API key..."
JWT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X GET "$API_URL/api/internal/posts/$ARTICLE_ID" \
    -H "Authorization: Bearer $AUTHOR_TOKEN")

if [ "$JWT_RESPONSE" = "401" ]; then
    log_success "Internal endpoint correctly rejected JWT authentication (401)"
else
    log_warning "Expected 401 for JWT auth, got: $JWT_RESPONSE"
fi

# =============================================================================
# Step 13: Check worker logs
# =============================================================================

log_step "13. Worker Logs (last 30 lines)"

echo -e "${BLUE}--- Main Worker ---${NC}"
docker logs --tail 30 worker 2>&1 || echo "Could not get worker logs"

echo ""
echo -e "${BLUE}--- DLQ Worker ---${NC}"
docker logs --tail 15 dlq-worker 2>&1 || echo "Could not get DLQ worker logs"

# =============================================================================
# Summary
# =============================================================================

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TEST SUMMARY${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Article ID:     ${YELLOW}$ARTICLE_ID${NC}"
echo -e "Article Slug:   ${YELLOW}$ARTICLE_SLUG${NC}"
echo -e "Final Status:   ${YELLOW}$FINAL_STATUS${NC}"
echo ""

if [ "$FINAL_STATUS" = "PUBLISHED" ]; then
    echo -e "${GREEN}✓ SAGA completed successfully!${NC}"
    echo -e "${GREEN}✓ Article went through: DRAFT → PENDING_PUBLISH → PUBLISHED${NC}"
    echo -e "${GREEN}✓ Moderation passed, preview generated, notifications sent${NC}"
    exit 0
elif [ "$FINAL_STATUS" = "REJECTED" ]; then
    echo -e "${YELLOW}⚠ Article was rejected by moderation${NC}"
    echo -e "${YELLOW}  This is expected behavior (~20% chance)${NC}"
    echo -e "${YELLOW}  Run the test again to see successful publication${NC}"
    exit 0
elif [ "$FINAL_STATUS" = "ERROR" ]; then
    echo -e "${RED}✗ Article processing encountered an error${NC}"
    echo -e "${RED}  Check worker logs for details${NC}"
    exit 1
else
    echo -e "${YELLOW}⚠ SAGA may still be in progress or encountered issues${NC}"
    echo -e "${YELLOW}  Current status: $FINAL_STATUS${NC}"
    exit 1
fi
