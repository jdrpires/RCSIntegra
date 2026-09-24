# RCS Integration Gateway

> Python gateway for integrating business applications with RCS messaging providers.

**Python · FastAPI · PostgreSQL · SQLAlchemy · RCS · Webhooks · Docker**

| | |
|---|---|
| **Type** | Enterprise integration gateway |
| **Focus** | Messaging orchestration, templates, callbacks and persistence |
| **Architecture** | Client API → integration boundary → external RCS provider |
| **Status** | Public technical project |

## Overview

RCSIntegra provides an integration boundary between applications and an external RCS messaging service. It receives normalized requests, validates and persists messaging data, communicates with the provider and records callbacks and delivery state.

The project demonstrates a pattern I use frequently in enterprise systems: **keep external-provider semantics behind a controlled integration layer instead of leaking them into the core application**.

## Architecture

```text
Business Application
        │
        ▼
  RCSIntegra API
 ┌──────┼────────┐
 │      │        │
Validation  Templates  Persistence
 │      │        │
 └──────┼────────┘
        ▼
 External RCS API
        │
        ▼
 Callbacks / Status
        │
        └──────► PostgreSQL
```

## Capabilities

- Basic RCS messages with SMS fallback.
- Single messages with templates or custom content.
- Conversational messaging through webhooks.
- Template-based conversational flows.
- Template creation and persistence.
- Delivery callbacks and response handling.
- Message and callback history.
- Phone, URL and content validation.
- Structured logging and error handling.
- REST interface with FastAPI.

Supported content includes text, images, video, PDF, suggestions, rich cards and carousels according to provider capabilities.

## Main API surface

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/rcs/basic` | Send a basic RCS message |
| `POST` | `/api/rcs/single` | Send rich/template content |
| `POST` | `/api/rcs/webhook` | Start a conversational flow |
| `POST` | `/api/rcs/templates` | Create a template |
| `GET` | `/api/messages/{message_id}` | Retrieve message state |
| `GET` | `/api/messages` | List messages |
| `POST` | `/api/rcs/callback` | Receive provider callbacks |

Interactive documentation is available at `/docs`.

## Engineering concerns

### Integration boundary

Provider-specific payloads and behavior remain inside the gateway. Client applications interact with a more controlled contract.

### Persistence

Messages, templates and callbacks are persisted so asynchronous provider behavior can be inspected and correlated.

### Validation

Input validation covers phone normalization, media URLs, content constraints and fallback handling.

### Failure handling

Provider failures are recorded rather than treated only as transient HTTP errors, improving operational diagnosis.

### Security

Provider tokens and database credentials belong in environment variables. Logs should avoid exposing sensitive data.

## Quick start

```bash
git clone https://github.com/jdrpires/RCSIntegra.git
cd RCSIntegra

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
python init_db.py
uvicorn main:app --reload
```

Example environment configuration:

```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/rcs_gateway
RCS_API_BASE_URL=https://<provider-host>
RCS_API_TOKEN=<provider-token>
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
DEBUG=False
```

> Never commit real database passwords, provider tokens or production credentials.

## Tests

The repository includes automated tests covering API behavior, validations, template substitution, content types, fallback behavior, callbacks, persistence and error scenarios.

```bash
python -m pytest tests/ -v
python -m pytest tests/ --cov=. --cov-report=term
```

## Docker

A Docker Compose environment can run the API and PostgreSQL together.

```bash
cp .env.docker .env.docker.local
# Configure secrets locally.

docker-compose --env-file .env.docker.local up -d
docker-compose ps
docker-compose logs -f rcs_gateway
```

## Project structure

```text
RCSIntegra/
├── main.py
├── models.py
├── schemas.py
├── database.py
├── rcs_client.py
├── services.py
├── init_db.py
├── examples.py
├── tests/
├── requirements.txt
└── .env.example
```

## Why this project is public

This repository is part of my public engineering portfolio and demonstrates enterprise integration patterns, asynchronous messaging workflows, API boundaries, persistence and provider isolation.

---

**Jean Pires** · [GitHub](https://github.com/jdrpires) · [Portfolio](https://github.com/jdrpires/jdrpires)
