#!/bin/bash
# ============================================================
# SE359 — Script triển khai Kubernetes (kind)
# ============================================================
# Cách dùng:
#   chmod +x k8s/deploy.sh
#   ./k8s/deploy.sh
# ============================================================

set -e

echo "=========================================="
echo "  SE359 Kubernetes Deployment Script"
echo "=========================================="

# ----------------------------------------------------------
# Bước 1: Tạo cluster (nếu chưa có)
# ----------------------------------------------------------
echo ""
echo "[1/6] Kiểm tra kind cluster..."
if kind get clusters 2>/dev/null | grep -q "se359"; then
    echo "  ✅ Cluster 'se359' đã tồn tại"
else
    echo "  ⏳ Tạo cluster 'se359'..."
    kind create cluster --config k8s/kind-config.yaml
    echo "  ✅ Cluster đã tạo xong"
fi

# ----------------------------------------------------------
# Bước 2: Build Docker images
# ----------------------------------------------------------
echo ""
echo "[2/6] Build Docker images..."
echo "  ⏳ Building backend..."
docker build -t se359-backend:latest -f backend/Dockerfile .
echo "  ⏳ Building frontend..."
docker build -t se359-frontend:latest --build-arg VITE_API_URL=http://localhost:30088 -f frontend/Dockerfile .
echo "  ✅ Images built"

# ----------------------------------------------------------
# Bước 3: Load images vào kind cluster
# ----------------------------------------------------------
echo ""
echo "[3/6] Load images vào kind cluster..."
kind load docker-image se359-backend:latest --name se359
kind load docker-image se359-frontend:latest --name se359
echo "  ✅ Images loaded"

# ----------------------------------------------------------
# Bước 4: Apply Kubernetes manifests
# ----------------------------------------------------------
echo ""
echo "[4/6] Apply Kubernetes manifests..."

echo "  → namespace"
kubectl apply -f k8s/namespace.yaml

echo "  → configmap & secret"
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

echo "  → PostgreSQL"
kubectl apply -f k8s/postgres/

echo "  ⏳ Đợi PostgreSQL ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n se359 --timeout=120s
echo "  ✅ PostgreSQL ready"

echo "  → Backend"
kubectl apply -f k8s/backend/

echo "  → Frontend"
kubectl apply -f k8s/frontend/

# ----------------------------------------------------------
# Bước 5: Đợi tất cả pods ready
# ----------------------------------------------------------
echo ""
echo "[5/6] Đợi tất cả pods ready..."
kubectl wait --for=condition=ready pod -l app=backend -n se359 --timeout=180s
kubectl wait --for=condition=ready pod -l app=frontend -n se359 --timeout=120s
echo "  ✅ Tất cả pods đã ready"

# ----------------------------------------------------------
# Bước 6: Hiển thị trạng thái
# ----------------------------------------------------------
echo ""
echo "[6/6] Trạng thái cluster:"
echo ""
echo "--- Pods ---"
kubectl get pods -n se359 -o wide
echo ""
echo "--- Services ---"
kubectl get svc -n se359
echo ""
echo "--- Deployments ---"
kubectl get deployments -n se359
echo ""
echo "=========================================="
echo "  ✅ DEPLOY THÀNH CÔNG!"
echo ""
echo "  Frontend:  http://localhost:30080"
echo "  Backend:   kubectl port-forward svc/backend-service 8000:8000 -n se359"
echo "=========================================="
