# Railway Deployment Guide

## Deploy Backend to Railway

### 1. Create Railway Account & Project

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `BorgeAI` repository
5. Railway will detect the Dockerfile in the `backend/` directory

### 2. Configure Root Directory

Railway needs to know where your backend code is:

1. In your Railway project, click on the service
2. Go to **Settings** → **Root Directory**
3. Set it to: `backend`
4. Save

### 3. Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically create a PostgreSQL instance
4. The `DATABASE_URL` environment variable will be automatically set

### 4. Set Environment Variables

Go to your backend service → **Variables** tab and add:

| Variable | Value | Notes |
|----------|-------|-------|
| `SECRET_KEY` | `your-secret-key-min-32-chars` | Generate a secure random string |
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI API key |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token expiration (24 hours) |
| `TESSERACT_CMD` | `/usr/bin/tesseract` | OCR command path |
| `ENVIRONMENT` | `production` | Environment name |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `["https://your-app.vercel.app"]` | Your Vercel frontend URL (JSON array) |

**Important**: For `CORS_ORIGINS`, use JSON array format:
```json
["https://your-app.vercel.app", "https://your-app.vercel.app"]
```

### 5. Deploy

1. Railway will automatically build and deploy when you push to GitHub
2. Or click **"Deploy"** manually
3. Wait for deployment to complete
4. Railway will provide a public URL like: `https://your-app.up.railway.app`

### 6. Update Vercel Frontend

1. Go to your Vercel project settings
2. Add/update environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://your-app.up.railway.app/api/v1`
3. Redeploy the frontend

### 7. Update Backend CORS

After you have your Vercel URL, update the `CORS_ORIGINS` variable in Railway:
```json
["https://your-app.vercel.app"]
```

Or for multiple origins:
```json
["https://your-app.vercel.app", "http://localhost:3000"]
```

## Railway-Specific Notes

- **Port**: Railway automatically sets `PORT` environment variable - our Dockerfile handles this
- **Database**: Railway's PostgreSQL `DATABASE_URL` is automatically injected
- **File Storage**: Uploads are stored in the container filesystem (ephemeral). For production, consider:
  - Railway Volumes (persistent storage)
  - AWS S3 / Google Cloud Storage
  - Cloudinary for file storage
- **Logs**: View logs in Railway dashboard under your service

## Troubleshooting

### Build Fails
- Check Railway logs for errors
- Ensure `backend/` is set as root directory
- Verify Dockerfile is correct

### Database Connection Issues
- Verify `DATABASE_URL` is set (Railway auto-sets this)
- Check PostgreSQL service is running
- Ensure database migrations run (tables auto-create on startup)

### 502 Bad Gateway (Application Failed to Respond)
The app starts (logs show "Uvicorn running on http://0.0.0.0:8080") but requests get 502. **Fix the target port:**

1. In Railway, open your **backend service** → **Settings**
2. Find **Networking** / **Public Networking** → **Target Port** (or "Port")
3. Either **clear** the target port (leave empty so Railway uses the same as `PORT`), or set it to the port from your logs (e.g. **8080**)
4. If it was set to e.g. 8000 or 3000 while the app listens on 8080, that mismatch causes 502
5. Save and **redeploy** if needed

Your start command uses `--port $PORT`; the public domain must forward to that same port.

### CORS Errors
- Verify `CORS_ORIGINS` includes your Vercel URL
- Check format is valid JSON array
- Ensure no trailing slashes in URLs

### OCR Not Working
- Tesseract is installed in Dockerfile
- Check logs for OCR errors
- Verify file uploads are working

## Production Recommendations

1. **File Storage**: Use Railway Volumes or external storage (S3)
2. **Database Backups**: Enable Railway PostgreSQL backups
3. **Monitoring**: Add Railway monitoring or external service
4. **Rate Limiting**: Add rate limiting middleware
5. **SSL**: Railway provides SSL automatically
6. **Custom Domain**: Add custom domain in Railway settings

## Quick Commands

```bash
# View logs
railway logs

# Open shell in Railway container
railway shell

# Check status
railway status
```
