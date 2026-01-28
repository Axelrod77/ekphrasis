FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir \
    "fastapi>=0.104.0" \
    "uvicorn[standard]>=0.24.0" \
    "sqlalchemy[asyncio]>=2.0.23" \
    "asyncpg>=0.29.0" \
    "alembic>=1.13.0" \
    "python-jose[cryptography]>=3.3.0" \
    "passlib[bcrypt]>=1.7.4" \
    "bcrypt==4.0.1" \
    "pydantic[email]>=2.5.0" \
    "pydantic-settings>=2.1.0" \
    "httpx>=0.25.0" \
    "beautifulsoup4>=4.12.0" \
    "pdfplumber>=0.10.0" \
    "celery[redis]>=5.3.0" \
    "redis>=5.0.0" \
    "python-multipart>=0.0.6" \
    "aiofiles>=23.2.0"
COPY . .
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
