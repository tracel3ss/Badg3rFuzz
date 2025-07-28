# tests/integration/test_token_cookie_generation.py
import pytest
from unittest.mock import patch, MagicMock
from badg3rfuzz import generar_token_y_cookie, stop_event, success_flag

@pytest.mark.integration
def test_generar_token_y_cookie_mocked():
    # Limpiar eventos para que no lancen excepción
    stop_event.clear()
    success_flag.clear()

    mock_driver = MagicMock()
    mock_driver.execute_script.return_value = "mocked_token"
    mock_driver.get_cookies.return_value = [{"name": "sessionid", "value": "abc123"}]

    with patch("badg3rfuzz.webdriver.Firefox", return_value=mock_driver), \
         patch("badg3rfuzz.FirefoxService") as mock_service:
        
        token, cookies = generar_token_y_cookie(
            site_key="dummy_sitekey",
            captcha_action="login",
            login_url="http://test/login",
            webdriver_type="firefox",
            verbose=False
        )

    assert token == "mocked_token"
    assert isinstance(cookies, dict)
    assert cookies.get("sessionid") == "abc123"
