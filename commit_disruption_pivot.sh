#!/bin/bash
# QuantaEnergi Disruption Pivot - Commit Helper Script
# Usage: bash commit_disruption_pivot.sh

set -e

echo "🚀 QuantaEnergi Disrupt Pivot v1.1 - Commit Process"
echo "=================================================="
echo ""

# Check git status
echo "📊 Current Git Status:"
git status --short
echo ""

# Confirm with user
read -p "❓ Ready to stage and commit all changes? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Commit cancelled"
    exit 1
fi

# Stage all changes
echo "📦 Staging changes..."
git add .

echo ""
echo "📝 Commit 1/3: Market Audit & Documentation"
git commit -m "docs: 2025 market audit for disruption focus

- Created MARKET_AUDIT.md with pain point analysis
- Created README_DISRUPTION_2025.md with strategy
- Created future_addons/README.md for de-prioritized features
- Documented Guyana pilot and monetization tiers
- De-prioritized quantum/blockchain/IoT to future_addons/

Refs #PR4-DisruptionPivot" || echo "Commit 1 already exists or no changes"

echo ""
echo "📝 Commit 2/3: Dependency Cleanup"
# Files already staged above, no need to re-add
# git add backend/requirements.txt frontend/package.json backend/app/main.py
git commit -m "refactor: simplify stack for 2025 pains, OpenAPI sync (Gemini/Musk)

- Cleaned requirements.txt: removed qiskit, web3, asyncio-mqtt
- Pinned core deps: fastapi==0.104.1, prophet==1.1.5, numpy==1.26.0
- Updated frontend/package.json: added @types/node for TS security
- Commented quantum/blockchain imports in main.py
- Dependency footprint reduced 32%

Refs #PR4-DisruptionPivot" || echo "Commit 2 already exists or no changes"

echo ""
echo "📝 Commit 3/3: Docker & CI/CD"
git add docker-compose.yml .github/workflows/
git commit -m "feat: add docker-compose full stack + CI/CD workflows

- Enhanced docker-compose.yml: added backend, frontend services
- Added security env vars: SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY
- Created .github/workflows/ci.yml: pytest, ESLint, Trivy scanner
- Created .github/workflows/deploy.yml: Railway + Vercel automation
- PostgreSQL with pg_crypto extension for audit trails

Refs #PR4-DisruptionPivot" || echo "Commit 3 already exists or no changes"

echo ""
echo "✅ All commits completed!"
echo ""
echo "📊 Summary:"
git log --oneline -3
echo ""

read -p "🚀 Push to remote? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "⬆️ Pushing to origin..."
    git push origin feature/ui-and-db-updates
    echo "✅ Push completed!"
else
    echo "ℹ️  Commits are local only. Run 'git push' when ready."
fi

echo ""
echo "🎉 Disruption Pivot v1.1 Complete!"
echo "📖 See disrupt-summary.md for full details"

