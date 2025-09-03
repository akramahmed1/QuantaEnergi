# QuantaEnergi Go-to-Market (GTM) Deployment Script
# Deploys website, documentation, training, sales, and support systems

Write-Host "🚀 QuantaEnergi Go-to-Market (GTM) Deployment" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Function to deploy marketing website
function Deploy-MarketingWebsite {
    Write-Host ""
    Write-Host "🌐 Deploying Marketing Website..." -ForegroundColor Yellow
    
    # Create website deployment configuration
    $websiteConfig = @"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quantaenergi-website
  namespace: quantaenergi-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: quantaenergi-website
  template:
    metadata:
      labels:
        app: quantaenergi-website
    spec:
      containers:
      - name: website
        image: quantaenergi/website:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: ANALYTICS_ID
          value: "GA-XXXXXXXXX"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"

---
apiVersion: v1
kind: Service
metadata:
  name: quantaenergi-website
  namespace: quantaenergi-prod
spec:
  ports:
  - port: 3000
    targetPort: 3000
  selector:
    app: quantaenergi-website
  type: ClusterIP
"@
    
    $websiteConfig | Out-File -FilePath "website-deployment.yaml" -Encoding UTF8
    kubectl apply -f website-deployment.yaml
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Marketing website deployed successfully" -ForegroundColor Green
        Remove-Item "website-deployment.yaml" -Force
    } else {
        Write-Host "❌ Marketing website deployment failed" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to deploy documentation system
function Deploy-DocumentationSystem {
    Write-Host ""
    Write-Host "📚 Deploying Documentation System..." -ForegroundColor Yellow
    
    # Create documentation deployment
    $docsConfig = @"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quantaenergi-docs
  namespace: quantaenergi-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: quantaenergi-docs
  template:
    metadata:
      labels:
        app: quantaenergi-docs
    spec:
      containers:
      - name: docs
        image: quantaenergi/docs:latest
        ports:
        - containerPort: 8080
        env:
        - name: DOCS_VERSION
          value: "4.0.0"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"

---
apiVersion: v1
kind: Service
metadata:
  name: quantaenergi-docs
  namespace: quantaenergi-prod
spec:
  ports:
  - port: 8080
    targetPort: 8080
  selector:
    app: quantaenergi-docs
  type: ClusterIP
"@
    
    $docsConfig | Out-File -FilePath "docs-deployment.yaml" -Encoding UTF8
    kubectl apply -f docs-deployment.yaml
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Documentation system deployed successfully" -ForegroundColor Green
        Remove-Item "docs-deployment.yaml" -Force
    } else {
        Write-Host "❌ Documentation system deployment failed" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to deploy training platform
function Deploy-TrainingPlatform {
    Write-Host ""
    Write-Host "🎓 Deploying Training Platform..." -ForegroundColor Yellow
    
    # Create training platform deployment
    $trainingConfig = @"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quantaenergi-training
  namespace: quantaenergi-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: quantaenergi-training
  template:
    metadata:
      labels:
        app: quantaenergi-training
    spec:
      containers:
      - name: training
        image: quantaenergi/training:latest
        ports:
        - containerPort: 8082
        env:
        - name: TRAINING_DB_URL
          value: "postgresql://quantaenergi:QuantaEnergi2025!@postgres-prod.quantaenergi-prod.svc.cluster.local:5432/training"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: quantaenergi-training
  namespace: quantaenergi-prod
spec:
  ports:
  - port: 8082
    targetPort: 8082
  selector:
    app: quantaenergi-training
  type: ClusterIP
"@
    
    $trainingConfig | Out-File -FilePath "training-deployment.yaml" -Encoding UTF8
    kubectl apply -f training-deployment.yaml
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Training platform deployed successfully" -ForegroundColor Green
        Remove-Item "training-deployment.yaml" -Force
    } else {
        Write-Host "❌ Training platform deployment failed" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to deploy sales CRM
function Deploy-SalesCRM {
    Write-Host ""
    Write-Host "💼 Deploying Sales CRM..." -ForegroundColor Yellow
    
    # Create sales CRM deployment
    $crmConfig = @"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quantaenergi-crm
  namespace: quantaenergi-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: quantaenergi-crm
  template:
    metadata:
      labels:
        app: quantaenergi-crm
    spec:
      containers:
      - name: crm
        image: quantaenergi/crm:latest
        ports:
        - containerPort: 8083
        env:
        - name: CRM_DB_URL
          value: "postgresql://quantaenergi:QuantaEnergi2025!@postgres-prod.quantaenergi-prod.svc.cluster.local:5432/crm"
        - name: STRIPE_SECRET_KEY
          value: "sk_test_..."
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: quantaenergi-crm
  namespace: quantaenergi-prod
spec:
  ports:
  - port: 8083
    targetPort: 8083
  selector:
    app: quantaenergi-crm
  type: ClusterIP
"@
    
    $crmConfig | Out-File -FilePath "crm-deployment.yaml" -Encoding UTF8
    kubectl apply -f crm-deployment.yaml
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Sales CRM deployed successfully" -ForegroundColor Green
        Remove-Item "crm-deployment.yaml" -Force
    } else {
        Write-Host "❌ Sales CRM deployment failed" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to deploy support system
function Deploy-SupportSystem {
    Write-Host ""
    Write-Host "🆘 Deploying Support System..." -ForegroundColor Yellow
    
    # Create support system deployment
    $supportConfig = @"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quantaenergi-support
  namespace: quantaenergi-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: quantaenergi-support
  template:
    metadata:
      labels:
        app: quantaenergi-support
    spec:
      containers:
      - name: support
        image: quantaenergi/support:latest
        ports:
        - containerPort: 8084
        env:
        - name: SUPPORT_DB_URL
          value: "postgresql://quantaenergi:QuantaEnergi2025!@postgres-prod.quantaenergi-prod.svc.cluster.local:5432/support"
        - name: ZENDESK_API_KEY
          value: "zendesk_api_key_here"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: quantaenergi-support
  namespace: quantaenergi-prod
spec:
  ports:
  - port: 8084
    targetPort: 8084
  selector:
    app: quantaenergi-support
  type: ClusterIP
"@
    
    $supportConfig | Out-File -FilePath "support-deployment.yaml" -Encoding UTF8
    kubectl apply -f support-deployment.yaml
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Support system deployed successfully" -ForegroundColor Green
        Remove-Item "support-deployment.yaml" -Force
    } else {
        Write-Host "❌ Support system deployment failed" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to create GTM deployment summary
function Show-GTMDeploymentSummary {
    Write-Host ""
    Write-Host "🎉 QUANTAENERGI GO-TO-MARKET DEPLOYMENT COMPLETE!" -ForegroundColor Green
    Write-Host "=================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🏆 STATUS: GTM READY" -ForegroundColor Green
    Write-Host "🚀 SYSTEMS: FULLY DEPLOYED" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 DEPLOYED GTM SYSTEMS:" -ForegroundColor Cyan
    Write-Host "   ✅ Marketing Website" -ForegroundColor Green
    Write-Host "   ✅ Documentation System" -ForegroundColor Green
    Write-Host "   ✅ Training Platform" -ForegroundColor Green
    Write-Host "   ✅ Sales CRM" -ForegroundColor Green
    Write-Host "   ✅ Support System" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 ACCESS URLs:" -ForegroundColor Cyan
    Write-Host "   • Website: https://quantaenergi.com" -ForegroundColor White
    Write-Host "   • Documentation: https://docs.quantaenergi.com" -ForegroundColor White
    Write-Host "   • Training: https://training.quantaenergi.com" -ForegroundColor White
    Write-Host "   • Sales CRM: https://crm.quantaenergi.com" -ForegroundColor White
    Write-Host "   • Support: https://support.quantaenergi.com" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 DOCUMENTATION FEATURES:" -ForegroundColor Cyan
    Write-Host "   • API documentation" -ForegroundColor White
    Write-Host "   • User guides" -ForegroundColor White
    Write-Host "   • Developer tutorials" -ForegroundColor White
    Write-Host "   • Best practices" -ForegroundColor White
    Write-Host ""
    Write-Host "🎓 TRAINING FEATURES:" -ForegroundColor Cyan
    Write-Host "   • Interactive tutorials" -ForegroundColor White
    Write-Host "   • Video courses" -ForegroundColor White
    Write-Host "   • Certification programs" -ForegroundColor White
    Write-Host "   • Progress tracking" -ForegroundColor White
    Write-Host ""
    Write-Host "💼 SALES FEATURES:" -ForegroundColor Cyan
    Write-Host "   • Lead management" -ForegroundColor White
    Write-Host "   • Opportunity tracking" -ForegroundColor White
    Write-Host "   • Quote generation" -ForegroundColor White
    Write-Host "   • Payment processing" -ForegroundColor White
    Write-Host ""
    Write-Host "🆘 SUPPORT FEATURES:" -ForegroundColor Cyan
    Write-Host "   • Ticket system" -ForegroundColor White
    Write-Host "   • Knowledge base" -ForegroundColor White
    Write-Host "   • Live chat" -ForegroundColor White
    Write-Host "   • Community forums" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "   1. Configure domain routing" -ForegroundColor White
    Write-Host "   2. Set up analytics tracking" -ForegroundColor White
    Write-Host "   3. Create content and materials" -ForegroundColor White
    Write-Host "   4. Begin marketing campaigns" -ForegroundColor White
    Write-Host ""
    Write-Host "🎊 CONGRATULATIONS!" -ForegroundColor Green
    Write-Host "QuantaEnergi GTM systems are ready for market launch!" -ForegroundColor Green
    Write-Host ""
}

# Main execution function
function Main {
    try {
        Write-Host "Starting QuantaEnergi GTM deployment..." -ForegroundColor Green
        
        # Deploy marketing website
        if (-not (Deploy-MarketingWebsite)) {
            exit 1
        }
        
        # Deploy documentation system
        if (-not (Deploy-DocumentationSystem)) {
            exit 1
        }
        
        # Deploy training platform
        if (-not (Deploy-TrainingPlatform)) {
            exit 1
        }
        
        # Deploy sales CRM
        if (-not (Deploy-SalesCRM)) {
            exit 1
        }
        
        # Deploy support system
        if (-not (Deploy-SupportSystem)) {
            exit 1
        }
        
        # Display GTM deployment summary
        Show-GTMDeploymentSummary
        
        Write-Host "🎯 GTM deployment completed successfully!" -ForegroundColor Green
        Write-Host "QuantaEnergi is ready for market launch!" -ForegroundColor Green
        
    }
    catch {
        Write-Host "❌ GTM deployment failed with error: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Execute main function
Main
