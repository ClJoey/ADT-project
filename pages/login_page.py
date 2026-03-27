from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class LoginPage(BasePage):

    USERNAME = (By.CSS_SELECTOR, "input[id*='dviNombreUsuario_Edit_I']")
    PASSWORD = (By.CSS_SELECTOR, "input[id*='dviPassword_Edit_I']")
    LOGIN_BTN = (By.ID, "Logon_PopupActions_Menu_DXI0_T")



    def load(self, url):
        self.driver.get(url)

    def login(self, user, password):
        self.wait_and_type(self.USERNAME, user)
        self.wait_and_click(self.LOGIN_BTN)
        self.wait_and_type(self.PASSWORD, password)
        self.wait_and_click(self.LOGIN_BTN)
    
    def username(self, user):
        self.wait_and_type(self.USERNAME, user)
        self.wait_and_click(self.LOGIN_BTN)

    def is_error_user_displayed(self):
        return self.driver.find_element(By.XPATH, "//div[contains(@class, 'dx-toast-message') and contains(text(), 'El usuario indicado no es valido')]").is_displayed()
    
    def is_error_user_password_displayed(self):
        return self.driver.find_element(By.XPATH, "//div[contains(@class, 'dx-toast-message') and contains(text(), 'Contraseña invalida')]").is_displayed()