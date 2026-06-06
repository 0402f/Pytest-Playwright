"""
系统通知页（NotificationsPage）
===============================
系统通知中心，管理公告、活动动态、账号安全等通知。

页面结构（由 explore_subpages.py 探索获取）：
1. 统计面板（通知总数 5 / 未读通知 5 / 高优提醒 0 / 系统公告 4）
2. 搜索框（placeholder="搜索标题、摘要或来源..."）
3. 分类标签页：全部通知 / 系统公告 / 活动动态 / 维护/紧急
4. 优先级筛选：全部级别 / 高优先级 / 普通 / 低优先级
5. 刷新列表按钮
6. 通知列表（标题+摘要+时间+来源+类型标签+优先级+已读/未读）
7. "标记已读" / "查看详情" 按钮

面试考点：
Q: 通知中心测试的重点？
A: 1) 不同分类 tab 切换后内容正确
   2) 已读/未读状态管理
   3) 优先级筛选
   4) 搜索功能
   5) 空状态（无通知时）
   6) 实时刷新
"""

from playwright.sync_api import Page
from pages.base_page import BasePage
from components.navbar import Navbar
from components.footer import Footer
from utils.logger import logger


class NotificationsPage(BasePage):
    """系统通知页"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.navbar = Navbar(page)
        self.footer = Footer(page)

    # ---- 元素定位器 ----
    SEARCH_INPUT = 'input[placeholder*="搜索标题"]'

    # 分类标签
    TAB_ALL = 'button.tab-btn:has-text("全部通知")'
    TAB_SYSTEM = 'button.tab-btn:has-text("系统公告")'
    TAB_ACTIVITY = 'button.tab-btn:has-text("活动动态")'
    TAB_URGENT = 'button.tab-btn:has-text("维护/紧急")'
    TAB_ACTIVE = "button.tab-btn.active"

    # 优先级筛选
    PRIORITY_ALL = 'button.priority-btn:has-text("全部级别")'
    PRIORITY_HIGH = 'button.priority-btn:has-text("高优先级")'
    PRIORITY_NORMAL = 'button.priority-btn:has-text("普通")'
    PRIORITY_LOW = 'button.priority-btn:has-text("低优先级")'

    # 刷新
    REFRESH_BTN = "button.refresh-top-btn, button:has-text('刷新列表')"

    # 通知列表
    NOTIFICATIONS = ".notification-item, [class*='notification']"
    NOTIFICATION_TITLES = f"{NOTIFICATIONS} h4, {NOTIFICATIONS} .title"
    NOTIFICATION_UNREAD = ".unread, [class*='unread']"

    # 操作按钮
    MARK_READ_BTN = 'button:has-text("标记已读")'
    VIEW_DETAIL_BTN = 'button:has-text("查看详情")'

    # 统计数字
    STATS = ".stats, [class*='stat']"

    # ---- 操作方法 ----

    def navigate(self) -> None:
        """导航到通知页"""
        url = f"{self.base_url}/notifications"
        logger.info(f"导航到: {url}")
        self.page.goto(url, wait_until="networkidle")

    def search(self, keyword: str) -> None:
        """搜索通知"""
        logger.info(f"通知页 → 搜索: '{keyword}'")
        self.fill(self.SEARCH_INPUT, keyword)
        self.press(self.SEARCH_INPUT, "Enter")
        self.wait_for_load_state("networkidle")

    def switch_tab(self, tab_name: str) -> None:
        """
        切换到指定通知分类标签

        Args:
            tab_name: 标签名，如 "系统公告", "活动动态", "维护/紧急", "全部通知"
        """
        logger.info(f"通知页 → 切换标签: {tab_name}")
        self.click(f'button.tab-btn:has-text("{tab_name}")')

    def get_active_tab(self) -> str:
        """获取当前激活的标签"""
        return self.get_text(self.TAB_ACTIVE)

    def filter_by_priority(self, priority: str) -> None:
        """
        按优先级筛选

        Args:
            priority: "全部级别" / "高优先级" / "普通" / "低优先级"
        """
        logger.info(f"通知页 → 优先级: {priority}")
        self.click(f'button.priority-btn:has-text("{priority}")')

    def click_refresh(self) -> None:
        """点击刷新列表"""
        logger.info("通知页 → 刷新列表")
        self.click(self.REFRESH_BTN)

    def click_mark_read(self) -> None:
        """点击标记已读"""
        logger.info("通知页 → 标记已读")
        self.click(self.MARK_READ_BTN)

    def click_view_detail(self) -> None:
        """点击第一个通知的查看详情"""
        logger.info("通知页 → 查看详情")
        self.page.locator(self.VIEW_DETAIL_BTN).first.click()

    # ---- 信息获取 ----

    def get_notification_count(self) -> int:
        """获取通知数量"""
        return self.count(self.NOTIFICATIONS)

    def get_notification_titles(self) -> list:
        """获取通知标题列表"""
        return self.get_all_texts(self.NOTIFICATION_TITLES)

    def get_unread_count(self) -> int:
        """获取未读通知数量"""
        return self.count(self.NOTIFICATION_UNREAD)

    # ---- 验证方法 ----

    def expect_page_loaded(self) -> None:
        """验证通知页加载"""
        self.expect_visible(self.TAB_ALL, "全部通知标签应该可见")
        self.expect_visible(self.NOTIFICATIONS, "通知列表应该可见")

    def expect_notification_count_greater_than(self, minimum: int) -> None:
        """验证通知数量"""
        count = self.get_notification_count()
        assert count > minimum, f"通知数量 {count} 应该 > {minimum}"
