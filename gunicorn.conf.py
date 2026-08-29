"""Gunicorn production settings with privacy-preserving access logs."""

workers = 2
threads = 4
timeout = 30
accesslog = "-"
errorlog = "-"

# Do not log the path, query string, referrer, or request line. Newsletter
# confirmation URLs contain one-time credentials and must not enter access logs.
access_log_format = '%(h)s %(t)s "%(m)s" %(s)s %(b)s %(L)s "%(a)s"'
