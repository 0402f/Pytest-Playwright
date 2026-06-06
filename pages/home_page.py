"""
首页（HomePage）
===============
HeritageCraft 平台首页，包含轮播图、系统公告、功能入口、精选推荐等模块。

页面结构（由 explore_site.py 探索获取）：
1. 顶部导航栏（Navbar 组件）
2. 轮播图区域（banner + 前后切换按钮）
3. 系统公告列表
4. 功能入口卡片（数字馆藏、传承空间、云上工坊、非遗地图）
5. 匠心推荐区域（非遗项目卡片）
6. 大师风采区域（传承人卡片）
7. 非遗好物区域（商品卡片）
8. 底部页脚（Footer 组件）

面试考点：
Q: 首页有很多模块，Page Object 要怎么设计？
A: 模块过多时可以拆分为多个"区域对象"（Section Object），
   如 HomeBannerSection、HomeRecommendSection，保持类职责单一。
   或者按功能模块拆方法，每个方法只验证一个模块。
"""

from playwright.sync_api import Page
from pages.base_page import BasePage
from components.navbar import Navbar
from components.footer import Footer
from utils.logger import logger


class HomePage(BasePage):
    """
    首页页面对象

    使用示例:
        home = HomePage(page)
        home.navigate()          # 访问首页
        home.navbar.go_to_culture()  # 通过导航栏跳转
        home.get_announcements() # 获取公告列表
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # 组合方式引入组件：HomePage "拥有" 导航栏和页脚
        self.navbar = Navbar(page)
        self.footer = Footer(page)

    # ================================================================
    # 元素定位器
    # ================================================================

    # 轮播图
    CAROUSEL_CONTAINER = ".home-container .top-section"  # 轮播图容器
    CAROUSEL_PREV = "button.control.prev"                 # 上一个
    CAROUSEL_NEXT = "button.control.next"                 # 下一个
    BANNER_TITLE = ".top-section h1, .top-section .banner-title"  # 轮播标题

    # 系统公告
    ANNOUNCEMENT_SECTION = ".section-block"              # 公告区域
    ANNOUNCEMENT_MORE = "a.more"                         # "更多 >" 链接
    ANNOUNCEMENT_HEADING = 'text=系统公告'               # 用文本定位

    # 功能入口卡片（4个）
    FEATURE_CARDS = "section.features-section .feature-card, section.features-section a"
    FEATURE_CARD_TITLES = "section.features-section h3"

    # 匠心推荐
    RECOMMEND_SECTION = ".recommend-section"
    RECOMMEND_ITEMS = f"{RECOMMEND_SECTION} .card, {RECOMMEND_SECTION} .item"

    # 大师风采
    MASTER_SECTION = ".home-container .bottom-split-section"
    MASTER_ITEMS = f"{MASTER_SECTION} .card, {MASTER_SECTION} .item"
    MASTER_VIEW_ALL = f'{MASTER_SECTION} a:has-text("查看全部")'

    # 非遗好物
    PRODUCT_SECTION = ".bottom-split-section"
    PRODUCT_GO_MALL = 'a:has-text("前往商城")'

    # 我要申报 & 活动报名 按钮
    APPLY_BTN = 'a:has-text("我要申报"), button:has-text("我要申报")'
    EVENT_SIGNUP_BTN = 'a:has-text("活动报名"), button:has-text("活动报名")'

    # ================================================================
    # 页面导航
    # ================================================================

    def navigate(self) -> None:
        """访问首页"""
        self._navigate_to("")

    def _navigate_to(self, path: str) -> None:
        """内部导航方法"""
        url = f"{self.base_url}{path}"
        logger.info(f"导航到: {url}")
        self.page.goto(url, wait_until="networkidle")

    # ================================================================
    # 页面操作方法
    # ================================================================

    def click_carousel_next(self) -> None:
        """点击轮播图 → 下一个"""
        logger.info("首页 → 轮播图下一个")
        self.click(self.CAROUSEL_NEXT)

    def click_carousel_prev(self) -> None:
        """点击轮播图 → 上一个"""
        logger.info("首页 → 轮播图上一个")
        self.click(self.CAROUSEL_PREV)

    def get_banner_text(self) -> str:
        """获取轮播图标题文本"""
        return self.get_text(self.BANNER_TITLE)

    def click_more_announcements(self) -> None:
        """点击公告区域的 '更多 >'"""
        logger.info("首页 → 更多公告")
        self.click(self.ANNOUNCEMENT_MORE)

    def get_announcement_count(self) -> int:
        """获取公告区域内的条目数量"""
        # 使用文本定位找到公告区域，然后计算其中可点击条目的数量
        return self.count(self.ANNOUNCEMENT_SECTION)

    def get_feature_card_count(self) -> int:
        """获取功能入口卡片数量（预期 4 个）"""
        return self.count(self.FEATURE_CARDS)

    def get_feature_titles(self) -> list:
        """获取功能卡片标题列表"""
        return self.get_all_texts(self.FEATURE_CARD_TITLES)

    def click_view_all_masters(self) -> None:
        """点击大师风采的 '查看全部'"""
        self.click(self.MASTER_VIEW_ALL)

    def click_go_mall(self) -> None:
        """点击 '前往商城'"""
        self.click(self.PRODUCT_GO_MALL)

    def click_apply(self) -> None:
        """点击 '我要申报'"""
        logger.info("首页 → 我要申报")
        self.click(self.APPLY_BTN)

    def click_event_signup(self) -> None:
        """点击 '活动报名'"""
        logger.info("首页 → 活动报名")
        self.click(self.EVENT_SIGNUP_BTN)

    # ================================================================
    # 验证方法（供测试用例调用）
    # ================================================================

    def expect_page_loaded(self) -> None:
        """验证首页核心元素加载完成（冒烟测试用）"""
        self.expect_visible(self.CAROUSEL_CONTAINER, "轮播图应该可见")
        self.expect_visible(self.FEATURE_CARDS, "功能卡片应该可见")
        logger.info("首页加载验证通过")

    def expect_feature_cards_count(self, expected: int = 4) -> None:
        """验证功能卡片数量"""
        self.expect_count(self.FEATURE_CARDS, expected, f"功能卡片应该有 {expected} 个")
