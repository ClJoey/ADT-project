import datetime
import pytest
from conftest import driver
from data.empresas import EMPRESAS
from data.credenciales import USER
from pages.login_page import LoginPage
from pages.init_page import InitPage
from pages.fisc_page import FiscPage
from utils.helpers import limpiar_descargas
from utils.auditoria import auditar_excel_final
import time


@pytest.mark.parametrize("empresa", EMPRESAS, ids=[e["nombre"] for e in EMPRESAS])
def test_reporte(driver, empresa):

    download_path = "C:\\Users\\PrDes\\Desktop\\ADT_TEST\\downloads"
    limpiar_descargas(download_path)

    # LOGIN
    login = LoginPage(driver)
    login.load("https://asistenciadt.baplicada.cl/Login.aspx?FiscalizacionDT=Login")
    login.login(USER[0]["usuario"], USER[0]["password"])

    # EMPRESA
    init = InitPage(driver)
    init.seleccionar_empresa_por_rut(empresa["rut"])
    init.fisc_init()
    init.confirm()
    

    fisc = FiscPage(driver)

    errores_empresa = []

    for reporte in empresa["reportes"]:
        print(f"\n>>> Iniciando reporte: {reporte}")
        
        fisc.seleccionar_reporte(reporte)
        print(f"    ✓ Reporte seleccionado: {reporte}")
        print(f"    → URL actual: {driver.current_url}")
        print(f"    → Título página: {driver.title}")
        print(f"    ✓ Reporte seleccionado: {reporte}")

        if empresa["filtro_cargo"] and reporte not in ["diario", "incidentes"]:
            fisc.seleccionar_cargo(empresa["Cargo"])
            print(f"    ✓ Cargo filtrado: {empresa['Cargo']}")

        fisc.generar_reporte()
        time.sleep(3)
        if not fisc.reporte_tiene_datos():
            print(f"    ✗ Reporte {reporte} no cargó (sin botón descarga)")
            errores_empresa.append(f"{reporte}: no cargó")
            continue

        print(f"    ✓ Reporte generado y con datos: {reporte}")

        if reporte == "jor_diaria":
            archivo = fisc.descargar_excel(download_path)

            if not archivo:
                print(f"    ✗ No se descargó archivo")
                errores_empresa.append(f"{reporte}: No se descargó archivo")
            else:
                print(f"    ✓ Archivo descargado: {archivo}")
                ok, errores = auditar_excel_final(archivo)
                print(f"    {'✓ Auditoría OK' if ok else f'✗ Auditoría FALLÓ: {errores}'}")

                if not ok:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    driver.save_screenshot(f"{download_path}\\error_{timestamp}.png")
                    with open(f"{download_path}\\errores_{timestamp}.txt", "w", encoding="utf-8") as f:
                        for e in errores:
                            f.write(e + "\n")
                    errores_empresa.append(f"{reporte}: {errores}")

            continue  # ← sin reset, directo al siguiente reporte

    # ASSERT FINAL POR EMPRESA
    assert not errores_empresa, f"{empresa['nombre']} | {errores_empresa}"