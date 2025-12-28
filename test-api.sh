#!/bin/bash

# ============================================
# API Test Script for CRUD Lab (Bash version)
# ============================================

BASE_URL="http://localhost"
PASSED=0
FAILED=0
CURL_TIMEOUT=10

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[1;33m'
blue='\033[0;34m'
cyan='\033[0;36m'
gray='\033[0;37m'
nc='\033[0m' # No Color

print_result() {
    local name="$1"
    local success="$2"
    local details="$3"
    
    if [ "$success" = "true" ]; then
        echo -e "${green}[PASS]${nc} $name"
        if [ -n "$details" ]; then
            echo -e "    $details"
        fi
        ((PASSED++))
    else
        echo -e "${red}[FAIL]${nc} $name"
        if [ -n "$details" ]; then
            echo -e "    ${yellow}$details${nc}"
        fi
        ((FAILED++))
    fi
}

header() {
    echo -e "${cyan}========================================${nc}"
    echo -e "${cyan} $1${nc}"
    echo -e "${cyan}========================================${nc}"
    echo ""
}

section() {
    echo -e "${blue}--- $1 ---${nc}"
}

# ============================================
# 1. SWAGGER DOCS AVAILABILITY
# ============================================
header "API TESTING STARTED"

section "1. SWAGGER DOCS"
curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/docs" | {
    read HTTP_CODE
    print_result "Backend Swagger (/docs)" "$([ $HTTP_CODE = 200 ] && echo true || echo false)" "Status: $HTTP_CODE"
}

curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/users/docs" | {
    read HTTP_CODE
    print_result "Users Swagger (/users/docs)" "$([ $HTTP_CODE = 200 ] && echo true || echo false)" "Status: $HTTP_CODE"
}

echo ""

# ============================================
# 2. USER SERVICE TESTS
# ============================================
section "2. USER SERVICE"

TEST_EMAIL="test_$(shuf -i 1000-9999 -n 1)@example.com"
TEST_USERNAME="testuser_$(shuf -i 1000-9999 -n 1)"
TEST_PASSWORD="password123"
USER_ID=""
ACCESS_TOKEN=""

# 2.1 Register User
section "Register User"
REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"username\":\"$TEST_USERNAME\",\"password\":\"$TEST_PASSWORD\"}")

HTTP_CODE=$(echo "$REGISTER_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$REGISTER_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "201" ]; then
    USER_ID=$(echo "$RESPONSE_BODY" | jq -r '.id // empty')
    print_result "Register User (POST /api/users)" true "Created user ID: $USER_ID, email: $TEST_EMAIL"
else
    print_result "Register User (POST /api/users)" false "Status: $HTTP_CODE"
fi

# 2.2 Login User
if [ -n "$USER_ID" ]; then
    section "Login User"
    LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/users/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$TEST_USERNAME&password=$TEST_PASSWORD")

    HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -n1)
    RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "200" ]; then
        ACCESS_TOKEN=$(echo "$RESPONSE_BODY" | jq -r '.access_token // empty')
        if [ -n "$ACCESS_TOKEN" ]; then
            print_result "Login User (POST /api/users/login)" true "Token: ${ACCESS_TOKEN:0:20}..."
        else
            print_result "Login User (POST /api/users/login)" false "No access_token in response"
        fi
    else
        print_result "Login User (POST /api/users/login)" false "Status: $HTTP_CODE"
    fi
fi

# 2.3 Get Current User
if [ -n "$ACCESS_TOKEN" ]; then
    section "Get Current User"
    CURRENT_USER_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/user" \
        -H "Authorization: Bearer $ACCESS_TOKEN")

    HTTP_CODE=$(echo "$CURRENT_USER_RESPONSE" | tail -n1)
    RESPONSE_BODY=$(echo "$CURRENT_USER_RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "200" ]; then
        USERNAME=$(echo "$RESPONSE_BODY" | jq -r '.username // empty')
        print_result "Get Current User (GET /api/user)" "$([ "$USERNAME" = "$TEST_USERNAME" ] && echo true || echo false)" "Username: $USERNAME"
    else
        print_result "Get Current User (GET /api/user)" false "Status: $HTTP_CODE"
    fi
fi

echo ""

# ============================================
# 3. ARTICLES TESTS
# ============================================
section "3. BACKEND SERVICE (ARTICLES)"

ARTICLE_ID=""
ARTICLE_SLUG=""

# 3.1 Get Articles List
section "Get Articles List"
ARTICLES_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/articles")
HTTP_CODE=$(echo "$ARTICLES_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$ARTICLES_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    ARTICLES_COUNT=$(echo "$RESPONSE_BODY" | jq '. | length')
    print_result "Get Articles List (GET /api/articles)" true "Found $ARTICLES_COUNT articles"
fi

# 3.2 Create Article
if [ -n "$ACCESS_TOKEN" ]; then
    section "Create Article"
    ARTICLE_TITLE="Test Article $(shuf -i 1000-9999 -n 1)"
    CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/articles" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -d "{\"title\":\"$ARTICLE_TITLE\",\"description\":\"Test desc\",\"body\":\"Test body\",\"tagList\":[\"test\",\"automation\"]}")

    HTTP_CODE=$(echo "$CREATE_RESPONSE" | tail -n1)
    RESPONSE_BODY=$(echo "$CREATE_RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "201" ]; then
        ARTICLE_ID=$(echo "$RESPONSE_BODY" | jq -r '.id // empty')
        ARTICLE_SLUG=$(echo "$RESPONSE_BODY" | jq -r '.slug // empty')
        AUTHOR_ID=$(echo "$RESPONSE_BODY" | jq -r '.author_id // empty')
        print_result "Create Article (POST /api/articles)" true "ID: $ARTICLE_ID, Slug: $ARTICLE_SLUG"
    else
        print_result "Create Article (POST /api/articles)" false "Status: $HTTP_CODE"
    fi
fi

# 3.3 Get Article by Slug
if [ -n "$ARTICLE_SLUG" ]; then
    section "Get Article by Slug"
    GET_SLUG_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/articles/$ARTICLE_SLUG")
    HTTP_CODE=$(echo "$GET_SLUG_RESPONSE" | tail -n1)
    print_result "Get Article by Slug (GET /api/articles/$ARTICLE_SLUG)" "$([ $HTTP_CODE = 200 ] && echo true || echo false)" "Status: $HTTP_CODE"
fi

echo ""

# ============================================
# 4. COMMENTS TESTS
# ============================================
section "4. COMMENTS SERVICE"

COMMENT_ID=""

# 4.1 Create Comment
if [ -n "$ACCESS_TOKEN" ] && [ -n "$ARTICLE_SLUG" ]; then
    section "Create Comment"
    COMMENT_BODY="Test comment $(shuf -i 1000-9999 -n 1)"
    COMMENT_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/articles/$ARTICLE_SLUG/comments" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -d "{\"body\":\"$COMMENT_BODY\"}")

    HTTP_CODE=$(echo "$COMMENT_RESPONSE" | tail -n1)
    RESPONSE_BODY=$(echo "$COMMENT_RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "201" ]; then
        COMMENT_ID=$(echo "$RESPONSE_BODY" | jq -r '.id // empty')
        print_result "Create Comment (POST /api/articles/$ARTICLE_SLUG/comments)" true "Comment ID: $COMMENT_ID"
    else
        print_result "Create Comment (POST /api/articles/$ARTICLE_SLUG/comments)" false "Status: $HTTP_CODE"
    fi
fi

# 4.2 Get Comments
if [ -n "$ARTICLE_SLUG" ]; then
    section "Get Comments"
    COMMENTS_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/articles/$ARTICLE_SLUG/comments")
    HTTP_CODE=$(echo "$COMMENTS_RESPONSE" | tail -n1)
    RESPONSE_BODY=$(echo "$COMMENTS_RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "200" ]; then
        COMMENTS_COUNT=$(echo "$RESPONSE_BODY" | jq '. | length')
        print_result "Get Comments (GET /api/articles/$ARTICLE_SLUG/comments)" true "Found $COMMENTS_COUNT comments"
    fi
fi

echo ""

# ============================================
# 5. CLEANUP
# ============================================
section "5. CLEANUP"

if [ -n "$ACCESS_TOKEN" ] && [ -n "$ARTICLE_SLUG" ]; then
    curl -s -w "%{http_code}" -X DELETE "$BASE_URL/api/articles/$ARTICLE_SLUG" \
        -H "Authorization: Bearer $ACCESS_TOKEN" | {
        read HTTP_CODE
        print_result "Delete Article (DELETE /api/articles/$ARTICLE_SLUG)" "$([[ $HTTP_CODE =~ 2[0-4] ]] && echo true || echo false)" "Status: $HTTP_CODE"
    }
fi

# ============================================
# SUMMARY
# ============================================
header "TEST SUMMARY"
echo -e "  ${green}Passed:${nc} $PASSED"
echo -e "  ${red}Failed:${nc} $FAILED"
echo -e "  ${nc}Total:${nc}  $(($PASSED + $FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "  ${green}ALL TESTS PASSED!${nc}"
else
    echo -e "  ${red}SOME TESTS FAILED!${nc}"
fi
echo -e "${cyan}========================================${nc}"
