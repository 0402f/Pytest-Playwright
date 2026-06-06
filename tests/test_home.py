"""
首页测试（test_home.py）
=======================
演示的测试模式：
1. 基础断言 - 页面标题、URL、元素可见性
2. 元素交互 - 点击、等待
3. 组件验证 - 导航栏、页脚
4. fixture 注入 - 使用预配置的 home_page fixture

面试考点：
Q: 一个测试函数应该测几个东西？
A: 一个测试函数只测一个"业务场景"。比如"首页加载"是一个场景，
   虽然里面会检查多个元素，但目标都是验证"首页正确加载了"。
   不要在一个测试里同时测"首页加载"和"导航跳转"。
"""

import pytest
from utils.logger import logger


class TestHomePage:
    """
    首页测试类

    面试考点：为什么要用测试类？
    - 组织相关的测试用例
    - 可以用 class 级别的 fixture（scope="class"）
    - 可以用 @pytest.mark 标记整个类的所有方法
    """

    @pytest.mark.smoke
    def test_page_loads_successfully(self, home_page):
        """
        【冒烟测试】验证首页能正常加载

        这是最重要的测试——如果这个测试失败了，说明网站可能挂了。
        冒烟测试 = 验证最基本的功能是否正常，像"按电源键看机器冒不冒烟"。
        """
        # Given: 用户访问首页
        home_page.navigate()

        # When & Then: 核心元素应该可见
        home_page.expect_page_loaded()

        # 验证页面标题
        assert home_page.page.title() == "HeritageCraft"
        logger.info("首页冒烟测试通过")

    @pytest.mark.smoke
    def test_navigation_bar_present(self, home_page):
        """
        【冒烟测试】验证导航栏

        使用 Navbar 组件验证所有导航链接都存在
        演示了 POM 中"组合优于继承"的组件设计
        """
        home_page.navigate()

        # 获取所有导航项文本
        nav_texts = home_page.navbar.get_all_nav_texts()
        logger.info(f"导航项: {nav_texts}")

        # 应该包含主要的导航链接
        assert "首页" in nav_texts, "导航栏应该包含 '首页'"
        assert "非遗文化" in nav_texts, "导航栏应该包含 '非遗文化'"
        assert "传承人" in nav_texts, "导航栏应该包含 '传承人'"

        # 或者用 Navbar 内置的验证方法
        home_page.navbar.expect_all_links_present()

    @pytest.mark.home
    def test_feature_cards_count(self, home_page):
        """
        【功能测试】验证首页功能入口卡片数量

        首页预期有 4 个功能入口卡片：
        数字馆藏、传承空间、云上工坊、非遗地图
        """
        home_page.navigate()

        count = home_page.get_feature_card_count()
        assert count == 4, f"预期 4 个功能卡片，实际 {count} 个"

        # 打印卡片标题（方便调试）
        titles = home_page.get_feature_titles()
        logger.info(f"功能卡片标题: {titles}")

    @pytest.mark.regression
    def test_footer_copyright(self, home_page):
        """
        【回归测试】验证页脚版权信息

        使用 Footer 组件
        """
        home_page.navigate()

        # 验证页脚可见
        assert home_page.footer.is_visible(), "页脚应该可见"

        # 验证版权信息
        copyright_text = home_page.footer.get_copyright_text()
        logger.info(f"版权信息: {copyright_text}")
        assert "湖北省非物质文化遗产" in copyright_text, "版权信息应包含机构名"

    @pytest.mark.smoke
    def test_announcements_section_visible(self, home_page):
        """
        【冒烟测试】验证系统公告区域存在

        使用文本定位来验证"系统公告"标题可见，
        这样不依赖于具体的 CSS 类名，更稳健
        """
        home_page.navigate()

        # 用文本定位验证公告区域存在
        home_page.expect_visible(home_page.ANNOUNCEMENT_HEADING, "系统公告标题应该可见")
        # 验证 "更多 >" 链接存在
        home_page.expect_visible(home_page.ANNOUNCEMENT_MORE, "'更多'链接应该可见")
        logger.info("系统公告区域验证通过")
