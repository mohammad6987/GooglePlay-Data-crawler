FROM python:3.9-slim

WORKDIR /app
ENV PYTHONUNBUFFERED 1
COPY reqs.txt .
RUN pip install -r reqs.txt

COPY . .

CMD ["sh", "-c", "sleep 5s && python -e PYTHONUNBUFFERED=1 -e PYTHONDONTWRITEBYTECODE=1 DBMS.py"]
