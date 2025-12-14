$ErrorActionPreference = "Stop"

# --- Configuration ---
$BaseUrl = "http://localhost"
$UserEmail = "testuser_$(Get-Random)@example.com"
$UserPassword = "password123"
$Username = "testuser_$(Get-Random)"
$ArticleTitle = "Test Article $(Get-Random)"
$ArticleSlug = "" # Will be populated
$ArticleId = 0 # Will be populated
$CommentId = 0 # Will be populated

# --- Helper Functions ---
function Invoke-ApiRequest {
    param (
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers = @{},
        [string]$Body = $null,
        [int[]]$ExpectedStatus = @(200, 201, 204)
    )

    Write-Host "[$Method] $Url" -NoNewline
    
    try {
        $params = @{
            Method = $Method
            Uri = $Url
            Headers = $Headers
            ContentType = "application/json"
        }
        if ($Body) { $params.Body = $Body }

        $response = Invoke-RestMethod @params
        
        Write-Host " - OK" -ForegroundColor Green
        return $response

    } catch {
        # Handle HTTP Errors (4xx, 5xx)
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            $stream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $responseBody = $reader.ReadToEnd()
            
            if ($ExpectedStatus -contains $statusCode) {
                Write-Host " - OK ($statusCode)" -ForegroundColor Green
                try {
                    return $responseBody | ConvertFrom-Json
                } catch {
                    return $responseBody
                }
            } else {
                Write-Host " - FAILED ($statusCode)" -ForegroundColor Red
                Write-Host "Response Body: '$responseBody'"
                throw "Request failed with status $statusCode"
            }
        } else {
            Write-Host " - ERROR: $($_.Exception.Message)" -ForegroundColor Red
            throw $_
        }
    }
}

# --- Test Scenario ---

Write-Host "`n=== Starting End-to-End Test ===`n" -ForegroundColor Cyan

# 0. Check Health/Docs
Write-Host "0. Checking Users Service Docs..." -ForegroundColor Yellow
try {
    $docs = Invoke-WebRequest -Uri "$BaseUrl/users/docs" -Method Head
    Write-Host " - OK ($($docs.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host " - FAILED to reach /users/docs" -ForegroundColor Red
}

# 1. Register User
Write-Host "1. Registering User..." -ForegroundColor Yellow
$registerBody = @{
    email = $UserEmail
    username = $Username
    password = $UserPassword
} | ConvertTo-Json

$user = Invoke-ApiRequest -Method POST -Url "$BaseUrl/api/users" -Body $registerBody -ExpectedStatus 201
Write-Host "Registered User ID: $($user.id)" -ForegroundColor Gray

# 2. Login
Write-Host "2. Logging in..." -ForegroundColor Yellow
$loginBody = "username=$Username&password=$UserPassword"
try {
    $tokenResponse = Invoke-RestMethod -Method POST -Uri "$BaseUrl/api/users/login" -Body $loginBody -ContentType "application/x-www-form-urlencoded"
    $Token = $tokenResponse.access_token
    Write-Host " - OK" -ForegroundColor Green
} catch {
    Write-Host " - FAILED" -ForegroundColor Red
    throw $_
}

$AuthHeader = @{ Authorization = "Bearer $Token" }

if (-not $Token) { throw "Failed to get access token" }
Write-Host "Token received." -ForegroundColor Green

# 3. Get Current User
Write-Host "3. Getting Current User Profile..." -ForegroundColor Yellow
$userProfile = Invoke-ApiRequest -Method GET -Url "$BaseUrl/api/user" -Headers $AuthHeader
if ($userProfile.email -ne $UserEmail) { 
    Write-Warning "User profile email mismatch. Expected $UserEmail, got $($userProfile.email)"
}

# 4. Create Article
Write-Host "4. Creating Article..." -ForegroundColor Yellow
$articleBody = @{
    title = $ArticleTitle
    description = "Test Description"
    body = "Test Body"
    tagList = @("test", "powershell")
} | ConvertTo-Json

$article = Invoke-ApiRequest -Method POST -Url "$BaseUrl/api/articles" -Headers $AuthHeader -Body $articleBody -ExpectedStatus 201
$ArticleSlug = $article.slug
$ArticleId = $article.id
Write-Host "Article created: $ArticleSlug (ID: $ArticleId)" -ForegroundColor Green

# 5. Get Article
Write-Host "5. Getting Article by Slug..." -ForegroundColor Yellow
$fetchedArticle = Invoke-ApiRequest -Method GET -Url "$BaseUrl/api/articles/$ArticleSlug"
if ($fetchedArticle.title -ne $ArticleTitle) { throw "Article title mismatch" }

# 6. Create Comment
Write-Host "6. Creating Comment..." -ForegroundColor Yellow
$commentBody = @{
    body = "Test Comment from PowerShell"
} | ConvertTo-Json

$comment = Invoke-ApiRequest -Method POST -Url "$BaseUrl/api/articles/$ArticleSlug/comments" -Headers $AuthHeader -Body $commentBody -ExpectedStatus 201
$CommentId = $comment.id
Write-Host "Comment created (ID: $CommentId)" -ForegroundColor Green

# 7. List Comments
Write-Host "7. Listing Comments..." -ForegroundColor Yellow
$comments = Invoke-ApiRequest -Method GET -Url "$BaseUrl/api/articles/$ArticleSlug/comments"
if ($comments.Count -eq 0) { throw "No comments found" }

# 8. Delete Comment
Write-Host "8. Deleting Comment..." -ForegroundColor Yellow
Invoke-ApiRequest -Method DELETE -Url "$BaseUrl/api/articles/$ArticleSlug/comments/$CommentId" -Headers $AuthHeader -ExpectedStatus 204 | Out-Null

# 9. Delete Article
Write-Host "9. Deleting Article..." -ForegroundColor Yellow
Invoke-ApiRequest -Method DELETE -Url "$BaseUrl/api/articles/$ArticleSlug" -Headers $AuthHeader -ExpectedStatus 204 | Out-Null

Write-Host "`n=== All Tests Passed Successfully! ===`n" -ForegroundColor Cyan
