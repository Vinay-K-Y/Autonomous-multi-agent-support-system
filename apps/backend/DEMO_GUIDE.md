# Autonomous Multi-Agent Support System - Demo Guide

## Overview

This guide demonstrates the Autonomous Multi-Agent Support System, a production-ready customer support platform that uses AI agents to handle support requests automatically. The system includes intent detection, knowledge base integration, ticket creation, and human escalation capabilities.

## Prerequisites

- Docker Desktop installed and running
- PowerShell (Windows) or terminal
- Basic understanding of REST APIs
- Optional: Ollama running locally for LLM functionality

## Quick Start

### 1. Start the System

```powershell
cd b:\Development\Projects\Autonomous-multi-agent-support-system\apps\backend
docker-compose up -d
```

This starts:
- **PostgreSQL** (port 5432) - Database
- **Redis** (port 6379) - Caching and rate limiting
- **Backend API** (port 8000) - FastAPI application

### 2. Verify System Status

```powershell
docker-compose ps
```

All services should show as "healthy" or "running".

### 3. Check API Health

```powershell
Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing
```

Expected response: `{"status":"healthy","service":"Autonomous Multi-Agent Support System","version":"1.0.0"}`

## Authentication Demo

### Login with Test User

```powershell
Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/auth/login' -Method POST -ContentType 'application/x-www-form-urlencoded' -Body 'username=admin@example.com&password=admin123' -UseBasicParsing
```

Response includes JWT access token for authenticated requests.

### Test Credentials

- **Admin**: admin@example.com / admin123
- **Support Agent**: support.agent@example.com / support123
- **Customer 1**: customer1@example.com / customer123
- **Customer 2**: customer2@example.com / customer123
- **Customer 3**: customer3@example.com / customer123

## Support Request Demo

### Basic Support Request

```powershell
$body = @{
    message = "I need help with my recent order"
    customer_id = "test_customer_123"
    conversation_id = "conv_123"
    language = "en"
    channel = "web"
} | ConvertTo-Json

Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/support' -Method POST -ContentType 'application/json' -Body $body -UseBasicParsing
```

### Refund Request

```powershell
$body = @{
    message = "I want a refund for my order"
    customer_id = "test_customer_123"
    conversation_id = "conv_124"
    language = "en"
    channel = "web"
} | ConvertTo-Json

Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/support' -Method POST -ContentType 'application/json' -Body $body -UseBasicParsing
```

### Account Issue

```powershell
$body = @{
    message = "My account is locked and I can't login"
    customer_id = "test_customer_123"
    conversation_id = "conv_125"
    language = "en"
    channel = "web"
} | ConvertTo-Json

Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/support' -Method POST -ContentType 'application/json' -Body $body -UseBasicParsing
```

## Synthetic Data Demo

### View Existing Data

The system comes pre-loaded with synthetic test data:

**Users**: 5 test users with different roles
**Conversations**: 4 sample conversations with message history
**Tickets**: 3 support tickets in various states
**Support Logs**: 3 request logs for analytics
**Human Reviews**: 2 quality assurance reviews

### Reset Synthetic Data

```powershell
docker-compose exec backend uv run python clear_all_data.py
docker-compose exec backend uv run python seed_data.py
```

## API Documentation

### Interactive API Docs

Open in browser: `http://localhost:8000/docs`

### Available Endpoints

**Authentication**
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info (requires auth)

**Support**
- `POST /api/v1/support` - Submit support request
- Rate limited: 100 requests per 60 seconds

**System**
- `GET /` - API information and endpoints
- `GET /health` - Health check

## Agent Workflow Demo

The system processes support requests through multiple AI agents:

1. **Memory Agent** - Retrieves conversation history
2. **Intent Agent** - Detects customer intent (refund, account issue, etc.)
3. **Knowledge Agent** - Searches knowledge base for relevant information
4. **Ticket Agent** - Decides if support ticket is needed
5. **Response Agent** - Generates appropriate response

### Example Response Structure

```json
{
  "response": "I understand you need help with your order. Let me assist you...",
  "intent": "order_issue",
  "confidence": 0.85,
  "ticket_created": false,
  "ticket_id": null
}
```

## Monitoring and Logs

### View Backend Logs

```powershell
docker-compose logs backend -f
```

### View Database Logs

```powershell
docker-compose logs postgres -f
```

### View Redis Logs

```powershell
docker-compose logs redis -f
```

## Rate Limiting Demo

The system implements rate limiting to prevent abuse:

- **Default**: 100 requests per 60 seconds
- **Authentication endpoints**: 10-20 requests per 60 seconds
- Rate limiting is applied per IP address

Test rate limiting by making rapid requests - you'll receive 429 status code after exceeding limits.

## Error Handling Demo

The system includes comprehensive error handling:

### Test Invalid Request

```powershell
$body = @{
    message = ""  # Empty message
    customer_id = "test"
} | ConvertTo-Json

Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/support' -Method POST -ContentType 'application/json' -Body $body -UseBasicParsing
```

Expected: 422 validation error with detailed error messages.

### Test Service Unavailable

Stop PostgreSQL and try a request to see graceful degradation.

## Stopping the System

```powershell
docker-compose down
```

To remove volumes (delete all data):

```powershell
docker-compose down -v
```

## Advanced Features

### CORS Configuration

The system is configured to accept requests from:
- `http://localhost:3000`
- `http://localhost:8080`
- IPv6 equivalents

### Database Migrations

View and manage database schema:

```powershell
docker-compose exec backend uv run alembic revision --autogenerate -m "description"
docker-compose exec backend uv run alembic upgrade head
```

### Environment Configuration

Key environment variables (in `.env`):
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `OPENAI_BASE_URL` - LLM endpoint (for Ollama)
- `OPENAI_API_KEY` - LLM API key
- `MODEL_NAME` - LLM model name
- `LLM_PROVIDER` - LLM provider (openai/gemini)

## Troubleshooting

### Backend Not Starting

```powershell
docker-compose logs backend
```

Check for:
- Database connection issues
- Port conflicts
- Missing dependencies

### Database Connection Issues

```powershell
docker-compose exec postgres psql -U support_user -d support_system
```

### Rate Limiting Too Aggressive

Modify `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_PERIOD` in `.env` file.

## Production Considerations

For production deployment:

1. **Security**: Change default passwords and JWT secrets
2. **SSL/TLS**: Enable HTTPS for API endpoints
3. **Scaling**: Use Docker Swarm or Kubernetes for horizontal scaling
4. **Monitoring**: Add Prometheus/Grafana for metrics
5. **Backup**: Implement regular PostgreSQL backups
6. **LLM**: Use production-grade LLM service instead of local Ollama

## Support and Documentation

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- Source Code: Available in repository

## Next Steps

1. Explore the interactive API documentation
2. Test different support scenarios
3. Review the synthetic data in the database
4. Customize the AI agent prompts for your use case
5. Integrate with your existing support systems
