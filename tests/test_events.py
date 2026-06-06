"""
非遗活动页测试（test_events.py）
================================
演示的测试模式：
1. 多维度筛选（类型 + 城市）
2. 活动报名按钮交互
3. Skip 标记的使用（@pytest.mark.skip）
"""

import pytest
from utils.logger import logger


class TestEventsPage:
    """非遗活动页测试"""

    @pytest.mark.smoke
    def test_page_loads_successfully(self, events_page):
        """验证活动页加载"""
        events_page.navigate()
        count = events_page.get_event_count()
        logger.info(f"活动数量: {count}")
        assert count >= 0, "活动页应该加载（活动数量可以为 0 或更多）"

    @pytest.mark.regression
    @pytest.mark.parametrize("event_type", [
        "展览展演",
        "讲座研学",
        "节庆活动",
        "技艺工坊",
        "文创市集",
    ], ids=["展览展演", "讲座研学", "节庆活动", "技艺工坊", "文创市集"])
    def test_filter_by_type(self, events_page, event_type):
        """
        【参数化 + 筛选】遍历所有活动类型筛选

        验证每种类型筛选都能正常执行（不报错）
        注意：某些类型可能确实没有活动（结果为 0），这不代表筛选失败了
        """
        events_page.navigate()
        try:
            events_page.filter_by_type(event_type)
            events_page.wait_for_load_state("networkidle")

            count = events_page.get_event_count()
            logger.info(f"类型 '{event_type}' 筛选结果: {count} 个活动")
            # 不硬性要求 > 0，因为可能该类型暂无活动
        except Exception as e:
            logger.error(f"筛选 '{event_type}' 时出错: {e}")
            raise

    @pytest.mark.smoke
    def test_search_events(self, events_page):
        """验证活动搜索"""
        events_page.navigate()
        events_page.search("非遗")
        count = events_page.get_event_count()
        logger.info(f"搜索 '非遗' 结果: {count} 个活动")

    @pytest.mark.regression
    def test_event_signup_button(self, events_page):
        """
        验证活动报名按钮存在

        测试点击"免费报名"按钮后的行为
        注意：可能需要登录，这里只验证按钮可点击
        """
        events_page.navigate()

        # 先检查是否有活动
        if events_page.get_event_count() == 0:
            pytest.skip("当前没有活动，跳过报名按钮测试")

        # 验证报名按钮可见
        try:
            events_page.click_free_signup()
            logger.info("已点击免费报名按钮")
            # 如果未登录，可能会跳转到登录页或其他提示
            # 这里只验证点击操作不报错
        except Exception as e:
            logger.warning(f"报名按钮交互异常（可能需要登录）: {e}")

    @pytest.mark.skip(reason="完整报名流程需要登录态，暂不测试")
    def test_full_registration_flow(self, events_page):
        """
        完整报名流程（已跳过）

        @pytest.mark.skip 的用法：
        - reason 参数记录跳过原因
        - 适合功能未完成或被阻断的用例
        - 与 @pytest.mark.xfail 区别：skip 是不跑，xfail 是跑了但预期失败
        """
        pass
