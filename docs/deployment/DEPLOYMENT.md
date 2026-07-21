# Deployment Guide

This guide outlines how to deploy PIA Industrial. 
PIA Industrial is designed as a standalone FastAPI backend and a React/Vite frontend.

## 1. Simplest Reliable Deployment (Local / VM)
Because the Knowledge Graph (NetworkX), Evidence store, and Document metadata use local SQLite and JSON files, a single-instance Virtual Machine (e.g. AWS EC2, DigitalOcean Droplet, Azure VM) with a persistent attached disk is the recommended deployment method.

Serverless architectures (like AWS Lambda or Vercel for the backend) are **not recommended** because they wipe local ephemeral storage between invocations, destroying your knowledge graph and document cache.

### Backend Setup (FastAPI)
1. Clone the repository and navigate to `backend/`.
2. Install Python 3.12+ and create a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` (No LLM API keys are required for the deterministic offline mode).
5. Start the backend using Uvicorn or Gunicorn:
   ```bash
   uvicorn app.api.server:app --host 0.0.0.0 --port 8000
   ```

### Frontend Setup (React/Vite)
1. Navigate to `frontend/`.
2. Install dependencies: `npm install`.
3. Create a `.env` file specifying your backend URL:
   ```env
   VITE_API_BASE_URL=http://your-server-ip:8000
   ```
4. Build the static frontend:
   ```bash
   npm run build
   ```
5. Serve the `dist/` directory using Nginx, Caddy, or Python's `http.server`.

---

## 2. Docker Deployment
Currently, PIA Industrial does not supply official Dockerfiles. Due to the local persistence requirements (SQLite and JSON caches), if you containerize the backend, **you must use persistent volume mounts** for the `backend/pia_store.db*` and `backend/data/` directories to avoid data loss on container restart.

---

## 3. CORS & Network Configuration
By default, the backend exposes permissive CORS headers for development purposes (`allow_origins=["*"]`). Before public internet deployment, you should configure the FastAPI CORS middleware in `backend/app/api/server.py` to only allow your specific frontend domain.

## 4. Known Limitations
- **Scaling**: Due to SQLite locking, the application is not designed to be scaled horizontally across multiple concurrent API servers behind a load balancer. It is best deployed as a single reliable backend instance.
- **Authentication**: This hackathon release does not include login or enterprise authentication. Do not deploy to a publicly accessible IP with sensitive industrial data without adding an authentication reverse proxy (e.g., OAuth2 Proxy).
