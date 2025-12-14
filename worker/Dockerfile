FROM python:3.12-slim

WORKDIR /app

COPY services/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "services.RunTasks", "worker", "--loglevel=info"]
