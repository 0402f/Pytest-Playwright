"""
社区交流页（CommunityPage）
===========================
非遗爱好者社区，支持话题讨论、发帖互动。

页面结构（由 explore_subpages.py 探索获取）：
1. 话题筛选标签（全部 / #年轻人回归非遗 / #非遗+文创 / #传承人坚守 / #非遗在身边 / +更多）
2. 帖子列表（作者+时间+内容摘要+话题标签）
3. 帖子互动按钮（点赞数 / 评论数 / 收藏）
4. "..." 更多按钮（每个帖子）
5. "查看全文" / "收起" 展开按钮
6. 浮动发布按钮（fab-btn）

面试考点：
Q: 社区/社交类功能测试关注什么？
A: 1) 话题筛选正确性
   2) 帖子内容展示（包括长文本截断和展开）
   3) 互动功能（点赞/评论/收藏的状态同步）
   4) 空状态处理（无帖子时展示）
   5) 权限控制（未登录时的操作限制）
"""

from playwright.sync_api import Page
from pages.base_page import BasePage
from components.navbar import Navbar
from components.footer import Footer
from utils.logger import logger


class CommunityPage(BasePage):
    """社区交流页"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.navbar = Navbar(page)
        self.footer = Footer(page)

    # ---- 元素定位器 ----
    # 话题筛选
    TOPIC_CHIPS = "button.topic-switch-chip"
    TOPIC_ACTIVE = "button.topic-switch-chip.active"
    TOPIC_MORE = "button.topic-plus-btn"

    # 帖子列表
    POSTS = ".post-item, [class*='post-item'], [class*='card']"
    POST_CONTENT = f"{POSTS} .content, {POSTS} p"
    POST_AUTHOR = f"{POSTS} .author, {POSTS} [class*='author']"

    # 互动按钮
    LIKE_BTN = "button.interaction-btn:first-of-type"
    COMMENT_BTN = "button.interaction-btn:nth-of-type(1)"
    COLLECT_BTN = 'button:has-text("收藏")'

    # 展开/收起
    EXPAND_BTN = 'button:has-text("查看全文")'
    COLLAPSE_BTN = 'button:has-text("收起")'
    MORE_BTN = "button.more-btn"

    # 浮动按钮
    FAB_BTN = "button.fab-btn"

    # ---- 操作方法 ----

    def navigate(self) -> None:
        """导航到社区页"""
        url = f"{self.base_url}/community"
        logger.info(f"导航到: {url}")
        self.page.goto(url, wait_until="networkidle")

    def filter_topic(self, topic: str) -> None:
        """
        切换话题筛选

        Args:
            topic: 话题名，如 "#年轻人回归非遗", "#非遗在身边", "全部"
        """
        logger.info(f"社区 → 话题筛选: {topic}")
        self.click(f'.topic-switch-chip:has-text("{topic}")')

    def get_active_topic(self) -> str:
        """获取当前活跃话题"""
        return self.get_text(self.TOPIC_ACTIVE)

    def get_all_topics(self) -> list:
        """获取所有话题标签"""
        return self.get_all_texts(self.TOPIC_CHIPS)

    def click_more_topics(self) -> None:
        """展开更多话题"""
        logger.info("社区 → 展开更多话题")
        self.click(self.TOPIC_MORE)

    def get_post_count(self) -> int:
        """获取帖子数量"""
        return self.count(self.POSTS)

    def get_post_authors(self) -> list:
        """获取帖子作者列表"""
        return self.get_all_texts(self.POST_AUTHOR)

    def click_like_on_first(self) -> None:
        """点赞第一个帖子"""
        logger.info("社区 → 点赞（第一个帖子）")
        self.page.locator(self.LIKE_BTN).first.click()

    def click_collect_on_first(self) -> None:
        """收藏第一个帖子"""
        logger.info("社区 → 收藏（第一个帖子）")
        self.page.locator(self.POSTS).first.locator(self.COLLECT_BTN).click()

    def click_expand_first(self) -> None:
        """展开第一个帖子的全文"""
        logger.info("社区 → 查看全文")
        self.page.locator(self.EXPAND_BTN).first.click()

    def click_fab(self) -> None:
        """点击浮动发布按钮"""
        logger.info("社区 → 点击发布按钮")
        self.click(self.FAB_BTN)

    # ---- 验证方法 ----

    def expect_page_loaded(self) -> None:
        """验证社区页加载"""
        self.expect_visible(self.TOPIC_CHIPS, "话题标签应该可见")
        self.expect_visible(self.POSTS, "帖子列表应该可见")

    def expect_topic_active(self, topic: str) -> None:
        """验证当前激活的话题"""
        self.expect_text(self.TOPIC_ACTIVE, topic, f"激活话题应为: {topic}")
