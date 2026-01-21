# Add your IP to Key Vault firewall
# Run this in a NEW PowerShell window

Write-Host "Adding your IP to Key Vault firewall..." -ForegroundColor Cyan

# Get your public IP
$myIp = (Invoke-WebRequest -Uri "https://api.ipify.org").Content.Trim()
Write-Host "Your public IP: $myIp" -ForegroundColor Green

# Connect to Azure if not already connected
try {
    $context = Get-AzContext -ErrorAction Stop
    Write-Host "Already connected to Azure as: $($context.Account.Id)" -ForegroundColor Green
} catch {
    Write-Host "Connecting to Azure..." -ForegroundColor Yellow
    Connect-AzAccount
}

# Add IP to Key Vault network rules
try {
    Write-Host "Adding IP $myIp to Key Vault kv-gcs-dev-gg4a6y..." -ForegroundColor Cyan
    Add-AzKeyVaultNetworkRule -VaultName "kv-gcs-dev-gg4a6y" -IpAddressRange "$myIp/32"
    Write-Host "✓ Successfully added IP to Key Vault firewall" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now run: python migrate_secrets_to_keyvault.py" -ForegroundColor Yellow
} catch {
    Write-Host "✗ Error adding IP to Key Vault: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Use Azure Portal" -ForegroundColor Yellow
    Write-Host "1. Go to https://portal.azure.com" -ForegroundColor White
    Write-Host "2. Navigate to Key Vault: kv-gcs-dev-gg4a6y" -ForegroundColor White
    Write-Host "3. Go to Networking" -ForegroundColor White
    Write-Host "4. Under Firewall, click 'Add existing client IP address' or add: $myIp" -ForegroundColor White
    Write-Host "5. Click Save" -ForegroundColor White
}
