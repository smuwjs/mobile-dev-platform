FROM python:3.12-slim
WORKDIR /app
RUN pip install fastapi sqlalchemy asyncpg celery redis python-jose pydantic pydantic-settings uvicorn alembic passlib
COPY app ./app
COPY pyproject.toml ./
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
