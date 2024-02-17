from selenium.webdriver.remote.webdriver import WebDriver
from utils.common import common
from utils.read_config import config


class BaseWindow:
    def __init__(self, driver: WebDriver, window_handle: str = '') -> None:
        self._driver = driver


class MainWindow(BaseWindow):
    _data = config.get_page_data(source='selectors')


class BaseWF(BaseWindow):
    def __init__(self, driver: WebDriver, window_handle: str = '') -> None:
        super().__init__(driver, window_handle)
        self._main_window = MainWindow(self._driver)


class ReoWF(BaseWF):
    def __init__(self, driver: WebDriver, window_handle: str = '') -> None:
        super().__init__(driver, window_handle)
        self._mainwindow = MainWindow(self._driver)
