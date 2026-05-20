# 🚀 Independent Production Deployment Guide

This guide explains how to deploy your backend and frontend to separate production environments (Render/Railway & Vercel) **without** touching your Streamlit Demo on Streamlit Cloud. 

## 1. Backend Deployment (Render or Railway)

We have created the necessary files (`asgi.py`, `render.yaml`, `Procfile`) so you can deploy the FastAPI backend easily.

### Option A: Railway (Recommended - Fastest)
1. Sign in to [Railway](https://railway.app/).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select this repository (`Milestone 1`).
4. Railway will automatically detect the `Procfile` in the root and build your backend.
5. Go to the **Variables** tab and add:
   - `GROQ_API_KEY`: `<your_api_key>`
6. Go to the **Settings** tab -> **Domains** and click **Generate Domain**.
7. *Copy this new Railway URL. You will need it for Vercel.*

### Option B: Render.com
1. Sign in to [Render](https://render.com/).
2. Click **New** -> **Blueprint**.
3. Connect your GitHub repository.
4. Render will automatically read `phase4/render.yaml` and set up the Web Service.
5. Provide your `GROQ_API_KEY` when prompted in the dashboard environment variables.
6. *Copy your new `.onrender.com` URL.*

---

## 2. Frontend Deployment (Vercel)

Phase 7 is a Next.js application perfectly structured for Vercel.

1. Sign in to [Vercel](https://vercel.com/).
2. Click **Add New** -> **Project**.
3. Import your GitHub repository.
4. In the "Configure Project" section, you must set the **Root Directory**.
   - **Root Directory**: Select `phase7`
5. Expand the **Environment Variables** section and add:
   - `NEXT_PUBLIC_API_URL`: `<Paste your Railway/Render URL here>` (e.g., `https://craveai-backend.up.railway.app`)
   - `NEXT_PUBLIC_GROQ_API_KEY`: `<your_api_key>`
6. Click **Deploy**.

## 3. Protecting your Backend (CORS)

Once your Vercel frontend is deployed (e.g., `https://my-craveai.vercel.app`), go back to your **Render/Railway Dashboard** and add a new environment variable to lock down your backend to only accept requests from your Vercel app:

- `ALLOWED_ORIGINS`: `https://my-craveai.vercel.app`

*(If left blank or missing, it will safely default to `*` allowing all requests).*

---

### What about Streamlit?
Your Streamlit app (`phase4/polished_ai_app.py`) will **not** be affected by these deployments. Streamlit Cloud will continue serving it seamlessly as your fallback/portfolio demo.
