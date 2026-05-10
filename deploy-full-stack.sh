#!/bin/bash

# Full-Stack Deployment Script - All Phases
echo "🚀 Deploying Complete Milestone 1 Restaurant Recommender..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Deploy Backend (Phase 4)
echo "🔧 Deploying Backend (Phase 4)..."
cd phase4
railway up

# Get backend URL
BACKEND_URL=$(railway variables | grep RAILWAY_PUBLIC_DOMAIN | awk '{print $2}')
echo "🌐 Backend URL: $BACKEND_URL"

# Deploy Frontend (Phase 7)
echo "🎨 Deploying Frontend (Phase 7)..."
cd ../phase7

# Set environment variable for frontend
railway variables set NEXT_PUBLIC_API_URL=https://$BACKEND_URL

# Deploy frontend
railway up

# Get frontend URL
FRONTEND_URL=$(railway variables | grep RAILWAY_PUBLIC_DOMAIN | awk '{print $2}')
echo "🌐 Frontend URL: https://$FRONTEND_URL"

echo "✅ Full-Stack Deployment Complete!"
echo "📋 Your app is live at: https://$FRONTEND_URL"
echo "🔧 Backend API at: https://$BACKEND_URL"
echo "📊 Check deployment status at: https://railway.app/dashboard"
