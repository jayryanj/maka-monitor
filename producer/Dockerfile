FROM python:3.9-slim

WORKDIR /app

COPY . .

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "maka_monitor.py"]