# 🎤 测试开发面试高频问答

> 基于本框架涉及的知识点，按出现频率整理。每个问题都配有"面试怎么回答"和"代码在哪里体现"。

---

## 一、自动化测试基础

### Q1: 什么是自动化测试？和手工测试的关系？

**回答思路：**
- 自动化测试 = 用代码/工具模拟用户操作，自动验证结果
- 不是替代手工测试，而是补充——自动化测回归/重复的，手工测探索性/一次性的
- 经典比例：70%手工 + 30%自动（因项目而异）

**框架中的体现：** 整个 tests/ 目录就是用代码模拟用户访问 HeritageCraft 各个页面。


### Q2: 什么是 UI 自动化？它的优缺点？

**回答：**
- UI 自动化 = 模拟用户在浏览器上的操作（点击、输入、滚动等）
- 优点：最接近真实用户、可发现前端+后端集成问题
- 缺点：执行慢、维护成本高、UI 变化容易导致失败

**框架中的体现：** 整个框架就是 UI 自动化框架——用 Playwright 控制浏览器访问网站，验证页面元素。


### Q3: 一个完整的自动化测试用例包含哪些部分？

**回答（AAA 模式）：**
- **Arrange（准备）**：设置测试数据和前置条件
- **Act（执行）**：执行被测操作
- **Assert（断言）**：验证结果是否符合预期

```python
# 框架中的例子（test_home.py）
def test_page_loads_successfully(self, home_page):
    # Arrange: 用户访问首页
    home_page.navigate()

    # Act & Assert: 核心元素应该可见
    home_page.expect_page_loaded()
    assert home_page.page.title() == "HeritageCraft"
```


---

## 二、Playwright 专项

### Q4: Playwright 和 Selenium 有什么区别？为什么选 Playwright？

**回答（高频！）：**

| 对比项 | Playwright | Selenium |
|--------|-----------|----------|
| 自动等待 | ✅ 内置（操作前自动等元素可交互） | ❌ 需手动写 WebDriverWait |
| 多浏览器 | Chromium/Firefox/WebKit | Chrome/Firefox/Safari/IE |
| 网络拦截 | ✅ 原生支持 | ❌ 需第三方 |
| 多标签页 | ✅ 原生 Context 隔离 | ❌ 切换窗口 |
| 速度 | 快（WebSocket 协议） | 慢（HTTP 协议） |
| 社区 | 较新但发展快 | 老牌但臃肿 |

**补充说：** "Playwright 的自动等待机制让代码更简洁，不需要到处写 sleep 和 wait，这也是选择它的主要原因。"

**框架中的体现：** `pages/base_page.py` 中的 `click()`, `fill()` 方法都享受 Playwright 的自动等待。


### Q5: Browser、Context、Page 三者什么关系？

**回答（必考题！）：**

```
Browser（浏览器进程）  ← 一个 Chrome/Firefox 实例
  ├── Context 1（隔离会话） ← 类似"隐身窗口"
  │   ├── Page 1（标签页）
  │   └── Page 2（标签页）
  └── Context 2（隔离会话）
      ├── Page 3（标签页）
      └── Page 4（标签页）
```

- **Browser**：一个浏览器进程，启动慢、占内存
- **Context**：一个隔离的浏览会话，不同 Context 的 cookies/storage 完全独立
- **Page**：一个标签页

**面试说：** "我们用 session 级别的 browser fixture（整个测试只启动一次），function 级别的 context fixture（每个测试独立隔离），既保证速度又保证隔离性。"

**框架中的体现：** `tests/conftest.py` 中 `browser`（session 级别）、`context`（function 级别）、`page`（function 级别）的 fixture 链。


### Q6: Playwright 的自动等待机制是什么？包含哪些检查？

**回答：**
Playwright 在执行 click/fill 等操作前，会自动等待元素满足以下条件（actionability checks）：
1. **Attached**：元素存在于 DOM
2. **Visible**：元素可见（display 不为 none，visibility 不为 hidden）
3. **Stable**：元素不再动画/移动中
4. **Receives Events**：不被其他元素遮挡
5. **Enabled**：未被禁用

**加上面试官喜欢的说法：** "这意味着我们不用像 Selenium 那样写一大堆 WebDriverWait，代码量减少 30-50%，稳定性反而更高。"

**框架中的体现：** `pages/base_page.py` 中 `click()` 方法的注释详细列出了这 5 个检查。


### Q7: wait_for_load_state 的三种状态怎么选？

**回答：**
- `domcontentloaded`：HTML 解析完成就返回（最快，适合静态页面）
- `load`：等待所有资源加载（图片、CSS、JS，适合需要完整渲染的页面）
- `networkidle`：网络连接空闲（适合 AJAX 多的 SPA 应用，等数据加载完）

**面试说：** "我们的 HeritageCraft 是 Vue.js 单页应用，数据通过 API 动态加载，所以主要用 networkidle。"

**框架中的体现：** `pages/home_page.py` → `_navigate_to()` → `wait_until="networkidle"`


---

## 三、设计模式

### Q8: 什么是 Page Object Model（POM）？为什么要用？

**回答（超高频！）：**
POM 是一种设计模式，把每个页面抽象为一个类：
- **页面元素** → 类的属性（定位器）
- **页面行为** → 类的方法

**好处：**
1. **易维护**：页面改版，只改 Page 类
2. **复用性**：多个测试共用同一个 Page 方法
3. **可读性**：测试代码像自然语言 `home_page.click_login()`
4. **职责分离**：页面逻辑 vs 测试逻辑

**框架中的体现：** 整个 `pages/` 目录，所有页面类都继承 `BasePage`。


### Q9: 为什么用"组合"而不是"继承"来引入导航栏和页脚？

**回答：**
- 继承（is-a）："导航栏是一种页面" → 逻辑不对
- 组合（has-a）："页面有导航栏" → 逻辑正确

```python
# 组合方式（框架使用的方式）
class HomePage(BasePage):
    def __init__(self, page):
        self.navbar = Navbar(page)   # "有" 导航栏
        self.footer = Footer(page)   # "有" 页脚

# vs 继承方式（不好）
class HomePage(BasePage, NavbarMixin):
    # 导航栏"是"页面的一部分 → 逻辑不通
```

**框架中的体现：** `pages/home_page.py` 中使用 `self.navbar = Navbar(page)`


### Q10: BasePage 基类应该包含哪些方法？

**回答：**
- **导航类**：navigate, reload, go_back
- **操作类**：click, dblclick, fill, type_text, select_option, check, hover
- **信息类**：get_text, get_all_texts, get_attribute, count
- **判断类**：is_visible, is_hidden, is_enabled, is_checked
- **等待类**：wait_for_element, wait_for_load_state, wait_for_timeout
- **截图类**：take_screenshot
- **JS类**：execute_js, scroll_to
- **断言类**：expect_visible, expect_text, expect_title, expect_url

**面试说：** "不要过度设计，20-30 个方法足够覆盖 90% 的场景。实在需要特殊操作的，直接在子页面类写。"

**框架中的体现：** `pages/base_page.py` 包含了所有这些方法。


---

## 四、pytest 专项

### Q11: Fixture 是什么？和 setup/teardown 有什么区别？

**回答（高频！）：**
Fixture 是 pytest 的依赖注入机制，比传统的 setup/teardown 更强大：
- 可以嵌套（一个 fixture 依赖另一个）
- 有 scope 级别（function/class/module/session）
- yield 替代 setup/teardown（更 Pythonic）
- 可以参数化

```python
@pytest.fixture
def page(context):
    page = context.new_page()   # ← setup（测试前）
    yield page                  # ← 给测试用
    page.close()                # ← teardown（测试后，一定执行）
```

**框架中的体现：** `tests/conftest.py` 中 browser → context → page 的 fixture 链。


### Q12: fixture 的 scope 有哪些？怎么选？

**回答：**
- `function`（默认）：每个测试函数一次 → 最安全，推荐
- `class`：每个测试类一次 → 类内共享
- `module`：每个 .py 文件一次 → 模块内共享
- `session`：整个测试会话一次 → 最省资源

**选择原则：**
- browser → session（启动一次，太慢了）
- context → function（保证隔离）
- page → function（保证隔离）

**面试说：** "session 级别省时间，function 级别保证隔离。浏览器启动慢用 session，页面状态用 function 避免污染。"

**框架中的体现：** `tests/conftest.py` 中 browser 是 session，context 和 page 是 function。


### Q13: conftest.py 的作用范围和层级覆盖？

**回答：**
conftest.py 的作用域是"当前目录 + 所有子目录"。如果多层目录都有 conftest.py：
- 内层的 fixture 覆盖外层的同名 fixture
- 外层的 fixture 内层也能用

```
project/
├── conftest.py          ← 影响整个项目
├── tests/
│   ├── conftest.py      ← 影响 tests/ 下所有
│   └── module/
│       └── conftest.py  ← 只影响 module/ 下
```


### Q14: @pytest.mark.parametrize 怎么用？什么场景用？

**回答：**
参数化测试 = 同一个测试逻辑，不同输入数据跑多次。

**使用场景：**
1. 多浏览器兼容性测试
2. 多搜索关键词验证
3. 多导航链接验证

```python
# 框架中的例子
@pytest.mark.parametrize("keyword", ["武当武术", "汉绣", "黄梅戏"])
def test_search(keyword):
    culture_page.search(keyword)
    assert culture_page.get_card_count() > 0
```

**面试说：** "参数化的好处是减少重复代码、新增数据只需加一行、'一个失败不影响其他'。这是数据驱动测试的核心实现方式。"

**框架中的体现：** `tests/test_navigation.py`、`tests/test_culture.py`、`tests/test_mall.py`


### Q15: @pytest.mark.skip 和 @pytest.mark.xfail 的区别？

**回答：**
- `skip`：不执行该测试（无条件跳过 or 条件跳过）
  - 场景：功能未完成、环境不支持、某浏览器暂不支持
- `xfail`：执行测试但预期失败
  - 场景：已知 bug 未修复、第三方 API 不稳定
  - 如果 xfail 的测试通过了 → XPASS（警告）
  - 如果 xfail 的测试失败了 → XFAIL（预期内）

**框架中的体现：** `tests/test_events.py` 中 `test_full_registration_flow` 用了 skip，`tests/test_mall.py` 中 `test_collect_product` 用了 xfail。


### Q16: pytest 的标记（markers）怎么用？

**回答：**
标记用于给测试分类，然后按分类运行：
```bash
pytest -m smoke        # 只跑冒烟测试
pytest -m "not slow"   # 排除慢速测试
pytest -m "smoke or regression"  # 冒烟或回归
```

**需要在 pytest.ini 中注册**（否则会有 warning）：
```ini
[pytest]
markers =
    smoke: 冒烟测试
    regression: 回归测试
    slow: 慢速测试
```

**框架中的体现：** `pytest.ini` 中定义了所有标记。


---

## 五、框架设计

### Q17: 从零搭建自动化测试框架，你会怎么做？

**回答思路（展示架构思维）：**
1. **需求分析**：被测系统是什么？什么架构？（Web/App/API）
2. **技术选型**：语言+工具+测试框架（Python+Playwright+pytest）
3. **目录结构设计**：pages/tests/config/utils/data/reports
4. **核心实现**：BasePage → 各页面对象 → fixtures → 测试用例
5. **增强功能**：日志、截图、报告、重试、并行
6. **CI/CD 集成**：Jenkins/GitHub Actions 自动运行

**配合说：** "这个 HeritageCraft 框架就是按照这个思路搭建的，你可以看项目的提交历史。"


### Q18: 如何提高自动化测试的稳定性？

**回答（面试官爱听！）：**
1. **用显式等待替代固定 sleep**（Playwright 已自动实现）
2. **测试数据独立**：每个测试用自己的数据，用完清理
3. **失败重试机制**：pytest-rerunfailures 重试 2 次
4. **失败截图 + 日志**：快速定位问题
5. **TestCase 原子性**：一个测试只测一件事
6. **环境一致性**：用 Docker 统一执行环境

**框架中的体现：** conftest.py 的失败截图、context 隔离、logger 日志。


### Q19: 自动化测试在 CI/CD 中怎么集成？

**回答：**
```yaml
# GitHub Actions 示例
- name: Run E2E Tests
  run: |
    pip install -r requirements.txt
    playwright install chromium --with-deps
    pytest tests/ --headless -v --html=reports/report.html
- name: Upload Report
  uses: actions/upload-artifact@v3
  with:
    name: test-report
    path: reports/
```

**关键点：** CI 环境用 headless 模式；失败时上传截图和报告作为 artifact。


### Q20: 如何处理验证码、扫码登录？

**回答（考察解决难题的能力）：**
- **方案1（开发配合）**：测试环境去掉验证码，或设置万能验证码
- **方案2（cookie 注入）**：预先登录获取 cookie，测试时注入跳过登录
- **方案3（API 模拟）**：直接调用登录 API 获取 token，set 到 localStorage
- **不推荐**：OCR 识别验证码（不稳定，维护成本高）


---

## 六、Python / 代码设计

### Q21: Python 的 yield 在 fixture 中是什么意思？

**回答：**
yield 把函数分成两部分，是生成器（generator）的特殊用法：
- yield 前 = setup（测试前执行）
- yield 后 = teardown（测试后一定执行，即使测试失败）

```python
@pytest.fixture
def browser():
    b = launch_browser()   # setup
    yield b                # 给测试用
    b.close()              # teardown（一定执行）
```

### Q22: 什么是单例模式？框架中哪里用了？

**回答：**
单例 = 全局只有一个实例。适合创建成本高、需要共享的对象。

框架中 `config/settings.py` 的 `settings` 对象就是单例的简化版：
```python
settings = Settings()  # 模块级，导入时只创建一次
```

---

## 💡 面试加分小技巧

1. **展示框架截图/结构图**：比纯说更直观
2. **主动提及 CI/CD**：说明你有"测试集成到开发流程"的意识
3. **能讲出 trade-off**：比如"基类方法不是越多越好，20个足够"
4. **准备好"踩坑经历"**：比如 CSS 选择器 vs XPath 的选择经验
5. **说出数据驱动 vs 关键字驱动**的区别
6. **提到 Allure 报告**：比 pytest-html 更专业
