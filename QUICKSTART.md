# Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

## 5-Minute Setup

### 1. Configure Environment

**Backend:**
```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/accounting_assistant
SECRET_KEY=your-secret-key-min-32-chars-change-in-production
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Frontend:**
```bash
cd frontend
cp .env.example .env
```

Edit `frontend/.env`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 2. Start Services

```bash
# From project root
docker-compose up -d
```

Wait for services to start (about 30 seconds).

### 3. Create Admin User

```bash
# Option 1: Using API
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123!",
    "full_name": "Admin User",
    "role": "admin"
  }'

# Option 2: Using Python script (if running locally)
cd backend
python scripts/create_admin.py admin@example.com SecurePassword123! "Admin User"
```

### 4. Access Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

### 5. Login and Upload

1. Go to http://localhost:3000
2. Login with your admin credentials
3. Upload an invoice (PDF, PNG, or JPG)
4. Wait for processing (OCR + AI analysis)
5. Review suggestions and approve/reject

## Troubleshooting

### Services not starting?
```bash
docker-compose logs
```

### Database connection issues?
```bash
docker-compose ps  # Check if db service is running
docker-compose exec db psql -U postgres -c "\l"  # Test connection
```

### OCR not working?
- Ensure Tesseract is installed in the Docker container
- Check backend logs: `docker-compose logs backend`

### AI suggestions failing?
- Verify OPENAI_API_KEY is set correctly
- Check API quota at https://platform.openai.com/usage

## Next Steps

- Review the full [README.md](README.md) for detailed documentation
- Check API documentation at http://localhost:8000/api/docs
- Customize accounting rules in `backend/app/services/rule_validation_service.py`
