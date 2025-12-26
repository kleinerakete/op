# ThetaOperator Engine

## Overview

ThetaOperator Engine is a pay-to-solve AI task execution platform. Users submit problems, receive dynamic pricing, confirm payment, and the system executes AI-powered workflows. The architecture implements a formal operator model where problems flow through defined workflows with payment gates before execution.

Core concept: No execution without payment confirmation. Problems are priced based on complexity, assigned to flows (sequences of operators), and only executed after payment is verified.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Flask** with SQLAlchemy ORM for the web application
- PostgreSQL database with JSONB columns for flexible payload storage
- Replit Auth integration for user authentication (OAuth2 via Flask-Dance)

### Core Domain Model
The system operates on a state machine pattern:
- **Problem**: The unit of work - tracks status from INTAKE → PRICED → PENDING_PAYMENT → PAID → EXECUTING → COMPLETED/FAILED
- **Flow**: Defines a sequence of operators to solve a problem type, with base pricing
- **Operator**: Individual worker units that transform inputs to outputs
- **RevenueEntry**: Tracks completed payments and earnings

### Payment Gate Pattern
The engine enforces a strict payment-before-execution rule:
1. User submits problem → system selects appropriate flow
2. Price computed based on flow base price + complexity multiplier
3. Payment must be confirmed before any execution begins
4. Revenue tracked on successful completion

### AI Integration
- OpenAI client configured via Replit AI Integrations
- Uses environment variables for API key and base URL
- Model: gpt-5 (default, configurable)

### Authentication
- Replit Auth via OAuth2 blueprint
- User sessions stored in database with browser session keys
- `@require_login` decorator protects authenticated routes

## External Dependencies

### Database
- PostgreSQL (via `DATABASE_URL` environment variable)
- SQLAlchemy with connection pooling (pool_pre_ping, 300s recycle)

### Authentication
- Replit OAuth2 (Flask-Dance integration)
- Session secret from `SESSION_SECRET` or `FLASK_SECRET_KEY`

### AI Services
- OpenAI API via Replit AI Integrations
- Environment: `AI_INTEGRATIONS_OPENAI_API_KEY`, `AI_INTEGRATIONS_OPENAI_BASE_URL`

### Required Python Packages
- Flask, Flask-SQLAlchemy, Flask-Login, Flask-Dance
- OpenAI Python SDK
- Werkzeug (ProxyFix for proper header handling)