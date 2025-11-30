# ============================================
# API Test Script for CRUD Lab
# ============================================

$baseUrl = "http://localhost"
$passed = 0
$failed = 0

function Write-TestResult {
    param($name, $success, $details = "")
    if ($success) {
        Write-Host "[PASS] $name" -ForegroundColor Green
        if ($details) { Write-Host "       $details" -ForegroundColor Gray }
        $script:passed++
    } else {
        Write-Host "[FAIL] $name" -ForegroundColor Red
        if ($details) { Write-Host "       $details" -ForegroundColor Yellow }
        $script:failed++
    }
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  API TESTING STARTED" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# 1. SWAGGER DOCS AVAILABILITY
# ============================================
Write-Host "--- 1. SWAGGER DOCS ---" -ForegroundColor Magenta

# Backend Swagger
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/docs" -Method Get -ErrorAction Stop
    Write-TestResult "Backend Swagger (/docs)" ($response.StatusCode -eq 200)
} catch {
    Write-TestResult "Backend Swagger (/docs)" $false $_.Exception.Message
}

# Users Swagger
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/users/docs" -Method Get -ErrorAction Stop
    Write-TestResult "Users Swagger (/users/docs)" ($response.StatusCode -eq 200)
} catch {
    Write-TestResult "Users Swagger (/users/docs)" $false $_.Exception.Message
}

Write-Host ""

# ============================================
# 2. USER SERVICE TESTS
# ============================================
Write-Host "--- 2. USER SERVICE ---" -ForegroundColor Magenta

$testEmail = "test_$(Get-Random)@example.com"
$testUsername = "testuser_$(Get-Random)"
$testPassword = "password123"
$userId = $null
$accessToken = $null

# 2.1 Register User (POST /users/register or POST /api/users)
try {
    $registerBody = @{
        email = $testEmail
        username = $testUsername
        password = $testPassword
    } | ConvertTo-Json
    
    # Try /api/users first (our implementation)
    $response = Invoke-WebRequest -Uri "$baseUrl/api/users" -Method Post -ContentType "application/json" -Body $registerBody -ErrorAction Stop
    $userData = $response.Content | ConvertFrom-Json
    $userId = $userData.id
    Write-TestResult "Register User (POST /api/users)" ($response.StatusCode -eq 201) "Created user ID: $userId, email: $testEmail"
} catch {
    Write-TestResult "Register User (POST /api/users)" $false $_.Exception.Message
}

# 2.2 Login User (POST /users/login or POST /api/users/login)
try {
    # OAuth2 form data format
    $loginBody = "username=$testUsername&password=$testPassword"
    
    $response = Invoke-WebRequest -Uri "$baseUrl/api/users/login" -Method Post -ContentType "application/x-www-form-urlencoded" -Body $loginBody -ErrorAction Stop
    $tokenData = $response.Content | ConvertFrom-Json
    $accessToken = $tokenData.access_token
    Write-TestResult "Login User (POST /api/users/login)" ($response.StatusCode -eq 200 -and $accessToken) "Token received: $($accessToken.Substring(0, 20))..."
} catch {
    Write-TestResult "Login User (POST /api/users/login)" $false $_.Exception.Message
}

# 2.3 Get Current User (GET /users/me or GET /api/user)
try {
    $headers = @{ Authorization = "Bearer $accessToken" }
    $response = Invoke-WebRequest -Uri "$baseUrl/api/user" -Method Get -Headers $headers -ErrorAction Stop
    $currentUser = $response.Content | ConvertFrom-Json
    Write-TestResult "Get Current User (GET /api/user)" ($response.StatusCode -eq 200 -and $currentUser.username -eq $testUsername) "Username: $($currentUser.username)"
} catch {
    Write-TestResult "Get Current User (GET /api/user)" $false $_.Exception.Message
}

# 2.4 Get User by ID (GET /users/{id})
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/users/$userId" -Method Get -ErrorAction Stop
    $userById = $response.Content | ConvertFrom-Json
    Write-TestResult "Get User by ID (GET /api/users/$userId)" ($response.StatusCode -eq 200) "Found: $($userById.username)"
} catch {
    # This endpoint might not exist, that's OK
    Write-TestResult "Get User by ID (GET /api/users/$userId)" $false "Endpoint may not be implemented"
}

Write-Host ""

# ============================================
# 3. BACKEND SERVICE TESTS (ARTICLES/POSTS)
# ============================================
Write-Host "--- 3. BACKEND SERVICE (ARTICLES/POSTS) ---" -ForegroundColor Magenta

$articleId = $null
$articleSlug = $null

# 3.1 Get Articles List (GET /posts or GET /api/articles)
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/articles" -Method Get -ErrorAction Stop
    $articles = $response.Content | ConvertFrom-Json
    Write-TestResult "Get Articles List (GET /api/articles)" ($response.StatusCode -eq 200) "Found $($articles.Count) articles"
} catch {
    Write-TestResult "Get Articles List (GET /api/articles)" $false $_.Exception.Message
}

# 3.2 Create Article (POST /posts or POST /api/articles) - Requires Auth
try {
    $headers = @{ Authorization = "Bearer $accessToken" }
    $articleBody = @{
        title = "Test Article $(Get-Random)"
        description = "This is a test article description"
        body = "This is the full body content of the test article."
        tagList = @("test", "automation")
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl/api/articles" -Method Post -ContentType "application/json" -Body $articleBody -Headers $headers -ErrorAction Stop
    $article = $response.Content | ConvertFrom-Json
    $articleId = $article.id
    $articleSlug = $article.slug
    Write-TestResult "Create Article (POST /api/articles)" ($response.StatusCode -eq 201 -and $article.author_id -eq $userId) "Article ID: $articleId, Slug: $articleSlug, Author ID: $($article.author_id)"
} catch {
    Write-TestResult "Create Article (POST /api/articles)" $false $_.Exception.Message
}

# 3.3 Get Article by Slug (GET /posts/{id} or GET /api/articles/{slug})
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/articles/$articleSlug" -Method Get -ErrorAction Stop
    $articleBySlug = $response.Content | ConvertFrom-Json
    Write-TestResult "Get Article by Slug (GET /api/articles/$articleSlug)" ($response.StatusCode -eq 200) "Title: $($articleBySlug.title)"
} catch {
    Write-TestResult "Get Article by Slug (GET /api/articles/$articleSlug)" $false $_.Exception.Message
}

# 3.4 Update Article (PUT /api/articles/{slug}) - Requires Auth
try {
    $headers = @{ Authorization = "Bearer $accessToken" }
    $updateBody = @{
        title = "Updated Title $(Get-Random)"
        description = "Updated description"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl/api/articles/$articleSlug" -Method Put -ContentType "application/json" -Body $updateBody -Headers $headers -ErrorAction Stop
    $updatedArticle = $response.Content | ConvertFrom-Json
    Write-TestResult "Update Article (PUT /api/articles/$articleSlug)" ($response.StatusCode -eq 200) "New title: $($updatedArticle.title)"
    $articleSlug = $updatedArticle.slug  # Slug may have changed
} catch {
    Write-TestResult "Update Article (PUT /api/articles/$articleSlug)" $false $_.Exception.Message
}

Write-Host ""

# ============================================
# 4. COMMENTS TESTS
# ============================================
Write-Host "--- 4. COMMENTS SERVICE ---" -ForegroundColor Magenta

$commentId = $null

# 4.1 Create Comment on Article - Requires Auth
try {
    $headers = @{ Authorization = "Bearer $accessToken" }
    $commentBody = @{
        body = "This is a test comment $(Get-Random)"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl/api/articles/$articleSlug/comments" -Method Post -ContentType "application/json" -Body $commentBody -Headers $headers -ErrorAction Stop
    $comment = $response.Content | ConvertFrom-Json
    $commentId = $comment.id
    Write-TestResult "Create Comment (POST /api/articles/$articleSlug/comments)" ($response.StatusCode -eq 201) "Comment ID: $commentId"
} catch {
    Write-TestResult "Create Comment (POST /api/articles/$articleSlug/comments)" $false $_.Exception.Message
}

# 4.2 Get Comments for Article
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/articles/$articleSlug/comments" -Method Get -ErrorAction Stop
    $comments = $response.Content | ConvertFrom-Json
    Write-TestResult "Get Comments (GET /api/articles/$articleSlug/comments)" ($response.StatusCode -eq 200) "Found $($comments.Count) comments"
} catch {
    Write-TestResult "Get Comments (GET /api/articles/$articleSlug/comments)" $false $_.Exception.Message
}

# 4.3 Delete Comment - Requires Auth
try {
    $headers = @{ Authorization = "Bearer $accessToken" }
    $response = Invoke-WebRequest -Uri "$baseUrl/api/articles/$articleSlug/comments/$commentId" -Method Delete -Headers $headers -ErrorAction Stop
    Write-TestResult "Delete Comment (DELETE /api/articles/$articleSlug/comments/$commentId)" ($response.StatusCode -eq 200 -or $response.StatusCode -eq 204) "Comment deleted"
} catch {
    Write-TestResult "Delete Comment (DELETE /api/articles/$articleSlug/comments/$commentId)" $false $_.Exception.Message
}

Write-Host ""

# ============================================
# 5. AUTHORIZATION TESTS
# ============================================
Write-Host "--- 5. AUTHORIZATION CHECKS ---" -ForegroundColor Magenta

# 5.1 Try to create article without token (should fail)
try {
    $articleBody = @{
        title = "Unauthorized Article"
        description = "Should fail"
        body = "No token provided"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl/api/articles" -Method Post -ContentType "application/json" -Body $articleBody -ErrorAction Stop
    Write-TestResult "Create Article WITHOUT Token (should fail)" $false "Expected 401, got $($response.StatusCode)"
} catch {
    $statusCode = $_.Exception.Response.StatusCode.Value__
    Write-TestResult "Create Article WITHOUT Token (should fail)" ($statusCode -eq 401 -or $statusCode -eq 403) "Correctly rejected with status $statusCode"
}

# 5.2 Try to get current user without token (should fail)
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/user" -Method Get -ErrorAction Stop
    Write-TestResult "Get Current User WITHOUT Token (should fail)" $false "Expected 401, got $($response.StatusCode)"
} catch {
    $statusCode = $_.Exception.Response.StatusCode.Value__
    Write-TestResult "Get Current User WITHOUT Token (should fail)" ($statusCode -eq 401 -or $statusCode -eq 403) "Correctly rejected with status $statusCode"
}

Write-Host ""

# ============================================
# 6. CLEANUP - Delete Article
# ============================================
Write-Host "--- 6. CLEANUP ---" -ForegroundColor Magenta

try {
    $headers = @{ Authorization = "Bearer $accessToken" }
    $response = Invoke-WebRequest -Uri "$baseUrl/api/articles/$articleSlug" -Method Delete -Headers $headers -ErrorAction Stop
    Write-TestResult "Delete Article (DELETE /api/articles/$articleSlug)" ($response.StatusCode -eq 200 -or $response.StatusCode -eq 204) "Article deleted"
} catch {
    Write-TestResult "Delete Article (DELETE /api/articles/$articleSlug)" $false $_.Exception.Message
}

Write-Host ""

# ============================================
# SUMMARY
# ============================================
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Passed: $passed" -ForegroundColor Green
Write-Host "  Failed: $failed" -ForegroundColor Red
Write-Host "  Total:  $($passed + $failed)" -ForegroundColor White
Write-Host ""

if ($failed -eq 0) {
    Write-Host "  ALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "  SOME TESTS FAILED!" -ForegroundColor Red
}
Write-Host "============================================" -ForegroundColor Cyan
