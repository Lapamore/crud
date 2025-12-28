FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY migrations /app/migrations
COPY ./src /app/src

CMD ["/usr/local/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]