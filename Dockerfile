# syntax=docker/dockerfile:1

# ---- base: runtime dependencies and application code ----
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
# Copy requirements first, so this layer is cached until dependencies change
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app

# ---- test: adds dev dependencies and tests (used by Jenkins) ----
FROM base AS test
COPY requirements-dev.txt pytest.ini ./
RUN pip install -r requirements-dev.txt
COPY tests ./tests
CMD ["pytest", "-q"]

# ---- runtime: small final image, runs as a normal user ----
FROM base AS runtime
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
