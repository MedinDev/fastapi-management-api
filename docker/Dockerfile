# Multi-stage build for optimization 
 
 # Builder stage 
 FROM python:3.11-slim as builder 
 
 WORKDIR /app 
 
 # Install system dependencies 
 RUN apt-get update && apt-get install -y \ 
     gcc \ 
     g++ \ 
     libffi-dev \ 
     && rm -rf /var/lib/apt/lists/* 
 
 # Install Poetry 
 RUN pip install poetry==1.7.0 
 
 # Copy dependency files 
 COPY pyproject.toml poetry.lock ./ 
 
 # Install dependencies 
 RUN poetry config virtualenvs.create false \ 
     && poetry install --no-interaction --no-ansi --no-root --only main 
 
 # Runtime stage 
 FROM python:3.11-slim 
 
 WORKDIR /app 
 
 # Install runtime system dependencies 
 RUN apt-get update && apt-get install -y \ 
     libpq-dev \ 
     curl \ 
     && rm -rf /var/lib/apt/lists/* 
 
 # Copy installed packages from builder 
 COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages 
 COPY --from=builder /usr/local/bin /usr/local/bin 
 
 # Copy application code 
 COPY . . 
 
 # Create non-root user 
 RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app 
 USER appuser 
 
 # Health check 
 HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \ 
     CMD curl -f http://localhost:8000/health || exit 1 
 
 EXPOSE 8000 
 
 CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]