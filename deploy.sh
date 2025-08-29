#!/bin/bash

# EnergyOpti-Pro Deployment Script
# This script automates the deployment process for local verification and cloud deployment

set -e

echo "🚀 EnergyOpti-Pro Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Local verification with Docker Compose
local_verification() {
    print_status "Starting local verification with Docker Compose..."
    
    # Build and start services
    docker-compose up --build -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check if backend is responding
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        print_success "Backend is responding at http://localhost:8000"
    else
        print_error "Backend is not responding. Check logs with: docker-compose logs backend"
        exit 1
    fi
    
    # Check if database is accessible
    if docker-compose exec db pg_isready -U energyopti_pro_user > /dev/null 2>&1; then
        print_success "Database is accessible"
    else
        print_error "Database is not accessible"
        exit 1
    fi
    
    # Check if Redis is accessible
    if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is accessible"
    else
        print_error "Redis is not accessible"
        exit 1
    fi
    
    print_success "Local verification completed successfully!"
    print_status "Services available at:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Database: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo ""
    print_status "View logs with: docker-compose logs -f"
    print_status "Stop services with: docker-compose down"
}

# Deploy to Render
deploy_render() {
    print_status "Deploying to Render..."
    
    if ! command -v render &> /dev/null; then
        print_error "Render CLI is not installed. Please install it first:"
        echo "  https://render.com/docs/install-cli"
        exit 1
    fi
    
    print_status "Please ensure you have:"
    echo "  1. Render CLI installed and authenticated"
    echo "  2. A Render account with a service created"
    echo "  3. Environment variables configured in Render dashboard"
    echo ""
    
    read -p "Press Enter to continue with Render deployment..."
    
    # Deploy using render.yaml
    render deploy
    
    print_success "Deployment to Render completed!"
}

# Deploy to Vercel (Frontend)
deploy_vercel() {
    print_status "Deploying frontend to Vercel..."
    
    if ! command -v vercel &> /dev/null; then
        print_error "Vercel CLI is not installed. Please install it first:"
        echo "  npm i -g vercel"
        exit 1
    fi
    
    cd frontend
    
    print_status "Please ensure you have:"
    echo "  1. Vercel CLI installed and authenticated"
    echo "  2. A Vercel account with a project created"
    echo "  3. Environment variables configured in Vercel dashboard"
    echo ""
    
    read -p "Press Enter to continue with Vercel deployment..."
    
    # Deploy to Vercel
    vercel --prod
    
    print_success "Frontend deployment to Vercel completed!"
    cd ..
}

# Main deployment menu
main() {
    echo ""
    echo "Choose deployment option:"
    echo "1) Local verification with Docker Compose"
    echo "2) Deploy backend to Render"
    echo "3) Deploy frontend to Vercel"
    echo "4) Full deployment (local + cloud)"
    echo "5) Exit"
    echo ""
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            check_docker
            local_verification
            ;;
        2)
            deploy_render
            ;;
        3)
            deploy_vercel
            ;;
        4)
            check_docker
            local_verification
            echo ""
            deploy_render
            echo ""
            deploy_vercel
            ;;
        5)
            print_status "Exiting deployment script"
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please enter 1-5"
            main
            ;;
    esac
}

# Run main function
main
