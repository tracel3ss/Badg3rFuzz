import pytest
from unittest.mock import patch, mock_open, MagicMock
import badg3rfuzz
import os

@patch("badg3rfuzz.os.path.exists")
def test_return_original_if_path_not_exists(path_exists_mock):
    path_exists_mock.return_value = False
    result = badg3rfuzz.convert_der_to_pem_if_needed("fakepath")
    assert result == "fakepath"

@patch("badg3rfuzz.os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"-----BEGIN CERTIFICATE-----")
def test_return_original_if_pem(open_mock, path_exists_mock):
    result = badg3rfuzz.convert_der_to_pem_if_needed("cert.pem")
    assert result == "cert.pem"

@patch("badg3rfuzz.os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"binarydata")
@patch("badg3rfuzz.tempfile.mkstemp")
@patch("badg3rfuzz.subprocess.run")
@patch("badg3rfuzz.os.remove")
def test_successful_der_to_pem_conversion(remove_mock, subprocess_run_mock, mkstemp_mock, open_mock, path_exists_mock):
    fd = os.open(os.devnull, os.O_RDONLY)
    mkstemp_mock.return_value = (fd, "temp.pem")

    subprocess_run_mock.return_value = MagicMock(returncode=0, stderr="")
    result = badg3rfuzz.convert_der_to_pem_if_needed("cert.der")

    # NO cerrar fd aquí, porque la función ya lo cierra
    assert result == "temp.pem"
    remove_mock.assert_not_called()

@patch("badg3rfuzz.os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"binarydata")
@patch("badg3rfuzz.tempfile.mkstemp")
@patch("badg3rfuzz.subprocess.run")
@patch("badg3rfuzz.os.remove")
def test_failed_der_to_pem_conversion(remove_mock, subprocess_run_mock, mkstemp_mock, open_mock, path_exists_mock):
    fd = os.open(os.devnull, os.O_RDONLY)
    mkstemp_mock.return_value = (fd, "temp.pem")

    subprocess_run_mock.return_value = MagicMock(returncode=1, stderr="error converting")

    result = badg3rfuzz.convert_der_to_pem_if_needed("cert.der")

    # NO cerrar fd aquí, porque la función ya lo cierra
    assert result is None
    remove_mock.assert_called_once_with("temp.pem")

@patch("badg3rfuzz.os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"binarydata")
@patch("badg3rfuzz.tempfile.mkstemp")
@patch("badg3rfuzz.subprocess.run", side_effect=FileNotFoundError)
@patch("badg3rfuzz.os.remove")
def test_openssl_not_found(remove_mock, subprocess_run_mock, mkstemp_mock, open_mock, path_exists_mock):
    fd = os.open(os.devnull, os.O_RDONLY)
    mkstemp_mock.return_value = (fd, "temp.pem")

    result = badg3rfuzz.convert_der_to_pem_if_needed("cert.der")

    # NO cerrar fd aquí, porque la función ya lo cierra
    assert result is None
    remove_mock.assert_called_once_with("temp.pem")

@patch("badg3rfuzz.os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open)
def test_error_reading_certificate(open_mock, path_exists_mock):
    open_mock.side_effect = Exception("Read error")
    result = badg3rfuzz.convert_der_to_pem_if_needed("cert.der")
    assert result is None
