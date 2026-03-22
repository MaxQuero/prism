# ---- Étape 1 : Builder ----
FROM python:3.10-slim AS builder

WORKDIR /app

# On installe les outils de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# On crée un Virtual Env dans le dossier /opt/venv
RUN python -m venv /opt/venv
# On s'assure que pip utilise le venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Étape 2 : Runtime ----
FROM python:3.10-slim

WORKDIR /app

# Sécurité : création de l'utilisateur
RUN groupadd -r prism && useradd -r -g prism prism

# On récupère TOUT le virtual env du builder
COPY --from=builder /opt/venv /opt/venv

# On ajoute le dossier bin du venv au PATH global du container
# C'est ÇA qui permet de trouver "uvicorn" directement
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

COPY --chown=prism:prism . .

USER prism
EXPOSE 8000

# Maintenant, "uvicorn" sera trouvé dans /opt/venv/bin/uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]