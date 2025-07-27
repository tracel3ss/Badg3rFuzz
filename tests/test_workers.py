import pytest
from unittest.mock import patch, MagicMock, mock_open
import threading
import queue
import badg3rfuzz

@pytest.fixture(autouse=False)
def reset_globals():
    badg3rfuzz.success_flag.clear()
    badg3rfuzz.stop_event.clear()
    with badg3rfuzz.attempts_lock:
        badg3rfuzz.attempts_done = 0
    while not badg3rfuzz.combo_queue.empty():
        badg3rfuzz.combo_queue.get()
        badg3rfuzz.combo_queue.task_done()

@pytest.mark.usefixtures("reset_globals")
@patch("badg3rfuzz.cargar_user_agents", return_value=["ua1", "ua2"])
@patch("badg3rfuzz.login_attempt")
@patch("badg3rfuzz.check_success")
@patch("time.sleep", return_value=None)
@patch("builtins.open", new_callable=mock_open)
def test_worker_success_flow(open_mock, sleep_mock, check_success_mock, login_attempt_mock, user_agents_mock):
    badg3rfuzz.combo_queue.put(("user1", "pass1"))
    badg3rfuzz.combo_queue.put(("user2", "pass2"))

    # Simula respuesta exitosa
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}
    login_attempt_mock.return_value = mock_response

    # check_success devuelve éxito en primer intento
    check_success_mock.side_effect = [(True, None), (False, None)]

    badg3rfuzz.worker(
        site_key="site",
        captcha_action="act",
        login_url="http://login",
        post_url="http://post",
        origin_url="http://origin",
        stop_on_success=True,
        log_filename="log.txt",
        webdriver_type="firefox",
        verbose=True,
        success_indicators=["ok"],
        fail_indicators=[],
        success_codes=[200],
        check_cookies=True,
        delay=0,
        jitter=0,
        user_agents_file="useragents.txt",
        proxies_list=None,
        proxy_timeout=10,
        disable_ssl_verify=False,
        ca_cert_path=None
    )

    # Validar escritura log éxito
    open_mock().write.assert_any_call("SUCCESS: user1:pass1\n")
    # success_flag seteado
    assert badg3rfuzz.success_flag.is_set()
    # Cola vacía tras stop_on_success
    assert badg3rfuzz.combo_queue.empty()
    # attempts_done incrementado
    assert badg3rfuzz.attempts_done >= 1

@pytest.mark.usefixtures("reset_globals")
@patch("badg3rfuzz.cargar_user_agents", return_value=["ua1"])
@patch("badg3rfuzz.login_attempt")
@patch("badg3rfuzz.check_success")
@patch("time.sleep", return_value=None)
@patch("builtins.open", new_callable=mock_open)
def test_worker_failure_flow(open_mock, sleep_mock, check_success_mock, login_attempt_mock, user_agents_mock):
    badg3rfuzz.combo_queue.put(("user_fail", "pass_fail"))

    # Respuesta fallida
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"fail": True}
    login_attempt_mock.return_value = mock_response

    # check_success retorna fallo
    check_success_mock.return_value = (False, "fail")

    badg3rfuzz.worker(
        site_key="k",
        captcha_action="a",
        login_url="http://login",
        post_url="http://post",
        origin_url="http://origin",
        stop_on_success=False,
        log_filename="log.txt",
        webdriver_type="chrome",
        verbose=False,
        success_indicators=[],
        fail_indicators=[],
        success_codes=[200],
        check_cookies=False,
        delay=0,
        jitter=0,
        user_agents_file="ua.txt",
        proxies_list=None,
        proxy_timeout=5,
        disable_ssl_verify=True,
        ca_cert_path=None
    )

    # Verificar escritura log fallo
    open_mock().write.assert_any_call("[-] FAIL: user_fail:pass_fail\n")
    # Flag éxito no seteado
    assert not badg3rfuzz.success_flag.is_set()
    assert badg3rfuzz.combo_queue.empty()

@pytest.mark.usefixtures("reset_globals")
@patch("badg3rfuzz.cargar_user_agents", return_value=["ua1"])
@patch("badg3rfuzz.login_attempt", side_effect=Exception("Proxy Error"))
@patch("builtins.print")
def test_worker_proxy_exception_handling(print_mock, login_attempt_mock, user_agents_mock):
    badg3rfuzz.combo_queue.put(("proxy_user", "proxy_pass"))

    badg3rfuzz.worker(
        site_key="sk",
        captcha_action="ca",
        login_url="http://login",
        post_url="http://post",
        origin_url="http://origin",
        stop_on_success=False,
        log_filename="log.txt",
        webdriver_type="firefox",
        verbose=True,
        success_indicators=[],
        fail_indicators=[],
        success_codes=[],
        check_cookies=False,
        delay=0,
        jitter=0,
        user_agents_file="ua.txt",
        proxies_list=None,
        proxy_timeout=5,
        disable_ssl_verify=False,
        ca_cert_path=None
    )

    # Debió imprimir mensaje con "Proxy Error"
    print_mock.assert_any_call("\r" + " " * 80 + "\r", end='')
    print_mock.assert_any_call("\033[91m[!] Proxy Error with proxy_user:proxy_pass: Proxy Error\033[0m")
    assert badg3rfuzz.combo_queue.empty()

@pytest.mark.usefixtures("reset_globals")
@patch("badg3rfuzz.cargar_user_agents", return_value=["ua1"])
@patch("badg3rfuzz.login_attempt", side_effect=Exception("Other Error"))
@patch("builtins.print")
def test_worker_general_exception_handling(print_mock, login_attempt_mock, user_agents_mock):
    badg3rfuzz.combo_queue.put(("userx", "passx"))

    badg3rfuzz.worker(
        site_key="sk",
        captcha_action="ca",
        login_url="http://login",
        post_url="http://post",
        origin_url="http://origin",
        stop_on_success=False,
        log_filename="log.txt",
        webdriver_type="chrome",
        verbose=True,
        success_indicators=[],
        fail_indicators=[],
        success_codes=[],
        check_cookies=False,
        delay=0,
        jitter=0,
        user_agents_file="ua.txt",
        proxies_list=None,
        proxy_timeout=5,
        disable_ssl_verify=False,
        ca_cert_path=None
    )

    # Debió imprimir mensaje general de error
    print_mock.assert_any_call("\r" + " " * 80 + "\r", end='')
    print_mock.assert_any_call("\033[91m[!] Error with userx:passx: Other Error\033[0m")
    assert badg3rfuzz.combo_queue.empty()

@pytest.mark.usefixtures("reset_globals")
@patch("badg3rfuzz.cargar_user_agents", return_value=["ua1"])
@patch("badg3rfuzz.login_attempt")
@patch("badg3rfuzz.check_success")
@patch("time.sleep", return_value=None)
@patch("builtins.open", new_callable=mock_open)
def test_worker_proxy_rotation_and_delay(open_mock, sleep_mock, check_success_mock, login_attempt_mock, user_agents_mock):
    badg3rfuzz.combo_queue.put(("user1", "pass1"))
    badg3rfuzz.combo_queue.put(("user2", "pass2"))
    proxies = ["proxy1", "proxy2", "proxy3"]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}
    login_attempt_mock.return_value = mock_response

    check_success_mock.return_value = (False, None)  # para no detenerse

    badg3rfuzz.worker(
        site_key="site",
        captcha_action="act",
        login_url="http://login",
        post_url="http://post",
        origin_url="http://origin",
        stop_on_success=False,
        log_filename="log.txt",
        webdriver_type="firefox",
        verbose=False,
        success_indicators=[],
        fail_indicators=[],
        success_codes=[200],
        check_cookies=False,
        delay=1,
        jitter=0.5,
        user_agents_file="ua.txt",
        proxies_list=proxies,
        proxy_timeout=10,
        disable_ssl_verify=False,
        ca_cert_path=None
    )
    # Se rotaron proxies, por lo que login_attempt_mock debe llamarse con proxies en orden
    called_proxies = [call.args[10] for call in login_attempt_mock.call_args_list]
    assert called_proxies == proxies[:len(called_proxies)]

    # time.sleep fue llamado con delay + jitter (aproximado)
    sleep_mock.assert_called()

@pytest.mark.usefixtures("reset_globals")
@patch("badg3rfuzz.cargar_user_agents", return_value=["ua1"])
@patch("badg3rfuzz.login_attempt")
@patch("badg3rfuzz.check_success")
@patch("time.sleep", return_value=None)
@patch("builtins.open", new_callable=mock_open)
def test_worker_queue_empty_handling(open_mock, sleep_mock, check_success_mock, login_attempt_mock, user_agents_mock):
    # Cola vacía al inicio, no hay combos para procesar

    badg3rfuzz.worker(
        site_key="site",
        captcha_action="act",
        login_url="http://login",
        post_url="http://post",
        origin_url="http://origin",
        stop_on_success=False,
        log_filename="log.txt",
        webdriver_type="chrome",
        verbose=False,
        success_indicators=[],
        fail_indicators=[],
        success_codes=[200],
        check_cookies=False,
        delay=0,
        jitter=0,
        user_agents_file="ua.txt",
        proxies_list=None,
        proxy_timeout=10,
        disable_ssl_verify=False,
        ca_cert_path=None
    )

    # No error, simplemente termina sin procesar

