export LANG=C.UTF-8

gunicorn — bind=0.0.0.0 — timeout 600 PungDuc_BE.wsgi & celery -A PungDuc_BE worker -l info -P gevent & celery -A PungDuc_BE beat -l INFO