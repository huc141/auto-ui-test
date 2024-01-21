from typing import List
from page_object.main import MainWF
from selenium.webdriver.remote.webdriver import WebDriver
from driver import driver
from page_object.base import BaseWF


class ReoWF(BaseWF):
    """
        开放给Case调用的公共方法
    """

    def __init__(self, driver: WebDriver, window_handle: str = '') -> None:
        super().__init__(driver, window_handle)
        self._mainwf = MainWF(self._driver)  # self._driver 是 BaseWindow 类的一个实例变量，它在该类的构造函数 __init__ 中被初始化。

    def attempt_login_by_device_uid(
            self,
            uid: str,
            name: str,
            unames: List[str],
            passwds: List[str],
            rm_device: bool
    ) -> tuple:
        """
            登录工作流(通过设备uid添加, 主要用于电池机)

            参数:
                - uid: 待登录的设备`uid`
                - name: 待登录设备名称, 用于登录前移除设备
                - unames: 尝试登录的用户名列表
                - passwds: 尝试登录的密码列表
                - rm_device: 可选, 执行工作流前是否先自动删除待测试设备

            注: 会循环提供的 `unames` 和 `passwds`, 直到登录成功

            返回值:
                - tuple: 正确执行操作返回`True`, 错误信息为空; 否则, 返回`False`与错误信息
        """
        return self._mainwf.attempt_login_by_device_uid(uid, name, unames, passwds, rm_device)


web_driver = driver.start()  # driver.start() 返回一个 WebDriver 对象。
Reo = ReoWF(web_driver)
