FROM python:3.13 AS base
WORKDIR /datavisyn

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmagic-dev \
    libpq-dev \ 
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000


FROM base AS test
CMD ["pytest", "-vv"]


FROM base AS production
CMD ["uvicorn", "datavisyn_project.core.base:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]