"""
非遗活动页（EventsPage）
========================
展示非遗相关活动，支持多维度筛选和在线报名。

页面结构（由 explore_subpages.py 探索获取）：
1. 搜索框（placeholder="搜索活动名称、地点、传承人..."）
2. 状态筛选：可报名 / 全部活动
3. 类型筛选标签：展览展演 / 讲座研学 / 节庆活动 / 技艺工坊 / 文创市集
4. 城市下拉选择
5. 排序方式选择（时间最近等）
6. 活动卡片（名称+日期+地点+传承人+剩余名额+报名按钮）
7. 活动日历组件
8. "立即报名" 按钮

面试考点：
Q: 如何处理日期筛选/日历组件？
A: 日历组件通常很复杂，避免直接操作。优先使用 API 传参，
   或者用 fill() 直接填入日期值（如果支持），
   确实需要点击日历的，可以用 locator 定位具体日期。
"""

from playwright.sync_api import Page
from pages.base_page import BasePage
from components.navbar import Navbar
from components.footer import Footer
from utils.logger import logger


class EventsPage(BasePage):
    """非遗活动页"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.navbar = Navbar(page)
        self.footer = Footer(page)

    # ---- 元素定位器 ----
    SEARCH_INPUT = 'input[placeholder*="搜索活动"]'
    SEARCH_BTN = 'button:has-text("搜索")'

    # 状态筛选
    STATUS_FILTER = "select:first-of-type, button:has-text('可报名')"

    # 类型筛选标签
    TYPE_TAGS = "button.filter-tag, .filter-tag"

    # 城市下拉
    CITY_SELECT = "select:last-of-type, button:has-text('全部城市')"

    # 排序
    SORT_SELECT = 'select, button:has-text("时间最近")'

    # 活动卡片
    EVENT_CARDS = ".event-card, [class*='event-card'], [class*='event-item']"
    EVENT_TITLES = f"{EVENT_CARDS} h3, {EVENT_CARDS} .title"
    EVENT_DATES = f"{EVENT_CARDS} .date, {EVENT_CARDS} [class*='date']"
    EVENT_SIGNUP_BTN = f'{EVENT_CARDS} button:has-text("报名"), {EVENT_CARDS} button:has-text("免费报名")'
    EVENT_FREE_BTN = 'button:has-text("免费报名")'  # 活动详情中的报名按钮

    # 活动日历
    CALENDAR = "[class*='calendar']"
    CALENDAR_EXPAND_BTN = 'button:has-text("展开")'

    # 无结果
    NO_RESULTS = "text=没有更多了"

    # ---- 操作方法 ----

    def navigate(self) -> None:
        """导航到活动页"""
        url = f"{self.base_url}/events"
        logger.info(f"导航到: {url}")
        self.page.goto(url, wait_until="networkidle")

    def search(self, keyword: str) -> None:
        """搜索活动"""
        logger.info(f"活动页 → 搜索: '{keyword}'")
        self.fill(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BTN)
        self.wait_for_load_state("networkidle")

    def filter_by_type(self, type_name: str) -> None:
        """
        按活动类型筛选

        Args:
            type_name: 类型名，如 "展览展演", "讲座研学", "技艺工坊"
        """
        logger.info(f"活动页 → 类型筛选: {type_name}")
        self.click(f'.filter-tag:has-text("{type_name}")')

    def filter_by_city(self, city: str) -> None:
        """按城市筛选"""
        logger.info(f"活动页 → 城市筛选: {city}")
        # 如果是 select 元素用 select_option，如果是按钮用 click
        try:
            self.select_option(self.CITY_SELECT, label=city)
        except Exception:
            self.click(f'button:has-text("{city}")')

    def sort_by(self, sort_type: str) -> None:
        """排序"""
        logger.info(f"活动页 → 排序: {sort_type}")
        try:
            self.select_option(self.SORT_SELECT, label=sort_type)
        except Exception:
            self.click(f'button:has-text("{sort_type}")')

    def click_first_signup(self) -> None:
        """点击第一个活动的报名按钮"""
        logger.info("活动页 → 报名（第一个活动）")
        self.page.locator(self.EVENT_SIGNUP_BTN).first.click()

    def click_free_signup(self) -> None:
        """点击 '免费报名' 按钮"""
        logger.info("活动页 → 免费报名")
        self.click(self.EVENT_FREE_BTN)

    def expand_calendar(self) -> None:
        """展开活动日历"""
        logger.info("活动页 → 展开日历")
        self.click(self.CALENDAR_EXPAND_BTN)

    # ---- 信息获取 ----

    def get_event_count(self) -> int:
        """获取活动数量"""
        return self.count(self.EVENT_CARDS)

    def get_event_titles(self) -> list:
        """获取活动标题列表"""
        return self.get_all_texts(self.EVENT_TITLES)

    def get_no_results_text(self) -> str:
        """获取无结果提示文本"""
        try:
            return self.get_text(self.NO_RESULTS)
        except Exception:
            return ""

    # ---- 验证方法 ----

    def expect_page_loaded(self) -> None:
        """验证活动页加载"""
        self.expect_visible(self.EVENT_CARDS, "活动卡片应该可见")

    def expect_results_count_greater_than(self, minimum: int) -> None:
        """验证活动数量大于指定值"""
        count = self.get_event_count()
        assert count >= minimum, f"活动数量 {count} 应该 >= {minimum}"
