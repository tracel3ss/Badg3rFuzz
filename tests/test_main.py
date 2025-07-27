import pytest
import queue
import threading
import badg3rfuzz
from unittest.mock import patch

def test_main(monkeypatch):
    # Clase para simular argumentos parseados
    class Args:
        no_banner = False
        success_indicators = []
        fail_indicators = []
        success_codes = [302]
        delay = 0
        jitter = 0
        user_agents_file = None
        check_cookies = True
        site_key = "fake_site_key"
        captcha_action = "fake_action"
        login_url = "http://fake.login.url"
        post_url = "http://fake.post.url"
        pass_file = None
        user_file = None
        user_fuzz = None
        threads = 1
        stop_on_success = False
        origin_url = None
        webdriver = "firefox"
        verbose = False
        proxy = None
        proxy_file = None
        proxy_timeout = 20
        disable_ssl_verify = False
        ca_cert = None

    # Parchar argparse para devolver args simulados
    monkeypatch.setattr("argparse.ArgumentParser.parse_args", lambda self: Args())

    # Parchar funciones para que no hagan nada real
    monkeypatch.setattr(badg3rfuzz, "print_banner", lambda: None)
    monkeypatch.setattr(badg3rfuzz, "preparar_combos", lambda user_file, pass_file, user_fuzz: None)
    monkeypatch.setattr(badg3rfuzz, "cargar_proxies", lambda proxy_file, proxy: [])
    monkeypatch.setattr(badg3rfuzz, "get_combined_patterns", lambda patterns, t: ["pattern1"])
    monkeypatch.setattr(badg3rfuzz, "mostrar_barra_progreso", lambda: None)
    monkeypatch.setattr(badg3rfuzz, "wait_for_threads", lambda threads, timeout=3: None)
    monkeypatch.setattr(badg3rfuzz, "cleanup_and_exit", lambda threads, start_time: None)
    monkeypatch.setattr(badg3rfuzz, "cleanup_temp_certs", lambda: None)
    monkeypatch.setattr("os.makedirs", lambda path, exist_ok=True: None)
    monkeypatch.setattr("os._exit", lambda code=0: None)
    monkeypatch.setattr("time.sleep", lambda x: None)

    # Setup combo_queue con un combo para simular carga
    badg3rfuzz.combo_queue = queue.Queue()
    badg3rfuzz.combo_queue.put(("user1", "pass1"))

    # Limpiar eventos globales para evitar efectos en tests
    badg3rfuzz.stop_event.clear()
    badg3rfuzz.success_flag.clear()

    # DummyThread con is_alive que retorna False para romper while
    class DummyThread:
        def start(self): pass
        def is_alive(self): return False
        def join(self, timeout=None): pass

    monkeypatch.setattr("threading.Thread", lambda *args, **kwargs: DummyThread())

    # Ejecutar main sin que haga nada real pero pasando todo el flujo
    badg3rfuzz.main()
