#!/bin/bash

# QuantaEnergi E2E Testing Automation Script
# This script automates the E2E testing process for the QuantaEnergi application

set -e  # Exit on any error

echo "🚀 Starting QuantaEnergi E2E Testing Automation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_DIR="frontend"
BACKEND_DIR="backend"
CYPRESS_CONFIG="cypress.config.js"
TEST_RESULTS_DIR="cypress/results"

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

# Function to check if required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "$CYPRESS_CONFIG" ]; then
        print_error "Cypress configuration not found. Please run this script from the project root."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    cd "$FRONTEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing npm dependencies..."
        npm install
    else
        print_status "Dependencies already installed, checking for updates..."
        npm update
    fi
    
    # Install Cypress if not already installed
    if [ ! -d "node_modules/.bin/cypress" ]; then
        print_status "Installing Cypress..."
        npm install --save-dev cypress
    fi
    
    cd ..
    print_success "Dependencies installed successfully"
}

# Function to start backend server
start_backend() {
    print_status "Starting QuantaEnergi backend server..."
    
    cd "$BACKEND_DIR"
    
    # Check if backend is already running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_warning "Backend server is already running on port 8000"
        cd ..
        return 0
    fi
    
    # Start backend server in background
    print_status "Starting backend server..."
    uvicorn app.main:app --reload --port 8000 --host 0.0.0.0 > backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Wait for backend to be ready
    print_status "Waiting for backend server to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend server is ready"
            cd ..
            return 0
        fi
        sleep 2
        echo -n "."
    done
    
    print_error "Backend server failed to start within 60 seconds"
    kill $BACKEND_PID 2>/dev/null || true
    cd ..
    exit 1
}

# Function to start frontend server
start_frontend() {
    print_status "Starting QuantaEnergi frontend server..."
    
    cd "$FRONTEND_DIR"
    
    # Check if frontend is already running
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_warning "Frontend server is already running on port 3000"
        cd ..
        return 0
    fi
    
    # Start frontend server in background
    print_status "Starting frontend server..."
    npm run dev > frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # Wait for frontend to be ready
    print_status "Waiting for frontend server to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend server is ready"
            cd ..
            return 0
        fi
        sleep 2
        echo -n "."
    done
    
    print_error "Frontend server failed to start within 60 seconds"
    kill $FRONTEND_PID 2>/dev/null || true
    cd ..
    exit 1
}

# Function to run Cypress tests
run_cypress_tests() {
    print_status "Running Cypress E2E tests..."
    
    cd "$FRONTEND_DIR"
    
    # Create results directory
    mkdir -p "$TEST_RESULTS_DIR"
    
    # Run Cypress tests
    print_status "Starting Cypress test runner..."
    
    # Check if running in CI environment
    if [ "$CI" = "true" ]; then
        print_status "Running in CI mode..."
        npx cypress run --config-file "$CYPRESS_CONFIG" --record false --reporter junit --reporter-options "mochaFile=$TEST_RESULTS_DIR/results.xml,toConsole=true"
    else
        print_status "Running in interactive mode..."
        npx cypress open --config-file "$CYPRESS_CONFIG"
    fi
    
    cd ..
    
    if [ $? -eq 0 ]; then
        print_success "Cypress tests completed successfully"
    else
        print_error "Cypress tests failed"
        exit 1
    fi
}

# Function to run specific test suites
run_test_suite() {
    local suite_name="$1"
    print_status "Running $suite_name test suite..."
    
    cd "$FRONTEND_DIR"
    
    case "$suite_name" in
        "auth")
            npx cypress run --spec "cypress/e2e/authentication.cy.js"
            ;;
        "dashboard")
            npx cypress run --spec "cypress/e2e/trading-dashboard.cy.js"
            ;;
        "api")
            npx cypress run --spec "cypress/e2e/api-integration.cy.js"
            ;;
        "all")
            npx cypress run
            ;;
        *)
            print_error "Unknown test suite: $suite_name"
            print_status "Available suites: auth, dashboard, api, all"
            exit 1
            ;;
    esac
    
    cd ..
}

# Function to generate test report
generate_report() {
    print_status "Generating test report..."
    
    if [ -f "$TEST_RESULTS_DIR/results.xml" ]; then
        print_success "Test results available in $TEST_RESULTS_DIR/results.xml"
        
        # Parse and display summary
        if command -v xmllint &> /dev/null; then
            total_tests=$(xmllint --xpath "string(//testsuites/@tests)" "$TEST_RESULTS_DIR/results.xml" 2>/dev/null || echo "0")
            failed_tests=$(xmllint --xpath "string(//testsuites/@failures)" "$TEST_RESULTS_DIR/results.xml" 2>/dev/null || echo "0")
            
            print_status "Test Summary:"
            print_status "  Total Tests: $total_tests"
            print_status "  Failed Tests: $failed_tests"
            print_status "  Passed Tests: $((total_tests - failed_tests))"
        fi
    else
        print_warning "No test results file found"
    fi
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        print_status "Stopping backend server..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        print_status "Stopping frontend server..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Remove log files
    rm -f "$BACKEND_DIR/backend.log" "$FRONTEND_DIR/frontend.log" 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "QuantaEnergi E2E Testing Automation Script"
    echo ""
    echo "Usage: $0 [OPTIONS] [TEST_SUITE]"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help          Show this help message"
    echo "  -i, --install       Install dependencies only"
    echo "  -s, --start         Start servers only"
    echo "  -t, --test          Run tests only (requires servers to be running)"
    echo "  -c, --cleanup       Cleanup and stop servers"
    echo "  -r, --report        Generate test report"
    echo ""
    echo "TEST_SUITE:"
    echo "  auth                Run authentication tests only"
    echo "  dashboard           Run trading dashboard tests only"
    echo "  api                 Run API integration tests only"
    echo "  all                 Run all tests (default)"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                  Run complete E2E testing (install, start, test, cleanup)"
    echo "  $0 -i              Install dependencies only"
    echo "  $0 -s              Start servers only"
    echo "  $0 -t dashboard    Run dashboard tests only"
    echo "  $0 -c              Cleanup and stop servers"
}

# Main execution
main() {
    local install_only=false
    local start_only=false
    local test_only=false
    local cleanup_only=false
    local report_only=false
    local test_suite="all"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -i|--install)
                install_only=true
                shift
                ;;
            -s|--start)
                start_only=true
                shift
                ;;
            -t|--test)
                test_only=true
                shift
                ;;
            -c|--cleanup)
                cleanup_only=true
                shift
                ;;
            -r|--report)
                report_only=true
                shift
                ;;
            auth|dashboard|api|all)
                test_suite="$1"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Set trap for cleanup on exit
    trap cleanup EXIT
    
    if [ "$cleanup_only" = true ]; then
        cleanup
        exit 0
    fi
    
    if [ "$report_only" = true ]; then
        generate_report
        exit 0
    fi
    
    if [ "$install_only" = true ]; then
        check_prerequisites
        install_dependencies
        exit 0
    fi
    
    if [ "$start_only" = true ]; then
        check_prerequisites
        start_backend
        start_frontend
        print_success "Servers started successfully"
        print_status "Backend: http://localhost:8000"
        print_status "Frontend: http://localhost:3000"
        print_status "Press Ctrl+C to stop servers"
        
        # Wait for user interrupt
        wait
        exit 0
    fi
    
    if [ "$test_only" = true ]; then
        run_test_suite "$test_suite"
        generate_report
        exit 0
    fi
    
    # Full execution
    check_prerequisites
    install_dependencies
    start_backend
    start_frontend
    
    # Wait a moment for servers to stabilize
    sleep 5
    
    run_cypress_tests
    generate_report
    
    print_success "QuantaEnergi E2E testing completed successfully! 🎉"
}

# Run main function with all arguments
main "$@"
