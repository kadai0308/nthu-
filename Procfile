release: python manage.py migrate
web: daphne course.channels.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2 --http-timeout 6000
worker: python manage.py runworker -v2