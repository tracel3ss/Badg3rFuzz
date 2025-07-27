# tests/conftest.py - Configuración global de pytest
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
import requests_mock


@pytest.fixture
def mock_webdriver():
    """Mock WebDriver para tests sin navegador real"""
    with patch('selenium.webdriver.Firefox') as mock_firefox, \
         patch('selenium.webdriver.Chrome') as mock_chrome:
        
        mock_driver = Mock()
        mock_driver.get_cookies.return_value = [
            {"name": "session", "value": "test123"}
        ]
        mock_driver.execute_script.return_value = "test_token_123"
        
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
    def _mock_response(status_code=200, json_data=None, text="", cookies=None):
        mock_resp = Mock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = json_data or {}
        mock_resp.text = text
        mock_resp.cookies = cookies or {}
        mock_resp.history = []
        mock_resp.url = "http://test.com/login"
        return mock_resp
    return _mock_response