# Deployment Guide - Power Trading Application

## Quick Access (Recommended for Testing)

### Method 1: GitHub Codespaces Port Forwarding ⚡ (2 minutes)

**Already done! Just share the URLs:**

1. In VS Code, click **PORTS** tab (bottom panel)
2. Find ports `3000` (Frontend) and `8000` (Backend)
3. Right-click each → **Port Visibility** → **Public**
4. Copy the **Forwarded Address** for each port
5. Share both URLs with your co-founder

**Access:**
- Frontend: `https://your-codespace-3000.app.github.dev`
- Backend API: `https://your-codespace-8000.app.github.dev`

Your co-founder can test immediately in any browser!

---

## Method 2: Deploy to Vercel (Frontend) + Render (Backend) 🚀

### A. Deploy Frontend to Vercel (Free)

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Build and Deploy:**
```bash
cd /workspaces/Power-Trading-application/frontend-react
vercel --prod
```

3. **Follow prompts:**
   - Link to existing project? `N`
   - Project name: `power-trading-dashboard`
   - Deploy? `Y`

**Result:** You'll get a URL like `https://power-trading-dashboard.vercel.app`

### B. Deploy Backend to Render (Free)

1. **Go to:** https://render.com
2. **Click:** "New +" → "Web Service"
3. **Connect GitHub repo:** `DataScience-beginner/Power-Trading-application`
4. **Configure:**
   - Name: `power-trading-api`
   - Branch: `Version-V0`
   - Root Directory: `/`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
   - Plan: `Free`

5. **Add Environment Variable:**
   - Key: `DATABASE_URL`
   - Value: `sqlite:///./power_trading.db`

**Result:** URL like `https://power-trading-api.onrender.com`

### C. Update Frontend API URL

After deploying backend, update frontend:

```bash
cd frontend-react
```

Create `.env.production`:
```env
VITE_API_URL=https://power-trading-api.onrender.com
```

Redeploy frontend:
```bash
vercel --prod
```

---

## Method 3: Deploy to Railway (Full Stack - One Click) 🎯

1. **Go to:** https://railway.app
2. **Click:** "Start a New Project"
3. **Select:** "Deploy from GitHub repo"
4. **Choose:** `Power-Trading-application`
5. **Railway auto-detects** Python backend
6. **Add service** for React frontend separately

**Cost:** Free tier includes 500 hours/month

---

## Method 4: Docker Deployment (Any Platform) 🐳

### Create Docker Configuration

Already included! Use these files:

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY frontend-react/package*.json ./
RUN npm install
COPY frontend-react/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./power_trading.db:/app/power_trading.db
  
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

Deploy to: DigitalOcean, AWS, Google Cloud, Azure

---

## Method 5: Share GitHub Codespace Directly 🔗

**Invite co-founder to codespace:**

1. In VS Code, click **Share** button (top right)
2. Enable **"Share running ports"**
3. Send invite link to co-founder
4. They get full access to your development environment

**Note:** Requires co-founder to have GitHub account

---

## Recommended for Your Use Case

**For Testing with Co-Founder:**
1. ✅ **Use Port Forwarding (Method 1)** - Instant, no deployment needed
2. Share the forwarded URLs
3. Co-founder can test all features immediately

**For Production Deployment:**
1. ✅ **Vercel (Frontend) + Render (Backend)** - Free, reliable, easy
2. Custom domain support
3. Auto-deploy on git push

---

## Pre-Deployment Checklist

Before sharing, ensure:
- ✅ Backend server running: `curl http://localhost:8000/api/health`
- ✅ Frontend server running: `curl http://localhost:3000`
- ✅ Database initialized: `python init_database.py`
- ✅ Mock data loaded: `python upload_mock_reports.py`
- ✅ Reports working: Test PDF/Excel downloads
- ✅ All clients visible in sidebar

---

## Testing Credentials & Data

**Current Data:**
- Client: Mellbro Sugars Pvt Ltd (NPT0027_KA0)
- Date Range: Jan 1-15, 2026
- Transactions: 2,072 records
- Energy Schedule: 18 days

**API Endpoints to Test:**
- `GET /api/clients` - List all clients
- `GET /api/transactions` - Get transactions
- `GET /api/analytics/summary` - Dashboard stats
- `GET /api/energy-schedule/summary` - Energy schedule data
- `GET /api/reports/daily-trading/pdf` - Download PDF report
- `GET /api/reports/daily-trading/excel` - Download Excel report

---

## Support & Monitoring

**Monitor your deployment:**
- Vercel: Dashboard at https://vercel.com/dashboard
- Render: Dashboard at https://dashboard.render.com
- Railway: Dashboard at https://railway.app/dashboard

**Logs:**
- Vercel: Real-time logs in dashboard
- Render: Click "Logs" tab in service
- Codespace: Terminal output shows all errors

---

## Cost Estimate

| Platform | Frontend | Backend | Database | Total |
|----------|----------|---------|----------|-------|
| **Codespaces** | Free* | Free* | Free* | **$0** |
| **Vercel + Render** | Free | Free | Free | **$0** |
| **Railway** | Free tier | Free tier | Included | **$0** |
| **Production** | $20/mo | $7/mo | $5/mo | **$32/mo** |

*GitHub Codespaces: 60 hours/month free for personal accounts

---

## Next Steps

1. **Choose Method 1 (Port Forwarding)** for immediate testing
2. Get co-founder feedback
3. If approved, deploy to **Vercel + Render** for permanent hosting
4. Add custom domain if needed
5. Set up monitoring and alerts

**Need help?** Just ask!
