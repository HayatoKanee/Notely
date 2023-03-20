web: daphne notely.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: celery -A notely worker --loglevel=info --concurrency=2
