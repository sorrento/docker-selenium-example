# Docker - Ejemplo de Selenium  Noticias Google / Bing

## Descripción
Este contenedor Docker ejecuta un script Python con Selenium de ejemplo que:
- Accede a Google / Bing
- Busca "Noticias" con la fecha del día actual
- Extrae el título, URL y descripción del primer resultado
- Guarda el resultado en un archivo JSON

---

## 1 📦 Requisitos Previos

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

## 2 Descargar desde GitHub 

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

### Paso 1: Verificar que Docker está corriendo
- En Windows: Abre **Docker Desktop** y espera a que el icono esté en verde
- En Linux/Mac: Abre una terminal y verifica con `docker --version`

### Paso 2: Abrir terminal en la carpeta DOCKER_DUMMY
- Windows: Usa PowerShell o CMD
- Linux/Mac: Abre Terminal
- Navega a la carpeta del proyecto

### Paso 3: Construir la imagen Docker

```bash
docker-compose build
```

Esta es la primera vez que ejecutas. Espera a que termine (descarga e instala todo).

### Paso 4: Ejecutar el contenedor

```bash
docker-compose up
```

El contenedor se ejecutará, realizará la búsqueda y guardará el resultado en `resultado_busqueda.json`.

### Paso 5: Ver resultados

Cuando el contenedor termine, verás un archivo `resultado_busqueda.json` en la carpeta con los resultados de la búsqueda.

---

## 📋 Comando Alternativo (Docker Directo)

Si prefieres no usar docker-compose:

```bash
docker build -t google-scraper .
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
| `resultado_busqueda.json` | Archivo de salida con los resultados |
| `output/` | Carpeta donde se guardan los resultados |

---

## ⏰ Ejecución Programada (Automatizada)

### En Windows (Task Scheduler)

1. **Abrir Task Scheduler**:
   - Presionar `Windows + R`
   - Escribir `taskschd.msc`

2. **Crear tarea**:
   - Click derecho > "Crear tarea básica"
   - Nombre: "Google News Scraper"
   - Trigger: Diario a las 08:00 AM (o la hora que desees)
   - Action: Ejecutar `powershell.exe` con argumentos:
     ```
     -Command "cd 'C:\ruta\a\tu\DOCKER_DUMMY'; docker-compose up --remove-orphans"
     ```

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

## 📊 Ver Logs (Rastrear la ejecución)

### Opción 1: Ver logs en tiempo real (RECOMENDADO)

Mientras el contenedor se está ejecutando, abre otra terminal en la carpeta y ejecuta:

```bash
docker-compose logs -f
```

Esto mostrará todos los mensajes que genera el script en vivo. Presiona `Ctrl+C` para detener la visualización de logs.

### Opción 2: Ver logs después de que terminó

Si el contenedor ya terminó, aún puedes ver los logs:

```bash
docker-compose logs
```

### Opción 3: Ver logs de un contenedor específico

Si tienes varios contenedores corriendo:

```bash
docker logs <nombre_del_contenedor>
```

Para ver el nombre exacto del contenedor:

```bash
docker-compose ps
```

### Opción 4: Ver solo las últimas 50 líneas

```bash
docker-compose logs --tail=50
```

### Opción 5: Seguir logs y mostrar timestamps

```bash
docker-compose logs -f -t
```

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
