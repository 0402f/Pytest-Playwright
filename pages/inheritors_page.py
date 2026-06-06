"""
传承人页（InheritorsPage）
==========================
展示非遗传承人信息，支持分类筛选和搜索。

页面结构（由 explore_subpages.py 探索获取）：
1. 顶部统计（国家级 102 / 省级 29 / 市级 10）
2. 搜索框（placeholder="搜索传承人姓名、技艺、地区..."）
3. 分类筛选按钮组（全部/民间文学/传统音乐/传统舞蹈/...共11个）
4. 传承人卡片列表（姓名+地区+类别标签+简介+级别标记）
5. "了解详情 →" 按钮（每个卡片）
6. "加载更多传承人" 按钮
7. 地图查看 & 申请入口

面试考点：
Q: 多个相似的筛选按钮怎么处理才优雅？
A: 用数据驱动 + 公共方法：定义一个 filter_by_category(name) 方法，
   通过文本匹配点击，测试侧用 @pytest.mark.parametrize 遍历所有分类。
"""

from playwright.sync_api import Page
from pages.base_page import BasePage
from components.navbar import Navbar
from components.footer import Footer
from utils.logger import logger


class InheritorsPage(BasePage):
    """传承人页"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.navbar = Navbar(page)
        self.footer = Footer(page)

    # ---- 元素定位器 ----
    SEARCH_INPUT = 'input[placeholder*="搜索传承人"]'
    FILTER_BUTTONS = "button.filter-btn"
    FILTER_ACTIVE = "button.filter-btn.active"

    INHERITOR_CARDS = ".inheritor-card, [class*='inheritor-card'], [class*='item-card']"
    CARD_NAMES = f"{INHERITOR_CARDS} h3, {INHERITOR_CARDS} .name"
    CARD_DETAIL_BTN = f'{INHERITOR_CARDS} button:has-text("了解详情"), {INHERITOR_CARDS} a:has-text("了解详情")'

    LOAD_MORE_BTN = 'button:has-text("加载更多")'
    MAP_BTN = 'button:has-text("查看完整地图")'
    APPLY_BTN = 'button:has-text("立即申请"), a:has-text("立即申请")'
    GUIDE_BTN = 'button:has-text("查看申请指南"), a:has-text("查看申请指南")'

    STATS_NUMBERS = ".stats-number, [class*='stat'] [class*='number']"

    # ---- 操作方法 ----

    def navigate(self) -> None:
        """导航到传承人页"""
        url = f"{self.base_url}/inheritors"
        logger.info(f"导航到: {url}")
        self.page.goto(url, wait_until="networkidle")

    def search(self, keyword: str) -> None:
        """搜索传承人"""
        logger.info(f"传承人页 → 搜索: '{keyword}'")
        self.fill(self.SEARCH_INPUT, keyword)
        # 按回车触发搜索
        self.press(self.SEARCH_INPUT, "Enter")
        self.wait_for_load_state("networkidle")

    def filter_by_category(self, category: str) -> None:
        """
        按分类筛选

        Args:
            category: 分类名称，如 "民间文学", "传统音乐", "全部"
        """
        logger.info(f"传承人页 → 筛选分类: {category}")
        # 使用 has-text 找到对应的筛选按钮并点击
        self.click(f'button.filter-btn:has-text("{category}")')

    def get_active_filter(self) -> str:
        """获取当前激活的筛选分类"""
        return self.get_text(self.FILTER_ACTIVE)

    def get_all_categories(self) -> list:
        """获取所有筛选分类名称"""
        return self.get_all_texts(self.FILTER_BUTTONS)

    def get_card_count(self) -> int:
        """获取传承人卡片数量"""
        return self.count(self.INHERITOR_CARDS)

    def get_inheritor_names(self) -> list:
        """获取所有传承人姓名"""
        return self.get_all_texts(self.CARD_NAMES)

    def click_first_detail(self) -> None:
        """点击第一个传承人的 '了解详情'"""
        logger.info("传承人页 → 了解详情（第一个）")
        self.page.locator(self.CARD_DETAIL_BTN).first.click()

    def click_load_more(self) -> None:
        """点击 '加载更多传承人'"""
        logger.info("传承人页 → 加载更多")
        self.click(self.LOAD_MORE_BTN)

    def click_apply(self) -> None:
        """点击 '立即申请'"""
        logger.info("传承人页 → 立即申请")
        self.click(self.APPLY_BTN)

    # ---- 验证方法 ----

    def expect_page_loaded(self) -> None:
        """验证传承人页核心元素加载"""
        self.expect_visible(self.INHERITOR_CARDS, "传承人卡片应该可见")
        self.expect_visible(self.FILTER_BUTTONS, "分类筛选按钮应该可见")

    def expect_filter_active(self, category: str) -> None:
        """验证当前激活的筛选分类"""
        self.expect_text(self.FILTER_ACTIVE, category, f"激活的筛选器应为: {category}")
