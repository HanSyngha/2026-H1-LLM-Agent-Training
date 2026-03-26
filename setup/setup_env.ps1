# ──────────────────────────────────────────────
# Windows PowerShell 환경 설정 스크립트
#
# 가상환경 생성, 프록시 설정, 패키지 설치를 수행합니다.
# 사용법: powershell -ExecutionPolicy Bypass -File setup\setup_env.ps1
# ──────────────────────────────────────────────

$ErrorActionPreference = "Stop"

# 프로젝트 루트 디렉토리 (이 스크립트의 상위 디렉토리)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 환경 설정을 시작합니다" -ForegroundColor Cyan
Write-Host " 프로젝트 경로: $ProjectRoot" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ──────────────────────────────────────────────
# 1. 프록시 환경 변수 설정
# ──────────────────────────────────────────────
$Proxy = if ($env:HTTP_PROXY) { $env:HTTP_PROXY } else { "http://your-proxy-host:8000" }

$env:HTTP_PROXY = $Proxy
$env:HTTPS_PROXY = $Proxy
$env:http_proxy = $Proxy
$env:https_proxy = $Proxy
$env:NO_PROXY = "localhost,127.0.0.1,.your-company.net"
$env:no_proxy = "localhost,127.0.0.1,.your-company.net"
$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"

Write-Host "[1/4] 프록시 설정 완료: $Proxy" -ForegroundColor Green
Write-Host "       NO_PROXY: $env:NO_PROXY" -ForegroundColor Green

# ──────────────────────────────────────────────
# 2. Python 가상환경 생성
# ──────────────────────────────────────────────
$VenvDir = Join-Path $ProjectRoot ".venv"

if (Test-Path $VenvDir) {
    Write-Host "[2/4] 기존 가상환경이 존재합니다: $VenvDir" -ForegroundColor Yellow
} else {
    Write-Host "[2/4] 가상환경을 생성합니다: $VenvDir" -ForegroundColor Green
    python -m venv $VenvDir
}

# 가상환경 활성화
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
if (-Not (Test-Path $ActivateScript)) {
    Write-Host "오류: 가상환경 활성화 스크립트를 찾을 수 없습니다: $ActivateScript" -ForegroundColor Red
    exit 1
}
& $ActivateScript

$PythonVersion = python --version
Write-Host "       가상환경 활성화 완료 (Python: $PythonVersion)" -ForegroundColor Green

# ──────────────────────────────────────────────
# 3. pip 업그레이드 및 패키지 설치
# ──────────────────────────────────────────────
Write-Host "[3/4] 패키지를 설치합니다..." -ForegroundColor Green

# SSL 검증 비활성화 (사내 프록시 인증서 이슈)
pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"

# pip 먼저 업그레이드
pip install --upgrade pip --proxy $Proxy --quiet

# npm strict-ssl 비활성화 (Node.js 패키지 사용 시)
if (Get-Command npm -ErrorAction SilentlyContinue) {
    npm config set strict-ssl false
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "오류: pip 업그레이드에 실패했습니다." -ForegroundColor Red
    exit 1
}

# requirements.txt에서 패키지 설치
$Requirements = Join-Path $ScriptDir "requirements.txt"

if (-Not (Test-Path $Requirements)) {
    Write-Host "오류: requirements.txt를 찾을 수 없습니다: $Requirements" -ForegroundColor Red
    exit 1
}

pip install -r $Requirements --proxy $Proxy
if ($LASTEXITCODE -ne 0) {
    Write-Host "오류: 패키지 설치에 실패했습니다." -ForegroundColor Red
    exit 1
}

Write-Host "       패키지 설치 완료" -ForegroundColor Green

# ──────────────────────────────────────────────
# 4. Playwright 브라우저(Chromium) 설치
# ──────────────────────────────────────────────
Write-Host "[4/4] Playwright Chromium 브라우저를 설치합니다..." -ForegroundColor Green
playwright install chromium
if ($LASTEXITCODE -ne 0) {
    Write-Host "경고: Playwright 설치에 실패했습니다. 나중에 수동으로 설치하세요." -ForegroundColor Yellow
} else {
    Write-Host "       Playwright 설치 완료" -ForegroundColor Green
}

# ──────────────────────────────────────────────
# 완료 메시지
# ──────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 환경 설정이 완료되었습니다!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " 가상환경 활성화:" -ForegroundColor White
Write-Host "   $VenvDir\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host " 연결 테스트:" -ForegroundColor White
Write-Host "   python setup\test_connection.py" -ForegroundColor Gray
Write-Host ""
Write-Host " .env 파일을 프로젝트 루트에 생성하고" -ForegroundColor White
Write-Host " 게이트웨이 URL과 API 키를 설정하세요." -ForegroundColor White
Write-Host "   copy .env.example .env" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
