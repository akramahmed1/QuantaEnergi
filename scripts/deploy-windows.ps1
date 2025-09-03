# QuantaEnergi Production Deployment Script for Windows
# This script completes the infrastructure deployment for production readiness

param(
    [string]$AWS_REGION = "us-east-1",
    [string]$CLUSTER_NAME = "quantaenergi-cluster",
    [string]$DOMAIN = "quantaenergi.com"
)

Write-Host "🚀 QuantaEnergi Production Infrastructure Deployment" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Function to check prerequisites
function Test-Prerequisites {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
    
    $tools = @("kubectl", "helm", "aws", "docker")
    $missing = @()
    
    foreach ($tool in $tools) {
        try {
            $null = Get-Command $tool -ErrorAction Stop
            Write-Host "✅ $tool is installed" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ $tool is not installed" -ForegroundColor Red
            $missing += $tool
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Host "❌ Missing required tools: $($missing -join ', ')" -ForegroundColor Red
        Write-Host "Please install the missing tools before proceeding." -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✅ All prerequisites are satisfied" -ForegroundColor Green
}

# Function to check AWS credentials
function Test-AWSCredentials {
    Write-Host "🔍 Checking AWS credentials..." -ForegroundColor Yellow
    
    try {
        $identity = aws sts get-caller-identity --query 'Arn' --output text 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ AWS credentials are configured: $identity" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "❌ Failed to verify AWS credentials" -ForegroundColor Red
    }
    
    Write-Host "❌ AWS credentials are not configured or invalid" -ForegroundColor Red
    Write-Host "Please run 'aws configure' to set up your credentials." -ForegroundColor Yellow
    return $false
}

# Function to create EKS cluster
function New-EKSCluster {
    Write-Host "🏗️  Creating EKS cluster..." -ForegroundColor Yellow
    
    # Check if cluster already exists
    $existing = eksctl get cluster --name $CLUSTER_NAME --region $AWS_REGION 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Cluster $CLUSTER_NAME already exists" -ForegroundColor Green
        return $true
    }
    
    Write-Host "Creating new EKS cluster: $CLUSTER_NAME in region: $AWS_REGION" -ForegroundColor Cyan
    
    # Create cluster configuration
    $clusterConfig = @"
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: $CLUSTER_NAME
  region: $AWS_REGION
  version: "1.28"
nodeGroups:
  - name: ng-1
    instanceType: t3.medium
    desiredCapacity: 2
    minSize: 1
    maxSize: 5
    volumeSize: 20
    ssh:
      allow: false
    iam:
      withAddonPolicies:
        autoScaler: true
        albIngress: true
addons:
  - name: vpc-cni
  - name: coredns
  - name: kube-proxy
"@
    
    $clusterConfig | Out-File -FilePath "cluster-config.yaml" -Encoding UTF8
    
    # Create cluster
    eksctl create cluster -f cluster-config.yaml
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ EKS cluster created successfully" -ForegroundColor Green
        Remove-Item "cluster-config.yaml" -Force
        return $true
    } else {
        Write-Host "❌ Failed to create EKS cluster" -ForegroundColor Red
        return $false
    }
}

# Function to install Kubernetes add-ons
function Install-KubernetesAddons {
    Write-Host "🔧 Installing Kubernetes add-ons..." -ForegroundColor Yellow
    
    # Install AWS Load Balancer Controller
    Write-Host "Installing AWS Load Balancer Controller..." -ForegroundColor Cyan
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update
    
    helm install aws-load-balancer-controller eks/aws-load-balancer-controller `
        -n kube-system `
        --set clusterName=$CLUSTER_NAME `
        --set serviceAccount.create=false `
        --set serviceAccount.name=aws-load-balancer-controller
    
    # Install cert-manager
    Write-Host "Installing cert-manager..." -ForegroundColor Cyan
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    
    helm install cert-manager jetstack/cert-manager `
        -n cert-manager `
        --create-namespace `
        --set installCRDs=true
    
    # Install NGINX Ingress Controller
    Write-Host "Installing NGINX Ingress Controller..." -ForegroundColor Cyan
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    
    helm install ingress-nginx ingress-nginx/ingress-nginx `
        -n ingress-nginx `
        --create-namespace `
        --set controller.service.type=LoadBalancer
    
    Write-Host "✅ Kubernetes add-ons installed successfully" -ForegroundColor Green
}

# Function to create namespaces
function New-Namespaces {
    Write-Host "📁 Creating namespaces..." -ForegroundColor Yellow
    
    $namespaces = @("quantaenergi", "monitoring")
    
    foreach ($ns in $namespaces) {
        kubectl create namespace $ns --dry-run=client -o yaml | kubectl apply -f -
        Write-Host "✅ Namespace $ns created/updated" -ForegroundColor Green
    }
}

# Function to deploy infrastructure
function Deploy-Infrastructure {
    Write-Host "🚀 Deploying infrastructure components..." -ForegroundColor Yellow
    
    # Deploy database layer
    Write-Host "Deploying database layer..." -ForegroundColor Cyan
    kubectl apply -f ../kubernetes/database.yaml
    
    # Deploy monitoring stack
    Write-Host "Deploying monitoring stack..." -ForegroundColor Cyan
    kubectl apply -f ../kubernetes/monitoring.yaml
    
    # Deploy application
    Write-Host "Deploying application..." -ForegroundColor Cyan
    kubectl apply -f ../kubernetes/deployment.yaml
    
    Write-Host "✅ Infrastructure deployment initiated" -ForegroundColor Green
}

# Function to wait for deployment
function Wait-ForDeployment {
    Write-Host "⏳ Waiting for deployment to complete..." -ForegroundColor Yellow
    
    $maxWait = 600  # 10 minutes
    $elapsed = 0
    
    while ($elapsed -lt $maxWait) {
        $pods = kubectl get pods -n quantaenergi -o json | ConvertFrom-Json
        $readyPods = ($pods.items | Where-Object { $_.status.phase -eq "Running" }).Count
        $totalPods = $pods.items.Count
        
        Write-Host "Pod status: $readyPods/$totalPods ready" -ForegroundColor Cyan
        
        if ($readyPods -eq $totalPods -and $totalPods -gt 0) {
            Write-Host "✅ All pods are running" -ForegroundColor Green
            return $true
        }
        
        Start-Sleep -Seconds 30
        $elapsed += 30
    }
    
    Write-Host "❌ Deployment timeout after $maxWait seconds" -ForegroundColor Red
    return $false
}

# Function to configure DNS and SSL
function Configure-DNSAndSSL {
    Write-Host "🌐 Configuring DNS and SSL..." -ForegroundColor Yellow
    
    # Get load balancer URL
    $ingressService = kubectl get service -n ingress-nginx ingress-nginx-controller -o json | ConvertFrom-Json
    $loadBalancerURL = $ingressService.status.loadBalancer.ingress[0].hostname
    
    if (-not $loadBalancerURL) {
        Write-Host "❌ Load balancer URL not available" -ForegroundColor Red
        return $false
    }
    
    Write-Host "Load Balancer URL: $loadBalancerURL" -ForegroundColor Cyan
    
    # Create Route53 hosted zone (if needed)
    Write-Host "Creating Route53 hosted zone..." -ForegroundColor Cyan
    aws route53 create-hosted-zone --name $DOMAIN --caller-reference $(Get-Date -Format "yyyyMMddHHmmss")
    
    # Get hosted zone ID
    $hostedZone = aws route53 list-hosted-zones --query "HostedZones[?Name=='$DOMAIN.'].Id" --output text
    $hostedZoneId = $hostedZone.Split('/')[-1]
    
    # Create DNS records
    $changeBatch = @{
        Changes = @(
            @{
                Action = "UPSERT"
                ResourceRecordSet = @{
                    Name = "api.$DOMAIN"
                    Type = "CNAME"
                    TTL = 300
                    ResourceRecords = @(@{Value = $loadBalancerURL})
                }
            },
            @{
                Action = "UPSERT"
                ResourceRecordSet = @{
                    Name = "app.$DOMAIN"
                    Type = "CNAME"
                    TTL = 300
                    ResourceRecords = @(@{Value = $loadBalancerURL})
                }
            },
            @{
                Action = "UPSERT"
                ResourceRecordSet = @{
                    Name = "monitoring.$DOMAIN"
                    Type = "CNAME"
                    TTL = 300
                    ResourceRecords = @(@{Value = $loadBalancerURL})
                }
            }
        )
    }
    
    $changeBatch | ConvertTo-Json -Depth 10 | Out-File -FilePath "dns-changes.json" -Encoding UTF8
    aws route53 change-resource-record-sets --hosted-zone-id $hostedZoneId --change-batch file://dns-changes.json
    
    Remove-Item "dns-changes.json" -Force
    
    Write-Host "✅ DNS and SSL configuration completed" -ForegroundColor Green
    return $true
}

# Function to run health checks
function Test-HealthChecks {
    Write-Host "🏥 Running health checks..." -ForegroundColor Yellow
    
    # Wait for services to be ready
    Start-Sleep -Seconds 60
    
    # Test backend health
    try {
        $backendHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
        Write-Host "✅ Backend health check passed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Backend health check failed" -ForegroundColor Red
    }
    
    # Test frontend health
    try {
        $frontendHealth = Invoke-RestMethod -Uri "http://localhost:3000/health" -Method Get -TimeoutSec 10
        Write-Host "✅ Frontend health check passed" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Frontend health check failed" -ForegroundColor Red
    }
    
    Write-Host "✅ Health checks completed" -ForegroundColor Green
}

# Function to display deployment summary
function Show-DeploymentSummary {
    Write-Host ""
    Write-Host "🎉 QuantaEnergi Infrastructure Deployment Complete!" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
    Write-Host "   - API: https://api.$DOMAIN" -ForegroundColor White
    Write-Host "   - App: https://app.$DOMAIN" -ForegroundColor White
    Write-Host "   - Monitoring: https://monitoring.$DOMAIN" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Management Commands:" -ForegroundColor Cyan
    Write-Host "   - Check pods: kubectl get pods -n quantaenergi" -ForegroundColor White
    Write-Host "   - Check services: kubectl get services -n quantaenergi" -ForegroundColor White
    Write-Host "   - Check ingress: kubectl get ingress -n quantaenergi" -ForegroundColor White
    Write-Host "   - View logs: kubectl logs -n quantaenergi -l app=quantaenergi-backend" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Run performance tests" -ForegroundColor White
    Write-Host "   2. Onboard pilot users" -ForegroundColor White
    Write-Host "   3. Monitor system performance" -ForegroundColor White
    Write-Host "   4. Begin beta launch process" -ForegroundColor White
    Write-Host ""
}

# Main execution
function Main {
    try {
        Write-Host "Starting QuantaEnergi production deployment..." -ForegroundColor Green
        
        # Check prerequisites
        Test-Prerequisites
        
        # Check AWS credentials
        if (-not (Test-AWSCredentials)) {
            exit 1
        }
        
        # Create EKS cluster
        if (-not (New-EKSCluster)) {
            exit 1
        }
        
        # Install add-ons
        Install-KubernetesAddons
        
        # Create namespaces
        New-Namespaces
        
        # Deploy infrastructure
        Deploy-Infrastructure
        
        # Wait for deployment
        if (-not (Wait-ForDeployment)) {
            Write-Host "❌ Deployment failed or timed out" -ForegroundColor Red
            exit 1
        }
        
        # Configure DNS and SSL
        Configure-DNSAndSSL
        
        # Run health checks
        Test-HealthChecks
        
        # Show summary
        Show-DeploymentSummary
        
        Write-Host "🎯 Deployment completed successfully!" -ForegroundColor Green
        Write-Host "QuantaEnergi is now ready for beta launch!" -ForegroundColor Green
        
    }
    catch {
        Write-Host "❌ Deployment failed with error: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Execute main function
Main
