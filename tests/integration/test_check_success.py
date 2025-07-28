# test_check_success.py
import pytest
from badg3rfuzz import check_success

class MockResponse:
    def __init__(self, text, json_data):
        self.text = text
        self._json = json_data

    def json(self):
        return self._json

@pytest.mark.unit
def test_check_success_true():
    mock_resp = MockResponse("Welcome back", {"Result": True})
    assert check_success(mock_resp) is True

@pytest.mark.unit
def test_check_success_false_text():
    mock_resp = MockResponse("Try again", {"Result": False})
    assert check_success(mock_resp) is False

@pytest.mark.unit
def test_check_success_false_json():
    mock_resp = MockResponse("Success", {"Result": False})
    assert check_success(mock_resp) is False
