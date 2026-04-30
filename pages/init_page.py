from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger
import time

logger = get_logger(__name__)

class InitPage(BasePage):

    FISSC_BTN = (By.ID, "Logon_PopupActions_Menu_DXI0_T")
    CANCEL_BTN= (By.ID, "Logon_PopupActions_Menu_DXI1_T")
    TABLA = (By.CSS_SELECTOR, "table[id*='dviFiscalizacionEmpresaDTs']")
    INPUT_NOMBRE_EMP = (By.CSS_SELECTOR, "input[name*='dviEmpresaAFiscalizarNombre_Edit_dropdown$DD']")
    INPUT_RUT_EMP = (By.CSS_SELECTOR, "input[id*='dviEmpresaAFiscalizarRUT_Edit_dropdown_DD_I']")
    CONFIRM_BTN =(By.ID, "Logon_PopupActions_Menu_DXI0_T")

    def seleccionar_empresa_por_rut(self, rut):
        logger.debug(f"[InitPage] Esperando que la tabla de empleadores sea visible...")
        self.wait_for_visible(self.TABLA)
        logger.debug(f"[InitPage] Tabla visible. Buscando fila con RUT: {rut}")

        opcion = (By.XPATH, f"//td[contains(text(), '{rut}')]")

        for intento in range(3):
            logger.debug(f"[InitPage] Intento {intento + 1}/3 — esperando 3s antes de hacer click en la fila...")
            time.sleep(3)

            logger.debug(f"[InitPage] Haciendo click en la fila de la empresa (RUT: {rut})...")
            self.wait_and_click(opcion)
            logger.debug(f"[InitPage] Click realizado. Esperando que el loader desaparezca...")
            self.wait_loader()
            logger.debug(f"[InitPage] Loader listo. Verificando autocompletado de inputs...")

            try:
                nombre_val = self.driver.find_element(*self.INPUT_NOMBRE_EMP).get_attribute("value")
                rut_val    = self.driver.find_element(*self.INPUT_RUT_EMP).get_attribute("value")
                logger.debug(f"[InitPage] Input NOMBRE='{nombre_val}' | Input RUT='{rut_val}'")
                if nombre_val and rut_val:
                    logger.debug(f"[InitPage] Autocompletado OK (intento {intento + 1}): {nombre_val}")
                    return
                else:
                    logger.warning(f"[InitPage] Inputs vacíos tras click (intento {intento + 1}/3) — NOMBRE='{nombre_val}' RUT='{rut_val}'")
            except Exception as ex:
                logger.warning(f"[InitPage] No se pudo leer los inputs (intento {intento + 1}/3): {ex}")

        raise Exception(f"La empresa con RUT {rut} no autocompletó los inputs tras 3 intentos")

    def fisc_init(self):
        logger.debug("[InitPage] Haciendo click en botón 'Fiscalizar'...")
        self.wait_and_click(self.FISSC_BTN)
        logger.debug("[InitPage] Click en Fiscalizar realizado. Esperando loader...")
        self.wait_loader()
        logger.debug("[InitPage] Loader listo tras Fiscalizar.")
    
    def confirmar_empresa(self, rut):
        element = (By.XPATH, f"//span[contains(text(), '{rut}')]")
        try:
            self.wait_for_visible(element)
            return True
        except:
            return False

    def confirm(self):
        logger.debug("[InitPage] Haciendo click en botón 'Confirmar'...")
        self.wait_and_click(self.CONFIRM_BTN)
        logger.debug("[InitPage] Click en Confirmar realizado. Esperando loader...")
        self.wait_loader()
        logger.debug("[InitPage] Loader listo tras Confirmar — debería estar en fisc_page.")
    
    def validar_autocompletado(self, rut):
        self.seleccionar_empresa_por_rut(rut)

        nombre_valor = self.wait_for_visible(self.INPUT_NOMBRE_EMP).get_attribute("value")
        rut_valor = self.wait_for_visible(self.INPUT_RUT_EMP).get_attribute("value")

        return nombre_valor == rut_valor