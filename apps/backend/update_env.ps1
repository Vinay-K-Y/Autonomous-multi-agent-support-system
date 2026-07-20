# Script to update .env file for local OpenAI-compatible LLM
$envPath = ".env"

# Check if .env exists
if (-not (Test-Path $envPath)) {
    Write-Host "Creating new .env file..."
    New-Item -Path $envPath -ItemType File | Out-Null
}

# Read existing content
$content = Get-Content $envPath -ErrorAction SilentlyContinue
if ($null -eq $content) { $content = @() }

# Update or add LLM configuration
$updated = $false
$newContent = @()

foreach ($line in $content) {
    if ($line -match "^LLM_PROVIDER=") {
        $newContent += "LLM_PROVIDER=openai"
        $updated = $true
    }
    elseif ($line -match "^OPENAI_API_KEY=") {
        $newContent += "OPENAI_API_KEY=ollama"
        $updated = $true
    }
    elseif ($line -match "^OPENAI_BASE_URL=") {
        $newContent += "OPENAI_BASE_URL=http://localhost:11435/v1"
        $updated = $true
    }
    elseif ($line -match "^MODEL_NAME=") {
        $newContent += "MODEL_NAME=llama3"
        $updated = $true
    }
    else {
        $newContent += $line
    }
}

# Add missing configurations
$newContent += ""
$newContent += "# OpenAI-compatible LLM Configuration"
$newContent += "OPENAI_API_KEY=ollama"
$newContent += "OPENAI_BASE_URL=http://localhost:11434/v1"
$newContent += ""
$newContent += "# Database Configuration"
$newContent += "DATABASE_URL=postgresql+asyncpg://support_user:support_password@localhost:5432/support_system"
$newContent += ""
$newContent += "# Redis Configuration"
$newContent += "REDIS_URL=redis://localhost:6379/0"
$newContent += ""
$newContent += "# Rate Limiting Configuration"
$newContent += "RATE_LIMIT_ENABLED=true"
$newContent += "RATE_LIMIT_REQUESTS=100"
$newContent += "RATE_LIMIT_PERIOD=60"

# Write back to file
Set-Content -Path $envPath -Value $newContent
Write-Host ".env file updated successfully!"
Write-Host ""
Write-Host "Updated configuration:"
Write-Host "  LLM_PROVIDER=openai"
Write-Host "  OPENAI_API_KEY=ollama"
Write-Host "  OPENAI_BASE_URL=http://localhost:11435/v1"
Write-Host "  MODEL_NAME=llama3"
Write-Host ""
Write-Host "Please restart your server to apply changes."
