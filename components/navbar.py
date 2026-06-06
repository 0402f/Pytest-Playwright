"""
导航栏组件（Navbar）
==================
导航栏是所有页面共用的顶部导航组件，包含 7 个导航链接和登录/注册按钮。

设计模式：组件化设计
- 不重复编写导航栏的定位器
- 所有页面通过组合（Composition）方式引入 Navbar
- 修改导航栏只需改这一个文件

面试考点：
Q: 组件化 vs 继承有什么区别？
A: 组合优于继承。Navbar 不是"一种页面"，而是"页面的组成部分"。
   组合（has-a）比继承（is-a）更灵活，一个页面可以组合多个组件。
"""

from playwright.sync_api import Page
from pages.base_page import BasePage

# ---- 日志 ----
from utils.logger import logger


class Navbar:
    """
    顶部导航栏组件

    使用方式：
        nav = Navbar(page)
        nav.go_to_culture()         # 导航到非遗文化页
        nav.get_all_nav_texts()     # 获取所有导航项文本
        nav.click_login()           # 点击登录/注册
    """

    def __init__(self, page: Page):
        """
        Args:
            page: Playwright Page 对象
        """
        self.page = page
        # 注入 BasePage 以复用其封装的方法（click, get_text 等）
        self._base = BasePage(page)

    # ================================================================
    # 元素定位器（集中管理，方便修改）
    # CSS Selector 写法说明：
    # - header.topnav: <header class="topnav">
    # - nav.links:      <nav class="links">
    # - .primary:       任意元素的 class="primary"
    # ================================================================

    # 导航容器选择器
    NAV_CONTAINER = "header.topnav nav.links"

    # 导航链接选择器（nav.links 下的所有 a 标签）
    NAV_LINKS = "header.topnav nav.links a"

    # 登录/注册按钮
    LOGIN_BTN = "header.topnav div.actions button.primary"

    # 品牌/Logo 区域
    BRAND = "header.topnav div.brand"

    # ================================================================
    # 导航操作方法
    # ================================================================

    def go_to_home(self) -> None:
        """导航到首页"""
        logger.info("导航栏 → 首页")
        self._base.click(f'{self.NAV_LINKS}:has-text("首页")')

    def go_to_culture(self) -> None:
        """导航到非遗文化页"""
        logger.info("导航栏 → 非遗文化")
        self._base.click(f'{self.NAV_LINKS}:has-text("非遗文化")')

    def go_to_inheritors(self) -> None:
        """导航到传承人页"""
        logger.info("导航栏 → 传承人")
        self._base.click(f'{self.NAV_LINKS}:has-text("传承人")')

    def go_to_events(self) -> None:
        """导航到非遗活动页"""
        logger.info("导航栏 → 非遗活动")
        self._base.click(f'{self.NAV_LINKS}:has-text("非遗活动")')

    def go_to_mall(self) -> None:
        """导航到非遗商城页"""
        logger.info("导航栏 → 非遗商城")
        self._base.click(f'{self.NAV_LINKS}:has-text("非遗商城")')

    def go_to_community(self) -> None:
        """导航到社区交流页"""
        logger.info("导航栏 → 社区交流")
        self._base.click(f'{self.NAV_LINKS}:has-text("社区交流")')

    def go_to_notifications(self) -> None:
        """导航到系统通知页"""
        logger.info("导航栏 → 系统通知")
        self._base.click(f'{self.NAV_LINKS}:has-text("系统通知")')

    def click_login(self) -> None:
        """点击登录/注册按钮"""
        logger.info("导航栏 → 点击登录/注册")
        self._base.click(self.LOGIN_BTN)

    # ================================================================
    # 信息获取方法
    # ================================================================

    def get_all_nav_texts(self) -> list:
        """
        获取所有导航项的文本

        Returns:
            例如: ["首页", "非遗文化", "传承人", "非遗活动", "非遗商城", "社区交流", "系统通知"]
        """
        return self._base.get_all_texts(self.NAV_LINKS)

    def get_nav_count(self) -> int:
        """获取导航链接数量"""
        return self._base.count(self.NAV_LINKS)

    def is_login_visible(self) -> bool:
        """检查登录按钮是否可见"""
        return self._base.is_visible_quick(self.LOGIN_BTN)

    # ================================================================
    # 验证方法
    # ================================================================

    def expect_all_links_present(self) -> None:
        """
        验证所有 7 个导航链接都存在
        用于冒烟测试：确保导航栏完整加载
        """
        expected_links = ["首页", "非遗文化", "传承人", "非遗活动", "非遗商城", "社区交流", "系统通知"]
        for link_text in expected_links:
            selector = f'{self.NAV_LINKS}:has-text("{link_text}")'
            self._base.expect_visible(selector, f"导航链接 '{link_text}' 应该存在")
        logger.info("所有导航链接验证通过")
