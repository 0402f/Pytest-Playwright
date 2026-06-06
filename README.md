# 🏯 HeritageCraft UI 自动化测试框架

> 基于 **Playwright + Python + pytest** 的 UI 自动化测试框架，专为初学者设计。

## 📚 适合谁看？

- 想学习 UI 自动化测试的 **测试工程师**
- 正在准备 **测试面试** 的同学（框架中标注了面试考点）
- 需要快速搭建自动化测试项目的团队

## 🏗️ 框架架构

```
Playwright/
├── config/              配置文件（URL、浏览器、超时等）
│   ├── config.yaml      所有可配置项集中管理
│   └── settings.py      加载 YAML 配置
├── pages/               页面对象层（POM 核心）
│   ├── base_page.py     ★ 基类，封装所有通用操作
│   ├── home_page.py     首页
│   ├── culture_page.py  非遗文化页
│   ├── inheritors_page.py  传承人页
│   ├── events_page.py   非遗活动页
│   ├── mall_page.py     非遗商城页
│   ├── community_page.py  社区交流页
│   └── notifications_page.py  系统通知页
├── components/          可复用 UI 组件
│   ├── navbar.py        导航栏
│   └── footer.py        页脚
├── tests/               测试用例层
│   ├── conftest.py      ★ pytest 配置 + fixtures + 失败截图
│   ├── test_home.py     首页测试
│   ├── test_navigation.py 导航测试（参数化示例）
│   ├── test_culture.py  非遗文化页测试
│   ├── test_events.py   活动页测试
│   ├── test_mall.py     商城页测试
│   └── test_community.py  社区+通知页测试
├── utils/               工具层
│   ├── logger.py        日志工具
│   └── data_loader.py   测试数据加载
├── data/
│   └── test_data.yaml   测试数据（数据驱动）
├── reports/             测试报告输出
├── logs/                日志文件输出
├── screenshots/         失败截图输出
├── pytest.ini           pytest 配置
├── requirements.txt     依赖包
├── run_tests.py         一键运行脚本
├── README.md            本文档
└── INTERVIEW_QA.md      ★ 面试高频问答
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux

# 安装依赖包
pip install -r requirements.txt

# 安装 Playwright 浏览器（首次使用）
playwright install chromium
```

### 2. 运行测试

```bash
# 方式一：一键运行（推荐新手使用）
python run_tests.py                    # 全部测试
python run_tests.py --smoke            # 仅冒烟测试
python run_tests.py --report           # 生成 HTML 报告
python run_tests.py --headless         # 无头模式

# 方式二：直接用 pytest（更灵活）
pytest tests/ -v                                 # 全部测试
pytest tests/ -v -m smoke                        # 冒烟测试
pytest tests/ -v -k "test_navigate"              # 按关键字筛选
pytest tests/ -v --html=reports/report.html      # 生成报告
```

### 3. 查看结果

- **控制台输出**：测试通过/失败实时显示
- **失败截图**：`screenshots/` 目录下自动保存
- **运行日志**：`logs/YYYYMMDD_test_run.log`
- **HTML 报告**：`reports/report.html`（浏览器打开）

## 📖 核心设计模式

### Page Object Model (POM)

```
页面 = 类（Page Object）
页面元素 = 类的属性
页面操作 = 类的方法

好处：
- 页面改版 → 只改 Page 类，测试代码不动
- 测试代码像"自然语言"一样可读
```

### 组件化

```
导航栏 = Navbar 组件（components/navbar.py）
页脚   = Footer 组件（components/footer.py）

页面使用组件 = 组合（has-a），不是继承（is-a）
```

### 数据驱动

```python
# 同一测试，不同数据，跑 N 次
@pytest.mark.parametrize("keyword", ["武当武术", "汉绣", "黄梅戏"])
def test_search(keyword):
    culture_page.search(keyword)
    assert culture_page.get_card_count() > 0
```

## 🧪 测试标记说明

| 标记 | 用途 | 运行命令 |
|------|------|---------|
| `@pytest.mark.smoke` | 冒烟测试 - 核心功能 | `-m smoke` |
| `@pytest.mark.regression` | 回归测试 - 完整功能 | `-m regression` |
| `@pytest.mark.slow` | 慢速测试 - 耗时较长 | `-m slow` |

## 🎯 学习路径（给初学者）

1. **先看架构图**：理解每层职责
2. **读 base_page.py**：所有框架的基础，注释最详细
3. **读 conftest.py**：理解 fixture 链和失败截图机制
4. **读 test_navigation.py**：参数化测试的最佳示例
5. **读 home_page.py**：看 POM 如何落地
6. **读 INTERVIEW_QA.md**：准备面试

## ⚙️ 配置说明

编辑 `config/config.yaml` 可以修改：
- `base_url`：测试网站地址
- `browser.type`：chromium / firefox / webkit
- `browser.headless`：是否隐藏浏览器窗口
- `timeout.default`：默认超时时间（毫秒）

## 📋 常见问题

**Q: 浏览器没有打开？**
A: 检查 `config.yaml` 中 `browser.headless` 是否为 `false`

**Q: 测试超时了？**
A: 增大 `config.yaml` 中 `timeout` 相关配置

**Q: 如何只跑一个测试？**
A: `pytest tests/test_home.py::TestHomePage::test_page_loads_successfully -v`

---

📝 面试相关请查看 [INTERVIEW_QA.md](./INTERVIEW_QA.md)
