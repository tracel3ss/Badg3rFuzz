import pytest
import sys
from unittest.mock import patch
from badg3rfuzz import main

@pytest.mark.integration
def test_main_entrypoint(monkeypatch, tmp_path):
    user_file = tmp_path / "users.txt"
    pass_file = tmp_path / "pass.txt"
    user_file.write_text("admin\n")
    pass_file.write_text("123456\n")

    test_args = [
        "badg3rfuzz.py",
        "--site-key", "dummy",
        "--captcha-action", "login",
        "--login-url", "http://test/login",
        "--post-url", "http://test/post",
        "--user-file", str(user_file),
        "--pass-file", str(pass_file),
        "--threads", "2",
        "--stop-on-success"
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with patch("badg3rfuzz.os._exit") as mock_exit, \
         patch("badg3rfuzz.login_attempt") as mock_login_attempt, \
         patch("badg3rfuzz.generar_token_y_cookie", return_value=("mocked_token", {"sessionid": "abc123"})), \
         patch("badg3rfuzz.print") as mock_print, \
         patch("badg3rfuzz.worker") as mock_worker:

        # Simular respuesta exitosa para login_attempt
        mock_resp = type("MockResp", (), {
            "status_code": 200,
            "text": "Welcome back",
            "cookies": {"session": "xyz"},
            "json": lambda: {"Result": True}
        })()
        mock_login_attempt.return_value = mock_resp

        # Hacer que worker imprima directamente, sin threads
        def fake_worker(*args, **kwargs):
            print("[+] Valid Login Found! admin:123456")

        mock_worker.side_effect = fake_worker

        main()

        mock_exit.assert_called_once()
        assert any("Valid Login Found" in str(c) for c in mock_print.call_args_list)
