import pytest
from badg3rfuzz import check_success

class MockResponse:
    def __init__(self, text, json_data):
        self.text = text
        self._json = json_data
        self.cookies = {}  # Simula cookies vacías
        self.status_code = 200  # Código HTTP por defecto
        self.history = []  # No hay redirecciones por defecto
        self.url = "http://example.com/home"  # URL de ejemplo para test de redirección

    def json(self):
        return self._json

# Indicadores de éxito y fallo comunes
success_indicators = ["welcome", "success", "logged in"]
fail_indicators = ["try again", "invalid", "error"]
success_codes = [302, 301]

@pytest.mark.unit
def test_check_success_true():
    mock_resp = MockResponse("Welcome back", {"Result": True})
    result, _ = check_success(mock_resp, success_indicators, fail_indicators, success_codes)
    assert result is True

@pytest.mark.unit
def test_check_success_false_text():
    mock_resp = MockResponse("Try again", {"Result": False})
    result, _ = check_success(mock_resp, success_indicators, fail_indicators, success_codes)
    assert result is False

@pytest.mark.unit
def test_check_success_false_json():
    mock_resp = MockResponse("Success", {"Result": False})
    result, _ = check_success(mock_resp, success_indicators, fail_indicators, success_codes)
    assert result is False
