FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first so the layer caches across code-only changes.
COPY requirements.txt .
RUN pip install -r requirements.txt \
 && python -m spacy download en_core_web_sm

COPY analyzer/ ./analyzer/
COPY templates/ ./templates/
COPY static/ ./static/
COPY app.py ./

# Drop privileges.
RUN useradd --create-home --uid 1000 appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Single worker — analysis is CPU-bound and the 512 MB machine only fits one
# resident spaCy model. Raise --timeout for long texts.
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "1", \
     "--threads", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
