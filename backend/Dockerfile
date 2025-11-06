# ---- Builder Stage ----
FROM python:3.11.4-slim-buster AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Final Stage ----
FROM python:3.11.4-slim-buster AS final

WORKDIR /app

# Optional: Create app user for non-root execution
RUN useradd -m appuser

# Copy dependencies
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy rest of app, preserve ownership and permissions
COPY . .

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to appuser
USER appuser

EXPOSE 5000

# Entrypoint
CMD ["python", "app.py"]
