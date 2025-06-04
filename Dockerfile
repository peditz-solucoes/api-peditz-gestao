FROM python:3.12-slim-bullseye AS production

ARG DATABASE_URL=sqlite:///build.db

WORKDIR /app

# Instala pacotes necessários para compilar dependências
RUN apt-get update && apt-get install -y \
    gcc \
    dumb-init \
    libpq-dev \
    python3-dev \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Define localizações para evitar problemas com encoding
ENV LANG=pt_BR.UTF-8 \
    LANGUAGE=pt_BR.UTF-8 \
    LC_ALL=pt_BR.UTF-8 \
    PYTHONUNBUFFERED=1

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do projeto
COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["uvicorn", "peditz.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
