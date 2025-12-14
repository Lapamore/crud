$ErrorActionPreference = "Stop"
$BaseUrl = "http://localhost"

function Get-Token {
    param ($Username, $Password)
    $loginBody = "username=$Username&password=$Password"
    $response = Invoke-RestMethod -Method POST -Uri "$BaseUrl/api/users/login" -Body $loginBody -ContentType "application/x-www-form-urlencoded"
    return $response.access_token
}

function Register-User {
    param ($Username, $Email, $Password)
    $body = @{ email = $Email; username = $Username; password = $Password } | ConvertTo-Json
    try {
        $user = Invoke-RestMethod -Method POST -Uri "$BaseUrl/api/users" -Body $body -ContentType "application/json"
        return $user
    } catch {
        Write-Host "User $Username might already exist. Logging in..." -ForegroundColor Gray
        return $null
    }
}

# 1. Create Author
$AuthorName = "author_$(Get-Random)"
$AuthorPass = "pass123"
$AuthorEmail = "$AuthorName@example.com"
Write-Host "1. Registering Author ($AuthorName)..."
$author = Register-User -Username $AuthorName -Email $AuthorEmail -Password $AuthorPass
if (-not $author) { 
    # If exists, we need to find ID. But for simplicity, let's assume fresh run or unique names.
    # If we can't get ID easily without login, let's login.
    $token = Get-Token -Username $AuthorName -Password $AuthorPass
    $author = Invoke-RestMethod -Method GET -Uri "$BaseUrl/api/user" -Headers @{ Authorization = "Bearer $token" }
    # The response structure might be wrapped.
    if ($author.user) { $author = $author.user } # Handle potential wrapper
}
$AuthorId = $author.id
$AuthorToken = Get-Token -Username $AuthorName -Password $AuthorPass

Write-Host "   Author ID: $AuthorId" -ForegroundColor Green

# 2. Create Subscriber
$SubName = "sub_$(Get-Random)"
$SubPass = "pass123"
$SubEmail = "$SubName@example.com"
Write-Host "2. Registering Subscriber ($SubName)..."
$sub = Register-User -Username $SubName -Email $SubEmail -Password $SubPass
$SubToken = Get-Token -Username $SubName -Password $SubPass

# 3. Subscribe
Write-Host "3. Subscribing $SubName to $AuthorName..."
$subBody = @{ target_user_id = $AuthorId } | ConvertTo-Json
Invoke-RestMethod -Method POST -Uri "$BaseUrl/api/users/subscribe" -Headers @{ Authorization = "Bearer $SubToken" } -Body $subBody -ContentType "application/json"
Write-Host "   Subscribed!" -ForegroundColor Green

# 4. Create Article (Triggers Celery)
Write-Host "4. Author creating article to trigger notification..."
$articleBody = @{
    title = "Celery Test Article $(Get-Random)"
    description = "Testing async tasks"
    body = "This should trigger a notification."
    tagList = @("celery", "test")
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri "$BaseUrl/api/articles" -Headers @{ Authorization = "Bearer $AuthorToken" } -Body $articleBody -ContentType "application/json" | Out-Null
Write-Host "   Article created!" -ForegroundColor Green

Write-Host "`n---------------------------------------------------"
Write-Host "Verification Steps:" -ForegroundColor Cyan
Write-Host "1. Run: docker-compose logs worker"
Write-Host "2. Look for: 'Processing notification for author_id=$AuthorId'"
Write-Host "3. Look for: 'Found 1 subscribers'"
Write-Host "---------------------------------------------------"
