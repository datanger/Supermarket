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
            if not qdrive_drives:
                logger.error("没有可用的Qdrive数据盘")
                return False
            
            # 从Qdrive数据中提取车型和日期信息
            all_vehicle_models = set()
            all_dates = set()
            
            # 静默分析Qdrive数据结构
            for qdrive_drive in qdrive_drives:
                data_path = os.path.join(qdrive_drive, 'data')
                
                if os.path.exists(data_path):
                    try:
                        # 遍历二级目录（车型目录）
                        vehicle_dirs = os.listdir(data_path)
                        
                        for vehicle_dir in vehicle_dirs:
                            vehicle_path = os.path.join(data_path, vehicle_dir)
                            
                            if os.path.isdir(vehicle_path):
                                # 提取车型：从2qd_3NRV1_v1中提取RV1
                                vehicle_model = vehicle_dir
                                # 使用正则表达式提取RV1部分
                                rv_match = re.search(r'3N([A-Z]+\d+)', vehicle_dir)
                                if rv_match:
                                    vehicle_model = rv_match.group(1)  # 提取RV1
                                else:
                                    # 如果没有匹配到3N+字母数字的模式，尝试其他方式
                                    if 'RV1' in vehicle_dir:
                                        vehicle_model = 'RV1'
                                    else:
                                        continue
                                
                                all_vehicle_models.add(vehicle_model)
                                
                                try:
                                    # 遍历三级目录（日期目录）
                                    date_dirs = os.listdir(vehicle_path)
                                    
                                    for date_dir in date_dirs:
                                        date_path = os.path.join(vehicle_path, date_dir)
                                        
                                        if os.path.isdir(date_path):
                                            # 从2025_08_21-10_19中提取20250821
                                            date_match = re.search(r'(\d{4})_(\d{2})_(\d{2})', date_dir)
                                            if date_match:
                                                year, month, day = date_match.groups()
                                                extracted_date = f"{year}{month}{day}"
                                                all_dates.add(extracted_date)
                                except Exception as e:
                                    logger.warning(f"读取三级目录时出错: {e}")
                    except Exception as e:
                        logger.warning(f"读取二级目录时出错: {e}")
            
            if not all_vehicle_models:
                logger.error("无法从Qdrive数据中获取车型信息")
                return False
            
            if not all_dates:
                logger.error("无法从Qdrive数据中获取日期信息")
                print("\n尝试使用当前系统日期作为备选方案...")
                current_date = datetime.datetime.now().strftime("%Y%m%d")
                all_dates.add(current_date)
                print(f"使用当前系统日期: {current_date}")
            
            # 显示检测到的信息
            print(f"\n检测到车型: {', '.join(sorted(all_vehicle_models))}")
            print(f"检测到日期: {', '.join(sorted(all_dates))}")
            
            # 自动选择主要车型和日期（用于根目录命名）
            if len(all_vehicle_models) == 1:
                main_vehicle_model = list(all_vehicle_models)[0]
            else:
                # 自动选择第一个车型
                main_vehicle_model = sorted(all_vehicle_models)[0]
            
            if len(all_dates) == 1:
                main_date = list(all_dates)[0]
            else:
                # 自动选择第一个日期
                main_date = sorted(all_dates)[0]
            
            # 创建根目录：日期-车型
            root_dir_name = f"{main_date}-{main_vehicle_model}"
            root_dir_path = os.path.join(backup_drive, root_dir_name)
            
            # 直接使用建议的根目录名称
            print(f"使用根目录名称: {root_dir_name}")
            
            # 用户选择A盘或B盘
            while True:
                disk_choice = input("请选择A盘或B盘 (A/B): ").strip().upper()
                if disk_choice in ['A', 'B']:
                    break
                else:
                    print("❌ 无效选择，请输入 A 或 B")
            
            # 创建根目录
            os.makedirs(root_dir_path, exist_ok=True)
            
            # 根据选择的Qdrive盘号创建对应的二级目录
            # 使用传入的qdrive_drives和预期的盘号映射
            expected_drive_numbers = ['201', '203', '230', '231']
            
            # 为每个车型和盘号创建对应的二级目录
            for vehicle_model in sorted(all_vehicle_models):
                for drive_number in expected_drive_numbers:
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
            logger.info(f"包含日期: {', '.join(sorted(all_dates))}")
            logger.info(f"包含盘号: {', '.join(expected_drive_numbers)}")
            logger.info(f"选择的盘类型: {disk_choice}盘")
            
            # 保存AB盘选择结果，供后续拷贝使用
            self.backup_disk_type = disk_choice
            self.backup_root_dir = root_dir_path
            
            return True
            
        except Exception as e:
            logger.error(f"创建backup盘目录结构时出错: {e}")
            return False 