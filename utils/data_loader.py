"""
测试数据加载工具
---------------
职责：从 YAML 文件中加载测试数据，支持参数化测试。

设计模式：数据驱动测试（Data-Driven Testing，DDT）
- 将测试数据与测试逻辑分离
- 同一套测试代码，不同的数据输入
- 新增测试场景只需添加数据，不需修改代码

面试可能问：
Q: 什么是数据驱动测试？为什么要用它？
A: 代码与数据分离。同一个测试方法，传入不同的数据集多次运行。
   好处：减少重复代码、易于扩展测试场景、非技术人员也能添加数据。
   实现方式：pytest 的 @pytest.mark.parametrize + YAML/JSON/Excel 数据文件
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List


class DataLoader:
    """
    测试数据加载器

    使用示例:
        loader = DataLoader("data/test_data.yaml")
        nav_data = loader.get("navigation_links")
        # [{"name": "首页", "path": "/"}, ...]
    """

    def __init__(self, data_path: str = None):
        """
        Args:
            data_path: YAML 数据文件路径，默认 data/test_data.yaml
        """
        if data_path is None:
            data_path = Path(__file__).parent.parent / "data" / "test_data.yaml"
        else:
            data_path = Path(data_path)

        if not data_path.exists():
            raise FileNotFoundError(f"测试数据文件不存在: {data_path}")

        with open(data_path, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取指定键的测试数据

        Args:
            key: 数据键（支持点号分隔的嵌套键）
            default: 默认值

        Returns:
            对应的数据值
        """
        keys = key.split(".")
        value = self._data
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_all(self) -> Dict:
        """返回全部数据"""
        return self._data

    def get_list(self, key: str) -> List:
        """
        获取列表类型的数据（参数化测试常用）

        Args:
            key: 数据键

        Returns:
            列表数据，如果不存在返回空列表
        """
        data = self.get(key)
        if isinstance(data, list):
            return data
        return []


# ---- 模块级单例 ----
# 全局数据加载器
data_loader = DataLoader()
