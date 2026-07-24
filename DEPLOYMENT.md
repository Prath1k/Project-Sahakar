# 🚀 Project Sahakar — End-to-End Production Deployment Guide

This guide provides step-by-step instructions for deploying Project Sahakar (SCAAR RAG Architecture, FastAPI Backend, and Vite/React Frontend) to production.

---

## ⭐ Strategy 1: Zero-Cost Cloud Stack (Recommended)
*Total Monthly Cost: **$0.00** | Deployment Time: **~15 minutes***

This strategy uses **Render.com** for the backend (Free Web Service), **Supabase** for the relational Fact Brain, and **Vercel** for the global CDN frontend. With a free **Cron-Job** keep-awake ping, it achieves 24/7 uptime for $0.00.

### Step 1: Prepare Database (Supabase Free Tier)
1. Go to [supabase.com](https://supabase.com) and create a new project.
2. Go to **Project Settings -> API** and copy your:
   - `Project URL` (`SUPABASE_URL`)
   - `anon / public API Key` (`SUPABASE_ANON_KEY`)
3. *(Optional)* Go to the **SQL Editor** in Supabase and run the following schema to initialize the Fact Brain:
   ```sql
   CREATE TABLE IF NOT EXISTS atomic_facts (
       id TEXT PRIMARY KEY,
       user_id TEXT NOT NULL,
       fact_text TEXT NOT NULL,
       category TEXT DEFAULT 'general',
       source TEXT DEFAULT 'conversation',
       is_active BOOLEAN DEFAULT TRUE,
       reconciled_from TEXT DEFAULT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```

### Step 2: Deploy Backend & RAG (Render.com)
1. Go to [Render.com](https://render.com) and log in with GitHub.
2. Click **New +** and select **Web Service**.
3. Choose **Build and deploy from a Git repository** and connect your `Project-Sahakar` repository.
4. Fill in the deployment details:
   - **Name**: `sahakar-backend`
   - **Root Directory**: `backend` *(Crucial!)*
   - **Environment**: `Docker`
   - **Instance Type**: `Free`
5. Go to **Environment Variables** and add all your secrets from your `.env` file:
   ```env
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY=your_gemini_api_key
   NVIDIA_NIM_API_KEY=your_nvidia_nim_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```
6. Click **Create Web Service**. Wait 3-5 minutes for it to build and deploy.
   - Copy your live backend URL (e.g., `https://sahakar-backend-xxxx.onrender.com`)

### Step 2.5: Set up 24/7 Keep-Awake Pinger
Render's free tier sleeps after 15 minutes of inactivity. To prevent this:
1. Go to [cron-job.org](https://cron-job.org) and create a free account.
2. Create a new cronjob pointing to your live Render URL (e.g., `https://sahakar-backend-xxxx.onrender.com/`).
3. Set it to execute every **10 minutes**. This keeps your backend awake 24/7 and consumes ~730 of your 750 free monthly Render hours, keeping it permanently free!

### Step 3: Deploy Frontend (Vercel)
1. Go to [vercel.com](https://vercel.com) and click **Add New -> Project**.
2. Import your GitHub repository (`Project-Sahakar`) and select the `frontend` root directory.
3. In **Environment Variables**, add the live Render backend URL you copied in Step 2:
   ```env
   VITE_API_BASE_URL=https://sahakar-backend-xxxx.onrender.com
   ```
4. Click **Deploy**!
5. Once built, open your live Vercel URL. Click **"Continue as Guest"** to test your live RAG + Voice + AI Agents!

---

## ⚙️ Strategy 2: All-in-One Docker / VPS Stack (Railway, Render, or Hetzner)
*Total Monthly Cost: **~$5.00** | Best for: Full Disk Persistence & Privacy*

If you prefer deploying everything on a single Linux server or Cloud container with persistent disk storage:

1. **Deploying on Render / Railway**:
   - Create a new **Web Service** pointing to the `/backend` directory.
   - Add a **Persistent Volume** mounted at `/app/app/chroma_storage` and `/app/app/scaar_fact_brain.db`.
   - Set the environment variables (`GROQ_API_KEY`, etc.).
2. **Deploying Frontend**:
   - Deploy `/frontend` as a Static Site on Render/Vercel and set `VITE_API_BASE_URL` to your Render backend URL.

---

## 🔍 How We Configured the Codebase for Cloud Deployment

To make this seamless, we applied two critical architectural updates:
1. **Frontend Cloud Routing (`src/lib/config.js`)**:
   - Created `API_BASE_URL` which automatically detects `import.meta.env.VITE_API_BASE_URL` in production, while falling back to empty string `""` in local development so Vite's dev proxy continues working without changes.
   - Updated `ChatInterface.jsx` and `useVoiceHandoff.js` to prepend `${API_BASE_URL}` to all backend fetch requests (`/chat`, `/agent/chat`, `/api/tts/speak`).
2. **Backend CORS & Database Persistence (`backend/app/main.py` & `scaar_engine.py`)**:
   - Verified `CORSMiddleware` allows cross-origin requests (`allow_origins=["*"]`) so Vercel/Cloudflare frontends can communicate securely.
   - Configured dual-layer storage: automatic Supabase PostgreSQL cloud sync when `SUPABASE_URL` is detected, with seamless SQLite/ChromaDB fallback for offline resilience.
