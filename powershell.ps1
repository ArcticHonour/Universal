# Get the current directory of the script
$scriptDir = Get-Location

# Set the script name
$scriptName = "app.py"

# Construct the full path to the script
$scriptPath = Join-Path $scriptDir $scriptName

# Give full permission to the Python script
icacls $scriptPath /grant Everyone:F

# Run the script in the background
Start-Process "python" -ArgumentList $scriptPath -NoNewWindow -RedirectStandardOutput $null -RedirectStandardError $null
