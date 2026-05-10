# Start the FastAPI backend using the project venv
$venvPython = "$PSScriptRoot\.venv\Scripts\python.exe"
$backendDir  = "$PSScriptRoot\backend"

Write-Host "Starting Alliance RAG backend on http://localhost:8000 ..." -ForegroundColor Cyan
& $venvPython -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --app-dir $backendDir
