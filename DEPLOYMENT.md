# 🚀 Project Sahakar — End-to-End Production Deployment Guide

This guide provides step-by-step instructions for deploying Project Sahakar (SCAAR RAG Architecture, FastAPI Backend, and Vite/React Frontend) to production.

---

## ⭐ Strategy 1: Zero-Cost Cloud Stack (Recommended)
*Total Monthly Cost: **$0.00** | Deployment Time: **~15 minutes***

This strategy uses **Hugging Face Spaces** for the backend (free 16GB RAM Docker container), **Supabase** for the relational Fact Brain, and **Vercel** for the global CDN frontend.

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

### Step 2: Deploy Backend & RAG (Hugging Face Spaces)
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. **Space Name**: `project-sahakar-backend` (or any name you prefer).
3. **Select the Space SDK**: Choose **Docker** -> **Blank**.
4. **Space Hardware**: Free (2 vCPU, 16GB RAM) — perfect for our ChromaDB vector engine and Edge-TTS!
5. Connect your GitHub repository:
   - If using the CLI / Git: Push the contents of the `/backend` folder directly to your Space repository.
   - Note: The Space root should contain `Dockerfile`, `requirements.txt`, and the `app/` directory.
6. Go to **Space Settings -> Variables and secrets** and add your secrets:
   ```env
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY=your_gemini_api_key
   NVIDIA_NIM_API_KEY=your_nvidia_nim_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```
7. Click **Restart Space**. Within 2 minutes, your FastAPI backend will be live!
   - Copy your live backend URL: `https://yourusername-project-sahakar-backend.hf.space`

### Step 3: Deploy Frontend (Vercel)
1. Go to [vercel.com](https://vercel.com) and click **Add New -> Project**.
2. Import your GitHub repository (`Project-Sahakar`) and select the `frontend` root directory.
3. In **Environment Variables**, add the live Hugging Face backend URL you copied in Step 2:
   ```env
   VITE_API_BASE_URL=https://yourusername-project-sahakar-backend.hf.space
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
