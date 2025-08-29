#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拷贝操作日志记录器 - 增强版数据完整性校验
Enhanced Copy Operation Logger - Focus on Data Integrity Verification
"""

import logging
import datetime
import os
import psutil

# 创建专门的拷贝日志记录器
copy_logger = logging.getLogger('copy_operations')
copy_logger.setLevel(logging.INFO)

# 全局变量存储日志文件路径
COPY_LOG_FILE = None
FILELIST_LOG_FILE = None
LOG_DIR = None

def setup_copy_logger():
    """设置拷贝操作日志记录器"""
    global copy_logger, COPY_LOG_FILE, FILELIST_LOG_FILE, LOG_DIR
    
    # 创建logs根目录
    logs_root = "logs"
    if not os.path.exists(logs_root):
        os.makedirs(logs_root)
        print(f"✅ 创建日志根目录: {logs_root}")
    
    # 创建以运行时间命名的二级目录
    run_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_subdir = os.path.join(logs_root, run_time)
    if not os.path.exists(log_subdir):
        os.makedirs(log_subdir)
        print(f"✅ 创建日志子目录: {log_subdir}")
    
    LOG_DIR = log_subdir
    
    # 生成日志文件名
    copy_log_file = os.path.join(log_subdir, "datacopy.txt")
    filelist_log_file = os.path.join(log_subdir, "filelist.txt")
    
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
    
    # 更新全局变量
    COPY_LOG_FILE = copy_log_file
    FILELIST_LOG_FILE = filelist_log_file
    
    print(f"📁 日志文件路径:")
    print(f"   拷贝日志: {copy_log_file}")
    print(f"   文件列表: {filelist_log_file}")
    
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

def log_source_drives_before_copy(source_drives: list, drive_info: dict):
    """
    记录拷贝前源驱动器的详细信息（用于后续校验）
    
    Args:
        source_drives: 源驱动器列表
        drive_info: 驱动器信息字典
    """
    try:
        if not COPY_LOG_FILE:
            return
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(COPY_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{timestamp}: ========== 拷贝前源驱动器信息（用于数据完整性校验）==========\n")
            f.write(f"{timestamp}: 拷贝开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{timestamp}: 源驱动器总数: {len(source_drives)}\n\n")
            
            for i, drive in enumerate(source_drives, 1):
                f.write(f"{timestamp}: 【源驱动器 {i}】: {drive}\n")
                
                if drive in drive_info and 'error' not in drive_info[drive]:
                    info = drive_info[drive]
                    
                    # 基本信息
                    f.write(f"{timestamp}:   卷标: {info.get('volume_name', 'Unknown')}\n")
                    f.write(f"{timestamp}:   文件系统: {info.get('fs_type', 'Unknown')}\n")
                    
                    # 磁盘使用情况
                    if info.get('total', 0) > 0:
                        total_gb = info['total'] / (1024**3)
                        used_gb = info['used'] / (1024**3)
                        free_gb = info['free'] / (1024**3)
                        f.write(f"{timestamp}:   总容量: {total_gb:.2f} GB\n")
                        f.write(f"{timestamp}:   已使用: {used_gb:.2f} GB\n")
                        f.write(f"{timestamp}:   可用空间: {free_gb:.2f} GB\n")
                    
                    # 数据目录统计
                    if 'data' in os.listdir(drive):
                        data_path = os.path.join(drive, 'data')
                        try:
                            from utils.file_utils import get_directory_stats
                            stats = get_directory_stats(data_path)
                            f.write(f"{timestamp}:   data目录统计: {stats['file_count']} 个文件, {stats['total_size']} 字节\n")
                        except Exception as e:
                            f.write(f"{timestamp}:   data目录统计失败: {e}\n")
                    
                    if 'logs' in os.listdir(drive):
                        logs_path = os.path.join(drive, 'logs')
                        try:
                            from utils.file_utils import get_directory_stats
                            stats = get_directory_stats(logs_path)
                            f.write(f"{timestamp}:   logs目录统计: {stats['file_count']} 个文件, {stats['total_size']} 字节\n")
                        except Exception as e:
                            f.write(f"{timestamp}:   logs目录统计失败: {e}\n")
                    
                    # BitLocker状态
                    if info.get('bitlocker_status'):
                        f.write(f"{timestamp}:   BitLocker状态: {info['bitlocker_status']}\n")
                else:
                    f.write(f"{timestamp}:   信息获取失败或驱动器错误\n")
                
                f.write(f"{timestamp}:   - 分隔线\n")
            
            f.write(f"{timestamp}: ========== 源驱动器信息记录完成 ==========\n\n")
            
    except Exception as e:
        print(f"记录源驱动器信息时出错: {e}")

def log_target_drives_before_copy(transfer_drives: list, backup_drives: list, drive_info: dict):
    """
    记录拷贝前目标驱动器的详细信息（用于后续校验）
    
    Args:
        transfer_drives: Transfer驱动器列表
        backup_drives: Backup驱动器列表
        drive_info: 驱动器信息字典
    """
    try:
        if not COPY_LOG_FILE:
            return
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(COPY_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{timestamp}: ========== 拷贝前目标驱动器信息（用于数据完整性校验）==========\n")
            
            # Transfer驱动器信息
            f.write(f"{timestamp}: Transfer驱动器 ({len(transfer_drives)} 个):\n")
            for i, drive in enumerate(transfer_drives, 1):
                f.write(f"{timestamp}:   【Transfer驱动器 {i}】: {drive}\n")
                
                if drive in drive_info and 'error' not in drive_info[drive]:
                    info = drive_info[drive]
                    f.write(f"{timestamp}:     卷标: {info.get('volume_name', 'Unknown')}\n")
                    
                    if info.get('total', 0) > 0:
                        total_gb = info['total'] / (1024**3)
                        used_gb = info['used'] / (1024**3)
                        free_gb = info['free'] / (1024**3)
                        f.write(f"{timestamp}:     总容量: {total_gb:.2f} GB\n")
                        f.write(f"{timestamp}:     已使用: {used_gb:.2f} GB\n")
                        f.write(f"{timestamp}:     可用空间: {free_gb:.2f} GB\n")
                
                # 检查现有data目录
                data_path = os.path.join(drive, 'data')
                if os.path.exists(data_path):
                    try:
                        from utils.file_utils import get_directory_stats
                        stats = get_directory_stats(data_path)
                        f.write(f"{timestamp}:     现有data目录: {stats['file_count']} 个文件, {stats['total_size']} 字节\n")
                        f.write(f"{timestamp}:     💡 注意: Transfer盘的data目录会累积多个源盘的数据\n")
                    except Exception as e:
                        f.write(f"{timestamp}:     现有data目录统计失败: {e}\n")
                else:
                    f.write(f"{timestamp}:     现有data目录: 不存在\n")
                
                f.write(f"{timestamp}:     - 分隔线\n")
            
            # Backup驱动器信息
            f.write(f"{timestamp}: Backup驱动器 ({len(backup_drives)} 个):\n")
            for i, drive in enumerate(backup_drives, 1):
                f.write(f"{timestamp}:   【Backup驱动器 {i}】: {drive}\n")
                
                if drive in drive_info and 'error' not in drive_info[drive]:
                    info = drive_info[drive]
                    f.write(f"{timestamp}:     卷标: {info.get('volume_name', 'Unknown')}\n")
                    
                    if info.get('total', 0) > 0:
                        total_gb = info['total'] / (1024**3)
                        used_gb = info['used'] / (1024**3)
                        free_gb = info['free'] / (1024**3)
                        f.write(f"{timestamp}:     总容量: {total_gb:.2f} GB\n")
                        f.write(f"{timestamp}:     已使用: {used_gb:.2f} GB\n")
                        f.write(f"{timestamp}:     可用空间: {free_gb:.2f} GB\n")
                
                # 检查现有目录结构
                backup_dirs = []
                for item in os.listdir(drive):
                    item_path = os.path.join(drive, item)
                    if os.path.isdir(item_path) and not item.startswith('.'):
                        backup_dirs.append(item)
                
                f.write(f"{timestamp}:     现有目录: {', '.join(backup_dirs) if backup_dirs else '无'}\n")
                
                # 检查是否有data目录
                data_path = os.path.join(drive, 'data')
                if os.path.exists(data_path):
                    try:
                        from utils.file_utils import get_directory_stats
                        stats = get_directory_stats(data_path)
                        f.write(f"{timestamp}:     现有data目录: {stats['file_count']} 个文件, {stats['total_size']} 字节\n")
                    except Exception as e:
                        f.write(f"{timestamp}:     现有data目录统计失败: {e}\n")
                else:
                    f.write(f"{timestamp}:     现有data目录: 不存在\n")
                
                f.write(f"{timestamp}:     - 分隔线\n")
            
            f.write(f"{timestamp}: ========== 目标驱动器信息记录完成 ==========\n\n")
            
    except Exception as e:
        print(f"记录目标驱动器信息时出错: {e}")

def log_copy_verification_summary(source_drives: list, transfer_drives: list, backup_drives: list):
    """
    记录拷贝完成后的校验总结（用于人工校验数据完整性）
    
    Args:
        source_drives: 源驱动器列表
        transfer_drives: Transfer驱动器列表
        backup_drives: Backup驱动器列表
    """
    try:
        if not COPY_LOG_FILE:
            return
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(COPY_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{timestamp}: ========== 拷贝完成后的数据完整性校验总结 ==========\n")
            f.write(f"{timestamp}: 拷贝完成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{timestamp}: 请人工校验以下信息:\n\n")
            
            # 源驱动器校验
            f.write(f"{timestamp}: 【源驱动器数据校验】\n")
            f.write(f"{timestamp}: 源驱动器总数: {len(source_drives)}\n")
            for i, drive in enumerate(source_drives, 1):
                f.write(f"{timestamp}:   源驱动器 {i}: {drive}\n")
                f.write(f"{timestamp}:     请检查: 原始数据是否完整，是否有损坏文件\n")
            
            # Transfer驱动器校验
            f.write(f"\n{timestamp}: 【Transfer驱动器数据校验】\n")
            f.write(f"{timestamp}: Transfer驱动器总数: {len(transfer_drives)}\n")
            f.write(f"{timestamp}: 💡 重要提醒: Transfer盘的data目录会累积多个源盘的数据\n")
            f.write(f"{timestamp}:   因此文件数量和大小会大于单个源盘，这是正常现象\n")
            for i, drive in enumerate(transfer_drives, 1):
                f.write(f"{timestamp}:   Transfer驱动器 {i}: {drive}\n")
                f.write(f"{timestamp}:     请检查:\n")
                f.write(f"{timestamp}:       1. data目录是否存在\n")
                f.write(f"{timestamp}:       2. 是否包含所有源盘的数据（累积检查）\n")
                f.write(f"{timestamp}:       3. 目录结构是否完整\n")
                f.write(f"{timestamp}:       4. 不要单独对比单个源盘的文件数量\n")
            
            # Backup驱动器校验
            f.write(f"\n{timestamp}: 【Backup驱动器数据校验】\n")
            f.write(f"{timestamp}: Backup驱动器总数: {len(backup_drives)}\n")
            for i, drive in enumerate(backup_drives, 1):
                f.write(f"{timestamp}:   Backup驱动器 {i}: {drive}\n")
                f.write(f"{timestamp}:     请检查:\n")
                f.write(f"{timestamp}:       1. 目录结构是否正确（根目录/二级目录/data/时间目录）\n")
                f.write(f"{timestamp}:       2. 是否跳过了2qd_3NRV1_v1这一级目录\n")
                f.write(f"{timestamp}:       3. 时间目录是否完整\n")
                f.write(f"{timestamp}:       4. 每个源盘的数据是否独立完整\n")
                f.write(f"{timestamp}:       5. 文件数量应与对应源盘一致\n")
            
            f.write(f"\n{timestamp}: 【校验步骤建议】\n")
            f.write(f"{timestamp}: 1. Transfer盘: 检查是否累积了所有源盘的数据（不要单独对比）\n")
            f.write(f"{timestamp}: 2. Backup盘: 每个源盘的数据应该独立完整，文件数量一致\n")
            f.write(f"{timestamp}: 3. 检查目标驱动器的目录结构是否正确\n")
            f.write(f"{timestamp}: 4. 随机抽样检查几个文件的内容完整性\n")
            f.write(f"{timestamp}: 5. 检查是否有文件损坏或丢失\n")
            
            f.write(f"\n{timestamp}: ========== 数据完整性校验总结完成 ==========\n\n")
            
    except Exception as e:
        print(f"记录拷贝校验总结时出错: {e}")

def log_single_copy_verification(source_drive: str, target_drive: str, source_stats: dict, target_stats: dict, copy_type: str):
    """
    记录单个拷贝操作的详细校验信息
    
    Args:
        source_drive: 源驱动器
        target_drive: 目标驱动器
        source_stats: 源目录统计信息
        target_stats: 目标目录统计信息
        copy_type: 拷贝类型
    """
    try:
        if not COPY_LOG_FILE:
            return
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(COPY_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{timestamp}: ========== {copy_type} 拷贝操作校验信息 ==========\n")
            f.write(f"{timestamp}: 源驱动器: {source_drive}\n")
            f.write(f"{timestamp}: 目标驱动器: {target_drive}\n")
            
            # 源目录统计
            f.write(f"{timestamp}: 源目录统计:\n")
            f.write(f"{timestamp}:   - 文件数量: {source_stats['file_count']}\n")
            f.write(f"{timestamp}:   - 总大小: {source_stats['total_size']} 字节\n")
            
            # 目标目录统计
            f.write(f"{timestamp}: 目标目录统计:\n")
            f.write(f"{timestamp}:   - 文件数量: {target_stats['file_count']}\n")
            f.write(f"{timestamp}:   - 总大小: {target_stats['total_size']} 字节\n")
            
            # 数据完整性检查
            f.write(f"{timestamp}: 数据完整性检查:\n")
            
            # 根据拷贝类型进行不同的校验逻辑
            if 'Transfer' in copy_type:
                # Transfer盘拷贝：考虑data目录合并的情况
                f.write(f"{timestamp}:   📝 Transfer盘拷贝说明: data目录会累积多个源盘的数据\n")
                
                # 检查本次拷贝的数据是否完整
                if source_stats['file_count'] > 0 and source_stats['total_size'] > 0:
                    f.write(f"{timestamp}:   ✅ 本次拷贝数据完整性: 100.00%\n")
                    f.write(f"{timestamp}:   📊 目标盘当前状态: 累积了 {target_stats['file_count']} 个文件, 总大小 {target_stats['total_size']} 字节\n")
                    f.write(f"{timestamp}:   💡 建议: 检查目标盘data目录中是否包含本次源盘的所有文件\n")
                    f.write(f"{timestamp}:   ⚠️ 注意: 不要因为文件数量增加而误判为拷贝失败\n")
                else:
                    f.write(f"{timestamp}:   ⚠️ 源盘数据为空，无法进行完整性校验\n")
                    
            else:
                # Backup盘拷贝：要求完全一致
                f.write(f"{timestamp}:   📝 Backup盘拷贝说明: 要求文件数量和大小完全一致\n")
                
                # 文件数量检查
                if source_stats['file_count'] == target_stats['file_count']:
                    f.write(f"{timestamp}:   ✅ 文件数量: 一致 ({source_stats['file_count']} = {target_stats['file_count']})\n")
                else:
                    f.write(f"{timestamp}:   ❌ 文件数量: 不一致 (源: {source_stats['file_count']} ≠ 目标: {target_stats['file_count']})\n")
                    f.write(f"{timestamp}:     缺失文件数: {abs(source_stats['file_count'] - target_stats['file_count'])}\n")
                
                # 文件大小检查
                size_diff = abs(source_stats['total_size'] - target_stats['total_size'])
                if size_diff < 1024:  # 允许1KB的误差
                    f.write(f"{timestamp}:   ✅ 文件大小: 一致 (误差 < 1KB)\n")
                else:
                    f.write(f"{timestamp}:   ❌ 文件大小: 不一致\n")
                    f.write(f"{timestamp}:     源大小: {source_stats['total_size']} 字节\n")
                    f.write(f"{timestamp}:     目标大小: {target_stats['total_size']} 字节\n")
                    f.write(f"{timestamp}:     差异: {size_diff} 字节 ({size_diff / (1024**2):.2f} MB)\n")
                
                # 拷贝效率
                if source_stats['total_size'] > 0:
                    efficiency = (target_stats['total_size'] / source_stats['total_size']) * 100
                    f.write(f"{timestamp}:   拷贝效率: {efficiency:.2f}%\n")
            
            f.write(f"{timestamp}: ========== {copy_type} 拷贝操作校验信息完成 ==========\n\n")
            
    except Exception as e:
        print(f"记录单个拷贝校验信息时出错: {e}")
