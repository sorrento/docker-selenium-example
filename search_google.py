from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import time
import json
import subprocess
import logging
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def log_info(msg):
    """Log de información"""
    print(f"\n[INFO] {msg}")
    logger.info(msg)

def log_success(msg):
    """Log de éxito"""
    print(f"[✓ OK] {msg}")
    logger.info(f"SUCCESS: {msg}")

def log_warning(msg):
    """Log de advertencia"""
    print(f"[⚠️  WARNING] {msg}")
    logger.warning(msg)

def log_error(msg):
    """Log de error"""
    print(f"[❌ ERROR] {msg}")
    logger.error(msg)

def check_docker_running():
    """Verifica si Docker está corriendo (solo en modo host)"""
    # Nota: Esta función no es necesaria cuando se ejecuta dentro de un contenedor Docker
    # Se mantiene por compatibilidad, pero siempre retorna True en contenedor
    if os.path.exists("/.dockerenv"):
        # Estamos dentro de un contenedor Docker
        log_info("Ejecutando dentro de contenedor Docker ✓")
        return True
    
    log_info("Verificando si Docker está disponible...")
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, check=False, timeout=5)
        if result.returncode == 0:
            log_success("Docker está corriendo y disponible")
            return True
        else:
            error_msg = result.stderr.decode('utf-8', errors='ignore').strip() if result.stderr else "Error desconocido"
            log_error(f"Error de Docker: {error_msg}")
            return False
    except subprocess.TimeoutExpired:
        log_error("Docker no respondió en 5 segundos - podría no estar activo")
        return False
    except FileNotFoundError:
        log_error("Docker no está instalado o no está en el PATH")
        return False
    except Exception as e:
        log_error(f"No se pudo verificar Docker: {e}")
        return False

def search_google_news(search_query, retry_count=0, headless=None, search_engine=None):
    """
    Busca en Google o Bing y extrae el contenido del primer resultado sin entrar
    
    Args:
        search_query: Término de búsqueda
        retry_count: Contador interno de reintentos
        headless: Si True, ejecuta sin ventana visible (más rápido). Si None, lee del .env
        search_engine: 'google' o 'bing'. Si None, lee del .env
    """
    
    # Usar configuración del .env si no se proporciona explícitamente
    if search_engine is None:
        search_engine = os.getenv("SEARCH_ENGINE", "bing").lower()
    if headless is None:
        headless = os.getenv("HEADLESS", "true").lower() == "true"
    
    log_info(f"Iniciando búsqueda: '{search_query}'")
    log_info(f"Motor de búsqueda: {search_engine.upper()}")
    log_info(f"Intento {retry_count + 1}")
    
    # Verificar que Docker está corriendo (o que estamos en un contenedor)
    if not check_docker_running():
        log_error("No se pudo verificar el entorno Docker")
        return None
    
    log_info("Configurando opciones de Chrome/Chromium...")
    
    # Configurar opciones de Chrome
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")  # Modo sin interfaz gráfica
        log_info("  ✓ Modo headless activado (sin ventana visual)")
    else:
        log_warning("  ⚠️  MODO INTERACTIVO - Ventana visible (más lento)")
        log_warning("  ⚠️  El navegador será visible para debugging")
    
    chrome_options.add_argument("--no-sandbox")
    log_info("  ✓ Sandbox deshabilitado")
    
    chrome_options.add_argument("--disable-dev-shm-usage")
    log_info("  ✓ /dev/shm deshabilitado")
    
    chrome_options.add_argument("--disable-gpu")
    log_info("  ✓ GPU deshabilitada")
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    log_info("  ✓ Características de automatización deshabilitadas")
    
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    log_info("  ✓ Opciones anti-detección de bots aplicadas")
    
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    log_info("  ✓ User-Agent realista configurado")
    
    driver = None
    
    try:
        log_info("Inicializando navegador Chrome/Chromium...")
        driver = webdriver.Chrome(options=chrome_options)
        log_success("Navegador iniciado correctamente")
        
        # Acceder al buscador correspondiente
        if search_engine == "google":
            log_info("Accediendo a https://www.google.com...")
            driver.get("https://www.google.com")
            log_success("Google cargado correctamente")
            search_field_name = "q"
        elif search_engine == "bing":
            log_info("Accediendo a https://www.bing.com...")
            driver.get("https://www.bing.com")
            log_success("Bing cargado correctamente")
            search_field_name = "q"
        else:
            log_error(f"Motor de búsqueda desconocido: {search_engine}")
            return None
        
        log_info("Esperando a que la página se estabilice (2 segundos)...")
        time.sleep(2)
        
        # Aceptar cookies si aparece el aviso (solo para Google)
        if search_engine == "google":
            log_info("Buscando diálogo de cookies...")
            try:
                accept_button = None
                
                # Intentar varios selectores para encontrar el botón de cookies
                selectores = [
                    (By.ID, "L2AGLb"),  # Selector por ID (más específico)
                    (By.XPATH, "//button[@id='L2AGLb']"),  # XPath por ID
                    (By.XPATH, "//button[.//div[contains(text(), 'Aceptar todo')]]"),  # XPath por contenido
                    (By.XPATH, "//button[contains(., 'Aceptar')]"),  # XPath flexible
                    (By.CSS_SELECTOR, "button.tHlp8d"),  # Por clase
                ]
                
                for selector_type, selector_value in selectores:
                    try:
                        log_info(f"  → Intentando selector: {selector_value}")
                        accept_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((selector_type, selector_value))
                        )
                        log_success(f"    ✓ Botón de cookies encontrado con selector: {selector_value}")
                        break
                    except:
                        continue
                
                if accept_button:
                    log_info("  → Haciendo click en botón de cookies...")
                    accept_button.click()
                    log_success("Cookies aceptadas")
                    time.sleep(2)
                else:
                    log_info("  → No se encontró botón de cookies")
            except Exception as e:
                log_warning(f"No se pudo aceptar cookies: {e}")
        
        # Buscar y llenar campo de búsqueda
        log_info("Buscando campo de búsqueda...")
        wait = WebDriverWait(driver, 15)
        search_box = wait.until(EC.presence_of_element_located((By.NAME, search_field_name)))
        log_success("Campo de búsqueda encontrado")
        
        log_info(f"Escribiendo búsqueda: '{search_query}'...")
        search_box.send_keys(search_query)
        log_success("Texto ingresado en el campo de búsqueda")
        
        log_info("Presionando Enter para buscar...")
        search_box.submit()
        log_success("Búsqueda iniciada")
        
        log_info("Esperando a que carguen los resultados (esto puede tardar)...")
        # Esperar a que los resultados se carguen según el buscador
        if search_engine == "google":
            # Google renderiza los resultados dinámicamente, esperar más tiempo
            try:
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div#search, a[data-ved]")))
                log_success("Página de resultados detectada")
            except:
                log_warning("Timeout esperando selectores principales, continuando...")
        elif search_engine == "bing":
            # Bing usa diferentes selectores
            try:
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ol#b_results, li.b_algo")))
                log_success("Página de resultados detectada")
            except:
                log_warning("Timeout esperando selectores principales, continuando...")
        
        log_info("Esperando 5 segundos para que se renderice completamente...")
        time.sleep(5)
        
        # Buscar el contenedor principal de resultados (no incluye tabs de navegación)
        log_info("Buscando contenedor de resultados...")
        results_container = None
        
        if search_engine == "google":
            contenedor_selectores = [
                "div#search",  # Contenedor principal de resultados
                "div#center_col",  # Columna central
                "div[role='main']",  # Área principal
            ]
        elif search_engine == "bing":
            contenedor_selectores = [
                "ol#b_results",  # Lista ordenada de resultados
                "div#b_results",  # Contenedor alternativo
                "div[role='main']",  # Área principal
            ]
        
        for selector in contenedor_selectores:
            try:
                results_container = driver.find_element(By.CSS_SELECTOR, selector)
                log_success(f"Contenedor encontrado: {selector}")
                break
            except:
                pass
        
        if not results_container:
            log_warning("No se encontró contenedor específico, usando toda la página")
            results_container = driver.find_element(By.TAG_NAME, "body")
        
        # Extraer primer resultado - intentar varios selectores en orden de preferencia
        log_info("Buscando resultados dentro del contenedor...")
        results = []
        
        # Intentar selectores en este orden (apuntando a resultados reales, no tabs)
        if search_engine == "google":
            selectores = [
                ("div.g", "Contenedor de resultado div.g (estructura clásica)"),
                ("div[data-sokoban-container]", "Contenedor Sokoban"),
                ("div.Gvuyqe", "Div class Gvuyqe (moderna)"),
                ("div[jscontroller][data-ved]", "Div con jscontroller y data-ved"),
            ]
        elif search_engine == "bing":
            selectores = [
                ("li.b_algo", "Elemento li.b_algo (estructura Bing)"),
                ("div.b_algo", "Contenedor div.b_algo"),
                ("li", "Elementos li genéricos"),
            ]
        
        for selector, descripcion in selectores:
            try:
                results = results_container.find_elements(By.CSS_SELECTOR, selector)
                # Filtrar resultados que tengan contenido real (no son tabs)
                results = [r for r in results if r.text and len(r.text.strip()) > 10]
                if results:
                    log_success(f"Encontrados {len(results)} elementos con {descripcion}")
                    break
            except:
                pass
            
            log_info(f"  → {descripcion}: {len(results) if results else 0} elementos encontrados")
        
        log_info(f"  → Total de resultados válidos: {len(results)} elementos")
        
        if not results:
            log_error("No se encontraron resultados con ningún selector conocido")
            log_warning("Guardando screenshot y HTML para debugging...")
            try:
                driver.save_screenshot("debug_no_results.png")
                log_info("Screenshot guardado: debug_no_results.png")
            except:
                pass
            try:
                with open("debug_page_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                log_info("HTML de la página guardado: debug_page_source.html")
            except:
                pass
            print("\n" + "="*70)
            if search_engine == "google":
                print("⚠️  CAUSA PROBABLE: Google está bloqueando el acceso automatizado")
            else:
                print("⚠️  CAUSA PROBABLE: No se encontraron resultados en Bing")
            print("="*70)
            print("Soluciones posibles:")
            print("  1. Espera 15-30 minutos e intenta de nuevo")
            print("  2. El buscador ha detectado múltiples accesos automatizados")
            print("  3. Verifica tu conexión a internet")
            print("="*70 + "\n")
            return None
        
        log_success(f"Encontrados {len(results)} resultados de búsqueda")
        log_info("Extrayendo información del PRIMER resultado...")
        first_result = results[0]
        
        # Extraer información del primer resultado
        try:
            # Obtener título - múltiples intentos
            log_info("  • Buscando título...")
            title = "Título no encontrado"
            
            # El título puede estar en h3, h2, o directamente en el div
            if search_engine == "google":
                selectores_titulo = [
                    (By.CSS_SELECTOR, "h3"),  
                    (By.CSS_SELECTOR, "h2"),
                    (By.XPATH, ".//div[@role='heading']"),
                    (By.XPATH, ".//span[@role='heading']"),
                ]
            elif search_engine == "bing":
                selectores_titulo = [
                    (By.CSS_SELECTOR, "h2"),  # En Bing es h2
                    (By.CSS_SELECTOR, "h3"),
                    (By.XPATH, ".//a"),  # El link en Bing contiene el título
                ]
            
            for selector_type, selector_value in selectores_titulo:
                try:
                    title_elem = first_result.find_element(selector_type, selector_value)
                    if title_elem and title_elem.text:
                        title = title_elem.text
                        log_success(f"    ✓ Título encontrado: '{title}'")
                        break
                except:
                    pass
            
            # Obtener URL - si es un link, extraer href
            log_info("  • Buscando URL...")
            url = "URL no encontrada"
            
            # Si first_result es un link directo
            if first_result.tag_name == "a":
                href = first_result.get_attribute("href")
                if href and not href.startswith("javascript"):
                    url = href
                    log_success(f"    ✓ URL encontrada (elemento es link): '{url}'")
            
            # Si no, buscar link dentro
            if url == "URL no encontrada":
                try:
                    link_elem = first_result.find_element(By.CSS_SELECTOR, "a")
                    href = link_elem.get_attribute("href")
                    if href and not href.startswith("javascript"):
                        url = href
                        log_success(f"    ✓ URL encontrada (dentro): '{url}'")
                except:
                    pass
            
            # Obtener descripción/snippet
            log_info("  • Buscando descripción/snippet...")
            snippet = "No hay descripción disponible"
            
            if search_engine == "google":
                selectores_snippet = [
                    (By.CSS_SELECTOR, "span.VwiC3b"),  # Selector moderno
                    (By.CSS_SELECTOR, "div.s"),  # Selector antiguo
                    (By.CSS_SELECTOR, "span.s"),
                    (By.XPATH, ".//div[@role='cell']//span"),
                    (By.XPATH, ".//div[contains(@class, 'snippet') or contains(@class, 'description')]"),
                    (By.XPATH, ".//span[contains(@class, 'preview')]"),
                ]
            elif search_engine == "bing":
                selectores_snippet = [
                    (By.CSS_SELECTOR, "p"),  # En Bing es generalmente un párrafo
                    (By.CSS_SELECTOR, "div.b_caption"),
                    (By.XPATH, ".//div[contains(@class, 'snippet')]"),
                ]
            
            for selector_type, selector_value in selectores_snippet:
                try:
                    snippet_elem = first_result.find_element(selector_type, selector_value)
                    if snippet_elem and snippet_elem.text:
                        snippet = snippet_elem.text
                        log_success(f"    ✓ Descripción encontrada")
                        break
                except:
                    pass
            
            # Si aún no tenemos datos válidos, intenta extraer todo el texto
            if title == "Título no encontrado":
                log_warning("    → No se encontró estructura estándar, extrayendo texto disponible...")
                all_text = first_result.text
                lines = [l.strip() for l in all_text.split('\n') if l.strip()]
                if lines:
                    title = lines[0] if lines else "Título no disponible"
                    if len(lines) > 1:
                        snippet = '\n'.join(lines[1:3])
                    log_info(f"    ✓ Extrayendo del texto disponible")
            
            # Crear resultado
            result_data = {
                "timestamp": datetime.now().isoformat(),
                "search_query": search_query,
                "result": {
                    "title": title,
                    "url": url,
                    "snippet": snippet
                }
            }
            
            print(f"\n{'='*70}")
            print(f"✅ BÚSQUEDA COMPLETADA EXITOSAMENTE")
            print(f"{'='*70}")
            print(f"📰 TÍTULO: {title}")
            print(f"🔗 URL: {url}")
            print(f"📝 DESCRIPCIÓN:\n{snippet}")
            print(f"{'='*70}\n")
            
            log_info("Guardando resultado en archivo JSON...")
            output_file = "output/resultado_busqueda.json"
            os.makedirs("output", exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            log_success(f"Archivo guardado en: {output_file}")
            
            log_success("✅ PROCESO COMPLETADO CON ÉXITO")
            return result_data
            
        except Exception as e:
            log_error(f"Error al extraer datos del resultado: {e}")
            log_error(f"Tipo de error: {type(e).__name__}")
            import traceback
            log_error(f"Traceback completo:\n{traceback.format_exc()}")
            
            log_warning("Guardando screenshot y HTML para debugging...")
            try:
                driver.save_screenshot("debug_extraction_error.png")
                log_info("Screenshot guardado: debug_extraction_error.png")
            except:
                pass
            try:
                with open("debug_page_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                log_info("HTML de la página guardado: debug_page_source.html")
            except:
                pass
            
            if retry_count < 1:
                log_info("Reintentando en 3 segundos...")
                time.sleep(3)
                return search_google_news(search_query, retry_count + 1, headless, search_engine)
            return None
    
    except Exception as e:
        log_error(f"Error general durante la búsqueda: {e}")
        log_error(f"Tipo de error: {type(e).__name__}")
        import traceback
        log_error(f"Traceback completo:\n{traceback.format_exc()}")
        
        log_warning("Guardando screenshot y HTML para debugging...")
        try:
            if driver:
                driver.save_screenshot("debug_general_error.png")
                log_info("Screenshot guardado: debug_general_error.png")
                with open("debug_page_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                log_info("HTML de la página guardado: debug_page_source.html")
        except:
            pass
        
        print("\n" + "="*70)
        print("POSIBLES CAUSAS:")
        print("="*70)
        print("  1. Google está bloqueando el acceso automatizado (MÁS PROBABLE)")
        print("  2. Problema de conexión a internet")
        print("  3. Chrome/Chromium no se pudo inicializar")
        print("  4. Cambios en la estructura HTML de Google")
        print("="*70 + "\n")
        return None
    
    finally:
        if driver:
            log_info("Cerrando navegador...")
            driver.quit()
            log_success("Navegador cerrado correctamente")

if __name__ == "__main__":
    # Obtener parámetros de línea de comandos
    headless = None  # Usar configuración del .env por defecto
    search_engine = None  # Usar configuración del .env por defecto
    
    # Verificar si se pasó --no-headless
    if "--no-headless" in sys.argv:
        headless = False
        log_warning("Modo sin headless activado (ventana visible)")
    
    # Verificar si se pasó --google para usar Google en lugar de Bing
    if "--google" in sys.argv:
        search_engine = "google"
        log_info("Google será utilizado como motor de búsqueda")
    
    # Obtener fecha de hoy en formato dd/mm/yyyy
    today = datetime.now().strftime("%d/%m/%Y")
    search_query = f"Noticias {today}"
    
    # Si no se especificó, usar del .env
    if headless is None:
        headless = os.getenv("HEADLESS", "true").lower() == "true"
    if search_engine is None:
        search_engine = os.getenv("SEARCH_ENGINE", "bing").lower()
    
    print(f"\n{'='*70}")
    print(f"{'🔍 SCRAPER DE NOTICIAS':^70}")
    print(f"{'='*70}")
    print(f"{'Fecha actual:':.<50} {today}")
    print(f"{'Búsqueda:':.<50} {search_query}")
    print(f"{'Motor de búsqueda:':.<50} {search_engine.upper()}")
    print(f"{'Modo headless:':.<50} {'Sí (sin ventana)' if headless else 'No (con ventana)'}")
    print(f"{'Hora de inicio:':.<50} {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*70}\n")
    
    resultado = search_google_news(search_query, headless=headless, search_engine=search_engine)
    
    if resultado:
        print("\n" + "="*70)
        print("📊 RESULTADO GUARDADO EN JSON")
        print("="*70)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("❌ No se pudo obtener el resultado")
        print("="*70)
        print("\n⚠️  POSIBLES SOLUCIONES:")
        print("  1. Google está bloqueando acceso automatizado (MÁS PROBABLE)")
        print("  2. Espera 15-30 minutos e intenta de nuevo")
        print("  3. Verifica tu conexión a internet")
        print("  4. Si persiste, Google puede requerir CAPTCHA")
        print("  5. Revisa los logs arriba para más detalles")
        print("="*70 + "\n")
        sys.exit(1)
