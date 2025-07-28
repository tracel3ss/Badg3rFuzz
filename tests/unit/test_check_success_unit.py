# tests/unit/test_check_success.py

import pytest
from unittest.mock import Mock
from badg3rfuzz import check_success


class MockResponse:
    def __init__(self, text="", json_data=None, raise_json=False, status_code=200, cookies=None):
        self.text = text
        self.status_code = status_code
        self.cookies = cookies or {}
        self._json_data = json_data
        self._raise_json = raise_json

    def json(self):
        if self._raise_json:
            raise ValueError("Invalid JSON")
        return self._json_data


@pytest.mark.unit
@pytest.mark.parametrize("json_data, raise_json, expected_success, expected_reason", [
    # Caso: JSON válido, Result=False con mensaje
    ({"Result": False, "Msg": "Credenciales incorrectas"}, False, False, "JSON Result=False: Credenciales incorrectas"),

    # Caso: JSON válido, Result=False sin mensaje
    ({"Result": False}, False, False, "JSON Result=False: Unknown JSON error"),

    # Caso: JSON válido, Result=True explícito
    ({"Result": True}, False, True, "JSON Result=True"),

    # Caso: No es JSON (ValueError), debe pasar de largo y retornar según otras capas (omitidas aquí)
    (None, True, None, None),  # No se evalúa success/failure en este test
])
def test_check_success_json_layer(json_data, raise_json, expected_success, expected_reason):
    response = MockResponse(json_data=json_data, raise_json=raise_json)

    success, reason = check_success(
        response=response,
        success_indicators=[],  # ignorado en esta capa
        fail_indicators=[],
        success_codes=[],
        check_cookies=False,
        verbose=True
    )

    if expected_success is None:
        # Este test no se encarga de validar otros caminos (como redirecciones o cookies)
        assert success in [True, False]  # Solo verificamos que no haya excepción
    else:
        assert success == expected_success
        assert reason == expected_reason
