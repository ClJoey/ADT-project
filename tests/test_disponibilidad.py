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

_ERRORES_RED = [
    "ERR_CONNECTION_REFUSED", "ERR_CONNECTION_TIMED_OUT", "ERR_CONNECTION_RESET",
    "ERR_NAME_NOT_RESOLVED", "ERR_INTERNET_DISCONNECTED", "ERR_TIMED_OUT",
    " 500 ", " 502 ", " 503 ", " 504 ",
]

def _detectar_error_red(driver):
    """Retorna el primer error crítico del browser log, o None si no hay."""
    try:
        logs = driver.get_log("browser")
        for entry in logs:
            if entry.get("level") == "SEVERE":
                msg = entry["message"]
                if any(err in msg for err in _ERRORES_RED):
                    return msg[:200]
    except Exception:
        pass
    return None

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
def test_disponibilidad(driver_factory, empresa):
    resultado = {"empresa": empresa["nombre"], "estado": "OK", "error": None, "captura": None}

    driver = driver_factory()

    MAX_INTENTOS = 3
    for intento in range(MAX_INTENTOS):
        login = LoginPage(driver)
        init = InitPage(driver)

        try:
            logger.debug(f"[Test] Cargando URL de login...")
            login.load(URL)
            error_red = _detectar_error_red(driver)
            if error_red:
                raise Exception(f"Error de red al cargar el portal: {error_red}")
            logger.debug(f"[Test] Haciendo login...")
            login.login(USER[0]["usuario"], USER[0]["password"])
            logger.debug(f"[Test] Login OK. Seleccionando empresa: {empresa['nombre']} (RUT: {empresa['rut']})")
            init.seleccionar_empresa_por_rut(empresa["rut"])
            logger.debug(f"[Test] Empresa seleccionada. Iniciando fiscalización...")
            init.fisc_init()
            logger.debug(f"[Test] fisc_init OK. Confirmando...")
            init.confirm()
            logger.debug(f"[Test] confirm OK. Esperando 3s para que cargue fisc_page...")
            time.sleep(3)

            logger.debug(f"[Test] Seleccionando reporte 'asistencia'...")
            fisc = FiscPage(driver)
            fisc.seleccionar_reporte("asistencia")
            logger.debug(f"[Test] Reporte seleccionado. Verificando empresa en panel: '{empresa['nom_informe']}'")
            if not fisc.verificar_empresa(empresa["nom_informe"], timeout=30):
                raise Exception("El formulario cargó pero no se verificó el nombre de la empresa en el panel")

            captura = guardar_captura(driver, empresa["nombre"], "disponibilidad_ok")
            resultado["captura"] = captura
            logger.info(f"PASS: {empresa['nombre']}")
            break

        except Exception as e:
            msg = str(e)
            if "GetHandleVerifier" in msg or "invalid session id" in msg.lower():
                msg = f"[Chrome] Sesión del navegador invalidada — el servidor no respondió correctamente.\nReporte de ChromeDriver: {msg[:300]}"
            elif "HTTPConnectionPool" in msg or "Read timed out" in msg:
                msg = f"[Selenium] Tiempo de espera agotado — el servidor tardó más de 300s en responder.\nDetalle: {msg[:200]}"
            logger.warning(f"{empresa['nombre']} (intento {intento + 1}/{MAX_INTENTOS}): {msg[:250]}")

            if intento < MAX_INTENTOS - 1:
                logger.info("Cerrando navegador y abriendo uno nuevo para reintentar...")
                try:
                    driver.quit()
                except Exception:
                    pass
                time.sleep(5)
                driver = driver_factory()
            else:
                resultado["estado"] = "FAIL"
                resultado["error"] = msg[:400]
                try:
                    resultado["captura"] = guardar_captura(driver, empresa["nombre"], "disponibilidad_error")
                except Exception:
                    logger.warning(f"No se pudo tomar captura de error para {empresa['nombre']} (driver caído)")
                logger.error(f"FAIL: {empresa['nombre']}")

    _guardar_resultado(resultado)

    if resultado["estado"] == "FAIL":
        pytest.fail(f"{empresa['nombre']} no pudo acceder a fisc_page: {resultado['error']}")
