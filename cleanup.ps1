# Cleanup script for Omnius project (PowerShell version)

Write-Host "This script will remove redundant files after reorganization." -ForegroundColor Yellow
Write-Host "Make sure you've backed up anything important before proceeding." -ForegroundColor Yellow
$confirm = Read-Host "Continue? (y/n)"

if ($confirm -ne "y") {
    Write-Host "Cleanup cancelled." -ForegroundColor Red
    exit 0
}

# Remove redundant Docker files (now moved to docker/ directory)
Write-Host "Removing redundant Docker files..." -ForegroundColor Cyan
Remove-Item -Path "Dockerfile.ml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "Dockerfile.simple" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "docker-compose.ml.yml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "docker-compose.simple.yml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "docker-compose.dev.yml" -Force -ErrorAction SilentlyContinue

# Remove redundant requirements files
Write-Host "Removing redundant requirements files..." -ForegroundColor Cyan
Remove-Item -Path "requirements.ml.embeddings.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "requirements.ml.vectordb.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "requirements.ml.llm.txt" -Force -ErrorAction SilentlyContinue

# Remove redundant documentation (now consolidated)
Write-Host "Removing redundant documentation files..." -ForegroundColor Cyan
Remove-Item -Path "BUILD_INFO.md" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "PREBUILT.md" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "ML_BUILD_GUIDE.md" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "DOCKER_OPTIMIZATION.md" -Force -ErrorAction SilentlyContinue

# Remove redundant build script
Write-Host "Removing redundant build script..." -ForegroundColor Cyan
Remove-Item -Path "build_ml.ps1" -Force -ErrorAction SilentlyContinue

# Remove original Docker files (now in docker/ directory)
Write-Host "Removing original Docker files (copied to docker/ directory)..." -ForegroundColor Cyan
Remove-Item -Path "Dockerfile" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "docker-compose.yml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "docker-compose.build.yml" -Force -ErrorAction SilentlyContinue

Write-Host "Cleanup complete! The project structure is now more organized." -ForegroundColor Green
Write-Host "All essential files are preserved in their appropriate locations." -ForegroundColor Green 