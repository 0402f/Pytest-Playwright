"""
页面对象基类（BasePage）
======================
这是整个框架的基石，所有页面类都必须继承它。

设计理念：
1. 封装 Playwright 的底层 API，提供更语义化的方法
2. 内置自动等待机制（Playwright 默认开启，我们在此基础上增强）
3. 提供通用操作：点击、输入、获取文本、截图、等待等
4. 子类只需关注页面特有的元素和行为

面试核心考点：
-------------
Q1: 什么是 Page Object Model（POM）？为什么用它？
A: POM 是一种设计模式，将每个页面抽象为一个类：
   - 页面元素定位器 → 类的属性
   - 页面操作行为     → 类的方法
   好处：代码复用、易维护、可读性强。页面改版时只需修改对应 Page 类。

Q2: Playwright 的自动等待机制是什么？和 Selenium 有什么区别？
A: Playwright 在执行操作前会自动等待元素满足条件：
   - click() 自动等待元素可见、可点击
   - fill()  自动等待元素可见、可编辑
   Selenium 需要手动写 WebDriverWait，Playwright 内置了，极大简化代码。

Q3: CSS Selector 和 XPath 怎么选？
A: 优先级：CSS Selector > text 选择器 > XPath
   - CSS: 简洁、浏览器原生支持、速度快
   - XPath: 功能强大（可按文本内容、父子关系定位），但复杂、性能差
   - 实际项目：能用 CSS 就用 CSS，特殊场景（如按文字定位按钮）用 XPath/text

Q4: 什么是显式等待和隐式等待？
A: - 隐式等待：设置全局超时，每次查找元素都等待固定时间（Selenium 概念）
   - 显式等待：针对特定条件等待，更灵活
   Playwright 的自动等待 = 内置的显式等待，每个操作都有默认30秒超时。

Q5: fixture 的 scope 级别有哪些？
A: function(默认-每个测试函数) → class(每个测试类) → module(每个模块) → session(整个测试会话)
   一般用 function 级别保证测试隔离；登录场景可用 session 级别共享状态以提速。
"""

import logging
from pathlib import Path
from typing import Optional
from playwright.sync_api import Page, Locator, expect

from config.settings import settings

# ---- 日志 ----
logger = logging.getLogger("HeritageCraft_UI_Auto")


class BasePage:
    """
    所有页面对象的基类

    Attributes:
        page (Page): Playwright 的 Page 对象，代表一个浏览器标签页
        base_url (str): 基础 URL，来自配置文件

    子类使用示例:
        class HomePage(BasePage):
            def __init__(self, page: Page):
                super().__init__(page)

            def click_login(self):
                self.click(".login-btn")  # 使用基类方法
    """

    def __init__(self, page: Page):
        """
        初始化页面对象

        Args:
            page: Playwright Page 实例（由 pytest-playwright 的 page fixture 注入）
        """
        self.page = page
        self.base_url = settings.base_url
        logger.debug(f"初始化页面对象: {self.__class__.__name__}")

    # ================================================================
    # 导航相关
    # ================================================================

    def navigate(self, path: str = "", wait_until: str = "domcontentloaded") -> None:
        """
        导航到指定页面

        Args:
            path: URL 路径，空字符串表示首页
                 例如: navigate("/culture") → http://host/culture
            wait_until: 导航等待策略
                        - "domcontentloaded": DOM 解析完成即返回（默认，最快）
                        - "load": 等待所有资源加载（图片、CSS等）
                        - "networkidle": 等待网络空闲（适合 AJAX 多的页面）

        面试考点：wait_until 三种策略的区别
        """
        url = f"{self.base_url}{path}"
        logger.info(f"导航到: {url}")
        self.page.goto(url, wait_until=wait_until, timeout=settings.timeout.navigation)

    def reload(self) -> None:
        """刷新当前页面"""
        logger.info("刷新页面")
        self.page.reload()

    def go_back(self) -> None:
        """浏览器后退"""
        logger.info("浏览器后退")
        self.page.go_back()

    def go_forward(self) -> None:
        """浏览器前进"""
        logger.info("浏览器前进")
        self.page.go_forward()

    # ================================================================
    # 元素操作（封装 Playwright API，加上日志和等待）
    # ================================================================

    def click(self, selector: str, timeout: int = None) -> None:
        """
        点击元素（带自动等待）

        Playwright 内部会自动等待元素：
        1. 出现在 DOM 中
        2. 可见（visibility 不为 hidden）
        3. 稳定（不再移动/动画结束）
        4. 可接收事件（不被其他元素遮挡）
        5. 未被禁用（disabled=false）

        Args:
            selector: CSS 选择器或 XPath
            timeout: 超时时间(ms)，默认使用配置值

        面试考点：Playwright 的 actionability checks（可操作性检查）
        """
        timeout = timeout or settings.timeout.element
        logger.debug(f"点击元素: {selector}")
        self.page.locator(selector).click(timeout=timeout)

    def dblclick(self, selector: str, timeout: int = None) -> None:
        """双击元素"""
        timeout = timeout or settings.timeout.element
        logger.debug(f"双击元素: {selector}")
        self.page.locator(selector).dblclick(timeout=timeout)

    def fill(self, selector: str, text: str, timeout: int = None) -> None:
        """
        在输入框中填入文本

        Playwright 的 fill() 和 type() 区别：
        - fill(): 清空后填入（一步完成，快）
        - type(): 逐字符输入（模拟真实键盘，触发 keydown/keyup 事件）

        Args:
            selector: 输入框的选择器
            text: 要填入的文本
            timeout: 超时时间
        """
        timeout = timeout or settings.timeout.element
        logger.info(f"输入文本到 {selector}: '{text}'")
        self.page.locator(selector).fill(text, timeout=timeout)

    def type_text(self, selector: str, text: str, delay: int = 50, timeout: int = None) -> None:
        """
        逐字符输入（模拟真实键盘输入）

        Args:
            selector: 输入框选择器
            text: 要输入的文本
            delay: 每个字符之间的延迟(ms)，模拟人类输入速度
            timeout: 超时时间
        """
        timeout = timeout or settings.timeout.element
        logger.info(f"逐字符输入到 {selector}: '{text}'")
        self.page.locator(selector).type(text, delay=delay, timeout=timeout)

    def clear(self, selector: str, timeout: int = None) -> None:
        """清空输入框"""
        timeout = timeout or settings.timeout.element
        logger.debug(f"清空输入框: {selector}")
        self.page.locator(selector).clear(timeout=timeout)

    def press(self, selector: str, key: str, timeout: int = None) -> None:
        """
        按下键盘按键

        Args:
            selector: 元素选择器
            key: 按键名称，如 "Enter", "Escape", "Tab", "ArrowDown"

        常用按键: Enter, Escape, Tab, Backspace, Delete, ArrowUp/Down/Left/Right
        组合键: "Control+A", "Shift+Tab"
        """
        timeout = timeout or settings.timeout.element
        logger.debug(f"按下 {key} 在元素 {selector}")
        self.page.locator(selector).press(key, timeout=timeout)

    def select_option(self, selector: str, value: str = None, label: str = None, index: int = None, timeout: int = None) -> None:
        """
        在下拉选择框中选择选项

        Args:
            selector: select 元素的选择器
            value: 按 option 的 value 属性选择
            label: 按 option 的显示文本选择
            index: 按选项的索引位置选择（从 0 开始）
            timeout: 超时时间

        三种选择方式只需提供一种：
            select_option("select#city", label="武汉")
            select_option("select#city", value="wuhan")
            select_option("select#city", index=0)
        """
        timeout = timeout or settings.timeout.element
        logger.info(f"选择下拉选项: {selector} (label={label}, value={value}, index={index})")
        locator = self.page.locator(selector)
        if label is not None:
            locator.select_option(label=label, timeout=timeout)
        elif value is not None:
            locator.select_option(value=value, timeout=timeout)
        elif index is not None:
            locator.select_option(index=index, timeout=timeout)

    def check(self, selector: str, timeout: int = None) -> None:
        """勾选复选框/单选框"""
        timeout = timeout or settings.timeout.element
        logger.debug(f"勾选: {selector}")
        self.page.locator(selector).check(timeout=timeout)

    def uncheck(self, selector: str, timeout: int = None) -> None:
        """取消勾选"""
        timeout = timeout or settings.timeout.element
        logger.debug(f"取消勾选: {selector}")
        self.page.locator(selector).uncheck(timeout=timeout)

    def hover(self, selector: str, timeout: int = None) -> None:
        """
        悬停在元素上（常用于触发 tooltip、下拉菜单等）
        """
        timeout = timeout or settings.timeout.element
        logger.debug(f"悬停在: {selector}")
        self.page.locator(selector).hover(timeout=timeout)

    # ================================================================
    # 获取信息
    # ================================================================

    def get_text(self, selector: str) -> str:
        """
        获取元素的文本内容

        注意：inner_text() 只返回可见文本，text_content() 返回全部文本（包括隐藏的）
        inner_text() 更贴近用户实际看到的文字
        """
        logger.debug(f"获取文本: {selector}")
        return self.page.locator(selector).inner_text()

    def get_all_texts(self, selector: str) -> list:
        """
        获取匹配选择器的所有元素的文本列表

        使用场景：获取导航菜单所有项、列表所有标题等
        """
        logger.debug(f"获取所有文本: {selector}")
        return self.page.locator(selector).all_inner_texts()

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        获取元素的属性值

        常用属性: href, src, class, id, value, placeholder, disabled

        Args:
            selector: 元素选择器
            attribute: 属性名
        Returns:
            属性值，不存在返回 None
        """
        logger.debug(f"获取属性: {selector}.{attribute}")
        return self.page.locator(selector).get_attribute(attribute)

    def get_input_value(self, selector: str) -> str:
        """获取输入框的当前值"""
        return self.page.locator(selector).input_value()

    def count(self, selector: str) -> int:
        """统计匹配选择器的元素数量"""
        return self.page.locator(selector).count()

    # ================================================================
    # 状态判断
    # ================================================================

    def is_visible(self, selector: str, timeout: int = None) -> bool:
        """
        判断元素是否可见

        注意：这是"等待可见"的包装，如果元素一直不可见会等超时！
        如果想要快速判断（不等），用 is_visible_quick()
        """
        timeout = timeout or settings.timeout.element
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def is_visible_quick(self, selector: str) -> bool:
        """
        快速判断元素是否可见（不等待）

        适合检查"不该出现"的元素（如错误提示是否消失了）
        """
        try:
            # 设置超时为0，立即返回
            self.page.locator(selector).wait_for(state="visible", timeout=1000)
            return True
        except Exception:
            return False

    def is_hidden(self, selector: str) -> bool:
        """判断元素是否隐藏"""
        try:
            self.page.locator(selector).wait_for(state="hidden", timeout=settings.timeout.element)
            return True
        except Exception:
            return False

    def is_enabled(self, selector: str) -> bool:
        """判断元素是否可用（未被禁用）"""
        return self.page.locator(selector).is_enabled()

    def is_checked(self, selector: str) -> bool:
        """判断复选框/单选框是否已选中"""
        return self.page.locator(selector).is_checked()

    # ================================================================
    # 等待策略（显式等待）
    # ================================================================

    def wait_for_element(self, selector: str, state: str = "visible", timeout: int = None) -> None:
        """
        显式等待元素达到指定状态

        Args:
            selector: 元素选择器
            state: 等待状态
                   - "visible": 元素可见（默认）
                   - "hidden":  元素隐藏
                   - "attached": 元素在 DOM 中（不一定可见）
                   - "detached": 元素从 DOM 中移除
            timeout: 超时时间

        面试考点：什么时候需要显式等待？
        - 动态内容加载（AJAX 请求后渲染）
        - 动画完成后操作
        - 页面跳转后等待特定元素
        """
        timeout = timeout or settings.timeout.element
        logger.debug(f"等待元素 {selector} 状态={state} (超时={timeout}ms)")
        self.page.locator(selector).wait_for(state=state, timeout=timeout)

    def wait_for_timeout(self, milliseconds: int) -> None:
        """
        固定时间等待（不推荐频繁使用）

        面试考点：为什么避免固定等待？
        - 浪费时间：网络快时不需要等那么久
        - 不稳定：网络慢时可能等不够
        - 尽量用 wait_for_element() 等基于条件的等待

        仅在以下场景使用：
        - 调试时临时加
        - 等待第三方动画播放
        - 等待不受我们控制的定时任务
        """
        logger.debug(f"固定等待 {milliseconds}ms")
        self.page.wait_for_timeout(milliseconds)

    def wait_for_load_state(self, state: str = "networkidle") -> None:
        """
        等待页面加载状态

        Args:
            state: "load" | "domcontentloaded" | "networkidle"
        """
        logger.info(f"等待页面加载状态: {state}")
        self.page.wait_for_load_state(state)

    # ================================================================
    # 截图
    # ================================================================

    def take_screenshot(self, name: str = None, full_page: bool = True) -> str:
        """
        截取当前页面截图

        Args:
            name: 截图文件名（不含扩展名），默认用时间戳
            full_page: 是否截取整页（True=全页，False=仅视口）

        Returns:
            截图文件路径

        面试考点：全页截图 vs 视口截图的使用场景
        - 全页：需要看完整页面内容（报告、长列表）
        - 视口：关注用户实际看到的范围（UI 布局验证）
        """
        if name is None:
            from datetime import datetime
            name = datetime.now().strftime("%Y%m%d_%H%M%S")

        screenshot_dir = Path(settings.screenshot.dir)
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        filepath = screenshot_dir / f"{name}.png"
        self.page.screenshot(path=str(filepath), full_page=full_page)
        logger.info(f"截图已保存: {filepath}")
        return str(filepath)

    # ================================================================
    # JavaScript 执行
    # ================================================================

    def execute_js(self, script: str, *args) -> any:
        """
        在浏览器中执行 JavaScript 代码

        使用场景：
        - 滚动到指定位置: execute_js("window.scrollTo(0, 500)")
        - 获取浏览器信息: execute_js("return navigator.userAgent")
        - 修改元素属性: execute_js("document.querySelector('.modal').remove()")

        面试考点：什么时候需要执行 JS？
        - Playwright API 无法直接操作时（如修改 Canvas）
        - 需要绕过某些交互限制时
        - 获取浏览器级别的信息时
        """
        logger.debug(f"执行 JS: {script[:80]}...")
        return self.page.evaluate(script, *args)

    def scroll_to(self, selector: str = None, x: int = 0, y: int = 0) -> None:
        """
        滚动页面

        Args:
            selector: 滚动到该元素位置（优先级最高）
            x: 水平滚动像素
            y: 垂直滚动像素
        """
        if selector:
            logger.debug(f"滚动到元素: {selector}")
            self.page.locator(selector).scroll_into_view_if_needed()
        else:
            logger.debug(f"滚动到坐标: ({x}, {y})")
            self.page.evaluate(f"window.scrollTo({x}, {y})")

    # ================================================================
    # 弹窗处理
    # ================================================================

    def accept_alert(self) -> str:
        """
        接受（点击确定）浏览器弹窗

        Playwright 自动处理 dialog，默认是 dismiss（取消）
        如需接受，需提前设置监听

        Returns:
            弹窗文本内容
        """
        dialog_message = []

        def handle_dialog(dialog):
            dialog_message.append(dialog.message)
            logger.info(f"接受弹窗: {dialog.message}")
            dialog.accept()

        self.page.on("dialog", handle_dialog)
        return dialog_message[0] if dialog_message else ""

    def dismiss_alert(self) -> str:
        """取消（点击取消）浏览器弹窗"""
        dialog_message = []

        def handle_dialog(dialog):
            dialog_message.append(dialog.message)
            logger.info(f"取消弹窗: {dialog.message}")
            dialog.dismiss()

        self.page.on("dialog", handle_dialog)
        return dialog_message[0] if dialog_message else ""


    # ================================================================
    # 断言辅助（让测试代码更语义化）
    # ================================================================

    def expect_visible(self, selector: str, message: str = "", strict: bool = False) -> None:
        """
        断言元素可见

        Args:
            selector: 元素选择器
            message: 失败时的自定义消息
            strict: 是否严格模式。True=选择器必须匹配恰好1个元素，False=至少匹配1个即可
                    默认 False，因为大多数页面有多个同类元素

        面试考点：Playwright 的 strict mode
        - strict=True: 要求 locator 恰好匹配 1 个元素（默认行为）
        - 如果匹配到多个元素，会抛出 strict mode violation 错误
        - 需要匹配多个元素时，用 .first / .nth() / .all() 或 strict=False
        """
        msg = message or f"元素应该可见: {selector}"
        locator = self.page.locator(selector)
        if strict:
            expect(locator).to_be_visible()
        else:
            # 非严格模式：检查第一个匹配的元素是否可见
            expect(locator.first).to_be_visible()

    def expect_hidden(self, selector: str, message: str = "") -> None:
        """断言元素隐藏（匹配第一个匹配到的元素）"""
        msg = message or f"元素应该隐藏: {selector}"
        expect(self.page.locator(selector).first).to_be_hidden()

    def expect_text(self, selector: str, text: str, message: str = "") -> None:
        """断言元素包含指定文本（匹配第一个匹配到的元素）"""
        msg = message or f"元素 {selector} 应包含文本: {text}"
        expect(self.page.locator(selector).first).to_contain_text(text)

    def expect_title(self, title: str, message: str = "") -> None:
        """断言页面标题"""
        msg = message or f"页面标题应为: {title}"
        expect(self.page).to_have_title(title)

    def expect_url(self, url: str, message: str = "") -> None:
        """断言当前 URL 包含指定字符串"""
        msg = message or f"URL 应包含: {url}"
        expect(self.page).to_have_url(url)

    def expect_count(self, selector: str, count: int, message: str = "") -> None:
        """断言元素数量"""
        msg = message or f"元素 {selector} 数量应为 {count}"
        expect(self.page.locator(selector)).to_have_count(count)
