# Cleanup Script - Remove Results Folder
# This script removes the deprecated results folder
# All data is now stored in Firebase Realtime Database

Write-Host "🧹 NeoxSecBot Cleanup Script" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

$resultsFolder = "results"

if (Test-Path $resultsFolder) {
    Write-Host "📁 Found results folder: $resultsFolder" -ForegroundColor Yellow
    Write-Host "⚠️  This folder is no longer needed (using Firebase now)" -ForegroundColor Yellow
    Write-Host ""
    
    $confirmation = Read-Host "Delete results folder? (y/n)"
    
    if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
        try {
            Remove-Item -Path $resultsFolder -Recurse -Force
            Write-Host "✅ Results folder deleted successfully!" -ForegroundColor Green
            Write-Host "💾 All data is now stored in Firebase only" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Error deleting folder: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "❌ Cleanup cancelled" -ForegroundColor Yellow
    }
}
else {
    Write-Host "✅ Results folder not found (already clean)" -ForegroundColor Green
    Write-Host "💾 Bot is using Firebase-only storage" -ForegroundColor Green
}

Write-Host ""
Write-Host "📊 Current Storage Configuration:" -ForegroundColor Cyan
Write-Host "  • Chat History: Firebase Realtime Database" -ForegroundColor White
Write-Host "  • Scan Results: Firebase Realtime Database" -ForegroundColor White
Write-Host "  • User Data: Firebase Realtime Database" -ForegroundColor White
Write-Host "  • Local Storage: None (Firebase only)" -ForegroundColor White
Write-Host ""
Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host ""

Pause
