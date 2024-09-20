FROM python:3.9-slim

WORKDIR /app

COPY reqs.txt .
RUN pip install --no-cache-dir -r reqs.txt

COPY . .

CMD ["sh", "-c", "sleep 20s && python -e PYTHONUNBUFFERED=1 -e PYTHONDONTWRITEBYTECODE=1 crawler.py"]
