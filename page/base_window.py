import os
import time
from datetime import date
from random import uniform
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Any, Literal, Dict, Callable
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
import pyautogui as pg
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from common import common
from utils.utils import util

"""基础窗口，所有窗口都继承自该窗口，提供了基础的页面操作能力"""


class BaseWindow:
    _timeout = common.ENV['element_timeout']

    _root_sel = "#remote-config-app > div.config-context-wrap > div"

    '''Record device status'''
    _device_statuses = {
        'ACTIVE': set(),
        'INACTIVE': set(),
        'WRONG_PASS': set(),
        'FAIL': set(),
        'OTHER': set()
    }

    def __init__(self, driver: WebDriver, window_handle: str = '') -> None:

        self._driver = driver

        pg.PAUSE = common.ENV['pyautogui.PAUSE'] if 'pyautogui.PAUSE' in common.ENV else 0.1
        pg.FAILSAFE = common.ENV['pyautogui.FAILSAFE'] if 'pyautogui.FAILSAFE' in common.ENV else 0.1

        if window_handle != '':
            self._driver.switch_to.window(window_handle)

        # self._logger = logger

    def get_title(self) -> str:

        return self._driver.title

    def wait_until(
            self,
            fn: Callable,
            element: WebElement,
            timeout: int,
            period: float,
            wait_attr: str = None,
            allow_null: bool = False
    ) -> WebElement:

        end_time = time.monotonic() + timeout
        err_msg = None
        while True:
            try:
                value = fn(element or self._driver)
                if value:
                    if wait_attr:
                        if wait_attr == 'text':
                            if value.text or allow_null:
                                return value
                        elif wait_attr == 'visible' or allow_null:
                            if value.is_displayed():
                                return value
                        else:
                            if value.get_attribute(wait_attr) or allow_null:
                                return value
                        raise ValueError(f"{wait_attr} not available")

                    return value
            except BaseException as err:
                err_msg = err
            time.sleep(period)
            if time.monotonic() > end_time:
                err_msg = f"{common.I18n['_error_msg']['_element_timeout']}"
                break
        raise TimeoutException(
            f"{common.I18n['_error_msg']['_element_not_found']}: {err_msg}"
        )

    def find_element_by_selector(
            self,
            selector: str,
            by: Literal = By.XPATH,
            element: WebElement = None,
            timeout: int = _timeout,
            period: float = 0.25,
            pause: float = 0,
            wait_attr: str = None,
            allow_null: bool = False
    ) -> WebElement:
        """
            查找符合选择器条件

            参数:
                - selector: 选择器路径
                - by: 选择器类型, 可选 By.XPATH | By.CSS_SELECTOR, 默认 By.XPATH
                - element: 相对路径的根元素, 默认 None
                - timeout: 超时时间, 默认5s
                - period: 重试间隙, 默认为0.25s
                - pause: 执行完操作后的等待时间, 默认为0
                - wait_attr: 需要等待显示的值 text|name|class|visible|title 等

            返回值:
                - WebElement: 查找到的元素
        """
        ret = self.wait_until(
            fn=lambda x: x.find_element(by, selector),
            element=element,
            timeout=timeout,
            period=period,
            wait_attr=wait_attr,
            allow_null=allow_null
        )
        if pause > 0:
            time.sleep(pause)
        return ret

    def find_elements_by_selector(
            self,
            selector: str,
            by: Literal = By.XPATH,
            element: WebElement = None,
            timeout: int = _timeout,
            period: float = 0.25
    ) -> WebElement:
        """
            查找符合选择器条件元素集合

            参数:
                - selector: 选择器路径
                - by: 选择器类型, 可选 By.XPATH | By.CSS_SELECTOR, 默认 By.XPATH
                - element: 相对路径的根元素, 默认 None
                - timeout: 超时时间, 默认5s
                - period: 重试间隙, 默认为0.25s

            返回值:
                - List[WebElement]: 查找到的元素集合
        """

        return self.wait_until(
            fn=lambda x: x.find_elements(by, selector),
            element=element,
            timeout=timeout,
            period=period
        )

    def click_on_element(
            self,
            selector: str = '.',
            by: Literal = By.XPATH,
            pause: float = 0.5,
            element: WebElement = None,
            timeout: int = _timeout,
            period: float = 0.25,
            idtext: str = None
    ) -> None:
        """
            在指定元素上执行鼠标左键单击操作

            参数:
                - selector: 选择器路径
                - by: 选择器类型, 可选 By.XPATH | By.CSS_SELECTOR, 默认 By.XPATH
                - pause: 执行完操作后的暂停时间, 单位为s
                - element: 相对路径的根元素, 默认 None
                - timeout: 超时时间, 默认5s
                - period: 重试间隙, 默认为0.25s
                - idtext: 验证文本, 与待点击的元素的文本一致则点击外部元素, 退出点击
        """
        ele_to_click = self.find_element_by_selector(
            selector=selector,
            by=by,
            element=element,
            timeout=timeout,
            period=period,
            wait_attr='text',
            allow_null=True
        )

        if ele_to_click.text == idtext or ele_to_click.get_attribute('title') == idtext:
            self.click_on_element(selector=self._root_sel, by=By.CSS_SELECTOR)
            return None

        WebDriverWait(
            driver=self._driver,
            timeout=timeout,
            poll_frequency=period
        ).until(
            method=EC.element_to_be_clickable(ele_to_click),
            message=f"{selector} {common.I18n['_error_msg']['_element_not_interactable']}"
        )
        ele_to_click.click()
        # self._driver.execute_script('arguments[0].click();', ele_to_click)
        time.sleep(pause)

    def input_text(
            self,
            selector: str,
            text: str,
            by: Literal = By.XPATH,
            element: WebElement = None
    ) -> None:
        """
            输入文本

            参数:
                - selector: 选择器
                - text: 待输入文本
                - by: 选择器类型, 可选 By.XPATH | By.CSS_SELECTOR, 默认 By.XPATH
                - element: 相对路径的根元素, 默认 None
        """
        target = self.find_element_by_selector(
            selector=selector,
            by=by,
            element=element
        )
        target.send_keys(Keys.CONTROL, 'a')
        target.send_keys(text)

    def get_element_text(
            self,
            selector: str,
            by: Literal = By.XPATH,
            element: WebElement = None,
            allow_null: bool = False,
            timeout: int = _timeout
    ) -> str:
        """
            获取元素文本

            参数:
                - selector: 选择器
                - by: 选择器类型, 可选 By.XPATH | By.CSS_SELECTOR, 默认 By.XPATH
                - element: 相对路径的根元素, 默认 None
                - allow_null: 是否允许为空值
                - timeout: 超时时间
        """
        return self.find_element_by_selector(
            selector=selector,
            by=by,
            element=element,
            wait_attr='text',
            timeout=timeout,
            allow_null=allow_null
        ).text

    def right_click(
            self,
            area: WebElement,
            pause: float = 0.5
    ) -> None:
        """
            在指定区域执行右键单击

            参数:
                - area: 执行右键单击的区域
                - pause: 执行完操作等待时间, 默认为0.5s
        """
        ac = ActionChains(self._driver)
        ac.move_to_element(area).perform()
        ac.context_click(area).perform()
        time.sleep(pause)

    def select_context_item(
            self,
            which: int,
            pause: float = 0.5
    ) -> None:
        """
            选择指定右键菜单项

            参数:
                - which: 待选择的菜单项, 从上到下, 默认为1, 选中第一项
                - pause: 执行完操作等待时间, 默认为0.5s
        """
        pg.typewrite(['down' for _ in range(which)])
        pg.typewrite(
            ['enter' if common.ENV['platform'] == 'Win32' else 'return']
        )
        time.sleep(pause)

    def click_on_image(
            self,
            img_name: str,
            pause: int = 0.5
    ) -> None:
        """
            点击图片

            参数:
                - img_name: 图片名称(不带后缀, 仅支持png图片), 图片需存放在 `test/assets/images` 下
                - pause: 执行完操作的等待时间
        """
        target = pg.locateOnScreen(os.path.join(
            common.ProjectRoot,
            'test',
            'assets',
            'images',
            f"{img_name}.png"
        ))
        if not target:
            raise ValueError(
                common.I18n['_error_msg']['_get_click_loc_fail']
            )
        pg.click(pg.center(target))

        if pause:
            time.sleep(pause)

    def scroll(
            self,
            steps: int,
            ele: WebElement = None,
            interval: float = 0.5,
            cb: Callable = None
    ) -> None:
        """
            鼠标滚动

            参数:
                - steps: 滚动单位, 表示滚轮滚动一次的距离, 小于0表示向上(左)滚动, 大于0表示向下(右)滚动
                - ele: 页面元素, 表示要执行滚动的元素, 不指定则直接执行滚动操作
                - interval: 单位滚动间隔, 如不指定该参数, 则直接滚动指定单位
                - cb: 回调函数, 若指定该参数, 执行完一次单位滚动, 会触发该回调函数
                    否则执行 time.sleep(interval)
                    - 回调函数应指定返回值为布尔值, 如果返回True, 则表示找到目标, 停止滚动
        """
        if cb and cb():
            return

        success = False
        unit = 100
        ac = ActionChains(self._driver)

        dist = abs(steps * unit)
        if interval:
            pace = unit if steps >= 0 else -unit
            while dist > 0:
                ac.move_to_element(ele).scroll_from_origin(
                    scroll_origin=ScrollOrigin.from_element(ele),
                    delta_x=0,
                    delta_y=pace
                ).perform() if ele else ac.scroll_by_amount(0, pace).perform()
                if cb and cb():
                    success = True
                    break
                time.sleep(interval)
                dist -= unit
        else:
            ac.scroll_from_origin(
                scroll_origin=ScrollOrigin.from_element(ele),
                delta_x=0,
                delta_y=dist
            ).perform() if ele else ac.scroll_by_amount(0, dist).perform()

        if cb and not success:
            raise ValueError(common.I18n['_error_msg']['_element_not_found'])

    def select_sys_file(
            self,
            path: str,
            cb: Callable = None
    ) -> tuple:
        """
            通过系统文件选择框打开文件/目录

            参数:
                - path: 待打开的文件(目录)完整路径
                - cb: 回调函数, 选择完文件后需要执行的操作 默认 `None`

            返回值:
                - (bool, str): 成功返回 `True`, 错误信息为空, 否则返回 `False`, 错误信息
        """
        try:
            pg.typewrite(path)
            pg.typewrite(
                ['enter' if common.ENV['platform'] ==
                            'Win32' else 'return' for _ in range(2)
                 ],
                0.25
            )

            if cb:
                cb()

            return True, ''
        except BaseException as err:
            return False, str(err)

    def date_picker(
            self,
            dt: str,
            up_arrow: str,
            down_arrow: str,
            day_sel: str,
            by: Literal = By.XPATH
    ) -> WebElement:
        """
            日期选择器

            参数:
                - dt: 待选择的日期, 必须为 `Y-m-d` 格式
                - up_arrow: 向上箭头选择器, 用于月份选取
                - down_arrow: 向下箭头选择器, 用于月份选取
                - day_sel: 日期选择器, 执行结果应是一个 `List[WebElement]`
                - by: 选择器类型, 同 `By`
        """
        if not util.is_valid_datetime(
                dt=dt,
                ref_fmt='%Y-%m-%d'
        ):
            raise ValueError(
                f"{common.I18n['_errror_msg']['_invalid_time']}: {dt}"
            )

        y, m, d = map(lambda x: int(x), dt.split('-'))
        ty, tm = date.today().year, date.today().month
        diff = (ty - y) * 12 + (tm - m)

        if diff > 0:
            for _ in range(diff):
                self.click_on_element(
                    selector=up_arrow,
                    by=by
                )
        if diff < 0:
            for _ in range(abs(diff)):
                self.click_on_element(
                    selector=down_arrow,
                    by=by
                )

        list = self.find_elements_by_selector(
            selector=day_sel,
            by=by
        )
        for e in list:
            if e.text == str(d):
                e.click()
                return e

        return None

    def get_current_window(self) -> common.EWindow:
        """
            获取当前窗口

            返回值:
                - EWindow: 见`Common.EWindow`
        """
        return common.EWindow(self._driver.window_handles.index(self._driver.current_window_handle))

    def get_exist_windows(self) -> int:
        """
            获取当前存在窗口

            返回值:
                - int: 当前存在窗口数
        """
        return len(self._driver.window_handles)

    def switch_to_window(
            self,
            name: common.EWindow
    ) -> None:
        """
            跳转到特定窗口

            参数:
                - name: 窗口名称, 见`Common.EWindow`
        """
        self._driver.switch_to.window(self._driver.window_handles[name.value])

    # def switch_to_self_window(self) -> None:
    #     '''
    #         回到当前窗口
    #     '''
    #     self._driver.switch_to.window(self._driver.current_window_handle)

    def close(self) -> None:

        self._driver.quit()

    def get_window_rect(self) -> Dict[str, float]:
        """
            获取窗口尺寸

            参数:
                - element: 元素

            返回值:
                - x: 窗口左上角坐标横坐标
                - y: 窗口左上角坐标纵坐标
                - width: 屏幕宽度
                - height: 屏幕高度
        """

        return {
            'x': self._driver.execute_script('return window.screenLeft'),
            'y': self._driver.execute_script('return window.screenTop'),
            'width': self._driver.execute_script('return window.screen.width'),
            'height': self._driver.execute_script('return window.screen.height')
        }

    def get_element_rect(
            self,
            ele: WebElement,
            ref: Literal['screen', 'window'] = 'window'
    ) -> Dict[str, float]:
        """
            获取元素位置尺寸参数

            参数:
                - element: 元素

            返回值:
                - x: 元素左上角坐标横坐标
                - y: 元素左上角坐标纵坐标
                - width: 元素宽度
                - height: 元素高度
        """

        erect = ele.rect
        if ref == 'window':
            # logger.debug('元素参数(窗口): {}'.format(erect))
            return erect

        wrect = self.get_window_rect()

        erect = {
            'x': wrect['x'] + erect['x'],
            'y': wrect['y'] + erect['y'],
            'width': erect['width'],
            'height': erect['height']
        }
        # logger.debug('元素参数(屏幕): {}'.format(erect))
        return erect

    def mouse_move_to_element(
            self,
            element: WebElement
    ) -> WebElement:
        """
            物理鼠标移动到指定元素中心点

            参数:
                - element: 页面元素

        """
        rect = self.get_element_rect(element, 'screen')
        pg.moveTo(
            x=rect['x'] + rect['width'] * uniform(0.3, 0.7),
            y=rect['y'] + rect['height'] * uniform(0.3, 0.7)
        )
        return element

    def dropdownbox_handler(
            self,
            selector: str,
            value: str,
            by: Literal = By.XPATH,
            element: WebElement = None
    ) -> bool:
        """
            处理下拉框弹出问题, 如果当前值与设置的值一致, 则不弹出下拉框

            参数:
                - selector: 选择器, 执行选择的结果必须为当前值与弹出下拉框按钮的列表
                - value: 目标值
                - by: 选择器类型
                - element: 相对路径的根元素, 默认 None

            返回值
                如果需要弹出下拉框则返回True, 否则返回False
        """
        list = self.find_elements_by_selector(
            selector=selector,
            by=by,
            element=element
        )
        if len(list) != 2:
            return False

        if list[0].text == value:
            return False

        list[1].click()
        return True

    def scroll_bar(
            self,
            element: WebElement,
            value: float,
            orientation: Literal['up', 'down', 'left', 'right'],
            maximum: float = None,
            minimum: float = None,
            pause: float = 0.5
    ) -> None:
        """
            滚动调节条(音量, 亮度, 对比度等)

            参数:
                - element: 滚动条元素
                - value: 需要调节的数值
                - orientation: 滚动方向(值变大), 取值范围 up|down|left|right
                - maximum: 最大值, 不传设为元素max属性的值, 若元素没有max属性, 则抛出错误
                - minimum: 最小值, 不传设为元素min属性的值, 若元素没有min属性, 则抛出错误
                - pause: 执行完暂停时间, 默认0.5s
        """
        time.sleep(0.5)
        maximum = maximum or element.get_attribute('max')
        minimum = minimum or element.get_attribute('min')
        if not maximum:
            raise ValueError(f"{common.I18n['_error_msg']['_no_maximum']}")
        if not minimum:
            raise ValueError(f"{common.I18n['_error_msg']['_no_minimum']}")

        if float(value) < float(minimum):
            value = float(minimum)
        if float(value) > float(maximum):
            value = float(maximum)

        # print('最大值：', maximum, '最小值：', minimum, '目标值：', value)
        if orientation not in ['left', 'right', 'up', 'down']:
            raise ValueError(
                f"{common.I18n['_error_msg']['_wrong_params']}: {orientation}, Valid value: up|down|left|right"
            )

        orgin_step = self._driver.execute_script(
            "return arguments[0].step",
            element
        )
        self._driver.execute_script(
            "arguments[0].step={}".format(maximum),
            element
        )

        match orientation:
            case 'left':
                zero = Keys.RIGHT
                target = Keys.LEFT
            case 'right':
                zero = Keys.LEFT
                target = Keys.RIGHT
            case 'up':
                zero = Keys.DOWN
                target = Keys.UP
            case 'down':
                zero = Keys.UP
                target = Keys.DOWN
            case _:
                zero = Keys.LEFT
                target = Keys.RIGHT

        element.send_keys(zero)
        # print('置零：', element.get_attribute('value'))

        self._driver.execute_script(
            "arguments[0].step={}".format(orgin_step),
            element
        )

        rg = int((value - float(minimum)) / float(orgin_step))
        # print('要走的步数：', rg)
        for _ in range(rg):
            element.send_keys(target)
        time.sleep(pause)

    def mouse_press(
            self,
            element: WebElement,
            duration: int
    ) -> None:
        """
            长按鼠标

            参数:
                - element: 执行长按元素
                - duration: 按键持续时间
                - type: 按键类型 左键|右键|滚轮
        """
        ac = ActionChains(self._driver)

        ac.click_and_hold(element).perform()

        time.sleep(duration)

        ac.click(element).perform()

    def parse_cube_canvas(
            self,
            element: WebElement,
            xunit: int = 24,
            yunit: int = 7
    ) -> List[Any]:
        """
            获取 Canvas 的数据

            参数:
                - element: Canvas元素
                - xunit: 横向方块个数
                - yunit: 纵向方块个数
        """
        # width = self._driver.execute_script("return arguments[0].getBoundingClientRect().width;", element) # 执行JavaScript代码，获取元素的宽度
        # height = self._driver.execute_script("return arguments[0].getBoundingClientRect().height;", element) # 执行JavaScript代码，获取元素的高度

        self._driver.execute_script("arguments[0].scrollIntoView();", element)
        rect = self.get_element_rect(element)
        uwdh = float(rect['width']) / xunit
        uhgh = float(rect['height']) / yunit

        # action = ActionChains(self._driver)
        colors: List[List[Any]] = []  # 用于存储颜色值的列表

        for i in range(yunit):  # 纵向循环
            colors.append([])
            for j in range(xunit):  # 横向循环
                x = rect['x'] + uwdh / 2 + j * uwdh  # 计算方块中心的x坐标
                y = rect['y'] + uhgh / 2 + i * uhgh  # 计算方块中心的y坐标
                # action.move_to_element_with_offset(element, x, y).click().perform() # 移动并点击方块中心
                color = self._driver.execute_script(
                    "return window.getComputedStyle(document.elementFromPoint(arguments[0], arguments[1])).backgroundColor;",
                    x, y)  # 执行JavaScript代码，获取方块背景颜色
                colors[i].append(color)  # 将颜色值添加到列表中
        return colors
