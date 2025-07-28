# tests/integration/test_token_cookie_generation.py
import pytest
from unittest.mock import patch, MagicMock
from badg3rfuzz import generar_token_y_cookie, stop_event, success_flag

@pytest.mark.integration
def test_generar_token_y_cookie_mocked():
 """Test completo para generar_token_y_cookie con mocking total"""
    
    # Mock completo del webdriver y dependencias
    mock_driver = Mock()
    mock_driver.get_cookies.return_value = [
        {"name": "sessionid", "value": "test123"},
        {"name": "csrftoken", "value": "csrf123"}
    ]
    mock_driver.execute_script.return_value = "mocked_recaptcha_token"
    mock_driver.get.return_value = None
    mock_driver.quit.return_value = None
    
    with patch('os.path.isfile', return_value=True):  # Mock geckodriver exists
        with patch('os.path.exists', return_value=True):  # Mock firefox exists
            with patch('selenium.webdriver.Firefox', return_value=mock_driver):
                with patch('selenium.webdriver.firefox.service.Service'):
                    with patch('selenium.webdriver.firefox.options.Options'):
                        with patch('selenium.webdriver.support.ui.WebDriverWait') as mock_wait:
                            # Mock WebDriverWait timeout (captcha not found)
                            mock_wait.return_value.until.side_effect = Exception("Timeout")
                            
                            # Mock threading events
                            with patch('badg3rfuzz.stop_event') as mock_stop:
                                with patch('badg3rfuzz.success_flag') as mock_success:
                                    mock_stop.is_set.return_value = False
                                    mock_success.is_set.return_value = False
                                    
                                    # Mock print_lock y active_drivers
                                    with patch('badg3rfuzz.print_lock'):
                                        with patch('badg3rfuzz.drivers_lock'):
                                            with patch('badg3rfuzz.active_drivers', []):
                                                
                                                # Ejecutar la función
                                                token, cookies = generar_token_y_cookie(
                                                    site_key="test_site_key",
                                                    captcha_action="login",
                                                    login_url="https://example.com/login",
                                                    webdriver_type="firefox",
                                                    verbose=True
                                                )
    
    # Verificar resultados
    assert token == "mocked_recaptcha_token"
    assert cookies == {"sessionid": "test123", "csrftoken": "csrf123"}
    
    # Verificar que se llamaron los métodos esperados
    mock_driver.get.assert_called_once_with("https://example.com/login")
    mock_driver.execute_script.assert_called_once()
    mock_driver.get_cookies.assert_called_once()
    mock_driver.quit.assert_called_once()

@pytest.mark.integration
def test_generar_token_y_cookie_chrome():
    """Test para generar_token_y_cookie con Chrome"""
    
    mock_driver = Mock()
    mock_driver.get_cookies.return_value = [{"name": "session", "value": "chrome_test"}]
    mock_driver.execute_script.return_value = "chrome_token"
    
    with patch('selenium.webdriver.Chrome', return_value=mock_driver):
        with patch('selenium.webdriver.chrome.service.Service'):
            with patch('selenium.webdriver.chrome.options.Options'):
                with patch('webdriver_manager.chrome.ChromeDriverManager') as mock_manager:
                    mock_manager.return_value.install.return_value = "/usr/local/bin/chromedriver"
                    
                    with patch('selenium.webdriver.support.ui.WebDriverWait') as mock_wait:
                        mock_wait.return_value.until.side_effect = Exception("Timeout")
                        
                        with patch('badg3rfuzz.stop_event') as mock_stop:
                            with patch('badg3rfuzz.success_flag') as mock_success:
                                mock_stop.is_set.return_value = False
                                mock_success.is_set.return_value = False
                                
                                with patch('badg3rfuzz.print_lock'):
                                    with patch('badg3rfuzz.drivers_lock'):
                                        with patch('badg3rfuzz.active_drivers', []):
                                            with patch('builtins.open', mock_open()):
                                                
                                                token, cookies = generar_token_y_cookie(
                                                    site_key="test_key",
                                                    captcha_action="submit",
                                                    login_url="https://test.com",
                                                    webdriver_type="chrome",
                                                    verbose=False
                                                )
    
    assert token == "chrome_token"
    assert cookies == {"session": "chrome_test"}

def mock_open(read_data=""):
    """Helper para crear mock_open"""
    from unittest.mock import mock_open as original_mock_open
    return original_mock_open(read_data=read_data)
