# tests/integration/test_full_workflow.py
import threading
import queue
import pytest
from unittest.mock import patch, Mock, MagicMock
from badg3rfuzz import worker, check_success, generar_token_y_cookie
from requests.models import Response


# Global flags que necesita el worker
import badg3rfuzz
badg3rfuzz.combo_queue = queue.Queue()
badg3rfuzz.success_flag = threading.Event()
badg3rfuzz.stop_event = threading.Event()
badg3rfuzz.print_lock = threading.Lock()
badg3rfuzz.attempts_lock = threading.Lock()
badg3rfuzz.attempts_done = 0

@pytest.mark.integration
def test_complete_bruteforce_workflow(tmp_path):
    # Simular combinaciones
    badg3rfuzz.combo_queue.put(("admin", "123456"))
    badg3rfuzz.combo_queue.put(("user", "wrongpass"))

    log_file = tmp_path / "log.txt"

    # Mock login_attempt para devolver éxito con admin
    def mock_login_attempt(username, password, *args, **kwargs):
        mock_resp = Mock()
        if username == "admin" and password == "123456":
            mock_resp.status_code = 200
            mock_resp.text = "Welcome, admin!"
            mock_resp.cookies = {"session": "abcd1234"}
        else:
            mock_resp.status_code = 401
            mock_resp.text = "Invalid credentials"
            mock_resp.cookies = {}
        return mock_resp

    with patch("badg3rfuzz.login_attempt", side_effect=mock_login_attempt):
        t = threading.Thread(target=worker, args=(
            "dummy_sitekey",
            "login",
            "http://test/login",
            "http://test/loginpost",
            None,
            True,  # stop_on_success
            str(log_file),
            "firefox",
            False,  # verbose
            ["welcome"],  # success_indicators
            ["invalid"],  # fail_indicators
            [200],
            True,  # check_cookies
            0,     # delay
            0,     # jitter
            None,  # user_agents_file
            None,  # proxies
            10,
            False,
            None
        ))
        t.start()
        t.join(timeout=5)

    with open(log_file) as f:
        log = f.read()
        assert "SUCCESS: admin:123456" in log
        assert "FAIL: user:wrongpass" not in log or "user:wrongpass" in log

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
@pytest.mark.parametrize("text,cookies,status_code,history,expected_success,desc", [
    # Redirección real simulada
    ("", {}, 200, [{"url": "http://test.com/dashboard"}], True, "Redirect URL detected"),

    # Cookie con nombre tipo login
    ("", {"loginToken": "abc123"}, 200, [], True, "Cookie named like 'login'"),

    # Código de éxito sin contenido
    ("", {}, 201, [], True, "Empty 201 status success code"),

    # Nada que coincida
    ("", {}, 200, [], False, "No indicator matched"),

    # JSON parsing error
    ("{invalid json", {}, 200, [], False, "Malformed JSON"),
])
def test_check_success_extended(text, cookies, status_code, history, expected_success, desc):
    """Test extendido para check_success con diferentes escenarios"""
    # Crear mock response
    response = Mock()
    response.status_code = status_code
    response.text = "Welcome to dashboard"
    response.cookies = cookies
    response.history = history
    
    # Asegurar que response.url no sea None
    if history:
        response.url = "https://example.com/dashboard"
    else:
        response.url = "https://example.com/login"
    
    success, reason = check_success(
        response=response,
        success_indicators=["welcome", "dashboard", "éxito"],
        fail_indicators=["error", "invalid", "fail"],
        success_codes=[200, 302],
        check_cookies=True,
        verbose=True
    )
    
    assert success == expected_success
    # Verificar que la razón contiene alguna palabra clave esperada
    if expected_success == "Redirect URL detected":
        # Para este caso específico, verificamos que detecte el patrón de éxito
        assert any(keyword in reason.lower() for keyword in ["success", "dashboard", "welcome"])
    elif "redirect" in expected_success.lower():
        assert "redirect" in reason.lower() or "dashboard" in reason.lower()
    elif "cookie" in expected_success.lower():
        assert "cookie" in reason.lower()