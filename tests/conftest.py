"""
pytest 配置文件（conftest.py）
=============================
这是 pytest 的特殊文件，pytest 会自动发现并加载它。
它定义了：
1. 自定义命令行选项
2. Fixtures（测试夹具）- 为测试提供浏览器、页面等资源
3. Hooks（钩子函数）- 在测试生命周期的特定节点执行逻辑

面试考点汇总：
---------------
Q1: conftest.py 是什么？作用范围是什么？
A: conftest.py 是 pytest 的"本地配置 + 插件"文件。
   作用范围是级联的 → 当前目录及所有子目录下的测试都能用。
   如果多级目录都有 conftest.py，内层的会覆盖外层的同名 fixture。

Q2: fixture 是什么？和 setup/teardown 有什么区别？
A: fixture 是 pytest 的"依赖注入"机制，比 setup/teardown 更灵活：
   - 可以嵌套引用（一个 fixture 依赖另一个）
   - 有 scope 级别（function/class/module/session）
   - 可以用 yield 实现 teardown（yield 前的代码是 setup，后的是 teardown）
   - 可以参数化

Q3: yield 在 fixture 中是什么意思？
A: yield 把 fixture 拆成两部分：
   - yield 之前 = setup（测试前执行）
   - yield 之后 = teardown（测试后执行，无论测试通过还是失败都会执行）

Q4: pytest_runtest_makereport 这个 hook 是什么？
A: 它是 pytest 提供的一个钩子函数，在 **每个测试阶段结束时** 被调用。
   三个阶段：setup / call / teardown。
   我们利用它在 call 阶段检查测试是否失败，失败就自动截图。

Q5: 为什么不自己写 browser fixture，而是用 pytest-playwright 的？
A: pytest-playwright 插件已经提供了 browser、context、page 等 fixture，
   并且支持 --browser、--headless 等命令行参数。
   我们只需要 "Override"（覆盖）部分 fixture 来注入自定义配置，
   而不是重新发明轮子。
"""

import pytest
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page, Browser, BrowserContext

from config.settings import settings
from utils.logger import logger


# ================================================================
# 自定义命令行选项
# 注意：pytest-playwright 已自带 --browser、--headless，
#       我们只加插件没有的选项
# ================================================================

def pytest_addoption(parser):
    """
    注册自定义命令行参数（pytest-playwright 已有的不再重复注册）

    pytest-playwright 自带的：
      --browser=chromium  选择浏览器
      --headed            有头模式
      --headless          无头模式

    用法:
        pytest --base-url=http://xxx  # 临时切换目标服务器
    """
    parser.addoption(
        "--target-url",
        action="store",
        default=settings.base_url,
        help=f"被测试网站的 base URL（默认: {settings.base_url}）"
    )


# ================================================================
# Override pytest-playwright 的 browser fixture
# 改为 session 级别（默认是 function），提升性能
# ================================================================

@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig):
    """
    【Session 级别】给 pytest-playwright 的 browser 提供启动参数

    pytest-playwright 会自动读取这个 fixture 来控制浏览器启动方式。
    我们通过覆盖它来注入慢放速度（调试用）。
    """
    return {
        "headless": pytestconfig.getoption("--headless", default=settings.browser.headless),
        "slow_mo": settings.timeout.slow_motion,
    }


@pytest.fixture(scope="session")
def browser(browser_type, browser_type_launch_args):
    """
    【Session 级别】覆盖 pytest-playwright 默认的 function 级别 browser

    整个测试会话只启动一次浏览器 → 节省大量时间（浏览器启动要 1-3 秒）
    每个测试的隔离由 context 层面保证
    """
    logger.info(f"启动浏览器: {browser_type} (headless={browser_type_launch_args.get('headless')})")
    # pytest-playwright 的 browser_type 返回已连接的 Playwright 实例
    # 直接调用 launch 方法
    browser = browser_type.launch(**browser_type_launch_args)
    logger.info(f"浏览器启动成功")

    yield browser

    logger.info("关闭浏览器")
    browser.close()


# ================================================================
# Override context：注入视口大小、base_url 等自定义配置
# ================================================================

@pytest.fixture
def context(browser: Browser, pytestconfig):
    """
    【Function 级别】为每个测试创建独立的浏览器上下文（隔离的"隐身窗口"）

    面试考点：为什么 Context 用 function 级别？
    - 保证测试隔离：每个测试的 cookies/localStorage 独立
    - A 测试的登录态不影响 B 测试
    """
    base_url = pytestconfig.getoption("--target-url", default=settings.base_url)

    context = browser.new_context(
        viewport={
            "width": settings.browser.viewport.width,
            "height": settings.browser.viewport.height
        },
        ignore_https_errors=settings.browser.ignore_https_errors,
        locale=settings.browser.locale,
        base_url=base_url,
    )
    logger.debug(f"创建浏览器上下文 (base_url={base_url})")

    yield context

    logger.debug("关闭浏览器上下文")
    context.close()


# ================================================================
# page fixture：由 pytest-playwright 自动提供，我们无需覆盖
# 但我们可以覆盖它来添加额外的初始化逻辑
# ================================================================

@pytest.fixture
def page(context: BrowserContext):
    """
    【Function 级别】为每个测试创建新页面

    pytest-playwright 自带 page fixture，这里覆盖是为了：
    1. 添加日志
    2. 保证和自定义 context 的衔接
    """
    page = context.new_page()
    logger.debug(f"创建新页面")

    yield page

    logger.debug(f"关闭页面")
    page.close()


# ================================================================
# 自动截图 Hook（面试常考）
# ================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试失败时自动截图

    执行时机：每个测试的每个阶段结束时
    - setup: 准备阶段
    - call:  测试执行阶段
    - teardown: 清理阶段
    """
    outcome = yield
    report = outcome.get_result()

    # 只在测试执行阶段（call）且失败时截图
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page", None)
        if page:
            test_name = item.nodeid.replace("::", "_").replace("/", "_")
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"FAILED_{test_name}_{timestamp}"

            screenshot_dir = Path(settings.screenshot.dir)
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            filepath = screenshot_dir / f"{filename}.png"

            page.screenshot(path=str(filepath), full_page=settings.screenshot.full_page)
            logger.info(f"!! 测试失败，截图已保存: {filepath}")


# ================================================================
# 自定义 Fixture：注入 Page Object（让测试代码更简洁）
# ================================================================

@pytest.fixture
def home_page(page: Page):
    """首页 Page Object"""
    from pages.home_page import HomePage
    return HomePage(page)


@pytest.fixture
def culture_page(page: Page):
    """非遗文化页 Page Object"""
    from pages.culture_page import CulturePage
    return CulturePage(page)


@pytest.fixture
def inheritors_page(page: Page):
    """传承人页 Page Object"""
    from pages.inheritors_page import InheritorsPage
    return InheritorsPage(page)


@pytest.fixture
def events_page(page: Page):
    """非遗活动页 Page Object"""
    from pages.events_page import EventsPage
    return EventsPage(page)


@pytest.fixture
def mall_page(page: Page):
    """非遗商城页 Page Object"""
    from pages.mall_page import MallPage
    return MallPage(page)


@pytest.fixture
def community_page(page: Page):
    """社区交流页 Page Object"""
    from pages.community_page import CommunityPage
    return CommunityPage(page)


@pytest.fixture
def notifications_page(page: Page):
    """系统通知页 Page Object"""
    from pages.notifications_page import NotificationsPage
    return NotificationsPage(page)
