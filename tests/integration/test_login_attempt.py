# tests/integration/test_login_attempt.py

import pytest
import threading
from unittest.mock import patch, Mock
from badg3rfuzz import login_attempt, check_success, generar_token_y_cookie, success_flag  # Ajusta el import a tu estructura real

@pytest.mark.integration
def test_login_attempt_fail_json():
    # Login fallido (malas credenciales o error interno)
    with patch("badg3rfuzz.generar_token_y_cookie", return_value=("fake_token", {"sessionid": "abc"})):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"Result": False, "Msg": "Credenciales inválidas"}

        with patch("badg3rfuzz.requests.Session.post", return_value=mock_resp):
            response = login_attempt(
                "baduser", "badpass", "key", "action",
                "https://site.com/login", "https://site.com/check"
            )
            success, msg = check_success(response)
            assert success is False
            assert "Credenciales inválidas" in msg

@pytest.mark.integration
def test_login_attempt_successful(monkeypatch):
    """Test de integración para login_attempt verificando que detecta éxito"""

    # Set up
    username = "admin"
    password = "password123"
    site_key = "dummy_key"
    captcha_action = "login"
    login_url = "https://example.com/Home/LoginExt"
    post_url = "https://example.com/Home/LoginExtCheck"

    mock_token = "mocked-token"
    mock_cookies = {"sessionid": "abcd1234"}

    # Preparar un mock para generar_token_y_cookie
    monkeypatch.setattr("badg3rfuzz.generar_token_y_cookie", lambda *args, **kwargs: (mock_token, mock_cookies))

    # Mock de requests.Session
    mock_response = Mock()
    mock_response.text = '{"Result": true}'  # <- éxito esperado
    mock_response.status_code = 200

    class MockSession:
        def __init__(self, *args, **kwargs):
            self.cookies = {}

        def __enter__(self):
            self.cookies.update(mock_cookies)
            return self

        def __exit__(self, *args):
            pass

        def post(self, url, headers=None, data=None, timeout=None):
            return mock_response

    monkeypatch.setattr("badg3rfuzz.requests.Session", MockSession)

    # Limpiar success_flag antes de ejecutar
    success_flag.clear()

    # Ejecutar
    response = login_attempt(username, password, site_key, captcha_action, login_url, post_url)

    # Validar
    assert response.status_code == 200
    assert check_success(response) is True
    assert success_flag.is_set()
