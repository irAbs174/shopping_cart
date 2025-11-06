FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc

COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
