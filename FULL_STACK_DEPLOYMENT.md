# 🚀 Full-Stack Deployment Guide - All Phases

## 📋 Project Architecture Overview

### **Phase 4 - Backend (FastAPI)**
- **Technology**: Python FastAPI with Uvicorn
- **Features**: LLM integration, vector search, hybrid ranking
- **Database**: Redis for caching, file-based storage
- **API**: RESTful endpoints for restaurant recommendations

### **Phase 7 - Frontend (Next.js)**
- **Technology**: Next.js 14 with TypeScript
- **Features**: Modern UI, AI recommendations, user preferences
- **Styling**: Tailwind CSS with Stitch AI design
- **State Management**: Zustand for global state

## 🌐 Full-Stack Deployment Options

### **Option 1: Railway (Recommended for Full-Stack)**
**🌟 Why Railway?**
- Free tier for full-stack applications
- Docker support
- Environment variables management
- Automatic deployments from GitHub
- Both frontend and backend can be deployed together

**📋 Requirements:**
- Railway account
- GitHub repository (✅ Ready)
- Docker configurations (✅ Created)

**🚀 Deployment Steps:**

#### **Backend Deployment (Phase 4)**
1. **Create Railway Service**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Deploy backend
   cd phase4
   railway up
   ```

2. **Environment Variables for Backend**
   - `GROQ_API_KEY`: Your Groq API key
   - `PYTHONPATH`: `/app`
   - `PORT`: `8000`

#### **Frontend Deployment (Phase 7)**
1. **Create Another Railway Service**
   ```bash
   cd phase7
   railway up
   ```

2. **Environment Variables for Frontend**
   - `NEXT_PUBLIC_API_URL`: Your Railway backend URL
   - `NEXT_PUBLIC_GROQ_API_KEY`: Your Groq API key

---

### **Option 2: Vercel + Render (Split Deployment)**
**🌟 Why this combo?**
- Vercel: Best for Next.js frontend
- Render: Good for Python backend
- Both have generous free tiers

**🚀 Deployment Steps:**

#### **Frontend on Vercel**
```bash
cd phase7
npm i -g vercel
vercel login
vercel --prod
```

#### **Backend on Render**
1. **Create Render account**
2. **Connect GitHub repository**
3. **Select `phase4` folder**
4. **Set environment variables**
5. **Deploy**

---

### **Option 3: Docker + DigitalOcean (Advanced)**
**🌟 Why Docker?**
- Complete control
- Scalable
- Both services in one place
- Professional setup

**🚀 Deployment Steps:**

#### **Create Docker Compose for Full Stack**
```yaml
version: '3.8'

services:
  backend:
    build: ./phase4
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./phase4/data:/app/data
    restart: unless-stopped

  frontend:
    build: ./phase7
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

---

## 🔧 Configuration Files Created

### **Backend Docker Configuration**
- ✅ `phase4/Dockerfile` - Backend containerization
- ✅ `phase4/docker-compose.yml` - Local development setup
- ✅ Health checks and restart policies

### **Frontend Configuration**
- ✅ `phase7/vercel.json` - Vercel deployment config
- ✅ `phase7/netlify.toml` - Alternative deployment config
- ✅ Production build optimized

### **Integration Configuration**
- ✅ API endpoint configuration
- ✅ Environment variable setup
- ✅ CORS configuration needed

## 📊 Deployment Comparison

| Platform | Backend | Frontend | Free Tier | Setup Time |
|----------|----------|-----------|------------|------------|
| **Railway** | ✅ | ✅ | ✅ | 15 min |
| **Vercel + Render** | ✅ | ✅ | ✅ | 20 min |
| **DigitalOcean** | ✅ | ✅ | ❌ | 30 min |
| **Heroku + Vercel** | ✅ | ✅ | ✅ | 25 min |

## 🎯 Recommended Full-Stack Setup

### **Best Option: Railway**
1. **Deploy Backend First**
   ```bash
   cd phase4
   railway up
   ```

2. **Get Backend URL**
   - Railway will provide: `https://your-backend.up.railway.app`

3. **Deploy Frontend**
   ```bash
   cd phase7
   railway up
   ```

4. **Configure Frontend**
   - Set `NEXT_PUBLIC_API_URL` to backend URL
   - Redeploy frontend

## 🔗 Integration Steps

### **1. API Configuration**
Update `phase7/src/lib/api.ts`:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### **2. Environment Variables**
**Backend Environment Variables:**
- `GROQ_API_KEY`: Your Groq API key
- `PYTHONPATH`: `/app`

**Frontend Environment Variables:**
- `NEXT_PUBLIC_API_URL`: Your deployed backend URL
- `NEXT_PUBLIC_GROQ_API_KEY`: Your Groq API key

### **3. CORS Configuration**
Add to Phase 4 FastAPI app:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 Quick Deployment Commands

### **Railway Full-Stack Deployment**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy backend
cd phase4
railway up

# Deploy frontend (in new terminal)
cd phase7
railway up
```

### **Vercel + Render Deployment**
```bash
# Frontend on Vercel
cd phase7
npm i -g vercel
vercel --prod

# Backend on Render (via web dashboard)
# 1. Go to render.com
# 2. Connect GitHub
# 3. Select phase4 folder
# 4. Set environment variables
# 5. Deploy
```

## 📞 Troubleshooting

### **Common Issues:**
1. **CORS Errors**: Add frontend URL to backend CORS
2. **Environment Variables**: Double-check all required variables
3. **Build Failures**: Check Dockerfile and dependencies
4. **Connection Issues**: Verify API URLs and ports

### **Health Checks:**
- Backend: `GET /health`
- Frontend: `GET /` (should load UI)

## 🎉 Success Criteria

**✅ Full-Stack Deployment Complete When:**
- Backend API is accessible and healthy
- Frontend loads and connects to backend
- Restaurant recommendations work end-to-end
- All phases integrated and functional
- Free tier limits not exceeded

---

**🚀 Your complete Milestone 1 project with all phases is ready for full-stack deployment!**
