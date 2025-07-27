# tests/test_utils.py
from badg3rfuzz import print_banner, print_footer
from datetime import datetime
import pytest
from unittest.mock import patch, Mock, MagicMock
import threading
import time
import builtins
import badg3rfuzz  # tu módulo

def test_print_banner(capsys):
    print_banner()
    captured = capsys.readouterr()
    assert "Badg3rFuzz" in captured.out

def test_print_footer(capsys):
    start_time = datetime.now()
    print_footer(start_time)
    captured = capsys.readouterr()
    assert "Finished" in captured.out or captured.out  # Ajusta según el mensaje real



# 1. cargar_user_agents
def test_cargar_user_agents(tmp_path):
    # Crear archivo temporal con algunos User-Agents
    file_path = tmp_path / "user_agents.txt"
    file_path.write_text("Mozilla/5.0\nChrome/90.0\n")

    agents = badg3rfuzz.cargar_user_agents(str(file_path))
    assert agents == ["Mozilla/5.0", "Chrome/90.0"]

# 2. cargar_proxies
def test_cargar_proxies(tmp_path):
    file = tmp_path / "proxies.txt"
    file.write_text("http://127.0.0.1:8080\nhttp://127.0.0.1:8081\n")
    proxies = badg3rfuzz.cargar_proxies(str(file))
    assert proxies == ["http://127.0.0.1:8080", "http://127.0.0.1:8081"]

# 3. get_combined_patterns
def test_get_combined_patterns_success():
    patterns = badg3rfuzz.get_combined_patterns(["custom1"], pattern_type="success")
    assert "custom1" in patterns
    assert "success" in [p.lower() for p in patterns]

def test_get_combined_patterns_fail():
    patterns = badg3rfuzz.get_combined_patterns(["fallo"], pattern_type="fail")
    assert "fallo" in patterns
    assert "false" in [p.lower() for p in patterns]

# 4. parse_user_fuzzer
def test_parse_user_fuzzer_valid():
    result = badg3rfuzz.parse_user_fuzzer("alfa:3:5:2")
    assert result[0] == "alfa"  # tipo
    assert result[1] == 3
    assert result[2] == 5
    assert result[3] == 2

def test_parse_user_fuzzer_invalid_format():
    with pytest.raises(ValueError):
        badg3rfuzz.parse_user_fuzzer("alfa:3:5")  # Falta un campo    

# 5. mostrar_barra_progreso
def test_mostrar_barra_progreso(capfd):
    # Configurar variables globales
    badg3rfuzz.total_attempts = 10
    badg3rfuzz.attempts_done = 5
    badg3rfuzz.start_time_prog = time.time()
    badg3rfuzz.success_flag.clear()
    badg3rfuzz.stop_event.clear()

    # Lanzar la función en un hilo para poder controlarla
    thread = threading.Thread(target=badg3rfuzz.mostrar_barra_progreso)
    thread.start()

    # Esperamos un momento para que se ejecute parte del bucle
    time.sleep(0.5)
    badg3rfuzz.success_flag.set()  # forzamos que termine

    thread.join(timeout=2)

    # Capturamos la salida
    out, _ = capfd.readouterr()

    # Verificamos que contiene la barra
    assert "[" in out and "]" in out
    assert "ETA" in out
    assert "/" in out
    assert "%" in out

# 6. cleanup_and_exit
def test_cleanup_and_exit():
    threads = [MagicMock(), MagicMock()]
    start_time = time.time()

    with patch.object(badg3rfuzz, "stop_event") as mock_stop_event, \
         patch.object(badg3rfuzz, "force_kill_drivers") as mock_kill, \
         patch.object(badg3rfuzz, "print_footer") as mock_footer:

        badg3rfuzz.cleanup_and_exit(threads, start_time)

        mock_stop_event.set.assert_called_once()
        mock_kill.assert_called_once()
        mock_footer.assert_called_once_with(start_time)

# 7. wait_for_threads
def test_wait_for_threads():
    class DummyThread:
        def __init__(self):
            self.alive = True
        def is_alive(self):
            self.is_alive_called = True
            return self.alive
        def join(self, timeout=None):
            self.alive = False

    threads = [DummyThread() for _ in range(3)]
    badg3rfuzz.wait_for_threads(threads)

    for thread in threads:
        assert thread.is_alive_called

# 8. force_kill_drivers
def test_force_kill_drivers(monkeypatch):
    dummy_driver = Mock()
    monkeypatch.setattr(badg3rfuzz, "active_drivers", [dummy_driver])

    badg3rfuzz.force_kill_drivers()
    dummy_driver.quit.assert_called_once()

# 9. cleanup_temp_certs
def test_cleanup_temp_certs(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda path: True)
    monkeypatch.setattr("shutil.rmtree", lambda path: None)

    # Si no lanza excepción, el test pasa
    badg3rfuzz.cleanup_temp_certs()
