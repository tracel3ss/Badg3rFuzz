import pytest
import sys
from unittest.mock import patch, Mock, mock_open
from badg3rfuzz import main

@pytest.mark.integration
@patch('builtins.print')
def test_main_entrypoint(mock_print):
    """Test del punto de entrada principal"""
    
    # Mock de argumentos de línea de comandos
    test_args = [
        'badg3rfuzz.py',
        '--url', 'https://example.com/login',
        '--userlist', 'users.txt',
        '--passlist', 'passwords.txt',
        '--threads', '1'
    ]
    
    # Mock de archivos de usuarios y contraseñas
    mock_users = "admin\nuser\ntest"
    mock_passwords = "123456\npassword\nadmin"
    
    with patch('sys.argv', test_args):
        with patch('builtins.open', mock_open_multiple_files({
            'users.txt': mock_users,
            'passwords.txt': mock_passwords
        })):
            with patch('badg3rfuzz.login_attempt') as mock_login:
                # Simular un login exitoso
                mock_response = Mock()
                mock_response.text = "Welcome admin!"
                mock_response.status_code = 200
                mock_response.cookies = {"sessionid": "success"}
                mock_response.url = "https://example.com/dashboard"
                mock_response.history = [Mock()]
                mock_login.return_value = mock_response
                
                with patch('badg3rfuzz.check_success') as mock_check:
                    mock_check.return_value = (True, "Success pattern detected: welcome")
                    
                    # Ejecutar main
                    try:
                        main()
                    except SystemExit:
                        pass  # Es esperado que main() termine con sys.exit()
    
    # Verificar que se imprimió el mensaje de login válido
    print_calls = [str(call) for call in mock_print.call_args_list]
    assert any("Valid Login Found" in call_str and "admin:123456" in call_str for call_str in print_calls)

def mock_open_multiple_files(files_dict):
    """Helper para mockear múltiples archivos"""
    def mock_open_wrapper(*args, **kwargs):
        filename = args[0]
        if filename in files_dict:
            return mock_open(read_data=files_dict[filename])(*args, **kwargs)
        else:
            raise FileNotFoundError(f"No such file: {filename}")
    return mock_open_wrapper
