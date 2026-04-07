import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

@pytest.fixture(scope="function")
def driver():

    download_path = os.path.abspath("downloads")

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    options = webdriver.ChromeOptions()

    # 👇 DETECTAR SI ESTAMOS EN CI
    if os.getenv("CI"):
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }

    options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # En CI no usar maximize
    if not os.getenv("CI"):
        driver.maximize_window()

    yield driver

    driver.quit()