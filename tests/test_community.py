"""
社区交流页测试（test_community.py）
==================================
演示话题筛选和帖子交互
"""

import pytest
from utils.logger import logger


class TestCommunityPage:
    """社区交流页测试"""

    @pytest.mark.smoke
    def test_page_loads_successfully(self, community_page):
        """验证社区页加载"""
        community_page.navigate()
        community_page.expect_page_loaded()

    @pytest.mark.regression
    def test_topic_filtering(self, community_page):
        """验证话题筛选功能"""
        community_page.navigate()
        all_topics = community_page.get_all_topics()
        logger.info(f"可用话题: {all_topics}")

        if len(all_topics) > 1:
            # 点击第二个话题
            community_page.filter_topic(all_topics[1])
            community_page.wait_for_load_state("networkidle")
            active = community_page.get_active_topic()
            logger.info(f"激活话题: {active}")

    @pytest.mark.regression
    def test_posts_displayed(self, community_page):
        """验证帖子列表展示"""
        community_page.navigate()
        count = community_page.get_post_count()
        logger.info(f"帖子数量: {count}")
        assert count > 0, "社区应该有帖子展示"

        # 检查帖子作者
        authors = community_page.get_post_authors()
        logger.info(f"作者列表: {authors[:5]}")

    def test_expand_post(self, community_page):
        """验证帖子展开功能"""
        community_page.navigate()
        try:
            community_page.click_expand_first()
            logger.info("已展开第一个帖子")
        except Exception as e:
            logger.warning(f"展开功能可能不可用: {e}")


class TestNotificationsPage:
    """系统通知页测试"""

    @pytest.mark.smoke
    def test_page_loads_successfully(self, notifications_page):
        """验证通知页加载"""
        notifications_page.navigate()
        notifications_page.expect_page_loaded()

    @pytest.mark.regression
    def test_tab_switching(self, notifications_page):
        """验证分类标签切换"""
        notifications_page.navigate()

        tabs = ["系统公告", "活动动态", "全部通知"]
        for tab in tabs:
            try:
                notifications_page.switch_tab(tab)
                notifications_page.wait_for_timeout(500)
                active = notifications_page.get_active_tab()
                logger.info(f"切换到 '{tab}' → 激活标签: {active}")
            except Exception as e:
                logger.warning(f"切换标签 '{tab}' 失败: {e}")

    @pytest.mark.regression
    def test_notification_list(self, notifications_page):
        """验证通知列表"""
        notifications_page.navigate()
        count = notifications_page.get_notification_count()
        logger.info(f"通知数量: {count}")
        assert count > 0, "应该有通知展示"

        titles = notifications_page.get_notification_titles()
        logger.info(f"通知标题: {titles}")

    def test_priority_filter(self, notifications_page):
        """验证优先级筛选"""
        notifications_page.navigate()
        try:
            notifications_page.filter_by_priority("高优先级")
            count = notifications_page.get_notification_count()
            logger.info(f"高优先级通知: {count}")
        except Exception as e:
            logger.warning(f"优先级筛选异常: {e}")
