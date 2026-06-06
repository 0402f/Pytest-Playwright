"""
一键运行测试脚本
===============
为初学者提供简单的测试运行入口，不用记住复杂的命令行参数。

用法：
    python run_tests.py                     # 运行全部测试
    python run_tests.py --smoke             # 只跑冒烟测试
    python run_tests.py --headless          # 无头模式（CI/CD用）
    python run_tests.py --file test_home    # 只跑指定文件
    python run_tests.py --browser firefox   # 切换浏览器
"""

import subprocess
import sys
import argparse
from pathlib import Path


# ---- 项目根目录 ----
PROJECT_ROOT = Path(__file__).parent


def run_pytest(args: list) -> int:
    """
    执行 pytest 命令

    Args:
        args: pytest 命令行参数列表

    Returns:
        退出码（0=成功，非0=失败）
    """
    # 构建完整的 pytest 命令
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",                    # 测试目录
        "-v",                        # 详细输出
        "-s",                        # 允许 print 输出
        "--tb=short",                # 简短的回溯信息
    ] + args

    print(f"\n{'='*60}")
    print(f"执行命令: {' '.join(cmd)}")
    print(f"{'='*60}\n")

    # 执行命令，实时输出结果
    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        # 不捕获输出，让 pytest 直接输出到控制台
    )
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="HeritageCraft UI 自动化测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python run_tests.py                        # 运行全部测试
  python run_tests.py --smoke                # 只跑冒烟测试（核心功能）
  python run_tests.py --regression           # 跑回归测试
  python run_tests.py --headless             # 无头模式（后台运行）
  python run_tests.py --file test_home       # 跑指定文件
  python run_tests.py --report               # 生成 HTML 报告
  python run_tests.py --smoke --headless     # 无头冒烟测试（CI推荐）
        """
    )

    # ---- 运行模式 ----
    parser.add_argument(
        "--smoke", action="store_true",
        help="只运行冒烟测试（核心功能快速验证）"
    )
    parser.add_argument(
        "--regression", action="store_true",
        help="运行回归测试（完整功能验证）"
    )
    parser.add_argument(
        "--slow", action="store_true",
        help="包含慢速测试"
    )

    # ---- 浏览器配置 ----
    parser.add_argument(
        "--headless", action="store_true",
        help="无头模式（不显示浏览器窗口）"
    )
    parser.add_argument(
        "--browser", default="chromium",
        choices=["chromium", "firefox", "webkit"],
        help="浏览器类型（默认: chromium）"
    )

    # ---- 文件选择 ----
    parser.add_argument(
        "--file", type=str,
        help="只运行指定的测试文件（如 test_home，不含 .py）"
    )

    # ---- 报告 ----
    parser.add_argument(
        "--report", action="store_true",
        help="生成 HTML 测试报告到 reports/ 目录"
    )

    # ---- 解析参数 ----
    args = parser.parse_args()
    pytest_args = []

    # 根据运行模式添加 pytest 标记筛选
    if args.smoke:
        pytest_args.extend(["-m", "smoke"])
        print(">>> 运行模式: 冒烟测试")
    elif args.regression:
        pytest_args.extend(["-m", "regression"])
        print(">>> 运行模式: 回归测试")
    elif args.slow:
        pytest_args.extend(["-m", "slow or smoke or regression"])
        print(">>> 运行模式: 全部（含慢速）")
    else:
        print(">>> 运行模式: 全部测试")

    # 浏览器配置
    if args.headless:
        pytest_args.append("--headless")
        print(">>> 浏览器模式: 无头")

    if args.browser != "chromium":
        pytest_args.extend(["--browser", args.browser])
        print(f">>> 浏览器: {args.browser}")

    # 指定文件
    if args.file:
        file_name = args.file
        if not file_name.endswith(".py"):
            file_name += ".py"
        pytest_args = [f"tests/{file_name}"] + pytest_args
        print(f">>> 测试文件: {file_name}")

    # HTML 报告
    if args.report:
        report_dir = PROJECT_ROOT / "reports"
        report_dir.mkdir(exist_ok=True)
        # 先清理旧报告
        for f in report_dir.glob("*"):
            f.unlink()
        pytest_args.extend([
            "--html", str(report_dir / "report.html"),
            "--self-contained-html",   # CSS/JS 内嵌，单文件分享
        ])
        print(f">>> HTML 报告: {report_dir / 'report.html'}")

    # 执行测试
    exit_code = run_pytest(pytest_args)

    # 输出结果
    print(f"\n{'='*60}")
    if exit_code == 0:
        print("✓ 测试全部通过！")
    else:
        print(f"✗ 测试有失败（退出码: {exit_code}）")
        print(f"  截图保存在: {PROJECT_ROOT / 'screenshots' / ''}")
    print(f"{'='*60}\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
