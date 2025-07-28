# tests/integration/test_check_success_integration.py
import pytest
from requests.models import Response
from unittest.mock import patch, Mock, mock_open
from badg3rfuzz import check_success, login_attempt

@pytest.mark.integration
@pytest.mark.parametrize("text,cookies,status_code,expected_success", [
    ("Bienvenido, admin!", {"sessionid": "xyz"}, 200, True),
    ("Invalid login", {}, 401, False),
    ("<html><script>window.location = '/dashboard';</script></html>", {}, 302, True),
    ("", {"auth_token": "abc123"}, 200, True),
    ('{"Result": false, "Msg": "Credenciales incorrectas"}', {}, 200, False),
    ('{"Result": true}', {}, 200, True),
    ("", {}, 302, True),  # Redirección con status_code en success_codes
])
def test_check_success_behavior(text, cookies, status_code, expected_success):
    res = Response()
    res.status_code = status_code
    res._content = text.encode("utf-8")
    res.cookies = cookies
    # Simular URL para redirecciones
    res.url = "https://example.com/dashboard" if status_code == 302 else "https://example.com/login"
    res.history = [Mock()] if status_code == 302 else []

    success, reason = check_success(
        response=res,
        success_indicators=["bienvenido", "dashboard", "éxito"],
        fail_indicators=["invalid", "incorrectas"],
        success_codes=[200, 302],
        check_cookies=True,
        verbose=True
    )
    assert success == expected_success, f"Reason: {reason}"

@pytest.mark.integration
def test_check_success_full_json_case():
    response = Response()
    response.status_code = 200
    response._content = b'{"Result": false, "Msg": "Credenciales incorrectas"}'
    response.cookies = {}

    success, reason = check_success(
        response=response,
        success_indicators=["bienvenido", "dashboard", "éxito"],
        fail_indicators=["invalid", "incorrectas"],
        success_codes=[200, 302],
        check_cookies=True,
        verbose=True
    )

    assert success is False
    assert reason == "Fail pattern detected: incorrectas"

@pytest.fixture
def mock_webdriver_complete(monkeypatch):
    """Mock completo para webdriver que intercepta todas las dependencias"""
    mock_driver = Mock()
    mock_driver.get_cookies.return_value = [{"name": "session", "value": "test123"}]
    mock_driver.execute_script.return_value = "test_token_123"
    mock_driver.get.return_value = None
    mock_driver.quit.return_value = None
    
    # Mock de las clases WebDriver
    monkeypatch.setattr("selenium.webdriver.Firefox", lambda *args, **kwargs: mock_driver)
    monkeypatch.setattr("selenium.webdriver.Chrome", lambda *args, **kwargs: mock_driver)
    
    # Mock de las opciones
    monkeypatch.setattr("selenium.webdriver.firefox.options.Options", Mock)
    monkeypatch.setattr("selenium.webdriver.chrome.options.Options", Mock)
    
    # Mock de los servicios
    mock_service = Mock()
    monkeypatch.setattr("selenium.webdriver.firefox.service.Service", lambda *args, **kwargs: mock_service)
    monkeypatch.setattr("selenium.webdriver.chrome.service.Service", lambda *args, **kwargs: mock_service)
    
    # Mock de ChromeDriverManager
    mock_manager = Mock()
    mock_manager.install.return_value = "/usr/local/bin/chromedriver"
    monkeypatch.setattr("webdriver_manager.chrome.ChromeDriverManager", lambda: mock_manager)
    
    # Mock de WebDriverWait y EC
    mock_wait = Mock()
    mock_wait.until.return_value = True
    monkeypatch.setattr("selenium.webdriver.support.ui.WebDriverWait", lambda *args, **kwargs: mock_wait)
    monkeypatch.setattr("selenium.webdriver.support.expected_conditions.presence_of_element_located", Mock)
    
    # Mock de os.path.isfile para evitar el sys.exit
    def mock_isfile(path):
        if "geckodriver" in path:
            return True
        return False
    monkeypatch.setattr("os.path.isfile", mock_isfile)
    
    # Mock de os.path.exists para firefox paths
    def mock_exists(path):
        if "firefox" in path.lower():
            return True
        return False
    monkeypatch.setattr("os.path.exists", mock_exists)
    
    yield mock_driver

@pytest.mark.parametrize("webdriver_type", ["firefox", "chrome"])
def test_integration_login_attempt_and_check_success(mock_webdriver_complete, monkeypatch, webdriver_type):
    """Test de integración completo con mocking adecuado"""
    
    # Mock de generar_token_y_cookie para que no ejecute webdriver real
    def mock_generar_token(site_key, captcha_action, login_url, webdriver_type="firefox", verbose=False):
        return "mocked_token", {"session": "mocked_session"}
    
    monkeypatch.setattr("badg3rfuzz.generar_token_y_cookie", mock_generar_token)
    
    # Mock de requests.Session
    mock_response = Mock()
    mock_response.text = "Login failed: incorrecto"
    mock_response.status_code = 200
    mock_response.cookies = {}
    mock_response.url = "https://example.com/login"
    mock_response.history = []
    mock_response.json.side_effect = ValueError("No JSON object could be decoded")
    
    mock_session = Mock()
    mock_session.__enter__ = Mock(return_value=mock_session)
    mock_session.__exit__ = Mock(return_value=None)
    mock_session.post.return_value = mock_response
    mock_session.cookies = {}
    
    monkeypatch.setattr("badg3rfuzz.requests.Session", lambda: mock_session)
    
    # Mock de threading events para evitar problemas
    mock_event = Mock()
    mock_event.is_set.return_value = False
    monkeypatch.setattr("badg3rfuzz.stop_event", mock_event)
    monkeypatch.setattr("badg3rfuzz.success_flag", mock_event)
    
    response = login_attempt(
        username="testuser",
        password="wrongpassword",
        site_key="dummykey",
        captcha_action="login",
        login_url="https://example.com/login",
        post_url="https://example.com/login",
        verbose=False,
        webdriver_type=webdriver_type,
    )
    
    success, reason = check_success(
        response=response,
        success_indicators=["bienvenido", "dashboard", "éxito"],
        fail_indicators=["incorrecto", "error", "invalido"],
        success_codes=[200, 302],
        check_cookies=True,
        verbose=True
    )
    assert success is False
    assert "incorrecto" in reason.lower()