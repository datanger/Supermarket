#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心系统检测器模块
Core System Detector Module
"""

import os
import shutil
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple

# 导入子模块
try:
    from drivers.drive_detector import DriveDetector
    from drivers.bitlocker_manager import BitlockerManager
    from data_copy.vector_data_handler import VectorDataHandler
    from data_copy.qdrive_data_handler import QdriveDataHandler
    from utils.file_utils import get_directory_stats, format_size, generate_directory_tree, copy_directory_with_rename
    from utils.progress_bar import create_progress_bar, update_progress, close_progress
    from logging_utils.copy_logger import log_copy_operation, log_source_drives_before_copy, log_target_drives_before_copy, log_copy_verification_summary, log_single_copy_verification
except ImportError:
    from data_copy_modules.drivers.drive_detector import DriveDetector
    from data_copy_modules.drivers.bitlocker_manager import BitlockerManager
    from data_copy_modules.data_copy.vector_data_handler import VectorDataHandler
    from data_copy_modules.data_copy.qdrive_data_handler import QdriveDataHandler
    from data_copy_modules.utils.file_utils import get_directory_stats, format_size, generate_directory_tree, copy_directory_with_rename
    from data_copy_modules.utils.progress_bar import create_progress_bar, update_progress, close_progress
    from data_copy_modules.logging_utils.copy_logger import log_copy_operation, log_source_drives_before_copy, log_target_drives_before_copy, log_copy_verification_summary, log_single_copy_verification

logger = logging.getLogger(__name__)

class CrossPlatformSystemDetector:
    """跨平台系统检测器类"""
    
    def __init__(self):
        """初始化系统检测器"""
        # 创建子模块实例
        self.drive_detector = DriveDetector()
        self.bitlocker_manager = BitlockerManager(self.drive_detector.os_type)
        self.vector_handler = VectorDataHandler()
        self.qdrive_handler = QdriveDataHandler()
        
        # 获取操作系统类型
        self.os_type = self.drive_detector.os_type
        
        # 初始化其他属性（延迟初始化）
        self.drives = []
        self.system_drives = []
        self.source_drives = []
        self.destination_drives = []
        self.drive_info = {}
        self.qdrive_drives = []
        self.vector_drives = []
        self.transfer_drives = []
        self.backup_drives = []
        
        logger.info(f"检测到操作系统: {self.os_type}")
    
    def detect_all_drives(self) -> List[str]:
        """检测系统中所有可用的驱动器"""
        self.drives = self.drive_detector.detect_all_drives()
        return self.drives
    
    def get_system_drives(self) -> List[str]:
        """获取系统驱动器列表"""
        self.system_drives = self.drive_detector.get_system_drives()
        return self.system_drives
    
    def classify_drives(self) -> Tuple[List[str], List[str]]:
        """将驱动器分类为源数据盘和目标备份盘"""
        source_drives, destination_drives = self.drive_detector.classify_drives()
        self.source_drives = source_drives
        self.destination_drives = destination_drives
        return source_drives, destination_drives
    
    def get_drive_information(self) -> Dict[str, Dict]:
        """获取所有驱动器的详细信息"""
        self.drive_info = self.drive_detector.get_drive_information()
        
        # 添加BitLocker状态信息
        if self.os_type == "windows":
            for drive in self.drive_info:
                if 'error' not in self.drive_info[drive]:
                    try:
                        self.drive_info[drive]['bitlocker_status'] = self.bitlocker_manager.check_bitlocker_status(drive)
                    except Exception as e:
                        logger.warning(f"无法获取驱动器 {drive} 的BitLocker状态: {e}")
                        self.drive_info[drive]['bitlocker_status'] = "Unknown"
        
        # 记录源驱动器和目标驱动器的信息到日志
        try:
            source_drives = self.source_drives if hasattr(self, 'source_drives') else []
            transfer_drives = self.transfer_drives if hasattr(self, 'transfer_drives') else []
            backup_drives = self.backup_drives if hasattr(self, 'backup_drives') else []
            
            if source_drives:
                log_source_drives_before_copy(source_drives, self.drive_info)
            if transfer_drives or backup_drives:
                log_target_drives_before_copy(transfer_drives, backup_drives, self.drive_info)
        except Exception as e:
            logger.warning(f"记录驱动器信息到日志时出错: {e}")
        
        return self.drive_info
    
    def unlock_all_locked_drives(self, recovery_key: str) -> Dict[str, bool]:
        """解锁所有被BitLocker锁定的驱动器（仅Windows）"""
        return self.bitlocker_manager.unlock_all_locked_drives(self.drive_info, recovery_key)
    
    def identify_data_drives(self) -> Tuple[List[str], List[str], List[str], List[str]]:
        """识别Qdrive、Vector、transfer和backup驱动器"""
        qdrive_drives, vector_drives, transfer_drives, backup_drives = self.drive_detector.identify_data_drives()
        self.qdrive_drives = qdrive_drives
        self.vector_drives = vector_drives
        self.transfer_drives = transfer_drives
        self.backup_drives = backup_drives
        # 记录数据驱动器分类信息到日志
        try:
            # 合并所有源驱动器
            source_drives = qdrive_drives + vector_drives
            if source_drives:
                log_source_drives_before_copy(source_drives, self.drive_info)
            if transfer_drives or backup_drives:
                log_target_drives_before_copy(transfer_drives, backup_drives, self.drive_info)
        except Exception as e:
            logger.warning(f"记录数据驱动器分类信息到日志时出错: {e}")
        
        return qdrive_drives, vector_drives, transfer_drives, backup_drives
    
    def check_vector_data_dates(self, vector_drive: str) -> Tuple[bool, List[str]]:
        """检查Vector数据盘中的日期数量"""
        return self.vector_handler.check_vector_data_dates(vector_drive)
    
    def extract_vehicle_model(self, vehicle_id: str) -> str:
        """从车号中提取车型"""
        return self.qdrive_handler.extract_vehicle_model(vehicle_id)
    
    def _extract_qdrive_number(self, qdrive_drive: str) -> str:
        """Extract Qdrive number (201, 203, 230, 231) from drive path"""
        import re
        if '201' in qdrive_drive:
            return '201'
        elif '203' in qdrive_drive:
            return '203'
        elif '230' in qdrive_drive:
            return '230'
        elif '231' in qdrive_drive:
            return '231'
        else:
            # Try to extract 3-digit number from path
            match = re.search(r'(\d{3})', qdrive_drive)
            if match:
                return match.group(1)
            return 'Unknown'
    
    def create_backup_directory_structure(self, backup_drive: str, qdrive_drives: List[str]) -> bool:
        """在backup盘创建Qdrive数据的目录结构"""
        return self.qdrive_handler.create_backup_directory_structure(backup_drive, qdrive_drives)
    
    def copy_qdrive_data_to_transfer(self, qdrive_drive: str, transfer_drive: str) -> bool:
        """Copy Qdrive data to transfer drive (maintain original structure)"""
        try:
            data_path = os.path.join(qdrive_drive, 'data')
            if not os.path.exists(data_path):
                logger.error(f"Qdrive data drive {qdrive_drive} does not contain data folder")
                return False
            
            # Get pre-copy statistics
            logger.info(f"Analyzing source directory {data_path}...")
            source_stats = get_directory_stats(data_path)
            logger.info(f"Source directory stats: {source_stats['file_count']} files, total size: {format_size(source_stats['total_size'])}")
            
            # Extract drive number from Qdrive path
            drive_number = self._extract_qdrive_number(qdrive_drive)
            
            # Record source data information to log
            log_copy_operation(f"The source path of Qdrive {drive_number} is: {os.path.dirname(data_path)}, The size of Qdrive {drive_number} to be copied is: {str(source_stats['total_size'])} bytes, and file number is {str(source_stats['file_count'])};")
            
            # Generate and record directory tree
            tree_str = generate_directory_tree(data_path)
            log_copy_operation(tree_str, 'filelist')
            
            target_data_path = os.path.join(transfer_drive, 'data')
            os.makedirs(target_data_path, exist_ok=True)
            
            # Record copy start
            log_copy_operation(f"Qdrive {drive_number} data started to copy to {transfer_drive};")
            
            # Create progress bar
            progress_bar = create_progress_bar(source_stats['file_count'], f"Copying Qdrive data to Transfer drive")
            
            # Copy directory with auto-rename functionality
            success = copy_directory_with_rename(data_path, target_data_path, lambda x: update_progress(progress_bar, x))
            
            if success:
                # Get post-copy statistics
                target_stats = get_directory_stats(target_data_path)
                logger.info(f"Copy operation completed:")
                logger.info(f"  Source directory: {source_stats['file_count']} files, {format_size(source_stats['total_size'])}")
                logger.info(f"  Target directory: {target_stats['file_count']} files, {format_size(target_stats['total_size'])}")
                
                # Record copy completion statistics
                log_copy_operation(f"Qdrive {drive_number} data has been copied to {transfer_drive}, with data size: {str(target_stats['total_size'])} bytes, and file number is {str(target_stats['file_count'])};")
                
                # Record copy verification information
                try:
                    log_single_copy_verification(qdrive_drive, transfer_drive, source_stats, target_stats, 'Qdrive_Transfer')
                except Exception as e:
                    logger.warning(f"Error recording copy verification information: {e}")
                
                # Record copy success
                log_copy_operation(f"Qdrive {drive_number} data has been copied successfully;")
                
                close_progress(progress_bar)
                return True
            else:
                logger.error(f"Failed to copy directory")
                close_progress(progress_bar)
                return False
            
        except Exception as e:
            logger.error(f"Error copying Qdrive data to transfer drive: {e}")
            log_copy_operation(f"Error copying Qdrive {drive_number} data: {e}", is_error=True)
            return False
    
    def _copy_directory_with_progress(self, src: str, dst: str, progress_bar) -> bool:
        """带进度条的目录拷贝函数"""
        try:
            # 创建目标目录
            os.makedirs(dst, exist_ok=True)
            
            # 遍历源目录
            for root, dirs, files in os.walk(src):
                # 计算相对路径
                rel_path = os.path.relpath(root, src)
                target_dir = os.path.join(dst, rel_path)
                
                # 创建子目录
                os.makedirs(target_dir, exist_ok=True)
                
                # 拷贝文件
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_dir, file)
                    
                    try:
                        shutil.copy2(src_file, dst_file)
                        update_progress(progress_bar, 1)
                    except Exception as e:
                        logger.warning(f"拷贝文件 {src_file} 时出错: {e}")
                        continue
            
            return True
            
        except Exception as e:
            logger.error(f"拷贝目录时出错: {e}")
            return False
    
    def copy_vector_data_to_transfer(self, vector_drive: str, transfer_drive: str) -> bool:
        """将Vector数据拷贝到transfer盘（保持原始结构）"""
        try:
            logs_path = os.path.join(vector_drive, 'logs')
            if not os.path.exists(logs_path):
                logger.error(f"Vector数据盘 {vector_drive} 中未找到logs文件夹")
                return False
            
            # 获取拷贝前的统计信息
            logger.info(f"正在统计源目录 {logs_path} 的文件信息...")
            source_stats = get_directory_stats(logs_path)
            logger.info(f"源目录统计: {source_stats['file_count']} 个文件, 总大小: {format_size(source_stats['total_size'])}")
            
            target_logs_path = os.path.join(transfer_drive, 'logs')
            os.makedirs(target_logs_path, exist_ok=True)
            
            # 创建进度条
            progress_bar = create_progress_bar(source_stats['file_count'], f"拷贝Vector数据到Transfer盘")
            
            # 使用自动重命名功能拷贝目录
            success = copy_directory_with_rename(logs_path, target_logs_path, lambda x: update_progress(progress_bar, x))
            
            if success:
                # 获取拷贝后的统计信息
                target_stats = get_directory_stats(target_logs_path)
                logger.info(f"拷贝完成统计:")
                logger.info(f"  源目录: {source_stats['file_count']} 个文件, {format_size(source_stats['total_size'])}")
                logger.info(f"  目标目录: {target_stats['file_count']} 个文件, {format_size(target_stats['total_size'])}")
                
                # 验证拷贝结果
                if source_stats['file_count'] == target_stats['file_count']:
                    logger.info(f"✅ 文件数量验证成功: {source_stats['file_count']} = {target_stats['file_count']}")
                else:
                    logger.warning(f"⚠️ 文件数量不匹配: 源 {source_stats['file_count']} ≠ 目标 {target_stats['file_count']}")
                
                if abs(source_stats['total_size'] - target_stats['total_size']) < 1024:  # 允许1KB的误差
                    logger.info(f"✅ 文件大小验证成功: {format_size(source_stats['total_size'])} ≈ {format_size(target_stats['total_size'])}")
                else:
                    logger.warning(f"⚠️ 文件大小不匹配: 源 {format_size(source_stats['total_size'])} ≠ 目标 {format_size(target_stats['total_size'])}")
            
            close_progress(progress_bar)
            return success
            
        except Exception as e:
            logger.error(f"拷贝Vector数据到transfer盘时出错: {e}")
            return False
    
    def copy_vector_data_to_backup(self, vector_drive: str, backup_drive: str, target_dir: str = None) -> bool:
        """Copy Vector data to backup drive (maintain original structure)"""
        try:
            logs_path = os.path.join(vector_drive, 'logs')
            if not os.path.exists(logs_path):
                logger.error(f"Vector data drive {vector_drive} does not contain logs folder")
                return False
            
            # Get source directory statistics
            logger.info(f"Analyzing source directory {logs_path}...")
            source_stats = get_directory_stats(logs_path)
            logger.info(f"Source directory stats: {source_stats['file_count']} files, total size: {format_size(source_stats['total_size'])}")
            
            # If target directory is specified, use it; otherwise copy directly to backup drive root
            if target_dir:
                target_logs_path = target_dir
                logger.info(f"Using specified target directory: {target_logs_path}")
            else:
                # Fix: Copy directly to backup drive root instead of creating logs subdirectory
                target_logs_path = backup_drive
                logger.info(f"Using backup drive root as target: {target_logs_path}")
            
            os.makedirs(target_logs_path, exist_ok=True)
            
            # Create progress bar
            progress_bar = create_progress_bar(source_stats['file_count'], f"Copying Vector data to Backup drive")
            
            # Copy directory with auto-rename functionality
            success = copy_directory_with_rename(logs_path, target_logs_path, lambda x: update_progress(progress_bar, x))
            
            if success:
                # Get post-copy statistics
                target_stats = get_directory_stats(target_logs_path)
                logger.info(f"Copy operation completed:")
                logger.info(f"  Source directory: {source_stats['file_count']} files, {format_size(source_stats['total_size'])}")
                logger.info(f"  Target directory: {target_stats['file_count']} files, {format_size(target_stats['total_size'])}")
                
                # Verify copy results
                if source_stats['file_count'] == target_stats['file_count']:
                    logger.info(f"✅ File count verification successful: {source_stats['file_count']} = {target_stats['file_count']}")
                else:
                    logger.warning(f"⚠️ File count mismatch: source {source_stats['file_count']} ≠ target {target_stats['file_count']}")
                
                if abs(source_stats['total_size'] - target_stats['total_size']) < 1024:  # Allow 1KB tolerance
                    logger.info(f"✅ File size verification successful: {format_size(source_stats['total_size'])} ≈ {format_size(target_stats['total_size'])}")
                else:
                    logger.warning(f"⚠️ File size mismatch: source {format_size(source_stats['total_size'])} ≠ target {format_size(target_stats['total_size'])}")
            
            close_progress(progress_bar)
            return success
            
        except Exception as e:
            logger.error(f"Error copying Vector data to backup drive: {e}")
            return False
    
    def copy_qdrive_data_to_backup(self, qdrive_drive: str, backup_drive: str, qdrive_handler=None, drive_number=None) -> bool:
        """将Qdrive数据拷贝到backup盘（按新目录结构）"""
        try:
            data_path = os.path.join(qdrive_drive, 'data')
            if not os.path.exists(data_path):
                logger.error(f"Qdrive数据盘 {qdrive_drive} 中未找到data文件夹")
                return False
            
            # 获取拷贝前的统计信息
            logger.info(f"正在统计源目录 {data_path} 的文件信息...")
            source_stats = get_directory_stats(data_path)
            logger.info(f"源目录统计: {source_stats['file_count']} 个文件, 总大小: {format_size(source_stats['total_size'])}")
            
            # 优先使用QdriveDataHandler中保存的目录信息
            if qdrive_handler and qdrive_handler.backup_root_dir and os.path.exists(qdrive_handler.backup_root_dir):
                root_path = qdrive_handler.backup_root_dir
                logger.info(f"使用QdriveDataHandler中保存的根目录: {root_path}")
            else:
                # 查找backup盘中的根目录
                root_dirs = [d for d in os.listdir(backup_drive) 
                            if os.path.isdir(os.path.join(backup_drive, d)) 
                            and not d.startswith('.')]
                
                if not root_dirs:
                    logger.error("backup盘中未找到根目录，请先创建目录结构")
                    return False
                
                # 使用最新的根目录
                root_dir = sorted(root_dirs)[-1]
                root_path = os.path.join(backup_drive, root_dir)
                logger.info(f"使用检测到的根目录: {root_path}")
            
            # 优先使用传入的盘号，如果没有则从驱动器路径中提取
            if not drive_number:
                if '201' in qdrive_drive:
                    drive_number = '201'
                elif '203' in qdrive_drive:
                    drive_number = '203'
                elif '230' in qdrive_drive:
                    drive_number = '230'
                elif '231' in qdrive_drive:
                    drive_number = '231'
                else:
                    # 尝试从路径中提取数字
                    import re
                    match = re.search(r'(\d{3})', qdrive_drive)
                    if match:
                        drive_number = match.group(1)
            
            if not drive_number:
                logger.error(f"无法从驱动器路径 {qdrive_drive} 中提取盘号")
                return False
            
            # 查找对应的二级目录
            target_subdir = None
            for subdir in os.listdir(root_path):
                if drive_number in subdir:
                    target_subdir = subdir
                    break
            
            if not target_subdir:
                logger.error(f"在根目录 {os.path.basename(root_path)} 中未找到包含盘号 {drive_number} 的二级目录")
                return False
            
            # 在二级目录下创建data文件夹
            target_data_path = os.path.join(root_path, target_subdir, 'data')
            os.makedirs(target_data_path, exist_ok=True)
            
            # 创建进度条
            progress_bar = create_progress_bar(source_stats['file_count'], f"拷贝Qdrive数据到Backup盘({drive_number})")
            
            # 遍历源data目录，跳过2qd_3NRV1_v1这一级，直接拷贝时间目录
            success = True
            copied_files = 0
            
            try:
                # 遍历源data目录下的车型目录（如2qd_3NRV1_v1）
                for vehicle_dir in os.listdir(data_path):
                    vehicle_path = os.path.join(data_path, vehicle_dir)
                    if os.path.isdir(vehicle_path):
                        # 遍历车型目录下的时间目录（如2025_08_21-13_53）
                        for time_dir in os.listdir(vehicle_path):
                            time_path = os.path.join(vehicle_path, time_dir)
                            if os.path.isdir(time_path):
                                # 直接拷贝时间目录到目标data目录
                                target_time_path = os.path.join(target_data_path, time_dir)
                                
                                # 如果目标时间目录已存在，先删除
                                if os.path.exists(target_time_path):
                                    import shutil
                                    shutil.rmtree(target_time_path)
                                
                                # 拷贝时间目录及其内容
                                import shutil
                                shutil.copytree(time_path, target_time_path)
                                copied_files += 1
                                logger.info(f"已拷贝时间目录: {time_dir}")
                                
                                # 更新进度条
                                if progress_bar:
                                    update_progress(progress_bar, 1)
            except Exception as e:
                logger.error(f"拷贝时间目录时出错: {e}")
                success = False
            
            if success:
                # 获取拷贝后的统计信息
                target_stats = get_directory_stats(target_data_path)
                logger.info(f"拷贝完成统计:")
                logger.info(f"  源目录: {source_stats['file_count']} 个文件, {format_size(source_stats['total_size'])}")
                logger.info(f"  目标目录: {target_stats['file_count']} 个文件, {format_size(target_stats['total_size'])}")
                
                # 验证拷贝结果
                if source_stats['file_count'] == target_stats['file_count']:
                    logger.info(f"✅ 文件数量验证成功: {source_stats['file_count']} = {target_stats['file_count']}")
                else:
                    logger.warning(f"⚠️ 文件数量验证: 源 {source_stats['file_count']} ≠ 目标 {target_stats['file_count']}")
                
                if abs(source_stats['total_size'] - target_stats['total_size']) < 1024:  # 允许1KB的误差
                    logger.info(f"✅ 文件大小验证成功: {format_size(source_stats['total_size'])} ≈ {format_size(target_stats['total_size'])}")
                else:
                    logger.warning(f"⚠️ 文件大小验证: 源 {format_size(source_stats['total_size'])} ≈ 目标 {format_size(target_stats['total_size'])}")
                
                # 记录拷贝校验信息
                try:
                    log_single_copy_verification(qdrive_drive, backup_drive, source_stats, target_stats, 'Qdrive_Backup')
                except Exception as e:
                    logger.warning(f"记录拷贝校验信息时出错: {e}")
                
                logger.info(f"✅ 成功拷贝 {copied_files} 个时间目录到 {target_data_path}")
            
            close_progress(progress_bar)
            return success
            
        except Exception as e:
            logger.error(f"拷贝Qdrive数据到backup盘时出错: {e}")
            return False
    
    def execute_data_copy_plan(self) -> bool:
        """执行完整的数据拷贝计划"""
        try:
            logger.info("开始执行数据拷贝计划")
            
            # 1. 识别所有驱动器
            qdrive_drives, vector_drives, transfer_drives, backup_drives = self.identify_data_drives()
            
            if not qdrive_drives and not vector_drives:
                logger.error("未找到任何数据源盘")
                return False
            
            if not transfer_drives and not backup_drives:
                logger.error("未找到任何目标盘")
                return False
            
            # 2. 检查Vector数据日期
            for vector_drive in vector_drives:
                is_single_date, dates = self.check_vector_data_dates(vector_drive)
                if is_single_date:
                    print(f"\nVector数据盘 {vector_drive} 包含单个日期数据: {dates[0]}")
                    confirm = input("确认拷贝此数据？(y/n): ").lower().strip()
                    if confirm != 'y':
                        logger.info(f"用户取消拷贝Vector数据盘 {vector_drive}")
                        vector_drives.remove(vector_drive)
                else:
                    print(f"\nVector数据盘 {vector_drive} 包含多个日期数据: {dates}")
                    print("暂停拷贝，请手动处理")
                    vector_drives.remove(vector_drive)
            
            # 3. 拷贝到transfer盘（并行处理）
            if transfer_drives:
                logger.info("开始并行拷贝数据到transfer盘")
                transfer_drive = transfer_drives[0]  # 使用第一个transfer盘
                
                # 并行拷贝Qdrive数据
                if qdrive_drives:
                    logger.info(f"并行拷贝 {len(qdrive_drives)} 个Qdrive数据盘到transfer盘")
                    self._parallel_copy_qdrive_to_transfer(qdrive_drives, transfer_drive)
                
                # 并行拷贝Vector数据
                if vector_drives:
                    logger.info(f"并行拷贝 {len(vector_drives)} 个Vector数据盘到transfer盘")
                    self._parallel_copy_vector_to_transfer(vector_drives, transfer_drive)
            
            # 4. 拷贝到backup盘（并行处理）
            if backup_drives:
                logger.info("开始并行拷贝数据到backup盘")
                backup_drive = backup_drives[0]  # 使用第一个backup盘
                
                # 并行拷贝Vector数据（保持原始结构）
                if vector_drives:
                    logger.info(f"并行拷贝 {len(vector_drives)} 个Vector数据盘到backup盘")
                    self._parallel_copy_vector_to_backup(vector_drives, backup_drive)
                
                # 创建Qdrive数据的目录结构
                if qdrive_drives:
                    if self.create_backup_directory_structure(backup_drive, qdrive_drives):
                        # 并行拷贝Qdrive数据到新目录结构
                        logger.info(f"并行拷贝 {len(qdrive_drives)} 个Qdrive数据盘到backup盘")
                        self._parallel_copy_qdrive_to_backup(qdrive_drives, backup_drive)
            
            logger.info("数据拷贝计划执行完成")
            return True
            
        except Exception as e:
            logger.error(f"执行数据拷贝计划时出错: {e}")
            return False
    
    def _parallel_copy_qdrive_to_transfer(self, qdrive_drives: List[str], transfer_drive: str):
        """并行拷贝Qdrive数据到transfer盘"""
        try:
            with ThreadPoolExecutor(max_workers=min(len(qdrive_drives), 4)) as executor:
                # 提交所有拷贝任务
                future_to_drive = {
                    executor.submit(self.copy_qdrive_data_to_transfer, drive, transfer_drive): drive
                    for drive in qdrive_drives
                }
                
                # 等待所有任务完成
                for future in as_completed(future_to_drive):
                    drive = future_to_drive[future]
                    try:
                        success = future.result()
                        if success:
                            logger.info(f"✅ 并行拷贝Qdrive数据盘 {drive} 到transfer盘成功")
                        else:
                            logger.error(f"❌ 并行拷贝Qdrive数据盘 {drive} 到transfer盘失败")
                    except Exception as e:
                        logger.error(f"❌ 并行拷贝Qdrive数据盘 {drive} 时出错: {e}")
                        
        except Exception as e:
            logger.error(f"并行拷贝Qdrive数据到transfer盘时出错: {e}")
    
    def _parallel_copy_vector_to_transfer(self, vector_drives: List[str], transfer_drive: str):
        """并行拷贝Vector数据到transfer盘"""
        try:
            with ThreadPoolExecutor(max_workers=min(len(vector_drives), 4)) as executor:
                # 提交所有拷贝任务
                future_to_drive = {
                    executor.submit(self.copy_vector_data_to_transfer, drive, transfer_drive): drive
                    for drive in vector_drives
                }
                
                # 等待所有任务完成
                for future in as_completed(future_to_drive):
                    drive = future_to_drive[future]
                    try:
                        success = future.result()
                        if success:
                            logger.info(f"✅ 并行拷贝Vector数据盘 {drive} 到transfer盘成功")
                        else:
                            logger.error(f"❌ 并行拷贝Vector数据盘 {drive} 到transfer盘失败")
                    except Exception as e:
                        logger.error(f"❌ 并行拷贝Vector数据盘 {drive} 时出错: {e}")
                        
        except Exception as e:
            logger.error(f"并行拷贝Vector数据到transfer盘时出错: {e}")
    
    def _parallel_copy_vector_to_backup(self, vector_drives: List[str], backup_drive: str):
        """并行拷贝Vector数据到backup盘"""
        try:
            with ThreadPoolExecutor(max_workers=min(len(vector_drives), 4)) as executor:
                # 提交所有拷贝任务
                future_to_drive = {
                    executor.submit(self.copy_vector_data_to_backup, drive, backup_drive): drive
                    for drive in vector_drives
                }
                
                # 等待所有任务完成
                for future in as_completed(future_to_drive):
                    drive = future_to_drive[future]
                    try:
                        success = future.result()
                        if success:
                            logger.info(f"✅ 并行拷贝Vector数据盘 {drive} 到backup盘成功")
                        else:
                            logger.error(f"❌ 并行拷贝Vector数据盘 {drive} 到backup盘失败")
                    except Exception as e:
                        logger.error(f"❌ 并行拷贝Vector数据盘 {drive} 时出错: {e}")
                        
        except Exception as e:
            logger.error(f"并行拷贝Vector数据到backup盘时出错: {e}")
    
    def _parallel_copy_qdrive_to_backup(self, qdrive_drives: List[str], backup_drive: str):
        """并行拷贝Qdrive数据到backup盘"""
        try:
            with ThreadPoolExecutor(max_workers=min(len(qdrive_drives), 4)) as executor:
                # 提交所有拷贝任务
                future_to_drive = {
                    executor.submit(self.copy_qdrive_data_to_backup, drive, backup_drive): drive
                    for drive in qdrive_drives
                }
                
                # 等待所有任务完成
                for future in as_completed(future_to_drive):
                    drive = future_to_drive[future]
                    try:
                        success = future.result()
                        if success:
                            logger.info(f"✅ 并行拷贝Qdrive数据盘 {drive} 到backup盘成功")
                        else:
                            logger.error(f"❌ 并行拷贝Qdrive数据盘 {drive} 到backup盘失败")
                    except Exception as e:
                        logger.error(f"❌ 并行拷贝Qdrive数据盘 {drive} 时出错: {e}")
                        
        except Exception as e:
            logger.error(f"并行拷贝Qdrive数据到backup盘时出错: {e}")
    
    def print_summary(self):
        """打印系统检测摘要"""
        print("\n" + "="*60)
        print("跨平台系统检测与数据拷贝摘要")
        print("="*60)
        
        print(f"\n操作系统: {self.os_type}")
        print(f"总驱动器数量: {len(self.drives)}")
        print(f"系统驱动器: {len(self.system_drives)}")
        print(f"源数据驱动器: {len(self.source_drives)}")
        print(f"目标备份驱动器: {len(self.destination_drives)}")
        
        print(f"\n数据驱动器识别:")
        print(f"  Qdrive数据盘: {len(self.qdrive_drives)}")
        print(f"  Vector数据盘: {len(self.vector_drives)}")
        print(f"  Transfer目标盘: {len(self.transfer_drives)}")
        print(f"  Backup目标盘: {len(self.backup_drives)}")
        
        print("\n驱动器详细信息:")
        print("-" * 60)
        
        for drive, info in self.drive_info.items():
            if 'error' not in info:
                total_gb = info['total'] / (1024**3)
                used_gb = info['used'] / (1024**3)
                free_gb = info['free'] / (1024**3)
                
                print(f"\n驱动器: {drive}")
                print(f"  卷标: {info['volume_name']}")
                print(f"  文件系统: {info['fs_type']}")
                print(f"  总容量: {total_gb:.2f} GB")
                print(f"  已使用: {used_gb:.2f} GB")
                print(f"  可用空间: {free_gb:.2f} GB")
                if self.os_type == "windows":
                    print(f"  BitLocker状态: {info.get('bitlocker_status', 'Unknown')}")
                print(f"  类型: ", end="")
                
                if info['is_system']:
                    print("系统盘", end=" ")
                if info['is_source']:
                    print("源数据盘", end=" ")
                if info['is_destination']:
                    print("目标备份盘", end=" ")
                print()
            else:
                print(f"\n驱动器: {drive}")
                print(f"  错误: {info['error']}")
        
        # 记录拷贝完成后的校验总结到日志
        try:
            source_drives = self.qdrive_drives + self.vector_drives
            log_copy_verification_summary(source_drives, self.transfer_drives, self.backup_drives)
        except Exception as e:
            logger.warning(f"记录拷贝校验总结到日志时出错: {e}")
        
        print("\n" + "="*60) 