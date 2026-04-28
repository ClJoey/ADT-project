import pytest
import json
import os
import time
from data.empresas import EMPRESAS
from data.credenciales import USER
from pages.login_page import LoginPage
from pages.init_page import InitPage
from pages.fisc_page import FiscPage
from utils.screenshots import guardar_captura
from utils.logger import get_logger

logger = get_logger(__name__)

URL = "https://asistenciadt.baplicada.cl/Login.aspx?FiscalizacionDT=Login"
RESULTS_FILE = os.path.join("reports", "disponibilidad_results.json")


def _guardar_resultado(resultado):
    os.makedirs("reports", exist_ok=True)
    resultados = []
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            try:
                resultados = json.load(f)
            except Exception:
                resultados = []
    resultados.append(resultado)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)


@pytest.mark.parametrize("empresa", EMPRESAS, ids=[e["nombre"] for e in EMPRESAS])
def test_disponibilidad(driver, empresa):
    resultado = {"empresa": empresa["nombre"], "estado": "OK", "error": None, "captura": None}

    login = LoginPage(driver)
    init = InitPage(driver)

    MAX_INTENTOS = 3
    for intento in range(MAX_INTENTOS):
        try:
            login.load(URL)
            login.login(USER[0]["usuario"], USER[0]["password"])
            init.seleccionar_empresa_por_rut(empresa["rut"])
            init.fisc_init()
            init.confirm()
            time.sleep(3)

            fisc = FiscPage(driver)
            if not fisc.esta_en_fisc_page():
                raise Exception("El menú de reportes no fue visible tras el ingreso")

            captura = guardar_captura(driver, empresa["nombre"], "disponibilidad_ok")
            resultado["captura"] = captura
            logger.info(f"PASS: {empresa['nombre']}")
            break

        except Exception as e:
            logger.warning(f"{empresa['nombre']} (intento {intento + 1}/{MAX_INTENTOS}): {str(e)[:200]}")
            if intento < MAX_INTENTOS - 1:
                logger.info("Reintentando en 20 segundos...")
                time.sleep(20)
            else:
                resultado["estado"] = "FAIL"
                resultado["error"] = str(e)[:300]
                try:
                    resultado["captura"] = guardar_captura(driver, empresa["nombre"], "disponibilidad_error")
                except Exception:
                    logger.warning(f"No se pudo tomar captura de error para {empresa['nombre']} (driver caído)")
                logger.error(f"FAIL: {empresa['nombre']}")

    _guardar_resultado(resultado)

    if resultado["estado"] == "FAIL":
        pytest.fail(f"{empresa['nombre']} no pudo acceder a fisc_page: {resultado['error']}")
