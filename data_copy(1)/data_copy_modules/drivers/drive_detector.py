#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驱动器检测模块
Drive Detection Module
"""

import os
import platform
import psutil
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class DriveDetector:
    """驱动器检测器类"""
    
    def __init__(self):
        """初始化驱动器检测器"""
        self.drives = []
        self.system_drives = []
        self.source_drives = []
        self.destination_drives = []
        self.drive_info = {}
        self.os_type = self._detect_os()
        
        # 数据拷贝相关属性
        self.qdrive_drives = []  # Qdrive数据盘（201, 203, 230, 231）
        self.vector_drives = []  # Vector数据盘（USB接口）
        self.transfer_drives = []  # transfer ssd目标盘
        self.backup_drives = []   # backup ssd目标盘
        
        logger.info(f"检测到操作系统: {self.os_type}")
    
    def _detect_os(self) -> str:
        """检测操作系统类型"""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        else:
            return "unknown"
    
    def detect_all_drives(self) -> List[str]:
        """
        检测系统中所有可用的驱动器
        
        Returns:
            List[str]: 驱动器路径列表
        """
        try:
            drives = []
            
            if self.os_type == "windows":
                # Windows系统：检测盘符
                for partition in psutil.disk_partitions():
                    if partition.device and os.path.exists(partition.device):
                        drives.append(partition.device)
            else:
                # Linux/macOS系统：检测挂载点
                for partition in psutil.disk_partitions():
                    if partition.mountpoint and os.path.exists(partition.mountpoint):
                        drives.append(partition.mountpoint)
            
            self.drives = drives
            logger.info(f"检测到 {len(drives)} 个驱动器: {drives}")
            return drives
            
        except Exception as e:
            logger.error(f"检测驱动器时出错: {e}")
            return []
    
    def get_system_drives(self) -> List[str]:
        """
        获取系统驱动器列表
        
        Returns:
            List[str]: 系统驱动器列表
        """
        system_drives = []
        
        try:
            if self.os_type == "windows":
                # Windows系统：检测系统盘
                system_root = os.environ.get('SystemRoot', 'C:\\Windows')
                system_drive = os.path.splitdrive(system_root)[0] + '\\'
                if system_drive in self.drives:
                    system_drives.append(system_drive)
                
                # 检测其他系统相关驱动器
                for drive in self.drives:
                    if self._is_windows_system_drive(drive):
                        if drive not in system_drives:
                            system_drives.append(drive)
                            
            elif self.os_type == "linux":
                # Linux系统：检测系统挂载点
                root_drive = '/'
                if root_drive in self.drives:
                    system_drives.append(root_drive)
                
                # 检查其他系统挂载点
                system_mounts = ['/boot', '/boot/efi', '/usr', '/var', '/tmp', '/proc', '/sys']
                for mount in system_mounts:
                    if mount in self.drives:
                        system_drives.append(mount)
                        
            elif self.os_type == "macos":
                # macOS系统：检测系统挂载点
                root_drive = '/'
                if root_drive in self.drives:
                    system_drives.append(root_drive)
                
                # 检查其他系统挂载点
                system_mounts = ['/System', '/Applications', '/Users', '/private', '/Volumes']
                for mount in system_mounts:
                    if mount in self.drives:
                        system_drives.append(mount)
                        
        except Exception as e:
            logger.error(f"获取系统驱动器时出错: {e}")
            if self.os_type == "windows":
                system_drives = ['C:\\']
            else:
                system_drives = ['/']
        
        self.system_drives = system_drives
        logger.info(f"识别到系统驱动器: {system_drives}")
        return system_drives
    
    def _is_windows_system_drive(self, drive: str) -> bool:
        """判断Windows驱动器是否为系统相关驱动器"""
        try:
            # 检查是否包含系统文件夹
            system_folders = ['Windows', 'Program Files', 'Program Files (x86)', 'Users', 'ProgramData']
            for folder in system_folders:
                if os.path.exists(os.path.join(drive, folder)):
                    return True
            
            # 检查是否为EFI分区
            if self._is_efi_partition(drive):
                return True
                
            # 检查是否为恢复分区
            if self._is_recovery_partition(drive):
                return True
                
        except Exception:
            pass
            
        return False
    
    def _is_efi_partition(self, drive: str) -> bool:
        """检查是否为EFI分区"""
        try:
            efi_path = os.path.join(drive, 'EFI')
            return os.path.exists(efi_path) and os.path.isdir(efi_path)
        except:
            return False
    
    def _is_recovery_partition(self, drive: str) -> bool:
        """检查是否为恢复分区"""
        try:
            recovery_path = os.path.join(drive, 'Recovery')
            return os.path.exists(recovery_path) and os.path.isdir(recovery_path)
        except:
            return False
    
    def exclude_system_drives(self) -> List[str]:
        """
        排除系统驱动器，返回可用于备份的驱动器
        
        Returns:
            List[str]: 排除系统驱动器后的驱动器列表
        """
        if not self.system_drives:
            self.get_system_drives()
            
        available_drives = [drive for drive in self.drives 
                           if drive not in self.system_drives]
        
        logger.info(f"排除系统驱动器后，可用驱动器: {available_drives}")
        return available_drives
    
    def classify_drives(self) -> Tuple[List[str], List[str]]:
        """
        将驱动器分类为源数据盘和目标备份盘
        
        Returns:
            Tuple[List[str], List[str]]: (源数据驱动器列表, 目标备份驱动器列表)
        """
        available_drives = self.exclude_system_drives()
        
        source_drives = []
        destination_drives = []
        
        for drive in available_drives:
            if self._is_source_drive(drive):
                source_drives.append(drive)
            elif self._is_destination_drive(drive):
                destination_drives.append(drive)
            else:
                # 如果无法确定，默认作为目标盘
                destination_drives.append(drive)
        
        self.source_drives = source_drives
        self.destination_drives = destination_drives
        
        logger.info(f"驱动器分类完成:")
        logger.info(f"  源数据驱动器: {source_drives}")
        logger.info(f"  目标备份驱动器: {destination_drives}")
        
        return source_drives, destination_drives
    
    def _is_source_drive(self, drive: str) -> bool:
        """
        判断驱动器是否为源数据驱动器
        
        Args:
            drive: 驱动器路径
            
        Returns:
            bool: 是否为源数据驱动器
        """
        try:
            # 检查是否包含数据文件夹
            data_folders = ['data', 'record', 'logs', 'backup', 'archive', 'source', 'raw']
            for folder in data_folders:
                if os.path.exists(os.path.join(drive, folder)):
                    return True
            
            # 检查是否包含特定文件类型
            data_files = ['.txt', '.log', '.csv', '.json', '.xml', '.dat', '.bin']
            try:
                for root, dirs, files in os.walk(drive, topdown=True):
                    for file in files:
                        if any(file.endswith(ext) for ext in data_files):
                            return True
                    break  # 只检查第一层目录
            except PermissionError:
                pass  # 忽略权限错误
                
        except Exception:
            pass
            
        return False
    
    def _is_destination_drive(self, drive: str) -> bool:
        """
        判断驱动器是否为目标备份驱动器
        
        Args:
            drive: 驱动器路径
            
        Returns:
            bool: 是否为目标备份驱动器
        """
        try:
            # 检查是否为几乎空的驱动器
            if self._is_disk_almost_empty(drive):
                return True
            
            # 检查是否包含备份相关文件夹
            backup_folders = ['backup', 'archive', 'copy', 'mirror', 'destination', 'target', 'temp']
            for folder in backup_folders:
                if os.path.exists(os.path.join(drive, folder)):
                    return True
                    
        except Exception:
            pass
            
        return False
    
    def _is_disk_almost_empty(self, drive: str) -> bool:
        """
        判断驱动器是否几乎为空
        
        Args:
            drive: 驱动器路径
            
        Returns:
            bool: 是否几乎为空
        """
        try:
            # 根据操作系统定义要排除的文件夹
            if self.os_type == "windows":
                excluded_folders = ['$RECYCLE.BIN', 'System Volume Information', 'found.000']
            elif self.os_type == "linux":
                excluded_folders = ['.Trash-1000', '.cache', 'lost+found']
            elif self.os_type == "macos":
                excluded_folders = ['.Trashes', '.Spotlight-V100', '.fseventsd']
            else:
                excluded_folders = []
            
            entries = os.listdir(drive)
            # 过滤掉排除的文件夹
            filtered_entries = [entry for entry in entries 
                              if entry not in excluded_folders 
                              and not entry.startswith('.')]
            
            # 如果过滤后的条目数量很少，认为磁盘几乎为空
            return len(filtered_entries) <= 2
            
        except Exception:
            return False
    
    def get_drive_information(self) -> Dict[str, Dict]:
        """
        获取所有驱动器的详细信息
        
        Returns:
            Dict[str, Dict]: 驱动器信息字典
        """
        drive_info = {}
        
        for drive in self.drives:
            try:
                # 获取磁盘使用情况
                usage = psutil.disk_usage(drive)
                
                # 获取文件系统信息
                fs_type = "Unknown"
                try:
                    for partition in psutil.disk_partitions():
                        if (self.os_type == "windows" and partition.device == drive) or \
                           (self.os_type != "windows" and partition.mountpoint == drive):
                            fs_type = partition.fstype or "Unknown"
                            break
                except:
                    fs_type = "Unknown"
                
                # 获取卷标信息
                volume_name = self._get_volume_name(drive)
                
                drive_info[drive] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'volume_name': volume_name,
                    'fs_type': fs_type,
                    'is_system': drive in self.system_drives,
                    'is_source': drive in self.source_drives,
                    'is_destination': drive in self.destination_drives
                }
                
            except Exception as e:
                logger.error(f"获取驱动器 {drive} 信息时出错: {e}")
                drive_info[drive] = {'error': str(e)}
        
        self.drive_info = drive_info
        return drive_info
    
    def _get_volume_name(self, drive: str) -> str:
        """获取驱动器卷标"""
        try:
            if self.os_type == "windows":
                # Windows系统：尝试获取卷标
                try:
                    import win32api
                    volume_name = win32api.GetVolumeInformation(drive)[0]
                    return volume_name if volume_name else os.path.basename(drive) or drive
                except ImportError:
                    return os.path.basename(drive) or drive
            else:
                # Linux/macOS系统：使用路径名
                return os.path.basename(drive) or drive
        except Exception:
            return drive
    
    def identify_data_drives(self) -> Tuple[List[str], List[str], List[str], List[str]]:
        """
        识别Qdrive、Vector、transfer和backup驱动器
        
        Returns:
            Tuple[List[str], List[str], List[str], List[str]]: (qdrive_drives, vector_drives, transfer_drives, backup_drives)
        """
        available_drives = self.exclude_system_drives()
        
        qdrive_drives = []
        vector_drives = []
        transfer_drives = []
        backup_drives = []
        
        for drive in available_drives:
            try:
                # 检查是否为Qdrive数据盘（包含data文件夹）
                if os.path.exists(os.path.join(drive, 'data')):
                    qdrive_drives.append(drive)
                    logger.info(f"识别到Qdrive数据盘: {drive}")
                    continue
                
                # 检查是否为Vector数据盘（包含logs文件夹）
                if os.path.exists(os.path.join(drive, 'logs')):
                    vector_drives.append(drive)
                    logger.info(f"识别到Vector数据盘: {drive}")
                    continue
                
                # 检查是否为transfer盘（卷标包含transfer或几乎为空）
                volume_name = self._get_volume_name(drive).lower()
                if 'transfer' in volume_name or self._is_disk_almost_empty(drive):
                    transfer_drives.append(drive)
                    logger.info(f"识别到transfer目标盘: {drive}")
                    continue
                
                # 检查是否为backup盘（卷标包含backup）
                if 'backup' in volume_name:
                    backup_drives.append(drive)
                    logger.info(f"识别到backup目标盘: {drive}")
                    continue
                
                # 如果无法确定，默认作为backup盘
                backup_drives.append(drive)
                logger.info(f"未识别驱动器类型，默认作为backup盘: {drive}")
                
            except Exception as e:
                logger.error(f"识别驱动器 {drive} 类型时出错: {e}")
                continue
        
        self.qdrive_drives = qdrive_drives
        self.vector_drives = vector_drives
        self.transfer_drives = transfer_drives
        self.backup_drives = backup_drives
        
        logger.info(f"驱动器识别完成:")
        logger.info(f"  Qdrive数据盘: {qdrive_drives}")
        logger.info(f"  Vector数据盘: {vector_drives}")
        logger.info(f"  Transfer目标盘: {transfer_drives}")
        logger.info(f"  Backup目标盘: {backup_drives}")
        
        return qdrive_drives, vector_drives, transfer_drives, backup_drives 