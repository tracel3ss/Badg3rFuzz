import pytest
import builtins
import os
import sys
from unittest.mock import patch, MagicMock
import badg3rfuzz

@pytest.fixture(autouse=True)
def reset_globals():
    # Antes de cada test, limpia los eventos y listas globales
    badg3rfuzz.stop_event.clear()
    badg3rfuzz.success_flag.clear()
    badg3rfuzz.active_drivers.clear()
    yield
    badg3rfuzz.stop_event.clear()
    badg3rfuzz.success_flag.clear()
    badg3rfuzz.active_drivers.clear()

def test_raises_if_stop_or_success_set():
    badg3rfuzz.stop_event.set()
    with pytest.raises(Exception, match="Operation cancelled by user"):
        badg3rfuzz.generar_token_y_cookie("key", "action", "url")
    badg3rfuzz.stop_event.clear()
    badg3rfuzz.success_flag.set()
    with pytest.raises(Exception, match="Operation cancelled by user"):
        badg3rfuzz.generar_token_y_cookie("key", "action", "url")

@patch("badg3rfuzz.webdriver.Firefox")
@patch("badg3rfuzz.FirefoxService")
@patch("badg3rfuzz.os.path.isfile")
@patch("badg3rfuzz.os.path.exists")
@patch("badg3rfuzz.sys.exit")
def test_firefox_flow(sys_exit_mock, path_exists_mock, path_isfile_mock, firefox_service_mock, firefox_webdriver_mock):
    # Configurar mocks para simular archivo geckodriver presente y path de firefox
    path_isfile_mock.return_value = True
    path_exists_mock.side_effect = lambda p: True if "firefox" in p.lower() else False

    # Crear un mock de driver con métodos necesarios
    driver_mock = MagicMock()
    driver_mock.get_cookies.return_value = [{"name": "session", "value": "abc123"}]
    driver_mock.execute_script.return_value = "fake_token"
    firefox_webdriver_mock.return_value = driver_mock

    # Llamar a la función
    token, cookies = badg3rfuzz.generar_token_y_cookie("site_key", "captcha_action", "http://login.url", webdriver_type="firefox")

    # Assert básico
    assert token == "fake_token"
    assert cookies == {"session": "abc123"}

    # Revisar que driver se añadió y luego quitó correctamente
    assert driver_mock not in badg3rfuzz.active_drivers
    driver_mock.quit.assert_called_once()

@patch("badg3rfuzz.os.path.isfile")
@patch("badg3rfuzz.sys.exit")
@patch("badg3rfuzz.webdriver.Firefox")
def test_firefox_no_geckodriver(firefox_webdriver_mock, sys_exit_mock, path_isfile_mock):
    path_isfile_mock.return_value = False

    # Evitar que intente iniciar Firefox real
    firefox_webdriver_mock.return_value = MagicMock()

    badg3rfuzz.generar_token_y_cookie("k", "a", "u")

    sys_exit_mock.assert_called_once_with(1)

@patch("badg3rfuzz.webdriver.Chrome")
@patch("badg3rfuzz.ChromeService")
@patch("badg3rfuzz.ChromeOptions")
@patch("badg3rfuzz.ChromeDriverManager")
def test_chrome_flow(chrome_manager_mock, chrome_options_mock, chrome_service_mock, chrome_webdriver_mock):
    driver_mock = MagicMock()
    driver_mock.get_cookies.return_value = [{"name": "sid", "value": "val"}]
    driver_mock.execute_script.return_value = "chrome_token"
    chrome_webdriver_mock.return_value = driver_mock

    chrome_manager_mock().install.return_value = "chromedriver_path"
    chrome_service_mock.return_value = "service_mock"
    chrome_options_mock.return_value = MagicMock()

    token, cookies = badg3rfuzz.generar_token_y_cookie("k", "a", "u", webdriver_type="chrome")

    assert token == "chrome_token"
    assert cookies == {"sid": "val"}
    driver_mock.quit.assert_called_once()
    assert driver_mock not in badg3rfuzz.active_drivers
