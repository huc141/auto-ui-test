import sys
from typing import Iterable
import yaml
import os


class Config(object):
    __raw_data = dict()

    def __init__(self) -> None:
        """
            Custom config should place in test/config and with yml or yaml suffix.
            Source are the same as config file name.
        """
        # os.chdir("..")
        p = os.path.join(os.getcwd(), 'test/config')
        for fname in os.listdir(p):
            # 如果文件的扩展名不是 'yml' 或 'yaml'，则跳过这个文件，不执行后续的处理。这个逻辑用于过滤掉不是 YAML 文件的内容，只处理 'config' 目录下的 YAML 文件。
            # fname.split('.')：这会将文件名（如 'example.yml'）按照点号分割成一个列表，即 ['example', 'yml']。
            if fname.split('.')[-1] not in ['yml', 'yaml']:  # [-1]：这表示获取列表的最后一个元素，即文件扩展名。对于 'example.yml'，它会得到 'yml'。
                continue
            with open(file=os.path.join(p, fname), encoding='utf-8') as stream:  # 打开file文件，as stream：将打开的文件对象赋值给名为 stream 的变量
                self.__raw_data[fname.split('.')[0]] = yaml.safe_load(stream)  # 获取文件名的前缀如case.yml中的case，作为__raw_data字典的键，值是从 YAML 文件加载得到的数据.
                # safe_load是 PyYAML 库的函数，用于从打开的 YAML 文件流中加载数据。这里的 stream 是 open 函数返回的文件对象。
                # yaml.safe_load 会将 YAML 格式的数据解析成 Python 对象，比如字典或列表。
        # print(self.__raw_data)

        # 'chromium_version' 是作为键传递给 get_data 方法的参数，表示我们要获取的特定配置项的名称。
        # '' 是作为默认值传递给 get_data 方法的参数。如果配置项不存在，或者在配置文件中该项的值为 None，则使用这个默认值。
        self.chromium_version = self.get_data('chromium_version', '')  # 调用了 Config 类的 get_data 方法，该方法用于获取配置信息。
        self.app_data_dir = self.get_data('app_data_dir', '')
        self.executable_path = self.get_data('executable_path', '')

    def get_data(self, key: str, default: str = '', source: str = 'global') -> str:
        """Get specific config"""
        # 这是一个三元表达式，用于返回根据给定键从配置数据中检索的值，如果键不存在，则返回默认值。
        # return self.__raw_data[source][key] if key in self.__raw_data[source] else default
        # 改写为if-else更易读的结构
        if key in self.__raw_data[source]:  # self.__raw_data[source] 表示从类实例的 __raw_data 字典中获取一个名为 source 的子字典。
            return self.__raw_data[source][key]  # self.__raw_data[source][key] 表示从 source 子字典中获取键为 key 的值。
        else:
            return default

    def get_page_data(self, tier: str = None, source: str = 'global'):
        """
            获取页面配置参数

            参数:
                - source: 参数源
                    - global(全局参数)[默认]
                    - case(用例参数)
                    - selectors(选择器参数)
                - tier: 层级, 默认取与当前文件名一致的字段下的所有字段, 支持多层级

            eg:
                - get_page_data(tier='test_device_setting.test_stream_case', source='case')
                    会取 test/config/case.yml 下 test_device_setting 块下的 test_stream_case 参数

                - get_page_data(source='case')
                    - 不指定tier, 假设当前文件为 test_add_device 会取 test/config/case.yml 下 test_device_setting 块下的所有参数;
                    # - 自动匹配用例参数中的设备名, 通过 get_page_data(source='case')['device'][device_name]可获得设备基础参数

                - get_page_data(tier=''), 不指定source, 默认为global, tier为'', 会取 test/config/global.yml 下的所有参数
        """
        if tier is None:
            co_filename = sys._getframe(1).f_code.co_filename
            tier = os.path.splitext(os.path.basename(co_filename))[0]  # os.path.basename(co_filename) 取 co_filename 的基本文件名，即去除路径后的文件名部分。
            # os.path.splitext(...) 将文件名和扩展名分开，返回一个包含文件名和扩展名的元组。[0] 取元组的第一个元素，即文件名部分。
        # # 获取指定来源 (`source`) 的原始数据
        _data = self.__raw_data[source]

        _ret = dict()  # 创建一个空字典 _ret，用于存储最终提取的数据。
        _dinfo = dict()  # 创建一个空字典 _dinfo，用于存储额外的信息，这里的额外信息在代码中并没有给出。

        # if source == 'case':
        #     # 用例配置自动注入设备基础参数
        #     _dinfo['device'] = dict()
        #     for k, v in self.__raw_data['device'].items():
        #         _dinfo['device'][k] = v

        if tier == '':
            return _data if not _dinfo else {**_data, **_dinfo}
        else:
            tiers = tier.split('.')
            for t in tiers:
                flag = False
                if isinstance(_data, Iterable):
                    for k, v in _data.items():
                        if k == t:
                            flag = True
                            _data = v
                            _ret = v
                            break
                else:
                    _ret = _data
                if not flag:
                    _ret = {}
                    break

            if not _ret:
                return _ret
            return _ret if not _dinfo else {**_ret, **_dinfo}


config = Config()
