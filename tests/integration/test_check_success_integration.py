# tests/integration/test_check_success_integration.py
import pytest
from requests.models import Response
from badg3rfuzz import check_success

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
