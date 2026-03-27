from pages.init_page import InitPage
from pages.login_page import LoginPage

def test_select_empleador(driver):
    login = LoginPage(driver)
    login.load("https://asistenciadt.baplicada.cl/Login.aspx?FiscalizacionDT=Login")
    login.login("nicolas.perez@baplicada.cl", "6Vxc+fMd")
    init = InitPage(driver)
    init.seleccionar_empresa_por_rut("76257834-4")
    init.fisc_init()

def test_validar_autocompletado(driver):
    login = LoginPage(driver)
    login.load("https://asistenciadt.baplicada.cl/Login.aspx?FiscalizacionDT=Login")
    login.login("nicolas.perez@baplicada.cl", "6Vxc+fMd")
    init = InitPage(driver)
    init.seleccionar_empresa_por_rut("76257834-4")
    assert init.validar_autocompletado("76257834-4")

def test_validar_cambio_empresa(driver):
    login = LoginPage(driver)
    login.load("https://asistenciadt.baplicada.cl/Login.aspx?FiscalizacionDT=Login")
    login.login("nicolas.perez@baplicada.cl", "6Vxc+fMd")
    init = InitPage(driver)
    init.seleccionar_empresa_por_rut("76257834-4")
    init.seleccionar_empresa_por_rut("96579730-0")
    assert init.validar_autocompletado("96579730-0")


def test_validar_empresa_seleccionada(driver):
    login = LoginPage(driver)
    login.load("https://asistenciadt.baplicada.cl/Login.aspx?FiscalizacionDT=Login")
    login.login("nicolas.perez@baplicada.cl", "FPt4ry3V")
    init = InitPage(driver)
    init.seleccionar_empresa_por_rut("76257834-4")
    init.fisc_init()
    assert init.confirmar_empresa("76257834-4")

