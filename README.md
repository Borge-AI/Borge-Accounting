# Accounting Assistant Platform

A production-grade AI-powered accounting assistant platform for accounting firms in Norway and Europe. This SaaS platform enables accounting firms to upload invoices, extract structured data via OCR, generate AI-powered accounting suggestions, and maintain comprehensive audit trails for compliance.

## Features

- **Document Ingestion**: Upload invoices (PDF, PNG, JPG) via secure API
- **OCR Processing**: Automatic text extraction from documents using Tesseract OCR
- **AI-Powered Suggestions**: LLM-based accounting suggestions for:
  - Account number recommendations
  - VAT code suggestions
  - Confidence scoring
  - Risk assessment
- **Rule Validation**: Automated validation of accounting rules and compliance
- **Audit Logging**: Immutable audit trail for all operations (GDPR-ready)
- **User Management**: JWT-based authentication with role-based access control (Admin/Accountant)
- **Professional UI**: Modern, minimal dashboard for invoice management and approval workflow

## Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **OCR**: Tesseract OCR with Norwegian language support
- **AI**: OpenAI GPT-4o-mini integration
- **File Storage**: Local filesystem (easily replaceable with S3/GCS)

### Frontend (Next.js)
- **Framework**: Next.js 14 with React 18
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios with interceptors

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Database**: PostgreSQL 15
- **Reverse Proxy**: Ready for nginx/traefik

## Project Structure

```
BorgeAI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py          # Authentication endpoints
│   │   │       ├── invoices.py      # Invoice upload & processing
│   │   │       ├── suggestions.py   # Suggestion approval workflow
│   │   │       └── audit.py         # Audit log viewer (admin)
│   │   ├── core/
│   │   │   ├── config.py            # Application settings
│   │   │   └── security.py          # JWT & password utilities
│   │   ├── db/
│   │   │   ├── database.py          # Database connection
│   │   │   └── models.py            # SQLAlchemy models
│   │   ├── services/
│   │   │   ├── ocr_service.py       # OCR text extraction
│   │   │   ├── ai_service.py        # LLM integration
│   │   │   ├── rule_validation_service.py  # Accounting rules
│   │   │   ├── confidence_scoring_service.py  # Confidence calculation
│   │   │   └── audit_service.py     # Audit logging
│   │   └── main.py                  # FastAPI app entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/                         # Next.js app directory
│   ├── components/                  # React components
│   ├── lib/                         # Utilities (API client)
│   ├── store/                       # Zustand stores
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- OpenAI API key (for AI suggestions)
- PostgreSQL (via Docker Compose)

## Quick Start

### 1. Clone and Setup

```bash
cd BorgeAI
```

### 2. Configure Environment

**Backend:**
```bash
cd backend
cp .env.example .env
# Edit .env and set:
# - DATABASE_URL (default: postgresql://postgres:postgres@localhost:5432/accounting_assistant)
# - SECRET_KEY (generate a secure random string, min 32 chars)
# - OPENAI_API_KEY (your OpenAI API key)
```

**Frontend:**
```bash
cd frontend
cp .env.example .env
# Edit .env and set:
# - NEXT_PUBLIC_API_URL (default: http://localhost:8000/api/v1)
```

### 3. Start Services

From the project root:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- FastAPI backend on port 8000
- Next.js frontend on port 3000

### 4. Initialize Database

The database tables are created automatically on first startup. To create an admin user, you can use the registration endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "secure_password",
    "full_name": "Admin User",
    "role": "admin"
  }'
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **API Health**: http://localhost:8000/health

## Development Setup (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (macOS)
brew install tesseract tesseract-lang

# Install Tesseract OCR (Ubuntu/Debian)
sudo apt-get install tesseract-ocr tesseract-ocr-nor

# Set environment variables
cp .env.example .env
# Edit .env with your settings

# Run migrations (tables auto-create on startup)
# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env

# Start development server
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Invoices
- `POST /api/v1/invoices/upload` - Upload invoice document
- `GET /api/v1/invoices/` - List invoices
- `GET /api/v1/invoices/{id}` - Get invoice details with suggestions

### Suggestions
- `GET /api/v1/suggestions/{id}` - Get suggestion details
- `POST /api/v1/suggestions/{id}/approve` - Approve or reject suggestion

### Audit Logs (Admin Only)
- `GET /api/v1/audit/` - List audit logs
- `GET /api/v1/audit/{id}` - Get audit log details

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Admin and Accountant roles
- **Password Hashing**: bcrypt with salt
- **Input Validation**: Pydantic models for all inputs
- **CORS Protection**: Configurable CORS origins
- **File Upload Limits**: Max file size and type validation
- **Audit Trail**: Immutable logs for compliance

## GDPR Compliance

The platform is designed with GDPR principles in mind:

- **Data Controller Model**: Accounting firms are data controllers
- **Audit Logging**: All AI inputs/outputs are logged
- **User Tracking**: All actions are associated with user IDs
- **Immutable Logs**: Audit logs cannot be modified
- **Data Minimization**: Only necessary data is stored
- **Access Control**: Role-based access to sensitive data

## Production Deployment Considerations

### Security
1. **Change Default Secrets**: Update `SECRET_KEY` in production
2. **HTTPS**: Use reverse proxy (nginx/traefik) with SSL certificates
3. **Database Security**: Use strong PostgreSQL passwords
4. **API Keys**: Store secrets in secure secret management (AWS Secrets Manager, HashiCorp Vault)
5. **Rate Limiting**: Implement rate limiting for API endpoints
6. **Input Sanitization**: Additional validation for file uploads

### Scalability
1. **Background Tasks**: Move OCR/AI processing to Celery/RQ workers
2. **File Storage**: Migrate to S3/GCS for file storage
3. **Database**: Use connection pooling and read replicas
4. **Caching**: Add Redis for session management and caching
5. **CDN**: Use CDN for static assets

### Monitoring
1. **Logging**: Integrate with centralized logging (ELK, Datadog)
2. **Metrics**: Add Prometheus metrics
3. **Error Tracking**: Integrate Sentry or similar
4. **Health Checks**: Implement comprehensive health check endpoints

### Database Migrations
For production, use Alembic for database migrations:

```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Troubleshooting

### OCR Not Working
- Ensure Tesseract is installed: `tesseract --version`
- Check `TESSERACT_CMD` in `.env` points to correct path
- Verify Norwegian language pack is installed

### Database Connection Issues
- Verify PostgreSQL is running: `docker-compose ps`
- Check `DATABASE_URL` in `.env`
- Ensure database exists: `docker-compose exec db psql -U postgres -l`

### AI Suggestions Failing
- Verify `OPENAI_API_KEY` is set correctly
- Check API quota and billing
- Review error logs in backend container

## License

This project is proprietary software for accounting firms.

## Support

For issues and questions, please contact your system administrator.
# Borge-Accounting
# Borge-Accounting
