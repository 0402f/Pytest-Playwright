"""
配置管理模块
-----------
职责：加载 config.yaml 配置文件，将其转换为 Python 对象，方便代码中访问。

设计模式：简单配置管理器（ConfigManager 单例的简化版）

面试可能问：
Q: 为什么不用 os.environ 直接读取环境变量？
A: YAML 文件更结构化，支持嵌套、注释，便于维护。
   实际项目中通常 YAML + 环境变量结合使用：
   - YAML 存默认值
   - 环境变量覆盖敏感信息（如 CI 环境的 base_url）
"""

import os
import yaml
from pathlib import Path


# ---- 配置加载器 ----
class Settings:
    """
    配置类：从 config.yaml 加载配置，提供属性式访问

    使用示例:
        from config.settings import settings
        print(settings.base_url)       # http://49.233.201.174:1234
        print(settings.timeout.default) # 30000
    """

    def __init__(self, config_path: str = None):
        """
        初始化配置

        Args:
            config_path: config.yaml 的路径，默认为当前文件同目录下的 config.yaml
        """
        if config_path is None:
            # 获取 config.yaml 的绝对路径（与 settings.py 同目录）
            config_path = Path(__file__).parent / "config.yaml"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)  # yaml.safe_load 比 yaml.load 更安全

        # 将 YAML 字典的键转为对象属性，方便访问
        # 例如 config.yaml 中的 base_url 可以通过 settings.base_url 访问
        self._build_attributes(self._config)

    def _build_attributes(self, data: dict, parent: object = None):
        """
        递归地将字典转为对象属性（支持嵌套访问）

        Args:
            data: 要转换的字典
            parent: 父对象（用于嵌套转换）
        """
        target = parent if parent is not None else self
        for key, value in data.items():
            if isinstance(value, dict):
                # 嵌套字典也转为对象
                nested = type("ConfigNode", (), {})()
                setattr(target, key, nested)
                self._build_attributes(value, nested)
            else:
                setattr(target, key, value)

    def get(self, key: str, default=None):
        """
        安全获取配置项（类似 dict.get）

        Args:
            key: 配置键，支持点号分隔的嵌套键，如 "timeout.default"
            default: 默认值

        Returns:
            配置值或默认值
        """
        keys = key.split(".")
        value = self._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def __repr__(self) -> str:
        return f"<Settings base_url={self.base_url}>"


# ---- 全局单例 ----
# 整个项目共享同一个配置实例
# 【面试考点】单例模式：确保全局只有一个配置对象，避免重复加载 YAML
settings = Settings()
