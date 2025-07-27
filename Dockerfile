# ===== Dockerfile =====
# FROM python:3.10-slim
# 
# LABEL maintainer="Security Team <security@company.com>"
# LABEL description="Badg3rFuzz - Security auditing tool"
# LABEL version="1.0.0"
# 
# # Variables de entorno
# ENV PYTHONUNBUFFERED=1
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV DISPLAY=:99
# ENV MOZ_HEADLESS=1
# 
# # Crear usuario no-root para seguridad
# RUN groupadd -r badg3r && useradd -r -g badg3r -s /bin/bash badg3r
# 
# # Instalar dependencias del sistema
# RUN apt-get update && apt-get install -y \
#     firefox-esr \
#     chromium \
#     xvfb \
#     wget \
#     unzip \
#     openssl \
#     ca-certificates \
#     && rm -rf /var/lib/apt/lists/*
# 
# # Crear directorio de trabajo
# WORKDIR /app
# 
# # Copiar archivos de dependencias
# COPY requirements.txt requirements-dev.txt ./
# 
# # Instalar dependencias de Python
# RUN pip install --no-cache-dir --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt
# 
# # Descargar WebDrivers
# RUN mkdir -p /app/drivers && \
#     cd /app/drivers && \
#     wget -O geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-v0.33.0-linux64.tar.gz" && \
#     tar -xzf geckodriver.tar.gz && \
#     chmod +x geckodriver && \
#     wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" && \
#     unzip chromedriver.zip && \
#     chmod +x chromedriver && \
#     rm *.tar.gz *.zip
# 
# # Copiar código fuente
# COPY . .
# 
# # Cambiar propietario a usuario no-root
# RUN chown -R badg3r:badg3r /app
# 
# # Cambiar a usuario no-root
# USER badg3r
# 
# # Configurar PATH para WebDrivers
# ENV PATH="/app/drivers:${PATH}"
# 
# # Puerto por defecto (si aplicable)
# EXPOSE 8080
# 
# # Healthcheck
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1
# 
# # Comando por defecto
# CMD ["python", "badg3rfuzz.py", "--help"]