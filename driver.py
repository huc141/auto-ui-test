from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from read_config import config

"""
提供了连接应用、启动应用、切换页面窗口等能力，当一个流程涉及到多个页面时，需要在不同窗口中跳转，需要用到窗口跳转的能力。
"""


class Driver(object):
    """
        定义一个 Driver 类，用于启动和关闭谷歌浏览器驱动
    """
    # 初始化 Driver 对象。它接受两个参数：version 是 Chrome 驱动的版本，path 是 Chrome 可执行文件的路径。
    def __init__(self, version: str, path: str) -> None:
        # 将传递进来的版本号和路径保存在对象的属性中。
        self._version = version
        self._path = path
        self._driver = None  # 初始化一个属性 _driver 为 None，用于保存 Chrome WebDriver 的实例。

    # 类的方法，用于启动 Chrome WebDriver
    def start(self):
        # 如果 _driver 已经存在（即不为 None），直接返回现有的实例，避免重复启动。
        if self._driver:
            return self._driver
        # 使用 ChromeDriverManager 管理器来安装 Chrome 驱动，并创建一个 ChromeService 对象，用于启动 Chrome WebDriver
        # ChromeDriverManager是一个用于管理 ChromeDriver 的 Python 库。version=self._version 是在安装 ChromeDriver 时指定的版本。
        driver_manager = ChromeDriverManager(version=self._version)

        # ChromeDriverManager 的 install() 方法会下载并返回 ChromeDriver 的实际可执行文件的路径。
        driver_path = driver_manager.install()

        # 创建 Chrome 驱动器服务.ChromeService 类，它是 ChromeDriver 的服务类。executable_path 参数是 ChromeDriver 的可执行文件路径
        wd_service = ChromeService(executable_path=driver_path)

        # wd_service = ChromeService(executable_path=ChromeDriverManager(version=self._version).install())

        wd_options = webdriver.ChromeOptions()  # 创建 Chrome WebDriver 的参数配置对象，。
        wd_options.binary_location = self._path  # 设置谷歌浏览器可执行文件的路径(在这里其实是reolink客户端的.exe执行路径)
        wd_options.add_argument('--user-data-dir=' + config.app_data_dir)  # 配置启动参数，指定用户数据目录。
        wd_options.add_argument('--disable-extensions')  # 禁用Chrome浏览器的扩展插件功能，避免插件对自动化测试造成干扰。
        wd_options.add_argument('--log-level=3')  # 设置浏览器的日志级别为 error，只输出错误级别及以上的日志
        wd_options.add_argument('--disable-logging')  # 禁用日志生成

        self._driver = webdriver.Chrome(service=wd_service, options=wd_options)
        return self._driver

    """    
    如果 self._driver 为真（即非空，表示浏览器驱动对象存在），则执行 self._driver.quit()，关闭浏览器。
    如果 self._driver 为假（即空，表示浏览器驱动对象不存在），则不执行后续的 self._driver.quit()，因为 Python 的短路逻辑不会计算后续的表达式。
    这行代码的目的是确保在调用 quit 方法之前先检查浏览器驱动对象是否存在，以防止在空对象上调用方法而引发异常。
    """
    def quit(self):
        # 调用WebDriver对象的 quit 方法。
        self._driver and self._driver.quit()  # 在 Python 中，and 是逻辑与运算符。对于 A and B，如果 A 为真，返回 B；如果 A 为假，返回 A。这是一个短路逻辑，即如果 A 为假，就不再计算 B。


driver = Driver(version=config.chromium_version, path=config.executable_path)
