#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拷贝操作日志记录器
Copy Operation Logger
"""

import logging
import datetime

# 创建专门的拷贝日志记录器
copy_logger = logging.getLogger('copy_operations')
copy_logger.setLevel(logging.INFO)

# 全局变量存储日志文件路径
COPY_LOG_FILE = None
FILELIST_LOG_FILE = None

def setup_copy_logger():
    """设置拷贝操作日志记录器"""
    global copy_logger, COPY_LOG_FILE, FILELIST_LOG_FILE
    
    # 生成时间戳文件名
    formatted_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
    copy_log_file = f"datacopy-{formatted_time}.txt"
    filelist_log_file = f"filelist-{formatted_time}.txt"
    
    # 创建拷贝日志文件处理器
    copy_file_handler = logging.FileHandler(copy_log_file, encoding='utf-8')
    copy_file_handler.setLevel(logging.INFO)
    
    # 创建文件列表日志文件处理器
    filelist_file_handler = logging.FileHandler(filelist_log_file, encoding='utf-8')
    filelist_file_handler.setLevel(logging.INFO)
    
    # 设置格式
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    copy_file_handler.setFormatter(formatter)
    filelist_file_handler.setFormatter(formatter)
    
    # 添加处理器
    copy_logger.addHandler(copy_file_handler)
    copy_logger.addHandler(filelist_file_handler)
    
    # 更新全局变量
    COPY_LOG_FILE = copy_log_file
    FILELIST_LOG_FILE = filelist_log_file
    
    return copy_log_file, filelist_log_file

def log_copy_operation(message: str, log_type: str = 'copy'):
    """
    记录拷贝操作日志
    
    Args:
        message: 日志消息
        log_type: 日志类型 ('copy' 或 'filelist')
    """
    try:
        if log_type == 'copy' and COPY_LOG_FILE:
            with open(COPY_LOG_FILE, 'a', encoding='utf-8') as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp}: {message}\n")
        elif log_type == 'filelist' and FILELIST_LOG_FILE:
            with open(FILELIST_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")
    except Exception as e:
        print(f"写入日志文件时出错: {e}") 