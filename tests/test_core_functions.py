# tests/test_core_functions.py - Tests de funciones principales
import pytest
from unittest.mock import patch, Mock, mock_open
import tempfile
import os
from datetime import datetime
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importar funciones del módulo principal
from badg3rfuzz import (
     cargar_diccionario, cargar_user_agents, cargar_proxies,
     check_success, generar_fuzzers, convert_der_to_pem_if_needed,
     generar_token_y_cookie
 )


class TestCoreFunction:
    
    def test_cargar_diccionario_file_exists(self, temp_wordlist):
        """Test cargar diccionario desde archivo existente"""
        result = cargar_diccionario(temp_wordlist)
        assert len(result) == 3
        assert "admin" in result
        assert "test" in result
        pass  # Implementar cuando importer el módulo
    
    def test_convert_der_to_pem_if_needed_with_non_der(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write("-----BEGIN CERTIFICATE-----\nFAKECERT\n-----END CERTIFICATE-----")
            f.flush()
            path = f.name

        result = convert_der_to_pem_if_needed(path)
        assert result == path

    @pytest.fixture
    def mock_webdriver(monkeypatch):
        mock_driver = Mock()
        mock_driver.get_cookies.return_value = [{"name": "session", "value": "test123"}]
        mock_driver.execute_script.return_value = "test_token_123"
        monkeypatch.setattr("selenium.webdriver.Firefox", lambda *a, **k: mock_driver)
        monkeypatch.setattr("selenium.webdriver.Chrome", lambda *a, **k: mock_driver)
        yield mock_driver

    def test_generar_token_y_cookie(mock_webdriver):
        site_key = "6LfKj9EpAAAAAP8xQ7R2vN5mT6wU3bY8zC1dE4fG"
        captcha_action = "login"
        login_url = "http://test.com/login"
        with patch("badg3rfuzz.webdriver.Firefox") as mock_driver:
            mock_driver_instance = mock_driver.return_value
            mock_driver_instance.execute_script.return_value = "test_token_123"
            mock_driver_instance.get_cookies.return_value = [{"name": "session", "value": "test123"}]
            
            token, cookies = generar_token_y_cookie(site_key, captcha_action, login_url, webdriver_type="firefox")

            assert token == "test_token_123"
            assert cookies == {"session": "test123"}

    def test_cargar_diccionario_file_not_exists(self):
        """Test cargar diccionario con archivo inexistente"""
        result = cargar_diccionario("nonexistent.txt")
        assert result == []
        pass
    
    def test_generar_fuzzers_digits(self):
        """Test generación de fuzzers numéricos"""
        result = generar_fuzzers("digits", 5, 5, 10)
        assert len(result) == 10
        assert all(len(item) == 5 for item in result)
        assert all(item.isdigit() for item in result)
        pass
    
    def test_generar_fuzzers_mix(self):
        """Test generación de fuzzers mixtos"""
        result = generar_fuzzers("mix", 3, 8, 5)
        assert len(result) == 5
        assert all(3 <= len(item) <= 8 for item in result)
        pass
    
    def test_check_success_json_response(self, mock_response):
        """Test detección de éxito por respuesta JSON"""
        mock_resp = mock_response(
            status_code=200,
            json_data={"Result": True, "Msg": "Login successful"}
        )
        
        success, msg = check_success(
            mock_resp, ["success"], ["error"], [302], True, False
        )
        assert success is True
        assert "Session cookie set" in msg
        pass
    
    def test_check_success_content_pattern(self, mock_response):
        """Test detección de éxito por patrón en contenido"""
        mock_resp = mock_response(
            text="Welcome to dashboard",
            status_code=200
        )
        
        success, msg = check_success(
            mock_resp, ["welcome", "dashboard"], ["error"], [302], True, False
        )
        assert success is True
        assert "Success pattern detected" in msg
        pass
    
    def test_check_success_fail_pattern(self, mock_response):
        """Test detección de fallo por patrón"""
        mock_resp = mock_response(
            text="Usuario o contraseña erróneos",
            status_code=200
        )
        
        success, msg = check_success(
            mock_resp, ["welcome"], ["erróneos", "error"], [302], True, False
        )
        assert success is False
        assert "Fail pattern detected" in msg
        pass