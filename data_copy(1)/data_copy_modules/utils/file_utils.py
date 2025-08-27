#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件工具模块
File Utilities Module
"""

import os
import shutil
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

def get_directory_stats(path: str) -> Dict[str, int]:
    """
    获取目录的统计信息
    
    Args:
        path: 目录路径
        
    Returns:
        Dict[str, int]: 包含文件数量和总大小的字典
    """
    try:
        file_count = 0
        total_size = 0
        
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    file_count += 1
                except (OSError, IOError) as e:
                    logger.warning(f"无法获取文件 {file_path} 的大小: {e}")
                    continue
        
        return {
            'file_count': file_count,
            'total_size': total_size
        }
        
    except Exception as e:
        logger.error(f"获取目录统计信息时出错: {e}")
        return {'file_count': 0, 'total_size': 0}

def format_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    
    Args:
        size_bytes: 字节数
        
    Returns:
        str: 格式化后的大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def generate_directory_tree(path: str, max_depth: int = 3) -> str:
    """
    生成目录树字符串
    
    Args:
        path: 根目录路径
        max_depth: 最大深度
        
    Returns:
        str: 目录树字符串
    """
    def _generate_tree(current_path: str, prefix: str, depth: int) -> str:
        if depth > max_depth:
            return ""
        
        result = ""
        try:
            items = sorted(os.listdir(current_path))
            for i, item in enumerate(items):
                item_path = os.path.join(current_path, item)
                is_last = (i == len(items) - 1)
                
                if os.path.isdir(item_path):
                    result += f"{prefix}{'└── ' if is_last else '├── '}{item}/\n"
                    if depth < max_depth:
                        new_prefix = prefix + ('    ' if is_last else '│   ')
                        result += _generate_tree(item_path, new_prefix, depth + 1)
                else:
                    result += f"{prefix}{'└── ' if is_last else '├── '}{item}\n"
                    
        except PermissionError:
            result += f"{prefix}└── [权限不足]\n"
        except Exception as e:
            result += f"{prefix}└── [错误: {e}]\n"
        
        return result
    
    return f"{os.path.basename(path)}/\n" + _generate_tree(path, "", 1)

def get_unique_filename(file_path: str) -> str:
    """
    获取唯一的文件名，如果文件已存在则自动重命名
    
    Args:
        file_path: 原始文件路径
        
    Returns:
        str: 唯一的文件路径
    """
    if not os.path.exists(file_path):
        return file_path
    
    # 分离文件名和扩展名
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    
    counter = 1
    while True:
        new_filename = f"{name}{counter}{ext}"
        new_file_path = os.path.join(directory, new_filename)
        
        if not os.path.exists(new_file_path):
            return new_file_path
        
        counter += 1

def copy_file_with_rename(src_file: str, dst_file: str) -> bool:
    """
    拷贝文件，如果目标文件已存在则自动重命名
    
    Args:
        src_file: 源文件路径
        dst_file: 目标文件路径
        
    Returns:
        bool: 拷贝是否成功
    """
    try:
        # 获取唯一的文件名
        unique_dst_file = get_unique_filename(dst_file)
        
        # 如果文件名发生了变化，记录日志
        if unique_dst_file != dst_file:
            logger.info(f"目标文件已存在，自动重命名: {os.path.basename(dst_file)} → {os.path.basename(unique_dst_file)}")
        
        # 拷贝文件
        shutil.copy2(src_file, unique_dst_file)
        return True
        
    except Exception as e:
        logger.error(f"拷贝文件时出错: {e}")
        return False

def copy_directory_with_rename(src_dir: str, dst_dir: str, progress_callback=None) -> bool:
    """
    拷贝目录，处理同名文件自动重命名
    
    Args:
        src_dir: 源目录路径
        dst_dir: 目标目录路径
        progress_callback: 进度回调函数
        
    Returns:
        bool: 拷贝是否成功
    """
    try:
        # 创建目标目录
        os.makedirs(dst_dir, exist_ok=True)
        
        # 遍历源目录
        for root, dirs, files in os.walk(src_dir):
            # 计算相对路径
            rel_path = os.path.relpath(root, src_dir)
            target_dir = os.path.join(dst_dir, rel_path)
            
            # 创建子目录
            os.makedirs(target_dir, exist_ok=True)
            
            # 拷贝文件
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_dir, file)
                
                try:
                    # 使用自动重命名功能拷贝文件
                    success = copy_file_with_rename(src_file, dst_file)
                    if success and progress_callback:
                        progress_callback(1)
                    elif not success:
                        logger.warning(f"拷贝文件失败: {src_file}")
                        
                except Exception as e:
                    logger.warning(f"拷贝文件 {src_file} 时出错: {e}")
                    continue
        
        return True
        
    except Exception as e:
        logger.error(f"拷贝目录时出错: {e}")
        return False 