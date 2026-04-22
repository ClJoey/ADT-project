import pytest
from pages.login_page import LoginPage, URL
from data.credenciales import USER
from utils.screenshots import guardar_captura
from utils.report_html import generar_html

_resultados = []

@pytest.fixture(scope="module", autouse=True)
def reporte_login():
    yield
    if _resultados:
        generar_html({
            "empresa": "00 Tests de Login",
            "rut": "N/A",
            "reportes": _resultados
        })

def test_login_ok(driver):
    login = LoginPage(driver)
    login.load()
    login.login(USER[0]["usuario"], USER[0]["password"])
    ok = login.is_login_exitoso()
    captura = guardar_captura(driver, "login", "test_login_ok")
    _resultados.append({
        "nombre": "Login exitoso con credenciales válidas",
        "estado": "OK" if ok else "FAIL",
        "errores": [] if ok else ["La tabla de empresas no apareció tras el login"],
        "captura": captura
    })
    assert ok

def test_login_usuario_institucional_incorrecto(driver):
    login = LoginPage(driver)
    login.load()
    login.username("cuenta_creada@cenco.cl")
    ok = login.is_error_user_displayed()
    captura = guardar_captura(driver, "login", "test_login_usuario_incorrecto")
    _resultados.append({
        "nombre": "Rechazo de usuario institucional inválido",
        "estado": "OK" if ok else "FAIL",
        "errores": [] if ok else ["Toast de error no apareció"],
        "captura": captura
    })
    assert ok

def test_login_password_incorrecta(driver):
    login = LoginPage(driver)
    login.load()
    login.login("abc@baplicada.cl", "1234")
    ok = login.is_error_user_password_displayed()
    captura = guardar_captura(driver, "login", "test_login_password_incorrecta")
    _resultados.append({
        "nombre": "Rechazo de contraseña incorrecta",
        "estado": "OK" if ok else "FAIL",
        "errores": [] if ok else ["Toast de contraseña inválida no apareció"],
        "captura": captura
    })
    assert ok

def test_login_campos_vacios(driver):
    login = LoginPage(driver)
    login.load()
    login.username("")
    ok = login.is_error_user_displayed()
    captura = guardar_captura(driver, "login", "test_login_campos_vacios")
    _resultados.append({
        "nombre": "Rechazo de campos vacíos",
        "estado": "OK" if ok else "FAIL",
        "errores": [] if ok else ["Toast de error no apareció con campos vacíos"],
        "captura": captura
    })
    assert ok
