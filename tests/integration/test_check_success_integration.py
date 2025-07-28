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
    assert reason == "JSON Result=False: Credenciales incorrectas"
@pytest.fixture
def mock_webdriver(monkeypatch):
    mock_driver = Mock()
    mock_driver.get_cookies.return_value = [{"name": "session", "value": "test123"}]
    mock_driver.execute_script.return_value = "test_token_123"
    monkeypatch.setattr("selenium.webdriver.Firefox", lambda *a, **k: mock_driver)
    monkeypatch.setattr("selenium.webdriver.Chrome", lambda *a, **k: mock_driver)
    yield mock_driver

@pytest.mark.parametrize("webdriver_type", ["firefox", "chrome"])
def test_integration_login_attempt_and_check_success(mock_webdriver, webdriver_type):
    response = login_attempt(
        username="testuser",
        password="wrongpassword",
        site_key="dummykey",
        captcha_action="login",
        login_url="https://example.com/login",
        post_url="https://example.com/login",
        verbose=False,
        webdriver_type=webdriver_type,  # Deberías tener una opción mock o stub
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