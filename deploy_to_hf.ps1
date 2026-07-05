# ==============================================================================
# Project Sahakar — Automated Hugging Face Spaces Deployment Script
# ==============================================================================

Write-Host "🚀 Starting Project Sahakar Backend Deployment to Hugging Face Spaces..." -ForegroundColor Cyan

# 1. Add GitHub Desktop Git to PATH automatically
$gitPath = "C:\Users\sricharan\AppData\Local\GitHubDesktop\app-3.6.2\resources\app\git\cmd"
if (Test-Path $gitPath) {
    $env:PATH += ";$gitPath"
    Write-Host "✅ Found GitHub Desktop Git. Added to PATH." -ForegroundColor Green
} else {
    Write-Host "⚠️ Could not find GitHub Desktop Git at default path. Checking system PATH..." -ForegroundColor Yellow
}

# Verify Git is accessible
try {
    $gitVersion = git --version
    Write-Host "✅ Using: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Git is not installed or not accessible. Please install Git for Windows from https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# 2. Get Hugging Face Token from User
Write-Host ""
Write-Host "🔑 To push to Hugging Face Spaces, you need a User Access Token with WRITE permissions." -ForegroundColor Yellow
Write-Host "👉 Get your token from: https://huggingface.co/settings/tokens" -ForegroundColor Yellow
$hfToken = Read-Host "Paste your Hugging Face Access Token here (e.g. hf_xxxxx)"

if ([string]::IsNullOrWhiteSpace($hfToken)) {
    Write-Host "❌ Error: Token cannot be empty. Aborting deployment." -ForegroundColor Red
    exit 1
}

# 3. Setup Temporary Clone Directory on Desktop
$spaceUrl = "https://sricharansairi:$($hfToken.Trim())@huggingface.co/spaces/sricharansairi/ProjectSahakar"
$targetDir = "C:\Users\sricharan\Desktop\ProjectSahakar_HF_Space"

if (Test-Path $targetDir) {
    Write-Host "🧹 Cleaning up old deployment folder on Desktop..." -ForegroundColor DarkGray
    Remove-Item -Path $targetDir -Recurse -Force
}

Write-Host ""
Write-Host "📥 Cloning Hugging Face Space repository..." -ForegroundColor Cyan
git clone $spaceUrl $targetDir

if (-not (Test-Path $targetDir)) {
    Write-Host "❌ Error: Failed to clone Space. Please check if your Access Token is valid and has WRITE permissions." -ForegroundColor Red
    exit 1
}

# 4. Copy Backend Code into Space Repository
Write-Host "📂 Copying Project Sahakar backend files into Space repository..." -ForegroundColor Cyan
Copy-Item -Path "C:\Users\sricharan\Documents\GitHub\Project-Sahakar\backend\*" -Destination $targetDir -Recurse -Force

# 5. Commit and Push to Hugging Face
Write-Host "⬆️ Committing and pushing Docker container to Hugging Face Spaces..." -ForegroundColor Cyan
Push-Location $targetDir

try {
    git config user.name "sricharansairi"
    git config user.email "sricharansairi@users.noreply.huggingface.co"
    git add .
    git commit -m "Deploy Project Sahakar RAG & Backend Engine (Docker UID 1000)"
    git push origin main
    
    Write-Host ""
    Write-Host "🎉 SUCCESS! Your backend has been pushed to Hugging Face Spaces!" -ForegroundColor Green
    Write-Host "🌐 View your Space live at: https://huggingface.co/spaces/sricharansairi/ProjectSahakar" -ForegroundColor Cyan
    Write-Host "⚠️ REMINDER: Go to Space Settings -> Variables and secrets to add your API keys (GROQ_API_KEY, SUPABASE_URL, etc.)!" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Error during git commit/push: $_" -ForegroundColor Red
} finally {
    Pop-Location
    # Clean up temp directory
    Write-Host "🧹 Cleaning up temporary Desktop directory..." -ForegroundColor DarkGray
    Remove-Item -Path $targetDir -Recurse -Force -ErrorAction SilentlyContinue
}
