class ReoWF(BaseWF):
    def __init__(self, driver: WebDriver, window_handle: str = '') -> None:
        super().__init__(driver, window_handle)
        self._mainwf = MainWF(self._driver)

    def attempt_login_by_device_uid(
            self,
            uid: str,
            name: str,
            unames: List[str],
            passwds: List[str],
            rm_device: bool
    ) -> tuple:
        return self._mainwf.attempt_login_by_device_uid(uid, name, unames, passwds, rm_device)


Reo = ReoWF(driver.start())