# Enterprise QR Asset Management System

A sophisticated, enterprise-grade QR code asset management platform built with modern Python technologies.

## 🏗️ Architecture Overview

This system follows **Clean Architecture** principles with a modular, hexagonal design pattern.

### Key Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   FastAPI    │  │   Web UI     │  │   WebSocket     │   │
│  │   REST API   │  │  (Bootstrap) │  │   Real-time     │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Use Cases    │  │   Services   │  │    DTOs         │   │
│  │   (Commands) │  │  (Business)  │  │   (Data)        │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Domain Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Entities   │  │Value Objects  │  │ Repositories    │   │
│  │  (Models)    │  │  (Value)     │  │  (Interfaces)   │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Database   │  │  Security    │  │ External APIs   │   │
│  │  (PostgreSQL)│  │  (JWT, RBAC) │  │   (QR, Email)   │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Features

- ✅ JWT Authentication & Authorization (RBAC)
- ✅ QR Code Generation & Scanning
- ✅ Asset Lifecycle Management
- ✅ Audit Trail & Activity Logging
- ✅ Multi-tenancy Support
- ✅ RESTful API (FastAPI)
- ✅ Responsive Web Dashboard (Bootstrap 5)
- ✅ Docker Containerization
- ✅ Database Migrations (Alembic)

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.14 |
| Framework | FastAPI (Async) |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL |
| Migrations | Alembic |
| Frontend | Bootstrap 5 + HTML + JavaScript |
| Auth | JWT + OAuth2 |
| Container | Docker |
| Testing | Pytest |

## 📦 Installation

### Prerequisites

- Python 3.14+
- Docker & Docker Compose
- PostgreSQL 15+

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd qr_asset_management

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Build and start services
docker-compose up -d --build

# Run migrations
docker-compose exec api alembic upgrade head

# Access the application
# API: http://localhost:8000
# Web: http://localhost:8000/web
# Docs: http://localhost:8000/docs
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔐 Authentication & Authorization

### JWT Token Structure

```json
{
  "sub": "user_id",
  "type": "access",
  "exp": 1234567890,
  "roles": ["admin", "manager"],
  "permissions": ["asset:create", "asset:read"]
}
```

### RBAC Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| Super Admin | System-wide access | All permissions |
| Admin | Organization management | Full CRUD |
| Manager | Department management | Read, Update |
| User | Basic operations | Read, Limited Write |
| Viewer | Read-only access | Read only |

## 📁 Project Structure

```
qr_asset_management/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── config.py                  # Configuration settings
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   └── endpoints.py       # API v1 routes
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── assets.py          # Asset management endpoints
│   │   │   ├── categories.py      # Category management endpoints
│   │   │   ├── users.py           # User management endpoints
│   │   │   └── roles.py           # Role management endpoints
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # Pydantic schemas
│   │   │   ├── assets.py
│   │   │   └── common.py
│   │   └── dtos/
│   │       ├── __init__.py
│   │       └── common.py          # Data Transfer Objects
│   ├── application/
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── asset_service.py   # Business logic services
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   └── asset_usecases.py  # Use case implementations
│   │   └── dto/
│   │       ├── __init__.py
│   │       └── commands.py        # Command patterns
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   ├── asset.py           # Asset entity
│   │   │   ├── user.py            # User entity
│   │   │   └── category.py        # Category entity
│   │   ├── value_objects/
│   │   │   ├── __init__.py
│   │   │   ├── qr_code.py         # QR code value object
│   │   │   └── asset_status.py    # Status value object
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   └── asset_repository.py # Repository interface
│   │   └── services/
│   │       ├── __init__.py
│   │       └── qr_generator.py    # Domain service for QR
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── database.py        # Database connection
│   │   │   └── session.py         # Async session
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   └── sqlalchemy_asset.py # SQLAlchemy implementation
│   │   ├── security/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # JWT handlers
│   │   │   └── rbac.py            # Role-based access control
│   │   └── external/
│   │       ├── __init__.py
│   │       └── qr_service.py      # External QR API client
│   └── interfaces/
│       └── web/
│           ├── __init__.py
│           ├── templates/
│           │   ├── base.html
│           │   ├── index.html
│           │   ├── login.html
│           │   └── assets/
│           └── static/
│               ├── css/
│               ├── js/
│               └── img/
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
│   ├── architecture.md
│   ├── api_specification.md
│   └── deployment_guide.md
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── TASKS.md
└── PROJECT.md
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit

# Run integration tests
pytest tests/integration

# Test coverage
pytest --cov=app --cov-report=html
```

## 🚀 Deployment

### Production Build

```bash
# Build Docker images
docker-compose build

# Push to container registry
docker-compose push

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | qr_assets |
| `DB_USER` | Database user | postgres |
| `DB_PASSWORD` | Database password | secret |
| `SECRET_KEY` | JWT secret key | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | 30 |
| `ALCHEMY_API_KEY` | Alchemy QR API key | - |

## 📊 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/login | User login |
| POST | /api/v1/auth/logout | User logout |
| POST | /api/v1/auth/refresh | Refresh token |

### Assets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/assets | List assets |
| POST | /api/v1/assets | Create asset |
| GET | /api/v1/assets/{id} | Get asset |
| PUT | /api/v1/assets/{id} | Update asset |
| DELETE | /api/v1/assets/{id} | Delete asset |
| GET | /api/v1/assets/{id}/qr | Generate QR code |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

For questions or support, please open an issue in the repository.

---

**Built with ❤️ using Python, FastAPI, and PostgreSQL**