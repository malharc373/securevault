# 🔐 SecureVault

A production-ready REST API for securely storing and managing secrets, built with Flask, PostgreSQL, and Docker. Features JWT authentication, bcrypt password hashing, rate limiting, and a fully automated CI/CD pipeline.

**Live API:** https://securevault-1-s9jl.onrender.com

***

## Features

- 🔑 **JWT Authentication** — stateless, token-based auth with 1-hour expiry
- 🔒 **bcrypt Password Hashing** — passwords never stored in plain text
- 🗄️ **PostgreSQL** — persistent, relational secret storage
- 🗑️ **Full CRUD** — create, read, and delete secrets
- 🚦 **Rate Limiting** — brute force protection on auth endpoints
- 🐳 **Dockerized** — fully containerized with Docker Compose
- ⚙️ **CI/CD Pipeline** — GitHub Actions auto-deploys to Render on every push

***

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Flask |
| Database | PostgreSQL |
| ORM | Flask-SQLAlchemy |
| Auth | PyJWT + bcrypt |
| Rate Limiting | Flask-Limiter |
| Server | Gunicorn |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions → Render |

***

## Project Structure

```
SecureVault/
├── app/
│   ├── main.py           # All routes and app logic
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Container definition
├── docker-compose.yml    # Multi-service orchestration
└── .github/
    └── workflows/
        └── deploy.yml    # CI/CD pipeline
```

***

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+

### Run Locally

```bash
# Clone the repo
git clone https://github.com/malharc373/securevault.git
cd securevault

# Start the API and PostgreSQL
docker compose up --build

# Initialize the database (first time only)
curl http://localhost:5001/init-db
```

The API will be available at `http://localhost:5001`.

***

## API Reference

### Authentication

#### `POST /register`
Register a new user.

**Rate limit:** 5 requests/minute

```bash
curl -X POST http://localhost:5001/register \
  -H "Content-Type: application/json" \
  -d '{"username": "malhar", "password": "test123"}'
```

**Response:**
```json
{ "message": "User created ✅" }
```

***

#### `POST /login`
Login and receive a JWT token.

**Rate limit:** 10 requests/minute

```bash
curl -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{"username": "malhar", "password": "test123"}'
```

**Response:**
```json
{ "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

***

### Secrets

All secrets endpoints require the `Authorization: Bearer <token>` header.

#### `POST /secrets`
Store a new secret.

```bash
curl -X POST http://localhost:5001/secrets \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "github_token", "value": "ghp_supersecret123"}'
```

**Response:**
```json
{ "message": "Secret stored ✅" }
```

***

#### `GET /secrets`
Retrieve all secrets for the authenticated user.

```bash
curl http://localhost:5001/secrets \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
[
  { "id": 1, "name": "github_token", "value": "ghp_supersecret123" }
]
```

***

#### `DELETE /secrets/<id>`
Delete a secret by ID.

```bash
curl -X DELETE http://localhost:5001/secrets/1 \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{ "message": "Secret deleted ✅" }
```

***

#### `GET /me`
Get the authenticated user's profile.

```bash
curl http://localhost:5001/me \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{ "id": 1, "username": "malhar" }
```

***

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing secret | `fallback` (change in prod!) |

Set these in Render's environment settings or a local `.env` file.

***

## CI/CD Pipeline

Every push to `main` triggers an automatic deployment to Render via GitHub Actions.

```
git push → GitHub Actions → Render Deploy Hook → Live in ~60s
```

To set up:
1. Get your deploy hook from Render → Settings → Deploy Hook
2. Add it as `RENDER_DEPLOY_HOOK` in GitHub → Settings → Secrets → Actions

***

## Deployment (Render)

1. Create a **PostgreSQL** database on Render
2. Create a **Web Service** pointing to this repo
3. Set environment variables: `DATABASE_URL`, `SECRET_KEY`
4. Hit `/init-db` once after first deploy to create tables
5. Add `RENDER_DEPLOY_HOOK` to GitHub secrets for auto-deploy

***

## Security Notes

- Passwords are hashed with **bcrypt** before storage — never stored plain
- JWT tokens expire after **1 hour**
- Rate limiting prevents brute force on `/login` and `/register`
- Change `SECRET_KEY` to a strong random value in production

***

## License

MIT