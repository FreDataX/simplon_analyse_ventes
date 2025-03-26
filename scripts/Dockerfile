FROM python:3.11-slim

WORKDIR /app

# Installe les dépendances nécessaires (ajuste selon tes besoins réels)
RUN apt-get update && apt-get install -y sqlite3
COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Ajoute scripts
COPY . .

CMD ["python", "main.py"]