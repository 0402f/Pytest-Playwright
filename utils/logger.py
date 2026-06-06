"""
日志工具模块
------------
职责：提供统一的日志记录功能，支持同时输出到控制台和文件。

设计要点：
1. 使用 Python 标准库 logging，不引入第三方依赖
2. 支持控制台 + 文件双输出
3. 控制台日志用 INFO 级别（简洁），文件日志用 DEBUG 级别（详细）
4. 自动创建日志目录

面试可能问：
Q: 为什么不直接用 print() 调试？
A: 1) print 无法区分级别（INFO/WARNING/ERROR）
   2) print 无法同时输出到文件
   3) 生产环境 print 可能被重定向丢失
   4) logging 支持多模块、格式化时间戳、按大小/时间轮转

Q: logging 的级别有哪些？
A: DEBUG(10) < INFO(20) < WARNING(30) < ERROR(40) < CRITICAL(50)
   设置级别后，低于该级别的日志不会被输出
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


# ---- 日志器名称 ----
# 使用项目名作为 logger 名称，方便区分不同项目的日志
LOGGER_NAME = "HeritageCraft_UI_Auto"


def setup_logger(
    name: str = LOGGER_NAME,
    log_dir: str = "logs",
    console_level: str = "INFO",
    file_level: str = "DEBUG",
) -> logging.Logger:
    """
    创建并配置日志器（Logger）

    Args:
        name: 日志器名称
        log_dir: 日志文件保存目录
        console_level: 控制台输出的最低日志级别
        file_level: 文件输出的最低日志级别

    Returns:
        配置好的 Logger 对象

    使用示例:
        logger = setup_logger()
        logger.info("测试开始")
        logger.debug("这是调试信息，只在文件中看到")
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler（防止多次调用时日志重复输出）
    if logger.handlers:
        return logger

    # 设为最低级别（DEBUG），由各个 handler 分别控制输出级别
    logger.setLevel(logging.DEBUG)

    # ---- 日志格式 ----
    # 控制台格式：简洁，只显示级别和消息
    console_formatter = logging.Formatter(
        "[%(levelname)-5s] %(message)s"
    )
    # 文件格式：详细，包含时间、模块、行号
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-5s] %(name)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ---- 控制台 Handler ----
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, console_level.upper(), logging.INFO))
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # ---- 文件 Handler ----
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)  # 自动创建目录

    # 日志文件名包含日期，方便按天追溯
    log_filename = f"{datetime.now().strftime('%Y%m%d')}_test_run.log"
    file_handler = logging.FileHandler(
        log_dir_path / log_filename, encoding="utf-8"
    )
    file_handler.setLevel(getattr(logging, file_level.upper(), logging.DEBUG))
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


# ---- 模块级 Logger ----
# 导入即可使用，无需每次配置
# 用法: from utils.logger import logger
#       logger.info("这是一条日志")
logger = setup_logger()
