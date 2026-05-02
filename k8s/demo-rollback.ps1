# SE359 — Script demo rollback trên Kubernetes
# Cách dùng: .\k8s\demo-rollback.ps1

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  SE359 — Demo Rollback Kubernetes" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# ----------------------------------------------------------
# Bước 1: Xem trạng thái hiện tại
# ----------------------------------------------------------
Write-Host ""
Write-Host "[1/5] Trạng thái hiện tại:" -ForegroundColor Yellow
kubectl get pods -n se359 -l app=backend
Write-Host ""
kubectl rollout history deployment/backend -n se359

# ----------------------------------------------------------
# Bước 2: Cố tình deploy version lỗi
# ----------------------------------------------------------
Write-Host ""
Write-Host "[2/5] Deploy version LỖI (image không tồn tại)..." -ForegroundColor Red
kubectl set image deployment/backend backend=se359-backend:broken-v999 -n se359

Write-Host "  ⏳ Đợi 10 giây để thấy pod fail..."
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "--- Pods sau khi deploy lỗi ---" -ForegroundColor Red
kubectl get pods -n se359 -l app=backend

# ----------------------------------------------------------
# Bước 3: Xem sự kiện lỗi
# ----------------------------------------------------------
Write-Host ""
Write-Host "[3/5] Sự kiện lỗi:" -ForegroundColor Red
kubectl get events -n se359 --sort-by='.lastTimestamp' | Select-Object -Last 5

# ----------------------------------------------------------
# Bước 4: Rollback
# ----------------------------------------------------------
Write-Host ""
Write-Host "[4/5] ROLLBACK về version trước..." -ForegroundColor Green
kubectl rollout undo deployment/backend -n se359

Write-Host "  ⏳ Đợi pods recovery..."
kubectl wait --for=condition=ready pod -l app=backend -n se359 --timeout=120s

# ----------------------------------------------------------
# Bước 5: Verify
# ----------------------------------------------------------
Write-Host ""
Write-Host "[5/5] Pods sau rollback:" -ForegroundColor Green
kubectl get pods -n se359 -l app=backend

Write-Host ""
Write-Host "--- Rollout history ---" -ForegroundColor Cyan
kubectl rollout history deployment/backend -n se359

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  ✅ ROLLBACK THÀNH CÔNG!" -ForegroundColor Green
Write-Host "  App đã quay về version ổn định." -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Green
