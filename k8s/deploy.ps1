# SE359 — Script triển khai Kubernetes (kind) cho Windows PowerShell
# Cách dùng: .\k8s\deploy.ps1

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  SE359 Kubernetes Deployment Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# ----------------------------------------------------------
# Bước 1: Tạo cluster (nếu chưa có)
# ----------------------------------------------------------
Write-Host ""
Write-Host "[1/6] Kiểm tra kind cluster..." -ForegroundColor Yellow

$clusters = kind get clusters 2>$null
if ($clusters -match "se359") {
    Write-Host "  ✅ Cluster 'se359' đã tồn tại" -ForegroundColor Green
} else {
    Write-Host "  ⏳ Tạo cluster 'se359'..." -ForegroundColor Yellow
    kind create cluster --config k8s/kind-config.yaml
    Write-Host "  ✅ Cluster đã tạo xong" -ForegroundColor Green
}

# ----------------------------------------------------------
# Bước 2: Build Docker images
# ----------------------------------------------------------
Write-Host ""
Write-Host "[2/6] Build Docker images..." -ForegroundColor Yellow

Write-Host "  ⏳ Building backend..."
docker build -t se359-backend:latest -f backend/Dockerfile .

Write-Host "  ⏳ Building frontend..."
docker build -t se359-frontend:latest --build-arg VITE_API_URL=http://localhost:30088 -f frontend/Dockerfile .

Write-Host "  ✅ Images built" -ForegroundColor Green

# ----------------------------------------------------------
# Bước 3: Load images vào kind cluster
# ----------------------------------------------------------
Write-Host ""
Write-Host "[3/6] Load images vào kind cluster..." -ForegroundColor Yellow

kind load docker-image se359-backend:latest --name se359
kind load docker-image se359-frontend:latest --name se359

Write-Host "  ✅ Images loaded" -ForegroundColor Green

# ----------------------------------------------------------
# Bước 4: Apply Kubernetes manifests
# ----------------------------------------------------------
Write-Host ""
Write-Host "[4/6] Apply Kubernetes manifests..." -ForegroundColor Yellow

Write-Host "  → namespace"
kubectl apply -f k8s/namespace.yaml

Write-Host "  → configmap & secret"
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

Write-Host "  → PostgreSQL"
kubectl apply -f k8s/postgres/

Write-Host "  ⏳ Đợi PostgreSQL ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n se359 --timeout=120s
Write-Host "  ✅ PostgreSQL ready" -ForegroundColor Green

Write-Host "  → Backend"
kubectl apply -f k8s/backend/

Write-Host "  → Frontend"
kubectl apply -f k8s/frontend/

# ----------------------------------------------------------
# Bước 5: Đợi tất cả pods ready
# ----------------------------------------------------------
Write-Host ""
Write-Host "[5/6] Đợi tất cả pods ready..." -ForegroundColor Yellow

kubectl wait --for=condition=ready pod -l app=backend -n se359 --timeout=180s
kubectl wait --for=condition=ready pod -l app=frontend -n se359 --timeout=120s

Write-Host "  ✅ Tất cả pods đã ready" -ForegroundColor Green

# ----------------------------------------------------------
# Bước 6: Hiển thị trạng thái
# ----------------------------------------------------------
Write-Host ""
Write-Host "[6/6] Trạng thái cluster:" -ForegroundColor Yellow

Write-Host ""
Write-Host "--- Pods ---" -ForegroundColor Cyan
kubectl get pods -n se359 -o wide

Write-Host ""
Write-Host "--- Services ---" -ForegroundColor Cyan
kubectl get svc -n se359

Write-Host ""
Write-Host "--- Deployments ---" -ForegroundColor Cyan
kubectl get deployments -n se359

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOY THÀNH CÔNG!" -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host "  Frontend:  http://localhost:30080" -ForegroundColor White
Write-Host "  Backend:   kubectl port-forward svc/backend-service 8000:8000 -n se359" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Green
