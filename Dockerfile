FROM python:3.13-alpine

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD ps aux | grep -v grep | grep main.py > /dev/null || exit 1

CMD ["python", "-u", "/app/main.py"]