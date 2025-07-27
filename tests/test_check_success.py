import pytest
from unittest.mock import MagicMock
import badg3rfuzz

def make_response(text="", status_code=200, url="", cookies=None, history=None, json_data=None):
    """Helper para crear un mock de response con propiedades necesarias."""
    resp = MagicMock()
    resp.text = text
    resp.status_code = status_code
    resp.url = url
    resp.cookies = cookies if cookies is not None else {}
    resp.history = history if history is not None else []
    if json_data is not None:
        resp.json.return_value = json_data
    else:
        resp.json.side_effect = ValueError("No JSON")
    return resp

def test_fail_pattern_found_verbose():
    response = make_response(text="Error: usuario erróneo")
    result, msg = badg3rfuzz.check_success(
        response,
        success_indicators=["success"],
        fail_indicators=["usuario"],
        success_codes=[302],
        verbose=True
    )
    assert result is False
    assert "Fail pattern detected" in msg

def test_success_pattern_found():
    response = make_response(text="Bienvenido al dashboard")
    result, msg = badg3rfuzz.check_success(
        response,
        success_indicators=["bienvenido", "dashboard"],
        fail_indicators=["error"],
        success_codes=[302]
    )
    assert result is True
    assert "Success pattern detected" in msg

def test_redirect_success():
    response = make_response(url="http://example.com/dashboard", history=[1])
    result, msg = badg3rfuzz.check_success(
        response,
        success_indicators=[],
        fail_indicators=[],
        success_codes=[302]
    )
    assert result is True
    assert "Success redirect to" in msg

def test_session_cookie_detected():
    response = make_response(
        cookies={"PHPSESSID": "abc123", "othercookie": "val"}
    )
    result, msg = badg3rfuzz.check_success(
        response,
        success_indicators=[],
        fail_indicators=[],
        success_codes=[302],
        check_cookies=True
    )
    assert result is True
    assert "Session cookie set" in msg

def test_json_result_false():
    response = make_response(json_data={"Result": False, "Msg": "Credenciales invalidas"})
    result, msg = badg3rfuzz.check_success(
        response,
        success_indicators=[],
        fail_indicators=[],
        success_codes=[302]
    )
    assert result is False
    assert "JSON Result=False" in msg

def test_json_result_true():
    response = make_response(json_data={"Result": True})
    result, msg = badg3rfuzz.check_success(
        response,
        success_indicators=[],
        fail_indicators=[],
        success_codes=[302]
    )
    assert result is True
    assert msg == "JSON Result=True"

def test_http_success_code_non_200_verbose():
    response = make_response(status_code=302)
    result, msg = badg3rfuzz.check_success(
        response,
        success_indicators=[],
        fail_indicators=[],
        success_codes=[302],
        verbose=True
    )
    assert result is True
    assert "Success HTTP code" in msg

def test_no_success_indicators():
    response = make_response(text="Nada relevante", status_code=404)
    result, msg = badg3rfuzz.check_success(
        response,
        success_indicators=["ok"],
        fail_indicators=["fail"],
        success_codes=[302]
    )
    assert result is False
    assert "No success indicators found" in msg

def test_check_cookies_false_does_not_detect_cookie():
    response = make_response(
        cookies={"sessionid": "abc123"}
    )
    result, msg = badg3rfuzz.check_success(
        response,
        success_indicators=[],
        fail_indicators=[],
        success_codes=[302],
        check_cookies=False
    )
    assert result is False
