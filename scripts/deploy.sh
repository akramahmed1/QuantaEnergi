#!/bin/bash
# QuantaEnergi Deployment Script - Local Test & Cloud Deploy
# Usage: ./deploy.sh [local|cloud|test]

set -e

echo "🚀 QuantaEnergi Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Local testing function
test_local() {
    echo -e "${BLUE}🧪 Testing local deployment...${NC}"
    
    # Build Docker image
    echo "📦 Building Docker image..."
    docker build -t quantaenergi-backend ./backend
    
    # Run container in background
    echo "🚀 Starting container..."
    docker run -d --name quantaenergi-test -p 8000:8000 \
        -e DATABASE_URL="sqlite:///app/test.db" \
        -e REDIS_URL="redis://localhost:6379" \
        -e SECRET_KEY="test-secret-key" \
        quantaenergi-backend
    
    # Wait for container to start
    echo "⏳ Waiting for container to start..."
    sleep 10
    
    # Test health endpoint
    echo "🔍 Testing health endpoint..."
    if curl -f http://localhost:8000/health; then
        echo -e "${GREEN}✅ Backend health check passed!${NC}"
    else
        echo -e "${RED}❌ Backend health check failed!${NC}"
        docker logs quantaenergi-test
        exit 1
    fi
    
    # Test dashboard endpoint
    echo "🔍 Testing dashboard endpoint..."
    if curl -f http://localhost:8000/dashboard; then
        echo -e "${GREEN}✅ Dashboard endpoint working!${NC}"
    else
        echo -e "${YELLOW}⚠️  Dashboard endpoint not available (expected for test)${NC}"
    fi
    
    # Cleanup
    echo "🧹 Cleaning up test container..."
    docker stop quantaenergi-test
    docker rm quantaenergi-test
    
    echo -e "${GREEN}🎉 Local test completed successfully!${NC}"
}

# Deploy backend to Railway
deploy_backend() {
    echo -e "${BLUE}📦 Deploying backend to Railway...${NC}"
    cd backend
    
    # Check if railway CLI is installed
    if ! command -v railway &> /dev/null; then
        echo -e "${RED}❌ Railway CLI not found. Install with: npm install -g @railway/cli${NC}"
        exit 1
    fi
    
    # Deploy to Railway
    railway up --detach
    echo -e "${GREEN}✅ Backend deployed to Railway${NC}"
    cd ..
}

# Deploy frontend to Vercel
deploy_frontend() {
    echo -e "${BLUE}🌐 Deploying frontend to Vercel...${NC}"
    cd frontend
    
    # Check if vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        echo -e "${RED}❌ Vercel CLI not found. Install with: npm install -g vercel${NC}"
        exit 1
    fi
    
    # Build frontend
    echo "🔨 Building frontend..."
    npm run build
    
    # Deploy to Vercel
    vercel --prod
    echo -e "${GREEN}✅ Frontend deployed to Vercel${NC}"
    cd ..
}

# Deploy to cloud
deploy_cloud() {
    echo -e "${BLUE}☁️  Starting cloud deployment...${NC}"
    
    # Deploy backend
    deploy_backend
    
    # Wait a bit for backend to be ready
    echo "⏳ Waiting for backend to be ready..."
    sleep 30
    
    # Deploy frontend
    deploy_frontend
    
    echo -e "${GREEN}🎉 Cloud deployment completed successfully!${NC}"
    echo -e "${YELLOW}📝 Next steps:${NC}"
    echo "1. Update CORS_ORIGINS in Railway with your Vercel domain"
    echo "2. Test the deployed application"
    echo "3. Configure environment variables in Railway dashboard"
}

# Show usage
show_usage() {
    echo "Usage: $0 [local|cloud|test]"
    echo ""
    echo "Commands:"
    echo "  local  - Test deployment locally with Docker"
    echo "  cloud  - Deploy to Railway (backend) and Vercel (frontend)"
    echo "  test   - Run local tests and show deployment status"
    echo ""
    echo "Examples:"
    echo "  $0 local    # Test locally"
    echo "  $0 cloud    # Deploy to cloud"
    echo "  $0 test     # Run tests"
}

# Main function
main() {
    case "${1:-test}" in
        "local")
            test_local
            ;;
        "cloud")
            deploy_cloud
            ;;
        "test")
            test_local
            echo ""
            echo -e "${YELLOW}💡 To deploy to cloud, run: $0 cloud${NC}"
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"