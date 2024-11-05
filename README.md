# FastAPI License Plate OCR App

This is a FastAPI application that provides functionality for license plate object detection and recognition. The project includes user authentication, email verification, and other RESTful endpoints.

## Prerequisites

Make sure you have the following installed:
- Docker & Docker Compose
- Python 3.12+
- Git

## Getting Started for backend

### 1. Clone the repository

```bash
git clone https://github.com/your-username/fastapi-lpocr-app.git
cd fastapi-lpocr-app
```

### 2. Set up the environment variables 
```bash
#for secret
import secrets
secrets.token_hex(20)
```

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
JWT_SECRET={secret}
JWT_ALGORITHM=

# App Secret Key
SECRET_KEY={secret}
```

### 3. Build and Run with Docker Compose
```bash
docker-compose up --build -d
```

### 4. Create a Virtual Environment
```bash
# create venv
python -m venv .venv

# activate for mac
source .venv/bin/activate
# activate for window
.venv\Scripts\Activate.ps1

# install lib in requirement
pip install -r requirements.txt
```
### 5. add ocr folder to path app/routes


### 6. run project
```bash
fastapi dev
```

### warning
please install pytorch cuda before run don't use cpu
- uninstall to torchvision first and
- install nvidia cudnn
- install pytorch cuda https://pytorch.org/get-started/locally/


```bash
 #plz del  ``` ``` after create db in postgresql and ``` ``` it again for create table in db and role
 # cuz i forgot install alembic for migration haha sorry
'''
@app.on_event("startup")
async def startup_event():
    await init_db()
'''
```