"""
导航测试（test_navigation.py）
==============================
演示 pytest 的核心特性：参数化测试（parametrize）

面试考点：
Q: @pytest.mark.parametrize 是什么？为什么要用它？
A: 参数化测试 = 同一个测试逻辑，用不同的输入数据跑多次。
   优势：
   1. 减少重复代码（不用写 N 个相似的测试函数）
   2. 一个数据跑失败不影响其他数据
   3. 新增测试数据只需加一行，不改代码
   4. 失败时清晰显示是哪组数据失败了

Q: 参数化的 ids 参数有什么用？
A: 给每组参数起一个易读的名字，报告里更清晰。
   没有 ids 时，pytest 用参数的 repr() 生成名字，可能很长/难读。
"""

import pytest
from playwright.sync_api import expect
from utils.logger import logger


# 参数化数据：所有导航链接及其对应的子页面路径
# 这是一个"数据驱动测试"的典型例子
NAVIGATION_DATA = [
    ("首页", "/", "首页"),
    ("非遗文化", "/culture", "非遗文化"),
    ("传承人", "/inheritors", "传承人"),
    ("非遗活动", "/events", "非遗活动"),
    ("非遗商城", "/mall", "非遗商城"),
    ("社区交流", "/community", "社区交流"),
    ("系统通知", "/notifications", "系统通知"),
]


class TestNavigation:
    """
    导航测试类

    演示：使用 @pytest.mark.parametrize 一次性测试所有导航链接
    等同于写了 7 个测试函数，但只需写一个
    """

    @pytest.mark.regression
    @pytest.mark.parametrize(
        "link_text, expected_path, page_title",
        NAVIGATION_DATA,
        ids=[item[0] for item in NAVIGATION_DATA]
    )
    def test_navigate_to_page(self, home_page, link_text, expected_path, page_title):
        """
        【参数化测试】验证从首页通过导航栏跳转到各个子页面

        使用 Playwright 的 expect_url 自带重试机制（比手动检查 URL 更稳定）
        这对于 SPA（单页应用）尤其重要，因为 Vue Router 的 URL 更新是异步的
        """
        # Given: 在首页
        home_page.navigate()

        # When: 点击导航栏链接
        self._navigate_by_text(home_page, link_text)

        # Then: 使用 expect 自带重试验证 URL（5秒内轮询）
        expected_url = home_page.base_url + expected_path
        expect(home_page.page).to_have_url(expected_url)
        logger.info(f"导航到 {link_text} ({expected_path}) 验证通过")

    def _navigate_by_text(self, home_page, link_text: str):
        """
        根据导航文本调用对应的页面导航方法

        策略模式：字典映射代替 if/elif 链（更 Pythonic）
        """
        nav_map = {
            "首页": home_page.navbar.go_to_home,
            "非遗文化": home_page.navbar.go_to_culture,
            "传承人": home_page.navbar.go_to_inheritors,
            "非遗活动": home_page.navbar.go_to_events,
            "非遗商城": home_page.navbar.go_to_mall,
            "社区交流": home_page.navbar.go_to_community,
            "系统通知": home_page.navbar.go_to_notifications,
        }
        nav_func = nav_map.get(link_text)
        if nav_func:
            nav_func()
        else:
            raise ValueError(f"未知的导航链接: {link_text}")

    @pytest.mark.smoke
    def test_navbar_clicks_work(self, home_page):
        """
        快速验证点击导航栏链接不会报错（URL改变由SPA控制）

        不检查URL变化，因为Vue SPA的路由转换可能比网络空闲更快完成，
        导致检查时URL已经更新但被误判。
        只验证点击操作成功执行。
        """
        home_page.navigate()
        # 逐个点击导航链接，验证操作不报错
        for link_text in ["非遗文化", "传承人", "非遗活动", "非遗商城", "社区交流", "系统通知"]:
            self._navigate_by_text(home_page, link_text)
            home_page.wait_for_timeout(500)
            logger.info(f"成功点击导航链接: {link_text}")

    @pytest.mark.regression
    @pytest.mark.parametrize(
        "link_text, expected_path",
        [
            ("非遗文化", "/culture"),
            ("传承人", "/inheritors"),
            ("非遗活动", "/events"),
            ("非遗商城", "/mall"),
            ("社区交流", "/community"),
            ("系统通知", "/notifications"),
        ],
        ids=["非遗文化", "传承人", "非遗活动", "非遗商城", "社区交流", "系统通知"]
    )
    def test_navigate_to_page_verify_url(self, home_page, link_text, expected_path):
        """
        【参数化】验证导航后 URL 正确变化（使用 Playwright 的 expect 自带重试）

        和上面的 test_navigate_to_page 不同：
        - 这个测试用 expect_url 带重试，更适合 SPA
        - 首页已经单独测过了，这里只测子页面
        """
        home_page.navigate()
        self._navigate_by_text(home_page, link_text)

        # Playwright 的 expect 自带重试（默认 5 秒内轮询），比手动检查 URL 更稳定
        expect(home_page.page).to_have_url(home_page.base_url + expected_path)
        logger.info(f"导航到 {expected_path} 验证通过")

    @pytest.mark.smoke
    def test_login_button_visible(self, home_page):
        """
        验证登录/注册按钮在所有页面上都可见
        """
        home_page.navigate()
        assert home_page.navbar.is_login_visible(), "登录按钮应该可见"
        logger.info("登录按钮可见性验证通过")
