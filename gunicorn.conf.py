import os

# Number of worker processes
workers = int(os.environ.get('GUNICORN_PROCESSES', '3'))
# Number of threads per worker
threads = int(os.environ.get('GUNICORN_THREADS', '4'))
# Request timeout
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '15'))

# Bind to port 443
bind = os.environ.get('GUNICORN_BIND', 'urban.evl.uic.edu:443')

# SSL configuration
certfile = os.environ.get('GUNICORN_CERTFILE', '/etc/ssl/certs/_.evl.uic.edu.crt')
keyfile = os.environ.get('GUNICORN_KEYFILE', '/etc/ssl/private/_.evl.uic.edu.key')

# Allow forwarded IPs if necessary (useful when behind certain types of proxies)
forwarded_allow_ips = os.environ.get('GUNICORN_FORWARDED_ALLOW_IPS', '*')

# Logging configuration (optional)
accesslog = os.environ.get('GUNICORN_ACCESSLOG', '-')
errorlog = os.environ.get('GUNICORN_ERRORLOG', '-')
loglevel = os.environ.get('GUNICORN_LOGLEVEL', 'info')

# IMPORTANT: Use an ASGI worker class for FastAPI
worker_class = "uvicorn.workers.UvicornWorker"
