FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    GUNICORN_CMD_ARGS="--bind 0.0.0.0:8000 --workers 2 --threads 4 --access-logfile - --error-logfile - --graceful-timeout 30 --timeout 60"

WORKDIR /app/backend

COPY backend/requirements.txt /tmp/requirements.txt
RUN groupadd --system pubia \
    && useradd --system --gid pubia --create-home --home-dir /home/pubia pubia \
    && python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

COPY --chown=pubia:pubia backend/ /app/backend/

USER pubia

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "from urllib.request import urlopen; response = urlopen('http://127.0.0.1:8000/health', timeout=3); raise SystemExit(0 if response.status == 200 else 1)"

CMD ["gunicorn", "pubia.wsgi:app"]
