# Docker - Ejemplo de Selenium  Noticias Google / Bing

## Descripción
Este contenedor Docker ejecuta un script Python con Selenium de ejemplo que:
- Accede a Google / Bing
- Busca "Noticias" con la fecha del día actual
- Extrae el título, URL y descripción del primer resultado
- Guarda el resultado en un archivo JSON

---

## 📦 Requisitos Previos

### Para instalar Docker
- **Windows/Mac**: Descargar [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: Ejecutar:
  ```bash
  sudo apt-get update
  sudo apt-get install docker.io docker-compose
  ```

### Verificar instalación
```bash
docker --version
docker-compose --version
```

---

## � Descargar desde GitHub

### Opción A: Clonar el repositorio (Recomendado)

1. **Abrir PowerShell o CMD** en la carpeta donde quieras descargar el proyecto

2. **Ejecutar**:
   ```bash
   git clone https://github.com/sorrento/docker-selenium-example.git
   cd docker-selenium-example
   ```

3. **Listo**, ahora tienes todos los archivos en tu máquina

### Opción B: Descargar como ZIP

1. Ir a: https://github.com/sorrento/docker-selenium-example
2. Click en **Code** > **Download ZIP**
3. Extraer la carpeta descargada
4. Listo para usar

---

## �🚀 Instalación y Ejecución

### Opción 1: Windows - Hacer doble clic (MÁS FÁCIL)

1. **Descargar/Copiar la carpeta** `DOCKER_DUMMY` en tu máquina

2. **Hacer doble clic en** `ejecutar.bat`

3. El script automáticamente:
   - Verifica que Docker esté instalado ✓
   - Verifica que Docker esté corriendo ✓
   - Construye la imagen
   - Ejecuta el contenedor
   - Muestra si hubo errores

4. **Ver resultados**:
   - El archivo `resultado_busqueda.json` estará en la carpeta

### Opción 2: Con Docker Compose (Terminal)

1. **Descargar/Copiar la carpeta** `DOCKER_DUMMY` en tu máquina

2. **Abrir PowerShell o CMD** en la carpeta

3. **Construir la imagen**:
   ```bash
   docker-compose build
   ```

4. **Ejecutar el contenedor**:
   ```bash
   docker-compose up
   ```

5. **Ver resultados**:
   - El archivo `resultado_busqueda.json` se guardará en la carpeta

### Opción 2: Con Docker Directo

1. **Construir la imagen**:
   ```bash
   docker build -t google-scraper .
   ```

2. **Ejecutar el contenedor**:
   ```bash
   docker run -v "%cd%/output:/app/output" google-scraper
   ```
   
   (En Linux/Mac usar `${PWD}` en lugar de `%cd%`)

---

## 📋 Archivos Incluidos

| Archivo | Descripción |
|---------|-------------|
| `Dockerfile` | Define la imagen Docker (Python + Selenium + Chrome) |
| `requirements.txt` | Dependencias Python necesarias |
| `search_google.py` | Script principal de web scraping |
| `docker-compose.yml` | Configuración para Docker Compose |
| `ejecutar.bat` | Script para Windows - ejecutar con doble clic |
| `run.sh` | Script para Linux/Mac - ejecutar con ./run.sh |
| `INSTALACION.md` | Este archivo |

---

## ⏰ Ejecución Programada (Automatizada)

### En Windows (Task Scheduler)

1. **Crear script batch** `ejecutar_scraper.bat`:
   ```batch
   @echo off
   cd /d "C:\ruta\a\tu\DOCKER_DUMMY"
   docker-compose up --remove-orphans
   pause
   ```

2. **Abrir Task Scheduler**:
   - Presionar `Windows + R`
   - Escribir `taskschd.msc`

3. **Crear tarea**:
   - Click derecho > "Crear tarea básica"
   - Nombre: "Google News Scraper"
   - Trigger: Diario a las 08:00 AM (o la hora que desees)
   - Action: Ejecutar programa `ejecutar_scraper.bat`

### En Linux/Mac (Cron)

1. **Abrir crontab**:
   ```bash
   crontab -e
   ```

2. **Agregar línea** (ejemplo: 8 AM cada día):
   ```bash
   0 8 * * * cd /home/usuario/DOCKER_DUMMY && docker-compose up --remove-orphans
   ```

3. **Guardar y salir** (Ctrl+X, luego S)

### En Linux/Mac con Systemd (Alternativa)

1. **Crear archivo** `/etc/systemd/system/google-scraper.service`:
   ```ini
   [Unit]
   Description=Google News Scraper
   After=docker.service
   Requires=docker.service

   [Service]
   Type=oneshot
   WorkingDirectory=/home/usuario/DOCKER_DUMMY
   ExecStart=/usr/bin/docker-compose up

   [Install]
   WantedBy=multi-user.target
   ```

2. **Crear timer** `/etc/systemd/system/google-scraper.timer`:
   ```ini
   [Unit]
   Description=Google News Scraper Timer
   Requires=google-scraper.service

   [Timer]
   OnCalendar=daily
   OnCalendar=08:00
   Persistent=true

   [Install]
   WantedBy=timers.target
   ```

3. **Activar**:
   ```bash
   sudo systemctl enable google-scraper.timer
   sudo systemctl start google-scraper.timer
   ```

---

## 🔍 Cómo Compartir con Terceros

### Paso 1: Preparar los archivos
Asegúrate de tener estos archivos en la carpeta:
- `Dockerfile`
- `requirements.txt`
- `search_google.py`
- `docker-compose.yml`
- `INSTALACION.md` (este archivo)

### Paso 2: Empaquetar
**Opción A - Comprimir carpeta**:
```bash
# Windows
tar.exe -a -c -f DOCKER_DUMMY.zip DOCKER_DUMMY

# Linux/Mac
zip -r DOCKER_DUMMY.zip DOCKER_DUMMY
```

**Opción B - Git**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin [tu-repositorio]
git push -u origin main
```

### Paso 3: Compartir
- Enviar archivo ZIP por email
- Compartir repositorio Git
- Usar servicios como Google Drive, Dropbox, etc.

### Instrucciones para el receptor
El tercero debe:
1. Descomprimir la carpeta
2. Instalar Docker Desktop (si no lo tiene)
3. Abrir terminal en la carpeta
4. Ejecutar: `docker-compose build && docker-compose up`

---

## 📊 Resultado Esperado

### Archivo `resultado_busqueda.json`
```json
{
  "timestamp": "2025-12-17T14:30:45.123456",
  "search_query": "Noticias 17/12/2025",
  "result": {
    "title": "Título de la noticia",
    "url": "https://ejemplo.com/noticia",
    "snippet": "Descripción/preview de la noticia..."
  }
}
```

---

## 🐛 Solución de Problemas

### Error: "No se encontraron resultados"
- **Causa**: Google está bloqueando el acceso desde navegadores automatizados
- **Solución**: 
  1. Espera 15-30 minutos
  2. Vuelve a intentar ejecutando el script de nuevo
  3. Google puede haber detectado demasiados accesos automatizados

### Error: "Docker no está corriendo"
- **Solución**: 
  1. Abre Docker Desktop
  2. Espera a que el icono esté en verde (completamente iniciado)
  3. Espera 30 segundos más
  4. Vuelve a ejecutar el script

### Error: "docker: command not found"
- **Solución**: Instalar Docker Desktop o verificar la instalación

---

## 🔧 Personalización

### Cambiar hora de ejecución (cron)
```bash
# Cada día a las 9 AM
0 9 * * * ...

# Cada lunes a las 8 AM
0 8 * * 1 ...

# Cada 6 horas
0 */6 * * * ...
```

### Cambiar búsqueda
Editar línea en `search_google.py`:
```python
search_query = "Tu búsqueda personalizada"
```

### Cambiar zona horaria
Editar `docker-compose.yml`:
```yaml
environment:
  - TZ=Europe/Madrid  # O tu zona horaria
```

---

## 📞 Soporte

Si encuentra problemas:
1. Verificar los logs: `docker-compose logs -f`
2. Revisar que Chrome y ChromeDriver estén en la imagen
3. Aumentar timeouts si la conexión es lenta
4. Verificar que Google no está bloqueando la IP

---

## 📄 Licencia
Este script es de uso libre para propósitos internos.
