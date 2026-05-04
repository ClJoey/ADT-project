import pytest
import socket
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
from dotenv import load_dotenv

load_dotenv()

socket.setdefaulttimeout(300)


def _crear_driver():
    download_path = os.path.abspath("downloads")
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    options = webdriver.ChromeOptions()

    if os.getenv("CI"):
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "download.extensions_to_open": "applications/pdf",
        "safebrowsing.disable_download_protection": True,
    }
    options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=options)
    d.set_page_load_timeout(300)
    d.set_script_timeout(120)

    if not os.getenv("CI"):
        d.maximize_window()

    return d


@pytest.fixture(scope="session", autouse=True)
def limpiar_resumen_previo():
    summary_path = os.path.join("reports", "summary_data.json")
    if os.path.exists(summary_path):
        os.remove(summary_path)


@pytest.fixture(scope="function")
def driver():
    d = _crear_driver()
    yield d
    d.quit()


@pytest.fixture(scope="function")
def driver_factory():
    """Fixture que provee una fábrica de drivers. Cierra todos al finalizar el test."""
    drivers = []

    def _crear():
        d = _crear_driver()
        drivers.append(d)
        return d

    yield _crear

    for d in drivers:
        try:
            d.quit()
        except Exception:
            pass


@pytest.fixture(scope="function")
def logged_in_driver(driver):
    from pages.login_page import LoginPage, URL
    from data.credenciales import USER
    login = LoginPage(driver)
    login.load(URL)
    login.login(USER[0]["usuario"], USER[0]["password"])
    return driver
