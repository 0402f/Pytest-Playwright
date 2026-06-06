"""
页脚组件（Footer）
=================
页面底部的通用页脚，包含版权信息、快速链接、联系我们等。

面试考点：
Q: 组件测试的优先级怎么排？
A: 高复用组件 > 核心业务流程 > 低频功能
   Footer 虽然复用度高，但业务重要性低，通常用 1-2 条冒烟测试覆盖即可。
"""

from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.logger import logger


class Footer:
    """
    页脚组件

    使用方式：
        footer = Footer(page)
        footer.get_copyright_text()
        footer.click_about_us()
    """

    def __init__(self, page: Page):
        self.page = page
        self._base = BasePage(page)

    # ---- 元素定位器 ----
    FOOTER = "footer.app-footer"
    COPYRIGHT = "footer.app-footer .footer-bottom p"
    ABOUT_US = 'footer.app-footer a:has-text("关于我们")'
    HELP_CENTER = 'footer.app-footer a:has-text("帮助中心")'
    FAQ = 'footer.app-footer a:has-text("常见问题")'
    FEEDBACK = 'footer.app-footer a:has-text("意见反馈")'
    CONTACT_US = 'footer.app-footer a:has-text("联系客服")'

    # ---- 操作方法 ----

    def get_copyright_text(self) -> str:
        """获取版权信息文本"""
        return self._base.get_text(self.COPYRIGHT)

    def click_about_us(self) -> None:
        """点击 '关于我们'"""
        logger.info("页脚 → 关于我们")
        self._base.click(self.ABOUT_US)

    def click_help_center(self) -> None:
        """点击 '帮助中心'"""
        logger.info("页脚 → 帮助中心")
        self._base.click(self.HELP_CENTER)

    def click_faq(self) -> None:
        """点击 '常见问题'"""
        logger.info("页脚 → 常见问题")
        self._base.click(self.FAQ)

    def click_feedback(self) -> None:
        """点击 '意见反馈'"""
        logger.info("页脚 → 意见反馈")
        self._base.click(self.FEEDBACK)

    def click_contact_us(self) -> None:
        """点击 '联系客服'"""
        logger.info("页脚 → 联系客服")
        self._base.click(self.CONTACT_US)

    # ---- 验证方法 ----

    def is_visible(self) -> bool:
        """检查页脚是否可见"""
        return self._base.is_visible_quick(self.FOOTER)

    def expect_copyright_contains(self, text: str) -> None:
        """验证版权信息包含指定文本"""
        self._base.expect_text(self.COPYRIGHT, text, f"版权信息应包含: {text}")
