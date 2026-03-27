from pages.login_page import LoginPage
import time

def test_login_ok(driver):
    login = LoginPage(driver)

    login.load("https://asistenciadt.baplicada.cl/Login.aspx?FiscalizacionDT=Login")
    login.login("nicolas.perez@baplicada.cl", "6Vxc+fMd")
    assert True

def test_login_usuario_institucional_incorrecto(driver):
    login = LoginPage(driver)
    login.load("https://asistenciadt.baplicada.cl/Login.aspx?FiscalizacionDT=Login")
    login.username("cuenta_creada@cenco.cl")
    time.sleep(2)
    assert login.is_error_user_displayed()

def test_login_password_user_incorrecta(driver):
    login = LoginPage(driver)
    login.load("https://asistenciadt.baplicada.cl/Login.aspx?FiscalizacionDT=Login")
    login.login("abc@baplicada.cl", "1234")
    time.sleep(4)
    assert login.is_error_user_password_displayed()


def test_login_campos_vacios(driver):
    login = LoginPage(driver)
    login.load("https://asistenciadt.baplicada.cl/Login.aspx?FiscalizacionDT=Login")
    login.username("")
    time.sleep(2)
    assert login.is_error_user_displayed()