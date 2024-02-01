from selenium.webdriver.remote.webdriver import WebDriver
from page.base_window import BaseWindow
from page.main_window import MainWindow
from common import common


class BaseWF(BaseWindow):
    """基本工作流"""

    def __init__(self, driver: WebDriver, window_handle: str = '') -> None:
        super().__init__(driver, window_handle)
        self._main_window = MainWindow(self._driver)
        # self._logger = Logger()

    def awake_device_by_need(self, name: str = None) -> None:
        """
            在需要的时候唤醒设备
            参数:
                - name: 待唤醒的设备, 默认唤醒全部设备
        """
        try:
            # 如果未指定设备名，尝试唤醒所有设备
            if not name:
                self._main_window.attempt_awake_devices()
            else:
                # 否则，尝试唤醒指定设备
                self._main_window.attempt_awake_devices([name])
        except BaseException as err:
            raise ValueError(
                f"{common.I18n['_error_msg']['_attempt_awake_device_fail']}: {err}"
            )
