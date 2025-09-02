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
        检测系统中所有可用的驱动器 - 包括加密驱动器
        
        Returns:
            List[str]: 驱动器路径列表
        """
        try:
            drives = []
            
            if self.os_type == "windows":
                # Windows系统：检测所有盘符，包括加密的
                for partition in psutil.disk_partitions():
                    if partition.device:
                        # 检查驱动器是否存在（包括加密的）
                        if os.path.exists(partition.device):
                            drives.append(partition.device)
                            logger.debug(f"检测到驱动器: {partition.device}")
                        else:
                            # 即使路径不存在，也尝试添加（可能是加密驱动器）
                            logger.debug(f"检测到可能加密的驱动器: {partition.device} (路径不存在)")
                            drives.append(partition.device)
            else:
                # Linux/macOS系统：检测挂载点
                for partition in psutil.disk_partitions():
                    if partition.mountpoint and self._is_drive_accessible(partition.mountpoint):
                        drives.append(partition.mountpoint)
            
            self.drives = drives
            logger.info(f"检测到 {len(drives)} 个驱动器: {drives}")
            return drives
            
        except Exception as e:
            logger.error(f"检测驱动器时出错: {e}")
            return []
    
    def _is_drive_accessible(self, drive_path: str) -> bool:
        """
        检查驱动器是否可访问 - 包括加密驱动器
        
        Args:
            drive_path: 驱动器路径
            
        Returns:
            bool: 是否可访问
        """
        try:
            # 检查路径是否存在（包括加密的驱动器）
            if not os.path.exists(drive_path):
                return False
            
            # 尝试获取基本信息，不扫描内容
            if self.os_type == "windows":
                # Windows: 检查盘符是否可访问，包括加密的
                try:
                    # 尝试访问驱动器根目录
                    os.listdir(drive_path)
                    return True
                except (PermissionError, OSError) as e:
                    # 权限错误可能是加密驱动器，仍然认为可访问
                    logger.debug(f"驱动器 {drive_path} 访问受限，可能是加密驱动器: {e}")
                    return True
                except Exception as e:
                    logger.debug(f"驱动器 {drive_path} 访问检查失败: {e}")
                    return False
            else:
                # Linux/macOS: 检查挂载点是否可访问
                return os.access(drive_path, os.R_OK)
                
        except (PermissionError, OSError) as e:
            # 权限错误可能是加密驱动器，仍然认为可访问
            logger.debug(f"驱动器 {drive_path} 访问受限，可能是加密驱动器: {e}")
            return True
        except Exception as e:
            logger.debug(f"驱动器 {drive_path} 访问检查失败: {e}")
            return False
    
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
        """判断Windows驱动器是否为系统相关驱动器 - 优化版本，不扫描内容"""
        try:
            # 只检查常见的系统盘符，不扫描内容
            system_drive_letters = ['C:', 'D:', 'E:']  # 常见的系统盘符
            
            # 检查盘符
            drive_letter = drive.rstrip('\\').upper()
            if drive_letter in system_drive_letters:
                return True
            
            # 检查是否为EFI分区（通过卷标判断，不扫描内容）
            if self._is_efi_partition(drive):
                return True
                
            # 检查是否为恢复分区（通过卷标判断，不扫描内容）
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
        判断驱动器是否为源数据驱动器 - 优化版本，不扫描内容
        
        Args:
            drive: 驱动器路径
            
        Returns:
            bool: 是否为源数据驱动器
        """
        try:
            # 只检查根目录，不深入扫描
            if not os.access(drive, os.R_OK):
                return False
            
            # 快速检查根目录下的文件夹
            try:
                entries = os.listdir(drive)
                # 检查是否包含数据相关文件夹
                data_folders = ['data', 'record', 'logs', 'backup', 'archive', 'source', 'raw']
                for folder in data_folders:
                    if folder in entries:
                        return True
                
                # 检查卷标是否包含数据相关关键词
                volume_name = self._get_volume_name(drive).lower()
                data_keywords = ['data', 'record', 'log', 'source', 'raw', '201', '203', '230', '231']
                if any(keyword in volume_name for keyword in data_keywords):
                    return True
                    
            except (PermissionError, OSError):
                # 权限错误，可能是加密盘，默认作为源盘
                logger.debug(f"驱动器 {drive} 访问受限，可能是加密盘，标记为源盘")
                return True
                
        except Exception:
            pass
            
        return False
    
    def _is_destination_drive(self, drive: str) -> bool:
        """
        判断驱动器是否为目标备份驱动器 - 优化版本，不扫描内容
        
        Args:
            drive: 驱动器路径
            
        Returns:
            bool: 是否为目标备份驱动器
        """
        try:
            # 检查卷标是否包含备份相关关键词
            volume_name = self._get_volume_name(drive).lower()
            backup_keywords = ['backup', 'archive', 'copy', 'mirror', 'destination', 'target', 'temp', 'transfer']
            if any(keyword in volume_name for keyword in backup_keywords):
                return True
            
            # 检查是否为几乎空的驱动器（快速检查）
            if self._is_disk_almost_empty(drive):
                return True
                    
        except Exception:
            pass
            
        return False
    
    def _is_disk_almost_empty(self, drive: str) -> bool:
        """
        判断驱动器是否几乎为空 - 优化版本，不深入扫描
        
        Args:
            drive: 驱动器路径
            
        Returns:
            bool: 是否几乎为空
        """
        try:
            if not os.access(drive, os.R_OK):
                return False
            
            # 根据操作系统定义要排除的文件夹
            if self.os_type == "windows":
                excluded_folders = ['$RECYCLE.BIN', 'System Volume Information', 'found.000']
            elif self.os_type == "linux":
                excluded_folders = ['.Trash-1000', '.cache', 'lost+found']
            elif self.os_type == "macos":
                excluded_folders = ['.Trashes', '.Spotlight-V100', '.fseventsd']
            else:
                excluded_folders = []
            
            try:
                entries = os.listdir(drive)
                # 过滤掉排除的文件夹
                filtered_entries = [entry for entry in entries 
                                  if entry not in excluded_folders 
                                  and not entry.startswith('.')]
                
                # 如果过滤后的条目数量很少，认为磁盘几乎为空
                return len(filtered_entries) <= 2
                
            except (PermissionError, OSError):
                # 权限错误，可能是加密盘，默认作为目标盘
                return True
                
        except Exception:
            return False
    
    def get_drive_information(self) -> Dict[str, Dict]:
        """
        获取所有驱动器的基本信息 - 包括加密驱动器
        
        Returns:
            Dict[str, Dict]: 驱动器信息字典
        """
        drive_info = {}
        
        for drive in self.drives:
            try:
                # 检查驱动器是否可访问
                is_accessible = False
                try:
                    os.listdir(drive)
                    is_accessible = True
                except (PermissionError, OSError):
                    is_accessible = False
                
                # 获取磁盘使用情况（如果可访问）
                total = used = free = 0
                if is_accessible:
                    try:
                        usage = psutil.disk_usage(drive)
                        total = usage.total
                        used = usage.used
                        free = usage.free
                    except (PermissionError, OSError):
                        pass
                
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
                
                # 获取卷标信息（快速获取）
                volume_name = self._get_volume_name(drive)
                
                # 判断是否是加密驱动器
                is_encrypted = False
                if not is_accessible:
                    is_encrypted = True
                elif fs_type == "Unknown" and not is_accessible:
                    is_encrypted = True
                
                # 进一步检查是否是BitLocker加密盘
                if is_encrypted and self.os_type == "windows":
                    try:
                        # 尝试使用manage-bde命令检查BitLocker状态
                        import subprocess
                        drive_letter = drive.rstrip('\\')
                        result = subprocess.run(
                            ["manage-bde", "-status", drive_letter],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            output = result.stdout
                            if "Lock Status:" in output:
                                is_encrypted = True
                                logger.debug(f"驱动器 {drive} 被识别为BitLocker加密盘")
                    except Exception as e:
                        logger.debug(f"检查驱动器 {drive} 的BitLocker状态时出错: {e}")
                        # 即使检查失败，仍然标记为加密盘
                        is_encrypted = True
                
                # 获取BitLocker状态（如果可用）
                bitlocker_status = "Unknown"
                if is_encrypted and self.os_type == "windows":
                    try:
                        import subprocess
                        drive_letter = drive.rstrip('\\')
                        result = subprocess.run(
                            ["manage-bde", "-status", drive_letter],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            output = result.stdout
                            # 查找锁定状态（支持中英文）
                            import re
                            
                            # 优先尝试匹配中文状态（因为系统是中文）
                            match = re.search(r'锁定状态:\s+(.*)', output)
                            if match:
                                status_text = match.group(1).strip()
                                if "已锁定" in status_text:
                                    bitlocker_status = "Locked"
                                elif "已解锁" in status_text:
                                    bitlocker_status = "Unlocked"
                                else:
                                    bitlocker_status = "Unknown"
                            else:
                                # 尝试匹配英文状态
                                match = re.search(r'Lock Status:\s+(.*)', output)
                                if match:
                                    status_text = match.group(1).strip()
                                    if "Locked" in status_text:
                                        bitlocker_status = "Locked"
                                    elif "Unlocked" in status_text:
                                        bitlocker_status = "Unlocked"
                                    else:
                                        bitlocker_status = "Unknown"
                                else:
                                    # 如果没有找到明确的状态，检查其他指标
                                    if "BitLocker" in output:
                                        # 检查是否包含锁定相关关键词
                                        if any(keyword in output for keyword in ["已锁定", "Locked", "锁定"]):
                                            bitlocker_status = "Locked"
                                        elif any(keyword in output for keyword in ["已解锁", "Unlocked", "解锁"]):
                                            bitlocker_status = "Unlocked"
                                        else:
                                            # 有BitLocker但状态不明，默认认为已锁定
                                            bitlocker_status = "Locked"
                                    else:
                                        # 如果驱动器被识别为加密但manage-bde命令没有返回BitLocker信息
                                        # 可能是因为驱动器被锁定，默认认为已锁定
                                        bitlocker_status = "Locked"
                        else:
                            # 命令失败，但驱动器被识别为加密，默认认为已锁定
                            bitlocker_status = "Locked"
                    except Exception as e:
                        logger.debug(f"获取驱动器 {drive} 的BitLocker状态时出错: {e}")
                        # 出错时，如果驱动器被识别为加密，默认认为已锁定
                        bitlocker_status = "Locked"
                
                drive_info[drive] = {
                    'total': total,
                    'used': used,
                    'free': free,
                    'volume_name': volume_name,
                    'fs_type': fs_type,
                    'is_accessible': is_accessible,
                    'is_encrypted': is_encrypted,
                    'bitlocker_status': bitlocker_status,
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
        """获取驱动器卷标 - 多种方法尝试"""
        try:
            if self.os_type == "windows":
                # 方法1: 尝试使用win32api
                try:
                    import win32api
                    volume_name = win32api.GetVolumeInformation(drive)[0]
                    if volume_name:
                        return volume_name
                except ImportError:
                    pass
                except (PermissionError, OSError):
                    pass
                
                # 方法2: 尝试使用subprocess调用Windows命令
                try:
                    import subprocess
                    result = subprocess.run(['wmic', 'logicaldisk', 'where', f'DeviceID="{drive[:-1]}"', 'get', 'VolumeName', '/value'], 
                                         capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if line.startswith('VolumeName='):
                                volume_name = line.split('=', 1)[1].strip()
                                if volume_name:
                                    return volume_name
                except Exception:
                    pass
                
                # 方法3: 尝试使用psutil获取标签
                try:
                    for partition in psutil.disk_partitions():
                        if partition.device == drive and hasattr(partition, 'label') and partition.label:
                            return partition.label
                except Exception:
                    pass
                
                # 方法4: 尝试读取驱动器属性文件
                try:
                    label_file = os.path.join(drive, 'System Volume Information', 'WPSettings.dat')
                    if os.path.exists(label_file):
                        # 这是一个简化的方法，实际可能需要更复杂的解析
                        return "System"
                except Exception:
                    pass
                
                # 方法5: 使用盘符作为备选
                return f"Drive_{drive[:-1]}"
            else:
                # Linux/macOS系统：使用路径名
                return os.path.basename(drive) or drive
        except Exception:
            return f"Drive_{drive[:-1]}" if drive.endswith('\\') else drive
    
    def _has_camera_fc_mp4_files(self, drive: str) -> bool:
        """
        Check if drive contains camera_fc*.mp4 files (indicates 201 drive)
        
        Args:
            drive: Drive path
            
        Returns:
            bool: True if contains camera_fc*.mp4 files
        """
        try:
            if not os.access(drive, os.R_OK):
                return False
            
            # Search for camera_fc*.mp4 files in the drive
            for root, dirs, files in os.walk(drive):
                for file in files:
                    if file.startswith('camera_fc') and file.endswith('.mp4'):
                        logger.debug(f"Found camera_fc*.mp4 file: {os.path.join(root, file)}")
                        return True
                # Limit search depth to avoid long scans
                if len(root.split(os.sep)) - len(drive.split(os.sep)) > 3:
                    dirs.clear()
            
            return False
        except Exception as e:
            logger.debug(f"Error checking camera_fc*.mp4 files in {drive}: {e}")
            return False
    
    def _has_camera_rc_mp4_files(self, drive: str) -> bool:
        """
        Check if drive contains camera_rc*.mp4 files (indicates 203 drive)
        
        Args:
            drive: Drive path
            
        Returns:
            bool: True if contains camera_rc*.mp4 files
        """
        try:
            if not os.access(drive, os.R_OK):
                return False
            
            # Search for camera_rc*.mp4 files in the drive
            for root, dirs, files in os.walk(drive):
                for file in files:
                    if file.startswith('camera_rc') and file.endswith('.mp4'):
                        logger.debug(f"Found camera_rc*.mp4 file: {os.path.join(root, file)}")
                        return True
                # Limit search depth to avoid long scans
                if len(root.split(os.sep)) - len(drive.split(os.sep)) > 3:
                    dirs.clear()
            
            return False
        except Exception as e:
            logger.debug(f"Error checking camera_rc*.mp4 files in {drive}: {e}")
            return False
    
    def _has_data_lidar_top_folder(self, drive: str) -> bool:
        """
        Check if drive contains data_lidar_top folder (indicates 230 drive)
        
        Args:
            drive: Drive path
            
        Returns:
            bool: True if contains data_lidar_top folder
        """
        try:
            if not os.access(drive, os.R_OK):
                return False
            
            # Search for data_lidar_top folder
            for root, dirs, files in os.walk(drive):
                if 'data_lidar_top' in dirs:
                    logger.debug(f"Found data_lidar_top folder: {os.path.join(root, 'data_lidar_top')}")
                    return True
                # Limit search depth to avoid long scans
                if len(root.split(os.sep)) - len(drive.split(os.sep)) > 3:
                    dirs.clear()
            
            return False
        except Exception as e:
            logger.debug(f"Error checking data_lidar_top folder in {drive}: {e}")
            return False
    
    def _has_data_lidar_front_folder(self, drive: str) -> bool:
        """
        Check if drive contains data_lidar_front folder (indicates 231 drive)
        
        Args:
            drive: Drive path
            
        Returns:
            bool: True if contains data_lidar_front folder
        """
        try:
            if not os.access(drive, os.R_OK):
                return False
            
            # Search for data_lidar_front folder
            for root, dirs, files in os.walk(drive):
                if 'data_lidar_front' in dirs:
                    logger.debug(f"Found data_lidar_front folder: {os.path.join(root, 'data_lidar_front')}")
                    return True
                # Limit search depth to avoid long scans
                if len(root.split(os.sep)) - len(drive.split(os.sep)) > 3:
                    dirs.clear()
            
            return False
        except Exception as e:
            logger.debug(f"Error checking data_lidar_front folder in {drive}: {e}")
            return False
    
    def _has_logs_folder(self, drive: str) -> bool:
        """
        Check if drive contains Logs or logs folder (indicates Vector drive)
        
        Args:
            drive: Drive path
            
        Returns:
            bool: True if contains Logs or logs folder
        """
        try:
            if not os.access(drive, os.R_OK):
                return False
            
            # Check for Logs or logs folder in root directory
            entries = os.listdir(drive)
            if 'Logs' in entries or 'logs' in entries:
                logger.debug(f"Found Logs/logs folder in {drive}")
                return True
            
            return False
        except Exception as e:
            logger.debug(f"Error checking Logs/logs folder in {drive}: {e}")
            return False
    
    def _is_echo_backup_drive(self, drive: str) -> bool:
        """
        Check if drive is Echo backup drive (Echo*backup)
        
        Args:
            drive: Drive path
            
        Returns:
            bool: True if is Echo backup drive
        """
        try:
            volume_name = self._get_volume_name(drive).lower()
            return volume_name.startswith('echo') and volume_name.endswith('backup')
        except Exception as e:
            logger.debug(f"Error checking Echo backup drive {drive}: {e}")
            return False
    
    def _is_echo_transfer_drive(self, drive: str) -> bool:
        """
        Check if drive is Echo transfer drive (Echo* but not ending with backup)
        
        Args:
            drive: Drive path
            
        Returns:
            bool: True if is Echo transfer drive
        """
        try:
            volume_name = self._get_volume_name(drive).lower()
            return volume_name.startswith('echo') and not volume_name.endswith('backup')
        except Exception as e:
            logger.debug(f"Error checking Echo transfer drive {drive}: {e}")
            return False

    def identify_data_drives(self, require_confirmation: bool = True) -> Tuple[List[str], List[str], List[str], List[str]]:
        """
        Automatically identify Qdrive (201, 203, 230, 231), Vector, transfer and backup drives
        
        Args:
            require_confirmation: Whether to require user confirmation
            
        Returns:
            Tuple[List[str], List[str], List[str], List[str]]: (qdrive_drives, vector_drives, transfer_drives, backup_drives)
        """
        # Perform automatic identification
        qdrive_drives, vector_drives, transfer_drives, backup_drives = self._perform_automatic_identification()
        
        # If confirmation is required, show results and get user confirmation
        if require_confirmation:
            return self._get_user_confirmation(qdrive_drives, vector_drives, transfer_drives, backup_drives)
        else:
            return qdrive_drives, vector_drives, transfer_drives, backup_drives
    
    def _perform_automatic_identification(self) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Perform automatic drive identification"""
        available_drives = self.exclude_system_drives()
        
        qdrive_201_drives = []
        qdrive_203_drives = []
        qdrive_230_drives = []
        qdrive_231_drives = []
        vector_drives = []
        transfer_drives = []
        backup_drives = []
        
        for drive in available_drives:
            try:
                logger.info(f"Analyzing drive: {drive}")
                
                # 1. Check for camera_fc*.mp4 files (201 drive)
                if self._has_camera_fc_mp4_files(drive):
                    qdrive_201_drives.append(drive)
                    logger.info(f"Identified Qdrive 201: {drive} (contains camera_fc*.mp4 files)")
                    continue
                
                # 2. Check for camera_rc*.mp4 files (203 drive)
                if self._has_camera_rc_mp4_files(drive):
                    qdrive_203_drives.append(drive)
                    logger.info(f"Identified Qdrive 203: {drive} (contains camera_rc*.mp4 files)")
                    continue
                
                # 3. Check for data_lidar_top folder (230 drive)
                if self._has_data_lidar_top_folder(drive):
                    qdrive_230_drives.append(drive)
                    logger.info(f"Identified Qdrive 230: {drive} (contains data_lidar_top folder)")
                    continue
                
                # 4. Check for data_lidar_front folder (231 drive)
                if self._has_data_lidar_front_folder(drive):
                    qdrive_231_drives.append(drive)
                    logger.info(f"Identified Qdrive 231: {drive} (contains data_lidar_front folder)")
                    continue
                
                # 5. Check for Logs or logs folder (Vector drive)
                if self._has_logs_folder(drive):
                    vector_drives.append(drive)
                    logger.info(f"Identified Vector drive: {drive} (contains Logs/logs folder)")
                    continue
                
                # 6. Check for Echo backup drive (Echo*backup)
                if self._is_echo_backup_drive(drive):
                    backup_drives.append(drive)
                    logger.info(f"Identified Echo backup drive: {drive}")
                    continue
                
                # 7. Check for Echo transfer drive (Echo* but not ending with backup)
                if self._is_echo_transfer_drive(drive):
                    transfer_drives.append(drive)
                    logger.info(f"Identified Echo transfer drive: {drive}")
                    continue
                
                # If cannot be identified, default to backup drive
                backup_drives.append(drive)
                logger.info(f"Unidentified drive, defaulting to backup: {drive}")
                
            except Exception as e:
                logger.error(f"Error identifying drive {drive}: {e}")
                continue
        
        # Combine all Qdrive drives
        qdrive_drives = qdrive_201_drives + qdrive_203_drives + qdrive_230_drives + qdrive_231_drives
        
        self.qdrive_drives = qdrive_drives
        self.vector_drives = vector_drives
        self.transfer_drives = transfer_drives
        self.backup_drives = backup_drives
        
        logger.info(f"Drive identification completed:")
        logger.info(f"  Qdrive 201 drives: {qdrive_201_drives}")
        logger.info(f"  Qdrive 203 drives: {qdrive_203_drives}")
        logger.info(f"  Qdrive 230 drives: {qdrive_230_drives}")
        logger.info(f"  Qdrive 231 drives: {qdrive_231_drives}")
        logger.info(f"  Vector drives: {vector_drives}")
        logger.info(f"  Transfer drives: {transfer_drives}")
        logger.info(f"  Backup drives: {backup_drives}")
        
        return qdrive_drives, vector_drives, transfer_drives, backup_drives
    
    def _get_user_confirmation(self, qdrive_drives: List[str], vector_drives: List[str], 
                             transfer_drives: List[str], backup_drives: List[str]) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Get user confirmation for drive identification results"""
        try:
            # Import confirmation interface
            from utils.confirmation_interface import ConfirmationInterface
            from utils.directory_tree_analyzer import DirectoryTreeAnalyzer
            
            # Create analyzer and confirmation interface
            analyzer = DirectoryTreeAnalyzer(max_depth=3, max_items_per_level=5)
            confirmation_ui = ConfirmationInterface()
            
            # Display results and get user confirmation
            choice = confirmation_ui.display_identification_results(
                qdrive_drives, vector_drives, transfer_drives, backup_drives, analyzer
            )
            
            # Handle user choice
            should_continue, new_qdrive, new_vector, new_transfer, new_backup = confirmation_ui.handle_user_confirmation(choice, self)
            
            if should_continue:
                return qdrive_drives, vector_drives, transfer_drives, backup_drives
            else:
                # Recursive call for re-identification
                return self.identify_data_drives(require_confirmation=True)
                
        except ImportError as e:
            logger.warning(f"Confirmation interface not available: {e}")
            logger.info("Proceeding without user confirmation...")
            return qdrive_drives, vector_drives, transfer_drives, backup_drives
        except Exception as e:
            logger.error(f"Error in user confirmation: {e}")
            logger.info("Proceeding without user confirmation...")
            return qdrive_drives, vector_drives, transfer_drives, backup_drives 