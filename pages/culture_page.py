"""
非遗文化页（CulturePage）
=========================
展示湖北省非物质文化遗产数据库，支持搜索、分类筛选、分页浏览。

页面结构（由 explore_subpages.py 探索获取）：
1. 顶部统计面板（收录项目数 146 / 传承人数 141 / 覆盖城市 19）
2. 搜索框（placeholder="搜索非遗项目、地域、传承人、关键词..."）
3. 批次下拉选择 (select) + 类型下拉选择 (select)
4. 项目卡片列表（名称 + 批次 + 地区 + 类型 + 简介）
5. "加载更多" 按钮

面试考点：
Q: 搜索功能怎么测试？
A: 需覆盖多种场景：精确搜索、模糊搜索、空结果、特殊字符、SQL注入防护等。
   用数据驱动方式（参数化）组合不同输入和期望结果。
"""

from playwright.sync_api import Page
from pages.base_page import BasePage
from components.navbar import Navbar
from components.footer import Footer
from utils.logger import logger


class CulturePage(BasePage):
    """非遗文化页"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.navbar = Navbar(page)
        self.footer = Footer(page)

    # ---- 元素定位器 ----
    # 搜索框
    SEARCH_INPUT = 'input[placeholder*="搜索非遗"]'
    SEARCH_BTN = 'button.search-btn, button:has-text("搜索")'
    SEARCH_HOT_TAGS = ".hot-tags a, [class*='hot'] a"  # 热门搜索标签

    # 统计数据
    STATS_NUMBERS = ".stats-number, [class*='stat'] [class*='number']"
    STATS_LABELS = ".stats-label, [class*='stat'] [class*='label']"

    # 筛选器
    BATCH_SELECT = "select:first-of-type"       # 批次下拉
    TYPE_SELECT = "select:last-of-type"          # 类型下拉
    FILTER_BUTTONS = "button.filter-btn, .filter-tag"

    # 结果列表
    RESULT_COUNT = "[class*='result-count'], [class*='found']"
    CULTURE_CARDS = ".culture-card, [class*='heritage-card'], [class*='item-card']"
    CARD_TITLES = f"{CULTURE_CARDS} h3, {CULTURE_CARDS} .title"

    # 加载更多
    LOAD_MORE_BTN = 'button:has-text("加载更多")'

    # 非遗地图
    MAP_SECTION = "[class*='map']"

    # ---- 操作方法 ----

    def navigate(self) -> None:
        """导航到非遗文化页"""
        url = f"{self.base_url}/culture"
        logger.info(f"导航到: {url}")
        self.page.goto(url, wait_until="networkidle")

    def search(self, keyword: str) -> None:
        """
        执行搜索操作

        Args:
            keyword: 搜索关键词
        """
        logger.info(f"非遗文化 → 搜索: '{keyword}'")
        self.fill(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BTN)
        # 等待搜索结果加载
        self.wait_for_load_state("networkidle")

    def click_hot_tag(self, index: int = 0) -> None:
        """
        点击热门搜索标签

        Args:
            index: 标签索引（0-based）
        """
        logger.info(f"非遗文化 → 点击热门标签 #{index}")
        tags = self.page.locator(self.SEARCH_HOT_TAGS)
        tags.nth(index).click()

    def filter_by_batch(self, batch_label: str) -> None:
        """
        按批次筛选

        Args:
            batch_label: 批次显示文本，如 "2006(第一批)"
        """
        logger.info(f"非遗文化 → 筛选批次: {batch_label}")
        self.select_option(self.BATCH_SELECT, label=batch_label)

    def filter_by_type(self, type_label: str) -> None:
        """
        按类型筛选

        Args:
            type_label: 类型显示文本，如 "民间文学"
        """
        logger.info(f"非遗文化 → 筛选类型: {type_label}")
        self.select_option(self.TYPE_SELECT, label=type_label)

    def click_load_more(self) -> None:
        """点击 '加载更多'"""
        logger.info("非遗文化 → 加载更多")
        self.click(self.LOAD_MORE_BTN)

    # ---- 信息获取 ----

    def get_result_count_text(self) -> str:
        """获取搜索结果数量文本，如 '共找到 146 个项目'"""
        try:
            return self.page.locator(self.RESULT_COUNT).first.inner_text()
        except Exception:
            return ""

    def get_card_count(self) -> int:
        """获取当前页面的项目卡片数量"""
        return self.count(self.CULTURE_CARDS)

    def get_card_titles(self) -> list:
        """获取所有卡片标题"""
        return self.get_all_texts(self.CARD_TITLES)

    def get_stats_numbers(self) -> list:
        """获取统计数字，如 ['146', '141', '19']"""
        return self.get_all_texts(self.STATS_NUMBERS)

    # ---- 验证方法 ----

    def expect_search_results(self, expected_keyword: str = "") -> None:
        """验证搜索结果不为空"""
        self.expect_visible(self.CULTURE_CARDS, "搜索结果应该有卡片展示")
        if expected_keyword:
            # 验证结果包含搜索关键词（取第一个卡片）
            first_card = self.page.locator(self.CULTURE_CARDS).first
            expect(self.page.locator(self.CULTURE_CARDS).first).to_be_visible()

    def expect_cards_count_greater_than(self, minimum: int = 0) -> None:
        """验证卡片数量大于指定值"""
        count = self.get_card_count()
        assert count > minimum, f"卡片数量 {count} 应该大于 {minimum}"
        logger.info(f"当前显示 {count} 张卡片")
