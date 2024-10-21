# FastAPI License Plate OCR App

This is a FastAPI application that provides functionality for license plate object detection and recognition. The project includes user authentication, email verification, and other RESTful endpoints.

## Prerequisites

Make sure you have the following installed:
- Docker & Docker Compose
- Python 3.12+
- Git

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/fastapi-lpocr-app.git
cd fastapi-lpocr-app
```

### 2. Set up the environment variables

```bash
# MAIL
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_PORT=
MAIL_SERVER=

# POSTGRESQL Database Config -use
POSTGRESQL_HOST=
POSTGRESQL_USER=
POSTGRESQL_PASSWORD=
POSTGRESQL_PORT=
POSTGRESQL_DB=

# REDIS
REDIS_HOST=
REDIS_PORT=
REDIS_URL=

# JWT Secret Key
JWT_SECRET=
JWT_ALGORITHM=

# App Secret Key
SECRET_KEY=
```

### 3. Build and Run with Docker Compose
```bash
docker-compose up --build -d
```

### 4. run project
```bash
fastapi dev
```