FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# COPY . /app (workdir=/app, context=backend/) flattens the contents of the
# backend/ directory into /app/. This accidentally copies backend/__init__.py
# to /app/__init__.py, which makes Python treat the whole /app tree as a
# single namespace package and breaks top-level app imports.
# Remove it so /app stays a plain directory on sys.path.
RUN rm -f /app/__init__.py

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
