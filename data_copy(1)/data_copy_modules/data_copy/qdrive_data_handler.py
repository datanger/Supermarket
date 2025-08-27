#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qdrive数据处理模块
Qdrive Data Handler Module
"""

import os
import re
import datetime
import logging
from typing import List

logger = logging.getLogger(__name__)

class QdriveDataHandler:
    """Qdrive数据处理器类"""
    
    def __init__(self):
        """初始化Qdrive数据处理器"""
        self.backup_disk_type = None  # 保存AB盘选择结果
        self.backup_root_dir = None   # 保存backup根目录路径
    
    def extract_vehicle_model(self, vehicle_id: str) -> str:
        """
        从车号中提取车型
        
        Args:
            vehicle_id: 车号（如：3NRV1_201）
            
        Returns:
            str: 车型（如：RV1）
        """
        try:
            # 匹配车型模式：字母+数字的组合
            match = re.search(r'([A-Z]+\d+)', vehicle_id)
            if match:
                return match.group(1)
            else:
                # 如果没有匹配到，返回车号的一部分
                return vehicle_id.split('_')[0] if '_' in vehicle_id else vehicle_id
        except Exception:
            return vehicle_id
    
    def create_backup_directory_structure(self, backup_drive: str, qdrive_drives: List[str]) -> bool:
        """
        在backup盘创建Qdrive数据的目录结构
        
        Args:
            backup_drive: backup目标盘路径
            qdrive_drives: Qdrive源盘列表
            
        Returns:
            bool: 创建是否成功
        """
        try:
            # 获取当前日期
            current_date = datetime.datetime.now().strftime("%Y%m%d")
            
            if not qdrive_drives:
                logger.error("没有可用的Qdrive数据盘")
                return False
            
            # 收集所有车型信息
            all_vehicle_models = set()
            for qdrive_drive in qdrive_drives:
                data_path = os.path.join(qdrive_drive, 'data')
                if os.path.exists(data_path):
                    for item in os.listdir(data_path):
                        item_path = os.path.join(data_path, item)
                        if os.path.isdir(item_path):
                            vehicle_model = self.extract_vehicle_model(item)
                            if vehicle_model:
                                all_vehicle_models.add(vehicle_model)
            
            if not all_vehicle_models:
                logger.error("无法从Qdrive数据中获取车型信息")
                return False
            
            # 显示检测到的所有车型
            print(f"\n检测到车型: {', '.join(sorted(all_vehicle_models))}")
            
            # 选择主要车型（用于根目录命名）
            if len(all_vehicle_models) == 1:
                main_vehicle_model = list(all_vehicle_models)[0]
            else:
                print("检测到多个车型，请选择主要车型用于根目录命名:")
                for i, model in enumerate(sorted(all_vehicle_models), 1):
                    print(f"  {i}. {model}")
                
                while True:
                    try:
                        choice = int(input("请选择车型编号: ").strip())
                        if 1 <= choice <= len(all_vehicle_models):
                            main_vehicle_model = sorted(all_vehicle_models)[choice - 1]
                            break
                        else:
                            print(f"请输入1到{len(all_vehicle_models)}之间的数字")
                    except ValueError:
                        print("请输入有效的数字")
            
            # 创建根目录：日期-主要车型
            root_dir_name = f"{current_date}-{main_vehicle_model}"
            root_dir_path = os.path.join(backup_drive, root_dir_name)
            
            print(f"建议的根目录名称: {root_dir_name}")
            
            # 人工确认根目录名称
            custom_name = input("请输入根目录名称（直接回车使用建议名称）: ").strip()
            if custom_name:
                root_dir_name = custom_name
                root_dir_path = os.path.join(backup_drive, root_dir_name)
            
            # 人工确认A盘或B盘
            while True:
                disk_choice = input("请选择A盘或B盘 (A/B): ").strip().upper()
                if disk_choice in ['A', 'B']:
                    break
                else:
                    print("请输入A或B")
            
            # 创建根目录
            os.makedirs(root_dir_path, exist_ok=True)
            
            # 根据选择的Qdrive盘号创建对应的二级目录
            # 从qdrive_drives中提取盘号信息
            drive_numbers = []
            for qdrive_drive in qdrive_drives:
                # 从路径中提取盘号（假设路径格式为 /path/to/drive_201 或 /path/to/201）
                drive_name = os.path.basename(qdrive_drive)
                if drive_name.startswith('drive_'):
                    drive_number = drive_name.replace('drive_', '')
                else:
                    drive_number = drive_name
                drive_numbers.append(drive_number)
            
            # 如果没有提取到盘号，使用默认的201、203、230、231
            if not drive_numbers:
                drive_numbers = ['201', '203', '230', '231']
                logger.warning("无法从Qdrive盘路径提取盘号，使用默认盘号")
            
            print(f"检测到的盘号: {', '.join(drive_numbers)}")
            
            # 为每个车型和盘号创建对应的二级目录
            for vehicle_model in sorted(all_vehicle_models):
                for drive_number in drive_numbers:
                    # 确保车型名称包含3N前缀
                    if not vehicle_model.startswith('3N'):
                        vehicle_model_with_prefix = f"3N{vehicle_model}"
                    else:
                        vehicle_model_with_prefix = vehicle_model
                    
                    subdir_name = f"{vehicle_model_with_prefix}_{drive_number}_{disk_choice}"
                    subdir_path = os.path.join(root_dir_path, subdir_name)
                    os.makedirs(subdir_path, exist_ok=True)
                    logger.info(f"创建二级目录: {subdir_path}")
            
            logger.info(f"成功在backup盘 {backup_drive} 创建目录结构")
            logger.info(f"包含车型: {', '.join(sorted(all_vehicle_models))}")
            logger.info(f"包含盘号: {', '.join(drive_numbers)}")
            logger.info(f"选择的盘类型: {disk_choice}盘")
            
            # 保存AB盘选择结果，供后续拷贝使用
            self.backup_disk_type = disk_choice
            self.backup_root_dir = root_dir_path
            
            return True
            
        except Exception as e:
            logger.error(f"创建backup盘目录结构时出错: {e}")
            return False 