# VELYNX API Test Commands (PowerShell)
# Usage: .\scripts\test-api.ps1
# Make sure backend is running first: cd backend; python -m uvicorn app.main:app --reload --port 8000

Write-Host "=== VELYNX API Tests ===" -ForegroundColor Cyan
Write-Host ""

# 1. Health check
Write-Host "1. Health check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "   Status: OK" -ForegroundColor Green
    $health | ConvertTo-Json -Depth 3 | Write-Host
} catch {
    Write-Host "   FAIL: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 2. Query test
Write-Host "2. Query test..." -ForegroundColor Yellow
$body = '{"text": "What is quantum computing?", "session_id": "test-1"}'
try {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method POST -ContentType "application/json" -Body $body
    Write-Host "   Confidence: $($result.confidence)" -ForegroundColor Green
    Write-Host "   Answer: $($result.answer)" -ForegroundColor White
    Write-Host "   Sources: $($result.sources.Count)" -ForegroundColor White
    Write-Host "   Dialogue Act: $($result.dialogue_act)" -ForegroundColor White
} catch {
    Write-Host "   FAIL: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Follow-up test (conversational)
Write-Host "3. Follow-up test (conversational)..." -ForegroundColor Yellow
$body2 = '{"text": "How does it work?", "session_id": "test-1"}'
try {
    $result2 = Invoke-RestMethod -Uri "http://localhost:8000/query" -Method POST -ContentType "application/json" -Body $body2
    Write-Host "   Dialogue Act: $($result2.dialogue_act)" -ForegroundColor Green
    Write-Host "   Answer: $($result2.answer)" -ForegroundColor White
} catch {
    Write-Host "   FAIL: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 4. Streaming test
Write-Host "4. Streaming test (first 2000 chars)..." -ForegroundColor Yellow
try {
    $stream = Invoke-WebRequest -Uri "http://localhost:8000/stream/query?text=What+is+machine+learning&session_id=stream-test" -ContentType "text/event-stream" -TimeoutSec 30
    $stream.Content.Substring(0, [Math]::Min(2000, $stream.Content.Length)) | Write-Host
    Write-Host "   Status: OK" -ForegroundColor Green
} catch {
    Write-Host "   FAIL: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 5. Ops status
Write-Host "5. Ops status..." -ForegroundColor Yellow
try {
    $ops = Invoke-RestMethod -Uri "http://localhost:8000/ops/status" -Method GET
    Write-Host "   Status: OK" -ForegroundColor Green
    $ops | ConvertTo-Json -Depth 3 | Write-Host
} catch {
    Write-Host "   FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
