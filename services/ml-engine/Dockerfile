# ----  Builder ----
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create a Virtual Env in the /opt/venv directory
RUN python -m venv /opt/venv
# Ensure that pip uses the venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Runtime ----
FROM python:3.10-slim

WORKDIR /app

# Security: create the 'prism' user
RUN groupadd -r prism && useradd -r -g prism prism

# Copy the entire virtual env from the builder
COPY --from=builder /opt/venv /opt/venv

# Add the bin folder of the venv to the global PATH of the container
# This is what allows "uvicorn" to be found directly
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

COPY --chown=prism:prism . .

USER prism
EXPOSE 8000

# "uvicorn" will be found in /opt/venv/bin/uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]