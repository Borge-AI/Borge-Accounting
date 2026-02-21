# Architecture Overview

## System Architecture

```
┌─────────────────┐
│   Next.js UI    │
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│   FastAPI API   │
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
┌───▼───┐ ┌──▼───┐ ┌────▼────┐ ┌───▼────┐
│PostgreSQL│ │OCR   │ │OpenAI  │ │File    │
│Database  │ │Service│ │API     │ │Storage │
└──────────┘ └───────┘ └────────┘ └────────┘
```

## Component Breakdown

### Backend Services

#### 1. **OCR Service** (`app/services/ocr_service.py`)
- Extracts text from PDF and image files
- Uses Tesseract OCR with Norwegian language support
- Returns raw text for AI processing

#### 2. **AI Service** (`app/services/ai_service.py`)
- Integrates with OpenAI GPT-4o-mini
- Generates accounting suggestions:
  - Account number
  - VAT code
  - Confidence score
  - Risk level
- Structured JSON responses

#### 3. **Rule Validation Service** (`app/services/rule_validation_service.py`)
- Validates Norwegian account numbers (4-digit format)
- Validates Norwegian VAT codes (0, 1, 2, 3, 5, 6)
- Applies risk assessment rules
- Ensures compliance with accounting standards

#### 4. **Confidence Scoring Service** (`app/services/confidence_scoring_service.py`)
- Calculates final confidence scores
- Adjusts based on validation results
- Applies risk-based multipliers

#### 5. **Audit Service** (`app/services/audit_service.py`)
- Immutable audit logging
- Logs all operations:
  - Document uploads
  - OCR outputs
  - AI prompts and responses
  - User approvals/rejections
- GDPR-compliant tracking

### Database Schema

#### Users Table
- Authentication and authorization
- Role-based access (admin/accountant)
- Password hashing with bcrypt

#### Invoices Table
- Document metadata
- Processing status tracking
- File path references

#### Suggestions Table
- AI-generated suggestions
- Approval status workflow
- User decision tracking

#### Audit Logs Table
- Immutable compliance records
- Full audit trail
- IP address and user agent logging

### API Endpoints

#### Authentication (`/api/v1/auth`)
- `POST /register` - User registration
- `POST /login` - JWT token generation
- `GET /me` - Current user info

#### Invoices (`/api/v1/invoices`)
- `POST /upload` - Document upload
- `GET /` - List invoices
- `GET /{id}` - Invoice details with suggestions

#### Suggestions (`/api/v1/suggestions`)
- `GET /{id}` - Get suggestion details
- `POST /{id}/approve` - Approve/reject suggestion

#### Audit (`/api/v1/audit`) - Admin Only
- `GET /` - List audit logs
- `GET /{id}` - Audit log details

### Frontend Components

#### Authentication
- Login page with JWT token management
- Protected routes
- Role-based UI rendering

#### Dashboard
- Invoice upload interface
- Invoice list with status indicators
- Real-time processing updates

#### Invoice Detail View
- Suggestion display with confidence meters
- Risk level indicators
- Approval/rejection workflow
- Notes field for decisions

#### Audit Log Viewer (Admin)
- Complete audit trail
- OCR output viewing
- AI prompt/response inspection
- Metadata display

## Data Flow

### Invoice Processing Pipeline

1. **Upload** → User uploads document via UI
2. **Storage** → File saved to filesystem
3. **Database** → Invoice record created (status: `uploaded`)
4. **OCR** → Text extracted from document
5. **Audit** → OCR output logged
6. **AI Processing** → LLM generates suggestions
7. **Audit** → AI prompt/response logged
8. **Validation** → Rules applied, confidence calculated
9. **Database** → Suggestion record created
10. **UI Update** → User sees suggestions
11. **Approval** → User approves/rejects
12. **Audit** → Decision logged

## Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt with salt
- **Role-Based Access**: Admin vs Accountant permissions
- **Input Validation**: Pydantic models
- **File Upload Limits**: Size and type restrictions
- **CORS Protection**: Configurable origins
- **Audit Trail**: Immutable compliance logs

## GDPR Compliance

- **Data Controller Model**: Accounting firms control data
- **Audit Logging**: All AI operations logged
- **User Tracking**: Actions linked to user IDs
- **Immutable Logs**: Cannot modify audit records
- **Data Minimization**: Only necessary data stored
- **Access Control**: Role-based data access

## Scalability Considerations

### Current Implementation
- Synchronous processing (suitable for MVP)
- Local file storage
- Single database instance

### Production Recommendations
- **Background Tasks**: Celery/RQ for async processing
- **Object Storage**: S3/GCS for file storage
- **Database**: Connection pooling, read replicas
- **Caching**: Redis for sessions and caching
- **CDN**: CloudFront/Cloudflare for static assets
- **Monitoring**: Prometheus, Grafana, Sentry

## Technology Stack

### Backend
- Python 3.11+
- FastAPI 0.109
- SQLAlchemy 2.0
- PostgreSQL 15
- Tesseract OCR
- OpenAI API

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Zustand (state management)
- Axios (HTTP client)

### Infrastructure
- Docker & Docker Compose
- PostgreSQL
- Nginx (recommended for production)

## Deployment Architecture

### Development
```
docker-compose up
```

### Production (Recommended)
```
┌─────────────┐
│   Nginx     │
│  (SSL/TLS)  │
└──────┬──────┘
       │
   ┌───┴────┐
   │       │
┌──▼──┐ ┌──▼──┐
│API  │ │Web  │
│Cont.│ │Cont.│
└──┬──┘ └──┬──┘
   │       │
┌──▼───────▼──┐
│ PostgreSQL  │
│   (RDS)     │
└─────────────┘
```

## Monitoring & Logging

### Recommended Production Setup
- **Application Logs**: Structured JSON logging
- **Error Tracking**: Sentry integration
- **Metrics**: Prometheus + Grafana
- **APM**: New Relic / Datadog
- **Audit Logs**: Separate immutable storage

## Future Enhancements

- Multi-language support (beyond Norwegian)
- Advanced analytics dashboard
- Accounting system integrations (Visma, Tripletex, etc.)
- Batch processing capabilities
- Webhook notifications
- Mobile app support
- Advanced ML models for better accuracy
