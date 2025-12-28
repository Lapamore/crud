FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app/src

WORKDIR /app/src

COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./src /app/src
COPY ./alembic.ini /app/alembic.ini
COPY ./migrations /app/migrations

EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port 8000