from selenium.webdriver.common.by import By
from base.base_window import BaseWindow
from utils.read_config import config
from utils.common import common
from utils.utils import util


class AddDeviceWindow(BaseWindow):

    """ Get current page settings"""
    _data = config.get_page_data(source='selectors')

    def select_device_by_name(
        self,
        name: str,
        uid: str
    ) -> tuple:
        """
            通过设备名选中设备

            参数:
                - name: 设备名称

            返回值:
                (bool, str): 正确执行操作返回True, 错误信息为空; 否则, 返回False与错误信息
        """

        try:
            # if name in self._device_statuses['ACTIVE']:
            #     raise ValueError(
            #         common.I18n['_error_msg']['_device_already_active']
            #     )

            list = self.find_elements_by_selector(
                selector=self._data['_device_list_selector'],
                by=By.CSS_SELECTOR
            )

            target = None
            for i in list:
                title = self.get_element_text(
                    selector='h4',
                    by=By.TAG_NAME,
                    element=i
                )
                if title == name:
                    target = i

            if target:
                # 点击添加设备按钮
                self.click_on_element(
                    selector=self._data['_click_device_selector'],
                    by=By.CSS_SELECTOR,
                    element=target
                )
                # 如果是电池机，会有二次弹窗
                if util.get_device_battery_type(uid) != common.EDeviceType.WIRED:
                    success, err = self.confirm_add_device_window()
                    if not success:
                        raise ValueError(err)

                return True, ''

            else:
                raise ValueError(
                    common.I18n['_error_msg']['_device_not_found'])

        except BaseException as err:
            return False, str(err)

    def handle_wifi(
        self,
        uid: str = None
    ) -> tuple:
        """
            配置WiFi窗口

            参数:
                - name: 设备名称, 可选, 默认为`None`
                - uid: 设备`uid`, 可选, 默认为`None`

            返回值:
                (bool, str): 正确执行操作返回True, 错误信息为空; 否则, 返回False与错误信息
        """

        try:
            if util.get_device_wifi_type(uid) == common.EDeviceWifiType.WIRED_ONLY:
                return True, ''

            self.click_on_element(
                selector=self._data['_wifi_card_inited_selector'],
                by=By.CSS_SELECTOR
            )

            self.click_on_element(
                selector=self._data['_confirm_wifi_selector'],
                by=By.CSS_SELECTOR
            )

            return True, ''

        except BaseException as err:
            return False, str(err)

    def login_device(
        self,
        password: str,
        uname: str = 'admin'
    ) -> tuple:
        """
            登陆设备

            参数:
                - password: 密码
                - uname: 用户名

            返回值: (bool, str): 正确执行操作返回`True`, 错误信息为空; 否则, 返回`False`与错误信息
        """
        try:
            self.input_text(
                selector=self._data['_uname_input_selector'],
                text=uname
            )

            self.input_text(
                selector=self._data['_password_input_selector'],
                by=By.CSS_SELECTOR,
                text=password
            )

            self.click_on_element(
                selector=self._data['_login_button_selector'],
                by=By.CSS_SELECTOR
            )

            try:
                e = self.find_element_by_selector(
                    selector=self._data['_login_tip'],
                    wait_attr='text'
                )
                if e.text == common.I18n['_connect_fail']:
                    self.click_on_element(
                        selector=self._data['_close_login_window']
                    )
                return False, e.text
            except:
                if self.get_exist_windows() > 1:
                    return False, ''

            return True, ''

        except BaseException as err:
            return False, str(err)

    def close_add_device_window(self) -> tuple:
        """
            关闭添加设备窗口

            返回值: (bool, str): 正确执行操作返回True, 错误信息为空; 否则, 返回False与错误信息
        """
        try:
            self.click_on_element(
                selector=self._data['_close_btn_selector'],
                timeout=0.5
            )
            return True, ''
        except BaseException as err:
            return False, str(err)

    def close_login_window(self) -> tuple:
        """
            关闭添加设备窗口

            返回值: (bool, str): 正确执行操作返回True, 错误信息为空; 否则, 返回False与错误信息
        """
        try:
            self.click_on_element(
                selector=self._data['_close_login_window'],
                timeout=0.5
            )
            return True, ''
        except BaseException as err:
            return False, str(err)

    def confirm_add_device_window(self) -> tuple:
        """
            确然添加设备弹窗

            返回值: (bool, str): 正确执行操作返回True, 错误信息为空; 否则, 返回False与错误信息
        """
        try:
            self.click_on_element(
                selector=self._data['_confirm_btn_selector']
            )
            return True, ''
        except BaseException as err:
            return False, str(err)

    def add_device_by_ip_host(
        self,
        dest: str,
        port: int = 9000
    ) -> tuple:
        """
            - 根据ip或域名连接设备(设备需已配网)
            - 需先执行 click_add_device_button() 打开新增设备窗口

            参数:
                - dest: 目标 ip/域名
                - port: 端口 默认9000
        """
        try:
            self.click_on_element(
                selector=self._data['_add_by_ip_host_btn']
            )

            self.input_text(
                selector=self._data['_input_ip_host_area'],
                text=dest
            )
            self.input_text(
                selector=self._data['_input_port_area'],
                text=port
            )
            self.click_on_element(
                selector=self._data['_add_device_btn']
            )

            return True, ''

        except BaseException as err:
            return False, str(err)

    def add_device_by_uid(
        self,
        uid: str
    ) -> tuple:
        """
            - 根据`uid`连接设备(设备需已配网)
            - 需先执行 click_add_device_button() 打开新增设备窗口

            参数:
                - uid: 目标 ip/域名

            返回值:
                - tuple: 正确执行操作返回`True`, 错误信息为空; 否则, 返回`False`与错误信息
        """
        try:
            self.input_text(
                selector=self._data['_input_uid_area'],
                text=uid
            )
            self.click_on_element(
                selector=self._data['_add_device_btn']
            )

            # 如果是电池机，会有二次弹窗
            if util.get_device_battery_type(uid) != common.EDeviceType.WIRED:
                self.switch_to_window(common.EWindow.POPUP)
                success, err = self.confirm_add_device_window()
                if not success:
                    raise ValueError(err)
                self.switch_to_window(common.EWindow.DEVICE)

            return True, ''

        except BaseException as err:
            return False, str(err)

    def add_device_by_ip(
        self,
        ip: str
    ) -> tuple:
        '''
            - 根据`uid`连接设备(设备需已配网)
            - 需先执行 click_add_device_button() 打开新增设备窗口

            参数:
                - uid: 目标 ip/域名

            返回值:
                - tuple: 正确执行操作返回`True`, 错误信息为空; 否则, 返回`False`与错误信息
        '''
        try:
            self.click_on_element(
                selector=self._data['_ip_btn']
            )

            self.input_text(
                selector=self._data['_input_ip_area'],
                text=ip
            )
            self.click_on_element(
                selector=self._data['_add_device_btn']
            )

            return True, ''

        except BaseException as err:
            return False, str(err)

    def init_device(
        self,
        passwd: str,
        name: str
    ) -> tuple:
        """
            - 初始化设备密码

            参数:
                - passwd: 密码

            返回值:
                - (dict, str):
                    - 成功返回设备网络信息, 错误信息为空;
                    - 失败返回 `None` 和错误信息
        """
        try:

            self.input_text(
                selector=self._data['_input_init_passwd_area'],
                text=passwd
            )
            self.input_text(
                selector=self._data['_input_init_passwd_confirm_area'],
                text=passwd
            )
            self.click_on_element(
                selector=self._data['_init_passwd_next']
            )

            self.input_text(
                selector=self._data['_input_init_name'],
                text=name
            )
            self.click_on_element(
                selector=self._data['_init_name_blank_area'],
                pause=0.25
            )
            self.click_on_element(
                selector=self._data['_init_name_end']
            )

            return True, ''

        except BaseException as err:
            return False, str(err)

    def get_lan_devices(self) -> tuple:
        """
            返回局域网设备列表

            返回值:
                - (List(str), str):
                    - devices:  局域网设备名称列表
                    - err: 如果发生异常, 返回错误描述, 否则为空
        """
        try:
            list = self.find_elements_by_selector(
                selector=self._data['_device_list_selector'],
                by=By.CSS_SELECTOR
            )
            _ret = []
            for e in list:
                title = self.get_element_text(
                    selector='h4',
                    by=By.TAG_NAME,
                    element=e
                )
                _ret.append(title)

            return _ret, ''

        except BaseException as err:
            return [], str(err)
