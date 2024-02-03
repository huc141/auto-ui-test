"""组合基础窗口提供的能力，提供操作主窗口元素的能力"""
import time
from typing import List
from utils.read_config import config
from utils.common import common
from base.base_window import BaseWindow
from selenium.webdriver.common.by import By
from page.add_device_window import AddDeviceWindow


class MainWindow(BaseWindow):
    _data = config.get_page_data(source='selectors')

    _mappings = {
        f"{common.I18n['_stream_mode']['high']}": 'high',
        f"{common.I18n['_stream_mode']['standard']}": 'std',
        f"{common.I18n['_stream_mode']['low']}": 'low'
    }

    def click_add_device_button(self) -> tuple:
        """
            打开添加设备窗口
        """
        try:
            self.click_on_element(
                selector=self._data['_add_device_selector'],
                by=By.CSS_SELECTOR
            )
            return True, ''
        except BaseException as err:
            return False, str(err)

    def get_device_list(self) -> List[str]:
        """
            获取设备列表
            返回值:
                - List[str]: 设备名称列表
        """
        res = []
        try:
            device_list = self.find_elements_by_selector(
                selector=self._data['_device_list_selector'],
                by=By.CSS_SELECTOR
            )

            for d in device_list:
                device_name = self.get_element_text(
                    selector=self._data['_device_list_item_name'],
                    by=By.CSS_SELECTOR,
                    element=d
                )

                res.append(device_name)

            return res
        except BaseException as err:
            # self._logger.error('获取设备列表失败: ' + str(err))
            return []

    def click_device_button(self, name: str, area: str = 'setting') -> tuple:
        """
            点击指定设备按钮
            参数:
                - name: 设备名称
                - area: 点击区域, 可选值 setting|card|sd 默认值: setting
                    - setting: 设备设置按钮
                    - card: 选中设备
                    - sd: 设备sd卡按钮
            返回值:
                (WebElement, str): 成功执行返回选择的元素, 错误信息为空, 否则返回None与错误信息
        """
        try:
            device_list = self.find_elements_by_selector(
                selector=self._data['_device_list_selector'],
                by=By.CSS_SELECTOR
            )
            valid_btn_txt: str = ''
            match area:
                case 'sd':
                    selector = self._data['_sd_card_btn_selector']
                    valid_btn_txt = 'SD Card'
                case 'card':
                    selector = self._data['_device_card_selector']
                case _:
                    selector = self._data['_device_btn_selector']
                    valid_btn_txt = common.I18n['_setting']

            target = None
            for d in device_list:

                device_name = self.get_element_text(
                    selector=self._data['_device_list_item_name'],
                    by=By.CSS_SELECTOR,
                    element=d
                )

                try:
                    item = self.find_element_by_selector(
                        selector=selector,
                        by=By.CSS_SELECTOR,
                        element=d,
                        wait_attr=valid_btn_txt and 'title' or 'class',
                        timeout=1
                    )
                except:
                    continue

                if device_name == name:
                    if valid_btn_txt and item.get_attribute('title') != valid_btn_txt:
                        raise ValueError(
                            common.I18n['_error_msg']['_not_active_device']
                        )
                    self.mouse_move_to_element(item)
                    item.click()
                    target = item
                    break

            if not target:
                raise ValueError(
                    common.I18n['_error_msg']['_element_not_found']
                )

            # 判断设备状态
            status = self.get_device_status(name=name)
            if status == common.I18n['_e_device_status']['WRONG_PASS']:
                self.switch_to_window(common.EWindow.DEVICE)
                self.click_on_element(
                    selector=self._data['_close_login_pannel']
                )
                self.switch_to_window(common.EWindow.MAIN)

            return target, ''

        except BaseException as err:
            return None, str(err)

    def remove_devices(self, names: List[str]) -> tuple:
        device_list = self.get_device_list()
        name_set = set(names)
        """
            移除设备
            参数
                - names: 待移除的设备名列表
            返回值:
                - (bool, str): 正确执行操作返回True, 错误信息为空; 否则, 返回False与错误信息
        """
        try:
            # for name in set(self.get_device_list()).intersection(set(names)):
            for name in device_list:
                if name in name_set:
                    # 选中设备
                    card, err = self.click_device_button(name=name, area='card')
                    if err:
                        raise ValueError(err)

                    self.right_click(area=card)
                    self.click_on_image('remove')

                    self.switch_to_window(common.EWindow.DEVICE)

                    self.click_on_element(
                        selector=self._data['_confirm_remove_device_btn']
                    )

                    self.switch_to_window(common.EWindow.MAIN)

            return True, ''

        except BaseException as err:
            return False, str(err)

    def switch_to_add_device_window(self) -> AddDeviceWindow:
        """获取添加设备窗口"""
        return AddDeviceWindow(self._driver, self._driver.window_handles[1])

    def get_device_status(
            self,
            name: str
    ) -> str:

        _devices = set()
        try:
            res = None
            device_list = self.find_elements_by_selector(
                selector=self._data['_device_list_selector'],
                by=By.CSS_SELECTOR
            )

            for d in device_list:

                device_name = self.get_element_text(
                    selector=self._data['_device_list_item_name'],
                    by=By.CSS_SELECTOR,
                    element=d
                )

                _devices.add(device_name)

                device_status = self.get_element_text(
                    selector=self._data['_device_list_item_status'],
                    by=By.CSS_SELECTOR,
                    element=d
                )

                for k in self._device_statuses.keys():
                    if device_status == common.I18n['_e_device_status'][k]:
                        self._device_statuses[k].add(device_name)
                    else:
                        if device_name in self._device_statuses[k].copy():
                            self._device_statuses[k].remove(device_name)

                if device_name == name:
                    res = device_status
            return res if res else common.I18n['_e_device_status']['OTHER']

        except BaseException as err:
            raise ValueError(err)
        finally:
            for s, devices in self._device_statuses.copy().items():
                for d in devices:
                    if d not in _devices:
                        self._device_statuses[s].remove(d)
            self._logger.debug('设备状态检测: ' + str(self._device_statuses))

    def attempt_awake_devices(self, devices: List[str] = []) -> None:
        """
            尝试唤醒设备
            参数:
                - devices: 尝试唤醒的设备名称列表
        """
        try:
            # 获取设备列表元素
            device_list = self.find_elements_by_selector(
                selector=self._data['_device_list_selector'],
                by=By.CSS_SELECTOR
            )
            # 遍历设备列表
            for d in device_list:
                # 获取设备名称
                device_name = self.get_element_text(
                    selector=self._data['_device_list_item_name'],
                    by=By.CSS_SELECTOR,
                    element=d
                )
                i = 0
                # 如果设备列表为空，或者当前设备在指定的设备列表中
                if devices == [] or device_name in devices:
                    # 在规定的尝试次数内进行尝试
                    while self.get_device_status(device_name) != common.I18n['_e_device_status']['ACTIVE']:
                        i += 1
                        sl = self.find_elements_by_selector(
                            selector=self._data['_device_btn_selector'],
                            by=By.CSS_SELECTOR,
                            element=d
                        )
                        time.sleep(1)
                        # 遍历设备的按钮并点击
                        for se in sl:
                            self._logger.debug(
                                '尝试唤醒设备: {}-第{}次'.format(device_name, i)
                            )
                            if se.get_attribute('title') == common.I18n['_retry']:
                                se.click()
                        # 如果超过设定的尝试次数，抛出 TimeoutError
                        if i >= self._timeout:
                            raise TimeoutError(
                                f"{device_name} - {common.I18n['_error_msg']['_retry_exceed_limit']} - 已重试{i}次"
                            )

        except BaseException as err:
            pass
            # self._logger.debug('唤醒设备错误: {}'.format(err))
