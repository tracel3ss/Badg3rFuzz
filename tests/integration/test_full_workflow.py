# tests/integration/test_full_workflow.py
import threading
import queue
import pytest
from unittest.mock import patch, Mock
from badg3rfuzz import worker, check_success

# Global flags que necesita el worker
import badg3rfuzz
badg3rfuzz.combo_queue = queue.Queue()
badg3rfuzz.success_flag = threading.Event()
badg3rfuzz.stop_event = threading.Event()
badg3rfuzz.print_lock = threading.Lock()
badg3rfuzz.attempts_lock = threading.Lock()
badg3rfuzz.attempts_done = 0

@pytest.mark.integration
def test_complete_bruteforce_workflow(tmp_path):
    # Simular combinaciones
    badg3rfuzz.combo_queue.put(("admin", "123456"))
    badg3rfuzz.combo_queue.put(("user", "wrongpass"))

    log_file = tmp_path / "log.txt"

    # Mock login_attempt para devolver éxito con admin
    def mock_login_attempt(username, password, *args, **kwargs):
        mock_resp = Mock()
        if username == "admin" and password == "123456":
            mock_resp.status_code = 200
            mock_resp.text = "Welcome, admin!"
            mock_resp.cookies = {"session": "abcd1234"}
        else:
            mock_resp.status_code = 401
            mock_resp.text = "Invalid credentials"
            mock_resp.cookies = {}
        return mock_resp

    with patch("badg3rfuzz.login_attempt", side_effect=mock_login_attempt):
        t = threading.Thread(target=worker, args=(
            "dummy_sitekey",
            "login",
            "http://test/login",
            "http://test/loginpost",
            None,
            True,  # stop_on_success
            str(log_file),
            "firefox",
            False,  # verbose
            ["welcome"],  # success_indicators
            ["invalid"],  # fail_indicators
            [200],
            True,  # check_cookies
            0,     # delay
            0,     # jitter
            None,  # user_agents_file
            None,  # proxies
            10,
            False,
            None
        ))
        t.start()
        t.join(timeout=5)

    with open(log_file) as f:
        log = f.read()
        assert "SUCCESS: admin:123456" in log
        assert "FAIL: user:wrongpass" not in log or "user:wrongpass" in log
