from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage

URL = "https://asistenciadt.baplicada.cl/Login.aspx?FiscalizacionDT=Login"

TOAST_USUARIO_INVALIDO = (By.XPATH, "//div[contains(@class,'dx-toast-message') and contains(text(),'El usuario indicado no es valido')]")
TOAST_PASSWORD_INVALIDA = (By.XPATH, "//div[contains(@class,'dx-toast-message') and (contains(text(),'Usuario o contraseña') or contains(text(),'Contraseña invalida') or contains(text(),'contraseña invalida'))]")


class LoginPage(BasePage):

    USERNAME = (By.CSS_SELECTOR, "input[id*='dviNombreUsuario_Edit_I']")
    PASSWORD = (By.CSS_SELECTOR, "input[id*='dviPassword_Edit_I']")
    LOGIN_BTN = (By.ID, "Logon_PopupActions_Menu_DXI0_T")

    def load(self, url=URL):
        self.driver.get(url)

    def login(self, user, password):
        self.wait_and_type(self.USERNAME, user)
        self.wait_and_click(self.LOGIN_BTN)
        self.wait_and_type(self.PASSWORD, password)
        self.wait_and_click(self.LOGIN_BTN)

    def username(self, user):
        self.wait_and_type(self.USERNAME, user)
        self.wait_and_click(self.LOGIN_BTN)

    def is_login_exitoso(self):
        try:
            self.wait_for_visible((By.CSS_SELECTOR, "table.LogonContent.LogonContentWidth"))
            return True
        except:
            return False

    def is_error_user_displayed(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(TOAST_USUARIO_INVALIDO)
            )
            return True
        except:
            return False

    def is_error_user_password_displayed(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(TOAST_PASSWORD_INVALIDA)
            )
            return True
        except:
            return False

    def is_any_credential_error_displayed(self, timeout=8):
        """Detecta cualquier toast de credencial inválida (usuario o contraseña) en una sola espera."""
        locator = (By.XPATH,
            "//div[contains(@class,'dx-toast-message') and ("
            "contains(text(),'Usuario o contraseña') or "
            "contains(text(),'Contraseña invalida') or "
            "contains(text(),'contraseña invalida') or "
            "contains(text(),'El usuario indicado no es valido'))]"
        )
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except:
            return False
