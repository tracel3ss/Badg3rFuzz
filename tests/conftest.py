# tests/conftest.py - Configuración global de pytest
import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, patch
import requests_mock

# Agregar el directorio del proyecto al path si no está
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m

@pytest.fixture
def mock_webdriver():
    with patch('selenium.webdriver.Firefox') as mock_firefox, \
         patch('selenium.webdriver.Chrome') as mock_chrome, \
         patch('selenium.webdriver.firefox.service.Service') as mock_firefox_service, \
         patch('selenium.webdriver.chrome.service.Service') as mock_chrome_service, \
         patch('selenium.webdriver.firefox.options.Options') as mock_firefox_options, \
         patch('selenium.webdriver.chrome.options.Options') as mock_chrome_options, \
         patch('webdriver_manager.chrome.ChromeDriverManager') as mock_chrome_manager, \
         patch('selenium.webdriver.support.ui.WebDriverWait') as mock_wait, \
         patch('os.path.isfile', return_value=True), \
         patch('os.path.exists', return_value=True):
        
        # Mock del service
        mock_service = Mock()
        mock_service.start.return_value = None
        mock_service.is_connectable.return_value = True
        mock_firefox_service.return_value = mock_service
        mock_chrome_service.return_value = mock_service
        
        # Mock del ChromeDriverManager
        mock_manager = Mock()
        mock_manager.install.return_value = "/usr/local/bin/chromedriver"
        mock_chrome_manager.return_value = mock_manager
        
        # Mock del WebDriverWait
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = Exception("Timeout - elemento no encontrado")
        mock_wait.return_value = mock_wait_instance
        
        # Mock del driver principal
        mock_driver = Mock()
        mock_driver.get_cookies.return_value = [
            {"name": "session", "value": "test123"},
            {"name": "csrftoken", "value": "csrf456"}
        ]
        mock_driver.execute_script.return_value = "test_token_123"
        mock_driver.get.return_value = None
        mock_driver.quit.return_value = None
        
        mock_firefox.return_value = mock_driver
        mock_chrome.return_value = mock_driver
        
        yield mock_driver

@pytest.fixture
def temp_wordlist():
    """Crear wordlists temporales para testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("admin\ntest\nuser\n")
        f.flush()
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def mock_response():
    """Mock response para requests"""
    def _mock_response(status_code=200, json_data=None, text="", cookies=None, url="http://test.com/login", history=None):
        mock_resp = Mock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = json_data or {}
        mock_resp.text = text
        mock_resp.cookies = cookies or {"session": "test123"}
        mock_resp.history = history or []
        mock_resp.url = url
        mock_resp.token = "test_token_123"
        
        # Mock del método json que puede fallar
        if json_data is None and not text.startswith('{'):
            mock_resp.json.side_effect = ValueError("No JSON object could be decoded")
        
        return mock_resp
    return _mock_response

@pytest.fixture(autouse=True)
def setup_global_mocks(monkeypatch):
    """Fixture que se ejecuta automáticamente para mockear variables globales problemáticas"""
    
    # Mock de threading events y locks que pueden causar problemas
    mock_print_lock = Mock()
    mock_drivers_lock = Mock()
    mock_active_drivers = []
    
    mock_stop_event = Mock()
    mock_stop_event.is_set.return_value = False
    
    mock_success_flag = Mock()
    mock_success_flag.is_set.return_value = False
    mock_success_flag.set.return_value = None
    mock_success_flag.clear.return_value = None
    
    # Aplicar mocks solo si el módulo existe
    try:
        import badg3rfuzz
        monkeypatch.setattr("badg3rfuzz.print_lock", mock_print_lock)
        monkeypatch.setattr("badg3rfuzz.drivers_lock", mock_drivers_lock)
        monkeypatch.setattr("badg3rfuzz.active_drivers", mock_active_drivers)
        monkeypatch.setattr("badg3rfuzz.stop_event", mock_stop_event)
        monkeypatch.setattr("badg3rfuzz.success_flag", mock_success_flag)
    except ImportError:
        pass  # El módulo no existe aún, está bien
    
    # Mock de sys.exit para que no termine los tests abruptamente
    def mock_exit(code=0):
        raise SystemExit(code)
    
    monkeypatch.setattr("sys.exit", mock_exit)

def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="chrome", help="Browser to use for Selenium tests"
    )

@pytest.fixture
def browser(request):
    return request.config.getoption("--browser")

# Fixture adicional para tests que necesitan generar_token_y_cookie mockeado
@pytest.fixture
def mock_token_generation(monkeypatch):
    """Mock completo para generar_token_y_cookie que evita webdriver real"""
    def mock_generar_token_y_cookie(site_key, captcha_action, login_url, webdriver_type="firefox", verbose=False):
        # Simular verificación de threading events
        try:
            import badg3rfuzz
            if hasattr(badg3rfuzz, 'stop_event') and badg3rfuzz.stop_event.is_set():
                raise Exception("Operation cancelled by user")
            if hasattr(badg3rfuzz, 'success_flag') and badg3rfuzz.success_flag.is_set():
                raise Exception("Operation cancelled by user")
        except ImportError:
            pass
        
        return "mocked_token_123", {"session": "mocked_session", "csrf": "mocked_csrf"}
    
    try:
        monkeypatch.setattr("badg3rfuzz.generar_token_y_cookie", mock_generar_token_y_cookie)
    except AttributeError:
        pass  # La función no existe aún, está bien
    
    return mock_generar_token_y_cookie