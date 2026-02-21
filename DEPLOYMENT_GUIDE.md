# Complete Deployment Guide

This guide walks you through deploying both the **backend (Railway)** and **frontend (Vercel)**.

---

## Prerequisites

- GitHub account with your `BorgeAI` repository pushed
- Railway account (free tier available)
- Vercel account (free tier available)
- OpenAI API key

---

## Part 1: Deploy Backend to Railway

### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign in with **GitHub**
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Find and select your **`BorgeAI`** repository
6. Click **"Deploy Now"**

### Step 2: Configure Backend Service

1. Railway will create a service automatically
2. Click on the service to open it
3. Go to **Settings** tab
4. Find **"Root Directory"** setting
5. Set it to: `backend`
6. Click **"Save"**

### Step 3: Add PostgreSQL Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"**
3. Choose **"Add PostgreSQL"**
4. Railway will automatically create a PostgreSQL instance
5. **Important**: Railway automatically sets `DATABASE_URL` environment variable - you don't need to set it manually!

### Step 4: Set Environment Variables

1. Go back to your **backend service** (not the database)
2. Click on **"Variables"** tab
3. Add the following environment variables:

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `SECRET_KEY` | `your-secret-key-here-min-32-chars` | Generate a secure random string (use: `openssl rand -hex 32`) |
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI API key from https://platform.openai.com/api-keys |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | We'll update this after Vercel deployment |
| `ENVIRONMENT` | `production` | Optional, defaults to "development" |
| `LOG_LEVEL` | `INFO` | Optional, defaults to "INFO" |

**Note**: 
- `DATABASE_URL` is automatically set by Railway (don't add it manually)
- `PORT` is automatically set by Railway (don't add it manually)
- Other variables have defaults and are optional

### Step 5: Deploy

1. Railway will automatically start building when you connect the repo
2. If not, click **"Deploy"** button
3. Wait for deployment to complete (check the **"Deployments"** tab)
4. Once deployed, Railway will provide a public URL like: `https://your-app-name.up.railway.app`
5. **Copy this URL** - you'll need it for Vercel!

### Step 6: Test Backend

1. Visit: `https://your-railway-url.up.railway.app/health`
2. You should see: `{"status": "healthy", "service": "accounting-assistant-api"}`
3. Visit: `https://your-railway-url.up.railway.app/api/docs`
4. You should see the API documentation

**✅ Backend is now deployed!**

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Create Vercel Project

1. Go to [vercel.com](https://vercel.com)
2. Sign in with **GitHub**
3. Click **"Add New..."** → **"Project"**
4. Find and import your **`BorgeAI`** repository
5. Click **"Import"**

### Step 2: Configure Frontend Build Settings

1. In the project configuration page, you'll see build settings
2. **Root Directory**: Click **"Edit"** next to Root Directory
3. Select **"frontend"** folder
4. Click **"Continue"**

### Step 3: Configure Framework

1. **Framework Preset**: Should auto-detect as **Next.js** (if not, select it)
2. **Build Command**: `npm run build` (default, should be correct)
3. **Output Directory**: `.next` (default, should be correct)
4. **Install Command**: `npm install` (default)

### Step 4: Set Environment Variables

1. Scroll down to **"Environment Variables"** section
2. Click **"Add"** and add:

| Variable Name | Value |
|---------------|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-railway-url.up.railway.app/api/v1` |

**Important**: Replace `your-railway-url.up.railway.app` with your actual Railway URL from Part 1!

### Step 5: Deploy

1. Click **"Deploy"** button
2. Wait for build to complete (usually 1-2 minutes)
3. Vercel will provide a URL like: `https://your-app.vercel.app`
4. **Copy this Vercel URL** - you'll need it for the next step!

**✅ Frontend is now deployed!**

---

## Part 3: Connect Frontend and Backend

### Step 1: Update Backend CORS

1. Go back to **Railway** dashboard
2. Open your **backend service**
3. Go to **"Variables"** tab
4. Find `CORS_ORIGINS` variable
5. Click **"Edit"**
6. Update the value to include your Vercel URL:

```json
["https://your-app.vercel.app", "http://localhost:3000"]
```

**Important**: Replace `your-app.vercel.app` with your actual Vercel URL!

7. Click **"Save"**
8. Railway will automatically redeploy with the new CORS settings

### Step 2: Test the Connection

1. Visit your Vercel frontend: `https://your-app.vercel.app`
2. Try to register/login
3. If you see CORS errors in the browser console, double-check:
   - `CORS_ORIGINS` in Railway includes your Vercel URL (no trailing slash)
   - `NEXT_PUBLIC_API_URL` in Vercel points to your Railway URL

---

## Part 4: Create Admin User

### Option 1: Using API (Recommended)

1. Open your Railway backend URL: `https://your-railway-url.up.railway.app/api/docs`
2. Find the **POST /api/v1/auth/register** endpoint
3. Click **"Try it out"**
4. Enter:
```json
{
  "email": "admin@example.com",
  "password": "SecurePassword123!",
  "full_name": "Admin User",
  "role": "admin"
}
```
5. Click **"Execute"**
6. You should get a 201 response with user details

### Option 2: Using curl

```bash
curl -X POST https://your-railway-url.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123!",
    "full_name": "Admin User",
    "role": "admin"
  }'
```

---

## Part 5: Verify Everything Works

1. **Frontend**: Visit `https://your-app.vercel.app`
2. **Login**: Use your admin credentials
3. **Upload**: Try uploading an invoice (PDF/PNG/JPG)
4. **Processing**: Wait for OCR + AI processing (may take 30-60 seconds)
5. **Review**: Check suggestions appear with confidence scores
6. **Approve/Reject**: Test the approval workflow

---

## Troubleshooting

### Backend Issues

**Build fails:**
- Check Railway logs (Deployments → View Logs)
- Ensure `backend/` is set as Root Directory
- Verify Dockerfile is correct

**Database connection errors:**
- Verify PostgreSQL service is running in Railway
- Check `DATABASE_URL` is automatically set (don't set it manually)
- Check Railway logs for connection errors

**CORS errors:**
- Verify `CORS_ORIGINS` includes your Vercel URL (exact match, no trailing slash)
- Check format is valid JSON array: `["https://your-app.vercel.app"]`
- Redeploy backend after changing CORS_ORIGINS

### Frontend Issues

**Build fails:**
- Check Vercel build logs
- Ensure Root Directory is set to `frontend`
- Verify `package.json` is correct

**API connection errors:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Check it points to your Railway backend URL
- Ensure URL ends with `/api/v1` (no trailing slash)

**404 errors:**
- Check Next.js routing is correct
- Verify API endpoints match

### General Issues

**OCR not working:**
- Tesseract is installed in Dockerfile
- Check Railway logs for OCR errors
- Verify file uploads are working

**AI suggestions failing:**
- Verify `OPENAI_API_KEY` is set correctly in Railway
- Check OpenAI API quota at https://platform.openai.com/usage
- Review Railway logs for API errors

---

## Production Checklist

- [ ] Backend deployed to Railway
- [ ] Frontend deployed to Vercel
- [ ] CORS configured correctly
- [ ] Environment variables set
- [ ] Admin user created
- [ ] Test upload works
- [ ] Test processing works
- [ ] Test approval workflow works
- [ ] SSL certificates active (automatic on Railway/Vercel)
- [ ] Custom domains configured (optional)

---

## URLs Summary

After deployment, you'll have:

- **Backend API**: `https://your-app.up.railway.app`
- **API Docs**: `https://your-app.up.railway.app/api/docs`
- **Frontend**: `https://your-app.vercel.app`
- **Database**: Managed by Railway (internal)

---

## Next Steps

1. **Custom Domain**: Add custom domains in Railway and Vercel settings
2. **File Storage**: Consider Railway Volumes or S3 for persistent file storage
3. **Monitoring**: Set up Railway monitoring or external service
4. **Backups**: Enable Railway PostgreSQL backups
5. **Rate Limiting**: Add rate limiting middleware for production

---

## Quick Reference

### Railway Commands (if using CLI)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# View logs
railway logs

# Open shell
railway shell
```

### Vercel Commands (if using CLI)
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# View logs
vercel logs
```

---

**🎉 Your app is now live!**
