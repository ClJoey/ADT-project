from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class FiscPage(BasePage):

    LIST_DT = (By.ID, "Vertical_NC_NB_GC0")

    REPORTE_NOMBRES_FORMALES = {
    "asistencia":     "Reporte de Asistencia",
    "jor_diaria":     "Reporte de Jornada Diaria",
    "domingos":       "Reporte de días domingo y/o días festivos",
    "modificaciones": "Reporte de modificaciones y/o alteraciones de turnos",
    "diario":         "Reporte Diario",
    "incidentes":     "Reporte de Incidentes Técnicos",
}

    REPORTES = {
        "asistencia": (By.ID, "Vertical_NC_NB_I0i0_T"),
        "jor_diaria": (By.ID, "Vertical_NC_NB_I0i1_T"),
        "domingos": (By.ID, "Vertical_NC_NB_I0i2_T"),
        "modificaciones": (By.ID, "Vertical_NC_NB_I0i3_T"),
        "diario": (By.ID, "Vertical_NC_NB_I0i4_T"),
        "incidentes": (By.ID, "Vertical_NC_NB_I0i5_T"),
    }

    REPORTE_BTN = (By.ID, "Vertical_mainMenu_Menu_DXI0_T")
    DOWN_EXCEL = (By.CSS_SELECTOR, "a[id*='dviDescargarEXCEL_View_HA']")
    DOWN_PDF   = (By.CSS_SELECTOR, "a[id*='dviDescargarPDF_View_HA']")
    BTN_CARGO = (By.CSS_SELECTOR, "a[id*='dviCargosBinding_ObjectsCreation_Menu_DXI0_T']")
    ALERTA_SIN_DATOS = (By.XPATH, "//div[contains(@class,'dx-toast-message') and contains(text(),'No hay trabajadores')]")
    TABLA_VACIA      = (By.XPATH, "//td[contains(@class,'dxdvEmptyData') and contains(.,'Sin datos para mostrar')]")

    # 1. Seleccionar reporte dinámico
    def seleccionar_reporte(self, nombre_reporte):
        locator = self.REPORTES[nombre_reporte]
        print(f"        [fisc_page] Buscando locator para: {nombre_reporte}")
        
        for intento in range(3):
            element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(locator)
            )
            print(f"        [fisc_page] Elemento encontrado, haciendo click... (intento {intento + 1})")
            self.driver.execute_script("arguments[0].click();", element)
            
            if self._hubo_cambio(timeout=5):
                print(f"        [fisc_page] Click registrado, esperando loader...")
                self.wait_loader()
                print(f"        [fisc_page] Loader terminado")
                return
            
            print(f"        [fisc_page] No hubo cambio, reintentando...")
            time.sleep(2)
        
        raise Exception(f"No se pudo cargar el reporte {nombre_reporte} tras 3 intentos")
    
    def click_reporte(self, nombre_reporte):
        locator = self.REPORTES[nombre_reporte]
        element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(locator)  # presence en vez de clickable
        )
        self.driver.execute_script("arguments[0].click();", element)
    
    def _hubo_cambio(self, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: any(
                    el.is_displayed()
                    for el in d.find_elements(By.CSS_SELECTOR, "table.dxlpLoadingPanel_XafTheme")
                )
            )
            return True
        except:
            return False

    # 2. Generar reporte
    def generar_reporte(self, timeout=15):
        """
        Hace click en 'Generar Reporte' y espera que el loader termine.
        Retorna (ok, sin_datos) donde:
          - ok       : False si el botón no apareció, True en cualquier otro caso.
          - sin_datos: True si se detectó el toast 'No hay trabajadores' ANTES
                       de que el loader terminara (ventana donde el toast todavía existe).
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(self.REPORTE_BTN)
            )
        except:
            print("Botón Generar Reporte no apareció")
            return False, False

        time.sleep(2)
        element = self.driver.find_element(*self.REPORTE_BTN)
        self.driver.execute_script("arguments[0].click();", element)

        # Detectar el toast ANTES de que el loader termine.
        # El toast aparece y desaparece mientras el loader está activo,
        # por lo que comprobarlo después de wait_loader() llega siempre tarde.
        sin_datos = self._detectar_toast_sin_datos(timeout=5)

        self.wait_loader()
        return True, sin_datos

    def _detectar_toast_sin_datos(self, timeout=5):
        """
        Detecta el toast 'No hay trabajadores' justo tras el click del botón,
        mientras el loader todavía está activo.
        Usa presence_of_element_located (no visibility) para capturarlo
        incluso durante el fade-in antes de que sea completamente opaco.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.ALERTA_SIN_DATOS)
            )
            return True
        except:
            return False

    


    # 3. Descargar PDF del reporte
    def descargar_pdf(self, download_path):
        boton = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(self.DOWN_PDF)
        )
        time.sleep(2)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", boton)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", boton)
        return self.wait_for_pdf(download_path)

    # 4. Descargar Excel
    def descargar_excel(self, download_path):
        boton = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(self.DOWN_EXCEL)
        )
        time.sleep(2)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", boton)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", boton)
        archivo = self.wait_for_file(download_path)
        return archivo


    # 4. Flujo completo
    def flujo_reporte(self, nombre_reporte, download_path):

        self.seleccionar_reporte(nombre_reporte)
        self.generar_reporte()
        time.sleep(3)
        archivo = self.descargar_excel(download_path)
        return archivo
    

    def seleccionar_cargo(self, cargo):
        self.wait_and_click(self.BTN_CARGO)
        self.wait_loader()
        time.sleep(2)
        # Entrar al iframe del popup de cargos
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[id*='PopupWindow'][id*='CIF']"))
        )
        self.driver.switch_to.frame(iframe)
        print("        [DEBUG] Dentro del iframe")

        # Click directo en el cargo
        cargo_locator = (By.XPATH, f"//td[contains(text(),'{cargo}')]")
        cargo_el = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(cargo_locator)
        )
        print(f"        [DEBUG] Cargo encontrado: {cargo_el.text}")
        self.driver.execute_script("arguments[0].click();", cargo_el)

        # Volver al contexto principal
        self.driver.switch_to.default_content()
        self.wait_loader()
        time.sleep(2)

    def reporte_tiene_datos(self, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.DOWN_EXCEL)
            )
            return True
        except:
            return False
    
    def hay_sin_datos(self, timeout=5):
        """
        Fallback: comprueba si el toast sigue en el DOM tras el wait_loader.
        Usa presence (no visibility) para detectarlo incluso durante el fade-out.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.ALERTA_SIN_DATOS)
            )
            return True
        except:
            return False

    def hay_tabla_vacia(self, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.TABLA_VACIA)
            )
            return True
        except:
            return False

    def pantalla_en_blanco(self, timeout=3):
        """
        Detecta si el formulario del reporte no cargó (pantalla en blanco).
        Retorna True si el botón 'Generar Reporte' no aparece en el timeout dado,
        lo que indica que el contenido del formulario no se renderizó.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.REPORTE_BTN)
            )
            return False  # Botón presente → página cargó correctamente
        except:
            return True   # No encontró el botón → pantalla en blanco