import pytest
from pages.init_page import InitPage
from utils.screenshots import guardar_captura
from utils.report_html import generar_html

_resultados = []

@pytest.fixture(scope="module", autouse=True)
def reporte_init():
    yield
    if _resultados:
        generar_html({
            "empresa": "01 Tests de Seleccion de Empresa",
            "rut": "N/A",
            "reportes": _resultados
        })

def test_select_empleador(logged_in_driver):
    init = InitPage(logged_in_driver)
    init.seleccionar_empresa_por_rut("76257834-4")
    init.fisc_init()
    captura = guardar_captura(logged_in_driver, "init", "test_select_empleador")
    _resultados.append({
        "nombre": "Selección de empleador por RUT",
        "estado": "OK",
        "errores": [],
        "captura": captura
    })

def test_validar_autocompletado(logged_in_driver):
    init = InitPage(logged_in_driver)
    init.seleccionar_empresa_por_rut("76257834-4")
    ok = init.validar_autocompletado("76257834-4")
    captura = guardar_captura(logged_in_driver, "init", "test_validar_autocompletado")
    _resultados.append({
        "nombre": "Validación de autocompletado de empresa",
        "estado": "OK" if ok else "FAIL",
        "errores": [] if ok else ["El nombre o RUT no se autocompletó correctamente"],
        "captura": captura
    })
    assert ok

def test_validar_cambio_empresa(logged_in_driver):
    init = InitPage(logged_in_driver)
    init.seleccionar_empresa_por_rut("76257834-4")
    init.seleccionar_empresa_por_rut("96579730-0")
    ok = init.validar_autocompletado("96579730-0")
    captura = guardar_captura(logged_in_driver, "init", "test_validar_cambio_empresa")
    _resultados.append({
        "nombre": "Cambio de empresa seleccionada",
        "estado": "OK" if ok else "FAIL",
        "errores": [] if ok else ["El cambio de empresa no se reflejó correctamente"],
        "captura": captura
    })
    assert ok

def test_validar_empresa_seleccionada(logged_in_driver):
    init = InitPage(logged_in_driver)
    init.seleccionar_empresa_por_rut("76257834-4")
    init.fisc_init()
    ok = init.confirmar_empresa("76257834-4")
    captura = guardar_captura(logged_in_driver, "init", "test_validar_empresa_seleccionada")
    _resultados.append({
        "nombre": "Confirmación de empresa seleccionada",
        "estado": "OK" if ok else "FAIL",
        "errores": [] if ok else ["El RUT de la empresa no aparece confirmado"],
        "captura": captura
    })
    assert ok
