# Smart Contract Security Audit Script for Windows

Write-Host "Starting Smart Contract Security Audit..."

# Create reports directory
New-Item -ItemType Directory -Force -Path "audit-reports" | Out-Null

# 1. Static Analysis with Slither (if installed)
Write-Host "1. Running Slither static analysis..."
if (Get-Command slither -ErrorAction SilentlyContinue) {
    slither . --json audit-reports/slither-report.json
    Write-Host "Slither report saved to audit-reports/slither-report.json"
} else {
    Write-Host "Slither not found. Install with: pip3 install slither-analyzer"
}

# 2. Check for common vulnerabilities
Write-Host "2. Checking for common vulnerabilities..."

# Check for reentrancy vulnerabilities
Write-Host "Checking for reentrancy vulnerabilities..."
Select-String -Path "contracts/*.sol" -Pattern "call|send|transfer" | Where-Object { $_.Line -notmatch "nonReentrant|//" }

# Check for integer overflow/underflow (without SafeMath in Solidity 0.8+)
Write-Host "Checking for integer overflow/underflow protection..."
Select-String -Path "contracts/*.sol" -Pattern "unchecked" -ErrorAction SilentlyContinue | Out-Null
if ($?) {
    Write-Host "Unchecked arithmetic blocks found - review manually"
} else {
    Write-Host "No unchecked arithmetic blocks found (Solidity 0.8+ has built-in checks)"
}

# Check for proper access control
Write-Host "Checking for access control implementation..."
Select-String -Path "contracts/*.sol" -Pattern "require|modifier|only" | Where-Object { $_.Line -match "owner|admin|role" }

# 3. Run tests
Write-Host "3. Running contract tests..."
npx hardhat test > audit-reports/test-results.txt
Write-Host "Test results saved to audit-reports/test-results.txt"

Write-Host "Security audit completed. Check audit-reports/ directory for detailed results."