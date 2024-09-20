# Use an official Python runtime as a parent image
FROM python:3.9-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /testApp


COPY reqs.txt /testApp/


RUN pip install -r reqs.txt


COPY . /testApp/


EXPOSE 8000


CMD ["pip freeze","python", "manage.py", "runserver", "0.0.0.0:8000"]
