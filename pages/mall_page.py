"""
非遗商城页（MallPage）
=====================
非遗商品展示与购买平台。

页面结构（由 explore_subpages.py 探索获取）：
1. 搜索框（placeholder="寻访非遗瑰宝..."）
2. 购物车 / 订单 / 我的 标签切换
3. 品类导航（汉绣/武当文创/黄梅挑花/编钟文创/楚式漆器 + 查看全部分类）
4. 分类标签过滤（全部/家居/文具/美食/饰品）
5. 商品卡片（图片+名称+传承人+销量+价格+收藏按钮）
6. "立即鉴赏" 按钮（跳转到商品详情）
7. "探索更多好物" / "获取定制方案" / "下载案例手册" 按钮
8. 轮播指示器

面试考点：
Q: 电商测试的重点是什么？
A: 1) 商品搜索/筛选/排序准确性
   2) 价格显示正确性
   3) 购物车增删改
   4) 收藏/取消收藏
   5) 边界条件：库存为0、已下架商品
"""

from playwright.sync_api import Page
from pages.base_page import BasePage
from components.navbar import Navbar
from components.footer import Footer
from utils.logger import logger


class MallPage(BasePage):
    """非遗商城页"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.navbar = Navbar(page)
        self.footer = Footer(page)

    # ---- 元素定位器 ----
    SEARCH_INPUT = 'input[placeholder*="寻访非遗"]'

    # Tab 切换
    TAB_CART = 'button:has-text("购物车"), a:has-text("购物车")'
    TAB_ORDERS = 'button:has-text("订单"), a:has-text("订单")'
    TAB_MINE = 'button:has-text("我的"), a:has-text("我的")'

    # 分类标签
    CATEGORY_TAGS = "button.filter-tag, .category-tag, [class*='category'] button"
    VIEW_ALL_CATEGORIES = 'button:has-text("查看全部分类"), a:has-text("查看全部分类")'

    # 商品卡片
    PRODUCT_CARDS = ".product-card, [class*='product-card'], [class*='item-card']"
    PRODUCT_NAMES = f"{PRODUCT_CARDS} h3, {PRODUCT_CARDS} .name, {PRODUCT_CARDS} [class*='name']"
    PRODUCT_PRICES = f"{PRODUCT_CARDS} .price, {PRODUCT_CARDS} [class*='price']"
    PRODUCT_COLLECT_BTN = 'button:has-text("收藏"), button:has-text("立即收藏")'
    PRODUCT_VIEW_BTN = 'button:has-text("鉴赏"), a:has-text("鉴赏")'

    # 底部按钮
    EXPLORE_MORE_BTN = 'button:has-text("探索更多好物"), a:has-text("探索更多好物")'
    CUSTOM_PLAN_BTN = 'button:has-text("获取定制方案"), a:has-text("获取定制方案")'
    DOWNLOAD_CATALOG_BTN = 'button:has-text("下载案例手册"), a:has-text("下载案例手册")'

    # ---- 操作方法 ----

    def navigate(self) -> None:
        """导航到商城页"""
        url = f"{self.base_url}/mall"
        logger.info(f"导航到: {url}")
        self.page.goto(url, wait_until="networkidle")

    def search(self, keyword: str) -> None:
        """搜索商品"""
        logger.info(f"商城 → 搜索: '{keyword}'")
        self.fill(self.SEARCH_INPUT, keyword)
        self.press(self.SEARCH_INPUT, "Enter")
        self.wait_for_load_state("networkidle")

    def filter_by_category(self, category: str) -> None:
        """按商品分类筛选"""
        logger.info(f"商城 → 分类: {category}")
        self.click(f'.filter-tag:has-text("{category}"), button:has-text("{category}")')

    def click_cart(self) -> None:
        """切换到购物车"""
        logger.info("商城 → 购物车")
        self.click(self.TAB_CART)

    def click_orders(self) -> None:
        """切换到订单"""
        logger.info("商城 → 订单")
        self.click(self.TAB_ORDERS)

    def click_mine(self) -> None:
        """切换到我的"""
        logger.info("商城 → 我的")
        self.click(self.TAB_MINE)

    def click_first_product(self) -> None:
        """点击第一个商品的 '立即鉴赏'"""
        logger.info("商城 → 鉴赏（第一个商品）")
        self.page.locator(self.PRODUCT_VIEW_BTN).first.click()

    def click_collect_first(self) -> None:
        """收藏第一个商品"""
        logger.info("商城 → 收藏（第一个商品）")
        self.page.locator(self.PRODUCT_COLLECT_BTN).first.click()

    def click_explore_more(self) -> None:
        """点击 '探索更多好物'"""
        self.click(self.EXPLORE_MORE_BTN)

    # ---- 信息获取 ----

    def get_product_count(self) -> int:
        """获取商品数量"""
        return self.count(self.PRODUCT_CARDS)

    def get_product_names(self) -> list:
        """获取商品名称列表"""
        return self.get_all_texts(self.PRODUCT_NAMES)

    def get_product_prices(self) -> list:
        """获取商品价格列表"""
        return self.get_all_texts(self.PRODUCT_PRICES)

    # ---- 验证方法 ----

    def expect_page_loaded(self) -> None:
        """验证商城页加载"""
        self.expect_visible(self.PRODUCT_CARDS, "商品卡片应该可见")

    def expect_product_count_greater_than(self, minimum: int = 0) -> None:
        """验证商品数量"""
        count = self.get_product_count()
        assert count > minimum, f"商品数量 {count} 应该 > {minimum}"
