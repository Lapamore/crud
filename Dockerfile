# 1. Base Image
FROM python:3.10-slim

# 2. Set Environment Variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set Work Directory
WORKDIR /app

# 4. Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Application Code and Alembic config
COPY alembic.ini .
COPY migrations /app/migrations
COPY ./src /app/src

# 6. Expose Port
EXPOSE 8000

# 7. Run Application
CMD ["/usr/local/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "10000"]