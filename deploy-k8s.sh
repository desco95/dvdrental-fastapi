#!/bin/bash
# deploy-k8s.sh - Script de despliegue automático en Kubernetes

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  DVD Rental - Kubernetes Deployment${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# Verificar Minikube
echo -e "${YELLOW}📋 Checking Minikube...${NC}"
if ! minikube status > /dev/null 2>&1; then
    echo -e "${YELLOW}Starting Minikube...${NC}"
    minikube start --driver=docker --memory=4096 --cpus=2
fi
echo -e "${GREEN}✓ Minikube running${NC}"
echo ""

# Habilitar Ingress
echo -e "${YELLOW}📋 Enabling Ingress addon...${NC}"
minikube addons enable ingress
minikube addons enable metrics-server
echo -e "${GREEN}✓ Addons enabled${NC}"
echo ""

# Aplicar manifiestos
echo -e "${YELLOW}🚀 Deploying to Kubernetes...${NC}"
echo ""

echo -e "${BLUE}[1/6]${NC} Creating namespace..."
kubectl apply -f k8s/namespace.yaml

echo -e "${BLUE}[2/6]${NC} Applying ConfigMap..."
kubectl apply -f k8s/configmap.yaml

echo -e "${BLUE}[3/6]${NC} Applying Secrets..."
kubectl apply -f k8s/secret.yaml

echo -e "${BLUE}[4/6]${NC} Creating PersistentVolume..."
kubectl apply -f k8s/postgres-pv.yaml

echo -e "${BLUE}[5/6]${NC} Deploying PostgreSQL..."
kubectl apply -f k8s/postgres-deployment.yaml
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
kubectl wait --for=condition=ready pod \
  -l app=postgres \
  -n dvdrental \
  --timeout=300s
echo -e "${GREEN}✓ PostgreSQL ready${NC}"

echo -e "${BLUE}[6/6]${NC} Deploying API..."
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/ingress.yaml
echo -e "${YELLOW}⏳ Waiting for API to be ready...${NC}"
kubectl wait --for=condition=ready pod \
  -l app=dvdrental-api \
  -n dvdrental \
  --timeout=300s
echo -e "${GREEN}✓ API ready${NC}"
echo ""

# Mostrar estado
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Deployment Status${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""
kubectl get all -n dvdrental
echo ""
kubectl get ingress -n dvdrental
echo ""

# Obtener URL
MINIKUBE_IP=$(minikube ip)
API_URL="http://$MINIKUBE_IP:30800"

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Deployment Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}🌐 Access URLs:${NC}"
echo -e "  Direct access:  $API_URL"
echo -e "  With domain:    http://dvdrental.local (requires hosts file)"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo ""
echo -e "1. Start Minikube tunnel (in another terminal):"
echo -e "   ${GREEN}minikube tunnel${NC}"
echo ""
echo -e "2. Add to /etc/hosts (or C:\\Windows\\System32\\drivers\\etc\\hosts):"
echo -e "   ${GREEN}$MINIKUBE_IP dvdrental.local${NC}"
echo ""
echo -e "3. Test the API:"
echo -e "   ${GREEN}curl $API_URL${NC}"
echo -e "   ${GREEN}curl http://dvdrental.local${NC}"
echo ""
echo -e "4. View logs:"
echo -e "   ${GREEN}kubectl logs -f -l app=dvdrental-api -n dvdrental${NC}"
echo ""
echo -e "5. Open dashboard:"
echo -e "   ${GREEN}minikube dashboard${NC}"
echo ""
echo -e "6. Run tests:"
echo -e "   ${GREEN}API_URL=$API_URL ./test-api.sh${NC}"
echo ""