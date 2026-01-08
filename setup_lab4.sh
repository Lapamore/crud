#!/bin/bash

# =============================================================================
# Quick setup script for Lab 4
# =============================================================================

echo "=== Lab 4: SAGA Choreography Quick Setup ==="

# Step 1: Start services
echo ""
echo "Step 1: Starting all services..."
docker-compose up -d --build

echo ""
echo "Waiting for services to start (30 seconds)..."
sleep 30

# Step 2: Run migrations
echo ""
echo "Step 2: Running migrations..."
docker exec backend alembic upgrade head
docker exec users-api alembic upgrade head

# Step 3: Initialize API keys
echo ""
echo "Step 3: Initializing API keys..."
API_RESPONSE=$(curl -s -X POST http://localhost/api/internal/init-keys)
echo "Response: $API_RESPONSE"

API_KEY=$(echo "$API_RESPONSE" | grep -o '"key":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -n "$API_KEY" ]; then
    echo ""
    echo "API Key obtained: ${API_KEY:0:30}..."
    
    # Update worker .env
    sed -i "s/internal_api_key=.*/internal_api_key=$API_KEY/" ./worker/.env 2>/dev/null || \
        echo "internal_api_key=$API_KEY" >> ./worker/.env
    
    echo "Worker .env updated"
    
    # Restart workers
    echo ""
    echo "Restarting workers..."
    docker-compose restart worker dlq-worker
    
    echo ""
    echo "=== Setup Complete! ==="
    echo ""
    echo "You can now run the full test:"
    echo "  ./test_saga.sh"
    echo ""
    echo "Or test manually:"
    echo "  1. Register user: POST http://localhost/api/users"
    echo "  2. Login: POST http://localhost/api/users/login"
    echo "  3. Create article: POST http://localhost/api/articles"
    echo "  4. Publish: POST http://localhost/api/articles/{id}/publish"
    echo ""
else
    echo "ERROR: Failed to get API key"
    exit 1
fi
