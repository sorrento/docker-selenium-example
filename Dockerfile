FROM python:3.11-slim

# Instalar dependencias del sistema para Selenium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar paquetes Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar script de búsqueda
COPY search_google.py .

# Ejecutar el script
CMD ["python", "search_google.py"]
