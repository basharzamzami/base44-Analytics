# Base44 - Palantir-for-SMBs Platform

Base44 is a multi-tenant, modular analytics platform designed for small and medium businesses (SMBs). It provides Palantir-like capabilities including data ingestion, normalization, KPI monitoring, graph analysis, and AI-powered insights in an SMB-appropriate package.

## Features

- **Multi-tenant Architecture**: Row-level tenant isolation with X-Tenant-ID header enforcement
- **Data Ingestion**: CSV upload and live connector support (HubSpot, Google Ads)
- **LLM-powered Normalization**: AI-assisted field mapping and data transformation
- **KPI Engine**: Real-time KPI calculation and monitoring
- **Alert System**: Rule-based alerts with anomaly detection
- **Graph Analysis**: Entity relationship exploration and link analysis
- **AI Assistant**: Natural language query interface with actionable insights
- **Dashboard**: Real-time visualization of KPIs, alerts, and tasks

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (primary), Neo4j (graph), Redis (cache)
- **Frontend**: React (Vite)
- **AI/ML**: LangChain, OpenAI, scikit-learn, Prophet
- **Infrastructure**: Docker, Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (optional, for AI features)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd base44
```

2. Set environment variables:
```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

3. Start the services:
```bash
docker-compose up -d
```

4. Wait for all services to be healthy (check with `docker-compose ps`)

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Demo Script

Run the demo script to see Base44 in action:

```bash
./scripts/demo_run.sh
```

This will:
1. Create two sample tenants
2. Upload sample CSV data
3. Trigger data normalization
4. Calculate KPIs
5. Generate alerts
6. Test the AI assistant
7. Create tasks from suggestions

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register tenant and admin user
- `POST /api/v1/auth/login` - Login with email/password
- `GET /api/v1/auth/me` - Get current user info

### Tenants
- `GET /api/v1/tenants/{id}` - Get tenant configuration

### Connectors
- `POST /api/v1/connectors` - Create connector
- `GET /api/v1/connectors` - List connectors
- `POST /api/v1/connectors/{id}/sync` - Trigger sync
- `GET /api/v1/connectors/{id}/map_preview` - Get field mapping suggestions

### KPIs
- `GET /api/v1/kpis` - List KPI definitions
- `POST /api/v1/kpis` - Create KPI definition
- `POST /api/v1/kpis/{id}/evaluate` - Evaluate KPI
- `GET /api/v1/kpis/{id}/values` - Get KPI values

### Alerts
- `GET /api/v1/alerts` - List alerts
- `POST /api/v1/alerts/{id}/ack` - Acknowledge alert
- `POST /api/v1/alerts/{id}/resolve` - Resolve alert

### AI Assistant
- `POST /api/v1/ask` - Ask natural language questions

### Dashboard
- `GET /api/v1/dashboard/{id}` - Get dashboard data

## Data Model

### Core Tables
- `tenants` - Tenant information and configuration
- `users` - User accounts with role-based access
- `connectors` - Data source configurations
- `raw_ingest` - Raw data from connectors
- `normalized_records` - Canonical data after transformation
- `kpi_definitions` - KPI calculation rules
- `kpi_values` - Calculated KPI values over time
- `alerts` - Alert definitions and instances
- `graph_nodes` - Entity nodes for graph analysis
- `graph_edges` - Relationships between entities
- `tasks` - Human-in-the-loop task management
- `audit_logs` - Activity tracking
- `annotations` - User annotations on records

## Vertical Support

Base44 includes pre-configured ontologies for:
- Marketing Agencies
- Urgent Care Clinics
- Retail SMBs
- Local Police Departments

Each vertical includes:
- Standardized data schemas
- Pre-defined KPIs
- Default alert rules
- Industry-specific insights

## Security

- JWT-based authentication
- Row-level tenant isolation
- Encrypted credential storage
- Audit logging
- RBAC (Role-Based Access Control)

## Development

### Running Tests

```bash
cd backend
python -m pytest app/tests/
```

### Database Migrations

```bash
cd backend
alembic upgrade head
```

### Adding New Connectors

1. Create connector class in `app/services/connectors/`
2. Implement sync logic
3. Add to connector registry
4. Update frontend connector UI

## Deployment

### Production Setup

1. Update `docker-compose.prod.yml` with production settings
2. Set secure environment variables
3. Configure SSL/TLS
4. Set up monitoring and logging
5. Deploy to your preferred cloud provider

### Terraform Infrastructure

See `infra/terraform/` for sample AWS infrastructure setup.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add your license here]

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation at `/docs`
- Review the API documentation at `/api/docs`

