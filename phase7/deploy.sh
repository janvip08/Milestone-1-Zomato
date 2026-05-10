#!/bin/bash

# Phase 7 Restaurant Recommender - Deployment Script
echo "🚀 Deploying Phase 7 Restaurant Recommender..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Deploy to Vercel
echo "🌐 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo "📋 Your app will be available at: https://your-app-name.vercel.app"
echo "📊 Check deployment status at: https://vercel.com/dashboard"
