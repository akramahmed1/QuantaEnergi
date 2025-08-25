#!/bin/bash

# EnergyOpti-Pro Deployment Script
# This script deploys the application to Render, Railway, and Vercel

set -e

echo "🚀 Starting EnergyOpti-Pro Deployment..."

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

# Check if required tools are installed
check_requirements() {
    print_status "Checking deployment requirements..."
    
    # Check for Git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    # Check for Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Check for npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    # Check for Vercel CLI
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI is not installed. Installing now..."
        npm install -g vercel
    fi
    
    # Check for Railway CLI
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI is not installed. Installing now..."
        npm install -g @railway/cli
    fi
    
    print_success "All requirements are met!"
}

# Deploy to Render
deploy_render() {
    print_status "Deploying to Render..."
    
    if [ ! -f "render.yaml" ]; then
        print_error "render.yaml not found!"
        exit 1
    fi
    
    # Check if Render CLI is installed
    if ! command -v render &> /dev/null; then
        print_warning "Render CLI not found. Please install it from https://render.com/docs/cli"
        print_status "You can deploy manually by pushing to your Git repository connected to Render."
        return
    fi
    
    # Deploy using Render CLI
    render deploy --service energyopti-pro-backend
    
    print_success "Render deployment initiated!"
}

# Deploy to Railway
deploy_railway() {
    print_status "Deploying to Railway..."
    
    if [ ! -f "railway.json" ]; then
        print_error "railway.json not found!"
        exit 1
    fi
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI not found. Please install it first: npm install -g @railway/cli"
        print_status "You can deploy manually by pushing to your Git repository connected to Railway."
        return
    fi
    
    # Login to Railway (if not already logged in)
    railway login
    
    # Deploy to Railway
    railway up
    
    print_success "Railway deployment initiated!"
}

# Deploy frontend to Vercel
deploy_vercel() {
    print_status "Deploying frontend to Vercel..."
    
    cd frontend
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        print_error "package.json not found in frontend directory!"
        exit 1
    fi
    
    # Install dependencies
    print_status "Installing frontend dependencies..."
    npm install
    
    # Build the project
    print_status "Building frontend..."
    npm run build
    
    # Deploy to Vercel
    print_status "Deploying to Vercel..."
    vercel --prod
    
    cd ..
    
    print_success "Vercel deployment completed!"
}

# Main deployment function
main() {
    print_status "Starting EnergyOpti-Pro deployment process..."
    
    # Check requirements
    check_requirements
    
    # Ask user which platforms to deploy to
    echo ""
    echo "Which platforms would you like to deploy to?"
    echo "1. Render (Backend)"
    echo "2. Railway (Backend)"
    echo "3. Vercel (Frontend)"
    echo "4. All platforms"
    echo "5. Exit"
    echo ""
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            deploy_render
            ;;
        2)
            deploy_railway
            ;;
        3)
            deploy_vercel
            ;;
        4)
            deploy_render
            deploy_railway
            deploy_vercel
            ;;
        5)
            print_status "Deployment cancelled."
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please enter a number between 1-5."
            exit 1
            ;;
    esac
    
    print_success "Deployment process completed!"
    echo ""
    print_status "Next steps:"
    echo "1. Set up environment variables in your deployment platforms"
    echo "2. Configure custom domains if needed"
    echo "3. Set up monitoring and logging"
    echo "4. Test the deployed application"
}

# Run main function
main "$@"
