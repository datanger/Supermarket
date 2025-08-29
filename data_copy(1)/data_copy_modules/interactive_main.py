#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式数据拷贝工具主程序
Interactive Data Copy Tool Main Program
"""

import os
import logging
from typing import List, Dict, Tuple
try:
    from core.system_detector import CrossPlatformSystemDetector
    from data_copy.qdrive_data_handler import QdriveDataHandler
    from logging_utils.copy_logger import setup_copy_logger
except ImportError:
    from data_copy_modules.core.system_detector import CrossPlatformSystemDetector
    from data_copy_modules.data_copy.qdrive_data_handler import QdriveDataHandler
    from data_copy_modules.logging_utils.copy_logger import setup_copy_logger

# 配置日志
logger = setup_copy_logger()

class InteractiveDataCopyTool:
    """交互式数据拷贝工具类"""
    
    def __init__(self):
        """初始化工具"""
        self.detector = CrossPlatformSystemDetector()
        self.qdrive_drives = []  # 用户选择的Qdrive盘
        self.vector_drive = None  # 用户选择的Vector盘
        self.transfer_drive = None  # 用户选择的transfer盘
        self.backup_drive = None  # 用户选择的backup盘
        self.copy_plan = {}  # 拷贝计划
        
    def show_all_drives(self) -> List[str]:
        """显示所有外接盘列表 - 优化版本，避免重复扫描"""
        print("\n" + "="*60)
        print("检测到的所有外接盘:")
        print("="*60)
        
        drives = self.detector.detect_all_drives()
        if not drives:
            print("❌ 未检测到任何驱动器")
            return []
        
        # 过滤掉系统盘，只显示外接盘
        system_drives = self.detector.get_system_drives()
        external_drives = [drive for drive in drives if drive not in system_drives]
        
        if not external_drives:
            print("❌ 未检测到外接盘")
            return []
        
        # 一次性获取所有驱动器信息，避免重复调用
        drive_info = self.detector.get_drive_information()
        
        # 显示驱动器信息
        for i, drive in enumerate(external_drives, 1):
            try:
                info = drive_info.get(drive, {})
                if 'error' not in info:
                    # 检查是否是加密驱动器
                    if info.get('is_encrypted', False):
                        bitlocker_status = info.get('bitlocker_status', 'Unknown')
                        if bitlocker_status == 'Locked':
                            print(f"{i:2d}. {drive} - 🔒 BitLocker加密驱动器 (已锁定，需要解锁)")
                        elif bitlocker_status == 'Unlocked':
                            print(f"{i:2d}. {drive} - 🔓 BitLocker加密驱动器 (已解锁)")
                        else:
                            print(f"{i:2d}. {drive} - 🔐 BitLocker加密驱动器 (状态: {bitlocker_status})")
                    elif not info.get('is_accessible', True):
                        print(f"{i:2d}. {drive} - ⚠️ 访问受限")
                    else:
                        total_gb = info.get('total', 0) / (1024**3)
                        free_gb = info.get('free', 0) / (1024**3)
                        volume_name = info.get('volume_name', 'Unknown')
                        print(f"{i:2d}. {drive} - {volume_name} - 总容量: {total_gb:.2f}GB - 可用: {free_gb:.2f}GB")
                else:
                    print(f"{i:2d}. {drive} - 错误: {info['error']}")
            except Exception as e:
                # 检查是否是加密驱动器
                try:
                    # 尝试访问驱动器
                    os.listdir(drive)
                    print(f"{i:2d}. {drive} - 状态正常")
                except (PermissionError, OSError):
                    print(f"{i:2d}. {drive} - 🔒 加密驱动器 (需要解锁)")
                except Exception as e2:
                    print(f"{i:2d}. {drive} - 无法获取信息: {e2}")
        
        return external_drives
    
    def select_qdrive_drives(self, external_drives: List[str]) -> List[str]:
        """人工选择Qdrive盘（201，203，230，231）- 优化版本，避免重复扫描"""
        print("\n" + "="*60)
        print("请选择Qdrive数据盘（201，203，230，231）:")
        print("="*60)
        print("请逐个选择，输入盘符或完整路径，输入'done'完成选择")
        
        selected_drives = []
        expected_numbers = ['201', '203', '230', '231']
        
        # 一次性获取驱动器信息，避免重复调用
        drive_info = self.detector.get_drive_information()
        
        # 创建盘号到驱动器的映射
        drive_number_mapping = {}
        
        while len(selected_drives) < 4:
            # 计算还需要选择的盘号
            remaining_numbers = []
            for num in expected_numbers:
                # 检查这个盘号是否已经被分配给某个驱动器
                if num not in drive_number_mapping.values():
                    remaining_numbers.append(num)
            
            print(f"\n当前已选择: {selected_drives}")
            print(f"还需要选择: {remaining_numbers}")
            
            # 显示可用的盘符列表（使用已获取的信息）
            print("\n可用的盘符列表:")
            available_drives = [drive for drive in external_drives if drive not in selected_drives]
            for i, drive in enumerate(available_drives, 1):
                try:
                    info = drive_info.get(drive, {})
                    if 'error' not in info:
                        total_gb = info.get('total', 0) / (1024**3)
                        free_gb = info.get('free', 0) / (1024**3)
                        volume_name = info.get('volume_name', 'Unknown')
                        print(f"  {i:2d}. {drive} - {volume_name} - 总容量: {total_gb:.2f}GB - 可用: {free_gb:.2f}GB")
                    else:
                        print(f"  {i:2d}. {drive} - 错误: {info['error']}")
                except Exception as e:
                    print(f"  {i:2d}. {drive} - 无法获取信息: {e}")
            
            # 提示用户选择哪个具体的Qdrive盘号
            if remaining_numbers:
                next_number = remaining_numbers[0]
                choice = input(f"\n请选择Qdrive盘 {next_number} (输入数字编号或输入'done'完成): ").strip()
            else:
                choice = input(f"\n请选择Qdrive盘 (输入数字编号或输入'done'完成): ").strip()
            
            if choice.lower() == 'done':
                if len(selected_drives) < 4:
                    print(f"⚠️ 警告：只选择了{len(selected_drives)}个盘，建议选择4个盘")
                    confirm = input("是否继续？(y/n): ").lower().strip()
                    if confirm != 'y':
                        continue
                break
            
            # 处理数字编号选择
            selected_drive = None
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(available_drives):
                    selected_drive = available_drives[choice_num - 1]
                else:
                    print(f"❌ 无效的数字编号: {choice_num}，请输入1-{len(available_drives)}之间的数字")
                    continue
            else:
                # 直接输入盘符的情况
                if choice in external_drives:
                    selected_drive = choice
                else:
                    print(f"❌ 无效选择: {choice}，请输入数字编号或正确的盘符")
                    continue
            
            # 验证选择（快速验证，不深入扫描）
            if selected_drive:
                # 快速检查是否包含data文件夹或卷标包含预期数字
                try:
                    # 方法1: 检查卷标是否包含预期数字
                    volume_name = drive_info.get(selected_drive, {}).get('volume_name', '').lower()
                    has_expected_number = any(num in volume_name for num in expected_numbers)
                    
                    # 方法2: 快速检查根目录下的data文件夹（不深入扫描）
                    has_data_folder = False
                    try:
                        if os.access(selected_drive, os.R_OK):
                            entries = os.listdir(selected_drive)
                            has_data_folder = 'data' in entries
                    except (PermissionError, OSError):
                        # 权限错误，可能是加密盘，通过卷标判断
                        pass
                    if has_expected_number or has_data_folder:
                        if selected_drive not in selected_drives:
                            # 确定这个驱动器对应的盘号
                            drive_number = None
                            for num in expected_numbers:
                                if num in volume_name.lower() or (has_data_folder and num not in [d for d in drive_number_mapping.values()]):
                                    if num not in [d for d in drive_number_mapping.values()]:
                                        drive_number = num
                                        break
                            
                            if drive_number:
                                drive_number_mapping[selected_drive] = drive_number
                                selected_drives.append(selected_drive)
                                print(f"✅ 已选择Qdrive盘 {drive_number}: {selected_drive}")
                            else:
                                print(f"⚠️ 无法确定 {selected_drive} 对应的盘号")
                                confirm = input("是否仍然选择该盘？(y/n): ").lower().strip()
                                if confirm == 'y':
                                    selected_drives.append(selected_drive)
                                    print(f"✅ 已选择Qdrive盘: {selected_drive}")
                        else:
                            print(f"⚠️ 该盘已被选择: {selected_drive}")
                    else:
                        print(f"⚠️ 警告: {selected_drive} 可能不是Qdrive数据盘")
                        confirm = input("是否仍然选择该盘？(y/n): ").lower().strip()
                        if confirm == 'y':
                            if selected_drive not in selected_drives:
                                selected_drives.append(selected_drive)
                                print(f"✅ 已选择Qdrive盘: {selected_drive}")
                            else:
                                print(f"⚠️ 该盘已被选择: {selected_drive}")
                        else:
                            print(f"已取消选择: {selected_drive}")
                            
                except Exception as e:
                    print(f"验证驱动器时出错: {e}")
                    # 如果验证失败，仍然允许选择
                    if selected_drive not in selected_drives:
                        selected_drives.append(selected_drive)
                        print(f"✅ 已选择Qdrive盘: {selected_drive} (验证跳过)")
                    else:
                        print(f"⚠️ 该盘已被选择: {selected_drive}")
        
        self.qdrive_drives = selected_drives
        self.qdrive_number_mapping = drive_number_mapping  # 保存盘号映射
        print(f"\n✅ Qdrive盘选择完成:")
        for drive, number in drive_number_mapping.items():
            print(f"  Qdrive盘 {number}: {drive}")
        return selected_drives
    
    def select_vector_drive(self, external_drives: List[str]) -> str:
        """人工选择Vector盘（单选）"""
        print("\n" + "="*60)
        print("请选择Vector数据盘:")
        print("="*60)
        print("说明：Vector盘应包含logs文件夹，数据结构为：logs/车号/日期时间")
        
        # 显示可用的盘符列表
        available_drives = [drive for drive in external_drives if drive not in self.qdrive_drives]
        print("\n可用的盘符列表:")
        for i, drive in enumerate(available_drives, 1):
            try:
                drive_info = self.detector.get_drive_information().get(drive, {})
                if 'error' not in drive_info:
                    total_gb = drive_info.get('total', 0) / (1024**3)
                    free_gb = drive_info.get('free', 0) / (1024**3)
                    volume_name = drive_info.get('volume_name', 'Unknown')
                    print(f"  {i:2d}. {drive} - {volume_name} - 总容量: {total_gb:.2f}GB - 可用: {free_gb:.2f}GB")
                else:
                    print(f"  {i:2d}. {drive} - 错误: {drive_info['error']}")
            except Exception as e:
                print(f"  {i:2d}. {drive} - 无法获取信息: {e}")
        
        while True:
            choice = input("\n请输入Vector盘符或完整路径 (输入数字编号): ").strip()
            
            # 处理数字编号选择
            selected_drive = None
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(available_drives):
                    selected_drive = available_drives[choice_num - 1]
                else:
                    print(f"❌ 无效的数字编号: {choice_num}，请输入1-{len(available_drives)}之间的数字")
                    continue
            else:
                # 直接输入盘符的情况
                if choice in external_drives:
                    selected_drive = choice
                else:
                    print(f"❌ 无效选择: {choice}，请输入数字编号或正确的盘符")
                    continue
            
            if selected_drive:
                # 检查是否包含logs文件夹
                logs_path = os.path.join(selected_drive, 'logs')
                if os.path.exists(logs_path):
                    self.vector_drive = selected_drive
                    print(f"✅ 已选择Vector盘: {selected_drive}")
                    return selected_drive
                else:
                    print(f"❌ {selected_drive} 中未找到logs文件夹，请重新选择")
    
    def select_transfer_drive(self, external_drives: List[str]) -> str:
        """人工选择transfer盘（单选）"""
        print("\n" + "="*60)
        print("请选择transfer目标盘:")
        print("="*60)
        print("说明：transfer盘用于接收Qdrive和Vector数据的原始结构拷贝")
        
        # 显示可用的盘符列表
        available_drives = [drive for drive in external_drives 
                          if drive not in self.qdrive_drives and drive != self.vector_drive]
        print("\n可用的盘符列表:")
        for i, drive in enumerate(available_drives, 1):
            try:
                drive_info = self.detector.get_drive_information().get(drive, {})
                if 'error' not in drive_info:
                    total_gb = drive_info.get('total', 0) / (1024**3)
                    free_gb = drive_info.get('free', 0) / (1024**3)
                    volume_name = drive_info.get('volume_name', 'Unknown')
                    print(f"  {i:2d}. {drive} - {volume_name} - 总容量: {total_gb:.2f}GB - 可用: {free_gb:.2f}GB")
                else:
                    print(f"  {i:2d}. {drive} - 错误: {drive_info['error']}")
            except Exception as e:
                print(f"  {i:2d}. {drive} - 无法获取信息: {e}")
        
        while True:
            choice = input("\n请输入transfer盘符或完整路径 (输入数字编号): ").strip()
            
            # 处理数字编号选择
            selected_drive = None
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(available_drives):
                    selected_drive = available_drives[choice_num - 1]
                else:
                    print(f"❌ 无效的数字编号: {choice_num}，请输入1-{len(available_drives)}之间的数字")
                    continue
            else:
                # 直接输入盘符的情况
                if choice in external_drives:
                    selected_drive = choice
                else:
                    print(f"❌ 无效选择: {choice}，请输入数字编号或正确的盘符")
                    continue
            
            if selected_drive:
                if selected_drive not in self.qdrive_drives and selected_drive != self.vector_drive:
                    self.transfer_drive = selected_drive
                    print(f"✅ 已选择transfer盘: {selected_drive}")
                    return selected_drive
                else:
                    print(f"❌ {selected_drive} 已被选择为数据源盘，不能作为目标盘")
    
    def select_backup_drive(self, external_drives: List[str]) -> str:
        """人工选择backup盘（单选）"""
        print("\n" + "="*60)
        print("请选择backup目标盘:")
        print("="*60)
        print("说明：backup盘用于接收Qdrive和Vector数据，Qdrive数据将重新组织目录结构")
        
        # 显示可用的盘符列表
        available_drives = [drive for drive in external_drives 
                          if drive not in self.qdrive_drives and drive != self.vector_drive and drive != self.transfer_drive]
        print("\n可用的盘符列表:")
        for i, drive in enumerate(available_drives, 1):
            try:
                drive_info = self.detector.get_drive_information().get(drive, {})
                if 'error' not in drive_info:
                    total_gb = drive_info.get('total', 0) / (1024**3)
                    free_gb = drive_info.get('free', 0) / (1024**3)
                    volume_name = drive_info.get('volume_name', 'Unknown')
                    print(f"  {i:2d}. {drive} - {total_gb:.2f}GB - 可用: {free_gb:.2f}GB")
                else:
                    print(f"  {i:2d}. {drive} - 错误: {drive_info['error']}")
            except Exception as e:
                print(f"  {i:2d}. {drive} - 无法获取信息: {e}")
        
        while True:
            choice = input("\n请输入backup盘符或完整路径 (输入数字编号): ").strip()
            
            # 处理数字编号选择
            selected_drive = None
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(available_drives):
                    selected_drive = available_drives[choice_num - 1]
                else:
                    print(f"❌ 无效的数字编号: {choice_num}，请输入1-{len(available_drives)}之间的数字")
                    continue
            else:
                # 直接输入盘符的情况
                if choice in external_drives:
                    selected_drive = choice
                else:
                    print(f"❌ 无效选择: {choice}，请输入数字编号或正确的盘符")
                    continue
            
            if selected_drive:
                if selected_drive not in self.qdrive_drives and selected_drive != self.vector_drive and selected_drive != self.transfer_drive:
                    self.backup_drive = selected_drive
                    print(f"✅ 已选择backup盘: {selected_drive}")
                    return selected_drive
                else:
                    print(f"❌ {selected_drive} 已被选择，不能重复选择")
    
    def create_copy_plan(self) -> Dict:
        """人工决定拷贝计划"""
        print("\n" + "="*60)
        print("请决定拷贝计划:")
        print("="*60)
        
        copy_plan = {
            'qdrive_to_transfer': False,
            'vector_to_transfer': False,
            'vector_to_backup': False,
            'qdrive_to_backup': False
        }
        
        print("📋 拷贝计划选择:")
        print("="*60)
        
        # 1. Transfer盘拷贝选择
        print("🔄 Transfer盘拷贝操作:")
        print("   将Qdrive和Vector数据拷贝到Transfer盘，保持原始目录结构")
        while True:
            choice = input("是否执行Transfer盘拷贝？(y/n): ").lower().strip()
            if choice in ['y', 'n']:
                if choice == 'y':
                    copy_plan['qdrive_to_transfer'] = True
                    copy_plan['vector_to_transfer'] = True
                    print("✅ 已选择Transfer盘拷贝：Qdrive + Vector数据")
                else:
                    print("❌ 跳过Transfer盘拷贝")
                break
            else:
                print("请输入 y 或 n")
        
        print()
        
        # 2. Backup盘拷贝选择
        print("💾 Backup盘拷贝操作:")
        print("   将Qdrive数据重新组织目录结构 + Vector数据保持原始结构")
        while True:
            choice = input("是否执行Backup盘拷贝？(y/n): ").lower().strip()
            if choice in ['y', 'n']:
                if choice == 'y':
                    copy_plan['qdrive_to_backup'] = True
                    copy_plan['vector_to_backup'] = True
                    print("✅ 已选择Backup盘拷贝：Qdrive(重新组织) + Vector(原始结构)")
                else:
                    print("❌ 跳过Backup盘拷贝")
                break
            else:
                print("请输入 y 或 n")
        
        self.copy_plan = copy_plan
        
        # 显示最终拷贝计划
        print("\n" + "="*60)
        print("📋 最终拷贝计划:")
        print("="*60)
        if copy_plan['qdrive_to_transfer'] or copy_plan['vector_to_transfer']:
            print("🔄 Transfer盘拷贝:")
            if copy_plan['qdrive_to_transfer']:
                print("   ✅ Qdrive数据 → Transfer盘（保持原始结构）")
            if copy_plan['vector_to_transfer']:
                print("   ✅ Vector数据 → Transfer盘（保持原始结构）")
        else:
            print("❌ Transfer盘拷贝：跳过")
            
        if copy_plan['qdrive_to_backup'] or copy_plan['vector_to_backup']:
            print("💾 Backup盘拷贝:")
            if copy_plan['qdrive_to_backup']:
                print("   ✅ Qdrive数据 → Backup盘（重新组织目录结构）")
            if copy_plan['vector_to_backup']:
                print("   ✅ Vector数据 → Backup盘（保持原始结构）")
        else:
            print("❌ Backup盘拷贝：跳过")
        
        return copy_plan
    
    def handle_bitlocker_unlock(self, external_drives: List[str]) -> bool:
        """处理BitLocker解锁（人工确认解密密钥）"""
        if self.detector.os_type != "windows":
            print("\n跳过BitLocker检查（非Windows系统）")
            return True
        
        print("\n" + "="*60)
        print("BitLocker状态检查:")
        print("="*60)
        
        # 获取驱动器信息，包括加密状态
        drive_info = self.detector.get_drive_information()
        
        # 检查所有外接盘
        locked_drives = []
        encrypted_drives = []
        
        for drive in external_drives:
            try:
                info = drive_info.get(drive, {})
                if info.get('is_encrypted', False):
                    encrypted_drives.append(drive)
                    bitlocker_status = info.get('bitlocker_status', 'Unknown')
                    
                    if bitlocker_status == 'Locked':
                        locked_drives.append(drive)
                        print(f"🔒 {drive}: BitLocker加密驱动器 (已锁定)")
                    elif bitlocker_status == 'Unlocked':
                        print(f"🔓 {drive}: BitLocker加密驱动器 (已解锁)")
                    else:
                        print(f"🔐 {drive}: BitLocker加密驱动器 (状态: {bitlocker_status})")
                else:
                    # 尝试使用传统方法检查
                    try:
                        status = self.detector.bitlocker_manager.check_bitlocker_status(drive)
                        if status == 'Locked':
                            locked_drives.append(drive)
                            print(f"🔒 {drive}: BitLocker已锁定")
                        else:
                            print(f"🔓 {drive}: BitLocker状态正常")
                    except Exception as e:
                        print(f"❓ {drive}: 无法检查BitLocker状态: {e}")
            except Exception as e:
                print(f"❓ {drive}: 无法检查驱动器状态: {e}")
        
        # 额外检查：如果驱动器检测器识别为加密但状态检查失败，强制标记为锁定
        for drive in external_drives:
            try:
                info = drive_info.get(drive, {})
                if info.get('is_encrypted', False) and drive not in locked_drives:
                    # 如果驱动器被识别为加密但不在锁定列表中，强制标记为锁定
                    if drive not in locked_drives:
                        locked_drives.append(drive)
                        print(f"🔒 {drive}: BitLocker加密驱动器 (强制标记为已锁定)")
            except Exception:
                pass
        
        if not encrypted_drives:
            print("✅ 未发现BitLocker加密驱动器")
            return True
        
        if not locked_drives:
            print("✅ 所有BitLocker加密驱动器都已解锁")
            return True
        
        print(f"\n发现 {len(locked_drives)} 个被锁定的BitLocker加密驱动器:")
        for drive in locked_drives:
            print(f"  - {drive}")
        
        print("\n⚠️  警告：这些驱动器被BitLocker加密锁定，无法访问其内容")
        print("您有以下选择：")
        print("1. 解锁驱动器（需要BitLocker密码）")
        print("2. 跳过这些驱动器，继续使用其他可用驱动器")
        print("3. 退出程序")
        
        while True:
            choice = input("\n请选择操作 (1/2/3): ").strip()
            
            if choice == '1':
                # 用户选择解锁驱动器
                print("\n请输入BitLocker密码来解锁驱动器")
                password = input("请输入BitLocker密码: ").strip()
                
                if not password:
                    print("❌ 密码不能为空")
                    continue
                
                print(f"\n正在尝试解锁 {len(locked_drives)} 个驱动器...")
                
                try:
                    # 使用密码解锁所有锁定的驱动器
                    unlock_results = {}
                    for drive in locked_drives:
                        print(f"\n正在解锁驱动器 {drive}...")
                        success = self.detector.bitlocker_manager._unlock_with_password(drive, password)
                        unlock_results[drive] = success
                        if success:
                            print(f"✅ {drive} 解锁成功")
                        else:
                            print(f"❌ {drive} 解锁失败")
                    
                    if unlock_results:
                        print("\n解锁结果汇总:")
                        success_count = sum(unlock_results.values())
                        for drive, success in unlock_results.items():
                            status = "✅ 成功" if success else "❌ 失败"
                            print(f"  {drive}: {status}")
                        
                        print(f"\n解锁完成：{success_count}/{len(locked_drives)} 个驱动器成功解锁")
                        
                        if success_count == len(locked_drives):
                            print("✅ 所有BitLocker加密驱动器解锁成功")
                            return True
                        elif success_count > 0:
                            print("⚠️ 部分驱动器解锁成功，可以继续使用")
                            confirm = input("是否继续？(y/n): ").lower().strip()
                            return confirm == 'y'
                        else:
                            print("❌ 所有驱动器解锁失败")
                            retry = input("是否重试？(y/n): ").lower().strip()
                            if retry == 'y':
                                continue
                            else:
                                return False
                    else:
                        print("❌ 解锁操作失败")
                        return False
                        
                except Exception as e:
                    print(f"❌ 解锁过程中出错: {e}")
                    retry = input("是否重试？(y/n): ").lower().strip()
                    if retry == 'y':
                        continue
                    else:
                        return False
                        
            elif choice == '2':
                # 用户选择跳过加密驱动器
                print("⚠️ 您选择跳过加密驱动器")
                print("注意：跳过加密驱动器意味着无法访问其中的数据")
                confirm = input("确认跳过？(y/n): ").lower().strip()
                if confirm == 'y':
                    print("✅ 已跳过加密驱动器，继续使用其他可用驱动器")
                    return True
                else:
                    continue
                    
            elif choice == '3':
                # 用户选择退出
                print("❌ 用户选择退出程序")
                return False
                
            else:
                print("❌ 无效选择，请输入 1、2 或 3")
    
    def execute_copy_plan(self) -> bool:
        """执行拷贝计划"""
        print("\n" + "="*60)
        print("开始执行数据拷贝计划:")
        print("="*60)
        
        # 选择拷贝性能模式
        print("\n请选择拷贝性能模式:")
        print("1. 标准模式 - 单线程拷贝，稳定可靠")
        print("2. 高性能模式 - 多线程并行拷贝，速度更快")
        print("3. 自定义模式 - 手动设置线程数和缓冲区大小")
        
        while True:
            mode_choice = input("\n请选择模式 (1/2/3): ").strip()
            if mode_choice in ['1', '2', '3']:
                break
            else:
                print("请输入1、2或3")
        
        # 根据模式设置拷贝参数
        if mode_choice == '1':
            # 标准模式
            max_workers = 1
            chunk_size = 8192  # 8KB
            buffer_size = 8192
            print("✅ 已选择标准模式")
        elif mode_choice == '2':
            # 高性能模式
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            if cpu_count >= 8:
                max_workers = 6
            elif cpu_count >= 4:
                max_workers = 4
            else:
                max_workers = 2
            chunk_size = 32768  # 32KB
            buffer_size = 32768
            print(f"✅ 已选择高性能模式 - {max_workers}线程并行拷贝")
        else:
            # 自定义模式
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            print(f"当前系统CPU核心数: {cpu_count}")
            
            while True:
                try:
                    max_workers = int(input(f"请输入线程数 (1-{cpu_count*2}): ").strip())
                    if 1 <= max_workers <= cpu_count * 2:
                        break
                    else:
                        print(f"请输入1到{cpu_count*2}之间的数字")
                except ValueError:
                    print("请输入有效的数字")
            
            while True:
                try:
                    chunk_size = int(input("请输入缓冲区大小(KB): ").strip())
                    chunk_size *= 1024  # 转换为字节
                    if chunk_size >= 1024:
                        break
                    else:
                        print("请输入至少1KB的缓冲区大小")
                except ValueError:
                    print("请输入有效的数字")
            
            buffer_size = chunk_size
            print(f"✅ 已选择自定义模式 - {max_workers}线程，{chunk_size//1024}KB缓冲区")
        
        try:
            # 第一步：优先创建backup基础目录结构（如果选择backup操作）
            if self.copy_plan['qdrive_to_backup'] or self.copy_plan['vector_to_backup']:
                print(f"\n📁 第一步：优先创建backup基础目录结构...")
                
                # 创建QdriveDataHandler实例（如果需要进行backup操作）
                qdrive_handler = None
                if self.copy_plan['qdrive_to_backup'] and self.qdrive_drives and self.backup_drive:
                    print("🔄 创建Qdrive数据backup目录结构...")
                    qdrive_handler = QdriveDataHandler()
                    if not qdrive_handler.create_backup_directory_structure(self.backup_drive, self.qdrive_drives):
                        print(f"❌ 创建Backup盘目录结构失败")
                        return False
                    print("✅ Qdrive backup目录结构创建完成")
                
                # 如果选择Vector数据拷贝到backup盘，也需要预先创建logs目录
                if self.copy_plan['vector_to_backup'] and self.vector_drive and self.backup_drive:
                    print("🔄 创建Vector数据backup目录结构...")
                    try:
                        # 如果Qdrive backup目录结构已创建，使用相同的根目录
                        if qdrive_handler and qdrive_handler.backup_root_dir:
                            vector_target_dir = os.path.join(qdrive_handler.backup_root_dir, "logs")
                        else:
                            # 如果没有Qdrive backup目录，在backup盘根目录创建logs文件夹
                            vector_target_dir = os.path.join(self.backup_drive, "logs")
                        
                        # 确保logs目录存在
                        os.makedirs(vector_target_dir, exist_ok=True)
                        print(f"✅ Vector backup目录结构创建完成: {vector_target_dir}")
                    except Exception as e:
                        print(f"❌ 创建Vector backup目录结构失败: {e}")
                        return False
                
                print("✅ Backup盘基础目录结构创建完成")
            else:
                print(f"\n📁 第一步：无需创建backup目录结构（未选择backup操作）")
            
            # 第二步：并行执行所有拷贝任务
            print(f"\n📁 第二步：开始并行数据拷贝（backup目录结构已准备就绪）...")
            
            import threading
            import time
            
            # 存储所有拷贝任务的结果
            copy_results = {}
            copy_threads = []
            
            # 1. Qdrive数据 → Transfer盘
            if self.copy_plan['qdrive_to_transfer'] and self.qdrive_drives and self.transfer_drive:
                print(f"启动Qdrive到Transfer盘拷贝任务...")
                for qdrive_drive in self.qdrive_drives:
                    def copy_qdrive_to_transfer(drive=qdrive_drive):
                        try:
                            success = self.detector.copy_qdrive_data_to_transfer(drive, self.transfer_drive)
                            copy_results[f"qdrive_{drive}_to_transfer"] = success
                            if success:
                                pass
                            else:
                                print(f"❌ {drive} → {self.transfer_drive} 拷贝失败")
                        except Exception as e:
                            copy_results[f"qdrive_{drive}_to_transfer"] = False
                            print(f"❌ {drive} → {self.transfer_drive} 拷贝出错: {e}")
                    
                    thread = threading.Thread(target=copy_qdrive_to_transfer)
                    copy_threads.append(thread)
                    thread.start()
            
            # 2. Vector数据 → Transfer盘
            if self.copy_plan['vector_to_transfer'] and self.vector_drive and self.transfer_drive:
                print(f"启动Vector到Transfer盘拷贝任务...")
                def copy_vector_to_transfer():
                    try:
                        success = self.detector.copy_vector_data_to_transfer(self.vector_drive, self.transfer_drive)
                        copy_results["vector_to_transfer"] = success
                        if success:
                            pass
                        else:
                            print(f"❌ {self.vector_drive} → {self.transfer_drive} 拷贝失败")
                    except Exception as e:
                        copy_results["vector_to_transfer"] = False
                        print(f"❌ {self.vector_drive} → {self.transfer_drive} 拷贝出错: {e}")
                
                thread = threading.Thread(target=copy_vector_to_transfer)
                copy_threads.append(thread)
                thread.start()
            
            # 3. Vector数据 → Backup盘
            if self.copy_plan['vector_to_backup'] and self.vector_drive and self.backup_drive:
                print(f"启动Vector到Backup盘拷贝任务...")
                def copy_vector_to_backup():
                    try:
                        # 如果Qdrive backup目录结构已创建，使用相同的根目录
                        if qdrive_handler and qdrive_handler.backup_root_dir:
                            # 直接在根目录下创建logs文件夹
                            vector_target_dir = os.path.join(qdrive_handler.backup_root_dir, "logs")
                            success = self.detector.copy_vector_data_to_backup(self.vector_drive, vector_target_dir)
                        else:
                            # 如果没有Qdrive backup目录，使用默认的backup盘
                            success = self.detector.copy_vector_data_to_backup(self.vector_drive, self.backup_drive)
                        
                        copy_results["vector_to_backup"] = success
                        if success:
                            pass
                        else:
                            print(f"❌ Vector数据拷贝失败")
                    except Exception as e:
                        copy_results["vector_to_backup"] = False
                        print(f"❌ Vector数据拷贝出错: {e}")
                
                thread = threading.Thread(target=copy_vector_to_backup)
                copy_threads.append(thread)
                thread.start()
            
            # 4. Qdrive数据 → Backup盘
            if self.copy_plan['qdrive_to_backup'] and self.qdrive_drives and self.backup_drive and qdrive_handler:
                print(f"启动Qdrive到Backup盘拷贝任务...")
                for qdrive_drive in self.qdrive_drives:
                    drive_number = self.qdrive_number_mapping.get(qdrive_drive, 'Unknown')
                    def copy_qdrive_to_backup(drive=qdrive_drive, number=drive_number):
                        try:
                            success = self.detector.copy_qdrive_data_to_backup(drive, self.backup_drive, qdrive_handler, number)
                            copy_results[f"qdrive_{number}_to_backup"] = success
                            if success:
                                pass
                            else:
                                print(f"❌ Qdrive盘 {number} ({drive}) → {self.backup_drive} 拷贝失败")
                        except Exception as e:
                            copy_results[f"qdrive_{number}_to_backup"] = False
                            print(f"❌ Qdrive盘 {number} ({drive}) → {self.backup_drive} 拷贝出错: {e}")
                    
                    thread = threading.Thread(target=copy_qdrive_to_backup)
                    copy_threads.append(thread)
                    thread.start()
            
            # 等待所有拷贝任务完成，并实时显示进度
            print(f"\n等待所有拷贝任务完成...")
            
            # 创建进度监控
            import time
            start_time = time.time()
            completed_tasks = 0
            total_threads = len(copy_threads)
            
            # 记录已完成的线程索引
            completed_thread_indices = set()
            
            # 实时进度监控循环
            while completed_tasks < total_threads:
                # 检查已完成的线程
                for i, thread in enumerate(copy_threads):
                    if i not in completed_thread_indices and not thread.is_alive():
                        completed_thread_indices.add(i)
                        completed_tasks += 1
                
                # 计算进度和预估时间
                progress = (completed_tasks / total_threads) * 100
                elapsed_time = time.time() - start_time
                
                # 格式化时间显示
                def format_time(seconds):
                    if seconds < 60:
                        return f"{seconds:.1f}秒"
                    elif seconds < 3600:
                        minutes = seconds / 60
                        return f"{minutes:.1f}分钟"
                    else:
                        hours = seconds / 3600
                        return f"{hours:.1f}小时"
                
                # 清屏并显示进度
                os.system('cls' if os.name == 'nt' else 'clear')
                
                print("="*60)
                print("数据拷贝进度监控")
                print("="*60)
                print(f"总任务数: {total_threads}")
                print(f"已完成: {completed_tasks}")
                print(f"进行中: {total_threads - completed_tasks}")
                print(f"进度: {progress:.1f}%")
                print(f"已用时间: {format_time(elapsed_time)}")
                
                if completed_tasks > 0:
                    avg_time_per_task = elapsed_time / completed_tasks
                    remaining_tasks = total_threads - completed_tasks
                    estimated_remaining = avg_time_per_task * remaining_tasks
                    print(f"预估剩余时间: {format_time(estimated_remaining)}")
                else:
                    print("预估剩余时间: 计算中...")
                
                print("="*60)
                
                # 显示进度条
                bar_length = 40
                filled_length = int(bar_length * progress / 100)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                print(f"[{bar}] {progress:.1f}%")
                
                if completed_tasks < total_threads:
                    print("\n正在等待任务完成...")
                    time.sleep(1)  # 每秒更新一次
                
                # 如果所有任务都完成了，跳出循环
                if completed_tasks >= total_threads:
                    break
            
            # 最终等待所有线程完成
            for thread in copy_threads:
                thread.join()
            
            # 统计拷贝结果
            total_tasks = len(copy_results)
            successful_tasks = sum(1 for success in copy_results.values() if success)
            failed_tasks = total_tasks - successful_tasks
            
            if failed_tasks == 0:
                return True
            else:
                print(f"\n⚠️ 有 {failed_tasks} 个任务失败，详细失败信息如下:")
                print("="*60)
                
                # 显示每个任务的详细状态
                for task_name, success in copy_results.items():
                    status_icon = "✅" if success else "❌"
                    status_text = "成功" if success else "失败"
                    print(f"{status_icon} {task_name}: {status_text}")
                
                print("="*60)
                print("💡 建议：")
                print("   1. 检查失败任务对应的源盘和目标盘")
                print("   2. 确认磁盘空间是否充足")
                print("   3. 检查文件权限和是否被占用")
                print("   4. 可以单独重新运行失败的任务")
                return False
            
        except Exception as e:
            print(f"❌ 执行拷贝计划时出错: {e}")
            logger.error(f"执行拷贝计划时出错: {e}", exc_info=True)
            return False
    
    def print_summary(self):
        """打印操作摘要"""
        print("\n" + "="*60)
        print("操作摘要:")
        print("="*60)
        
        print(f"操作系统: {self.detector.os_type}")
        print("Qdrive盘:")
        if hasattr(self, 'qdrive_number_mapping') and self.qdrive_number_mapping:
            for drive, number in self.qdrive_number_mapping.items():
                print(f"  {number}: {drive}")
        else:
            print(f"  {self.qdrive_drives}")
        print(f"Vector盘: {self.vector_drive}")
        print(f"Transfer盘: {self.transfer_drive}")
        print(f"Backup盘: {self.backup_drive}")
        print(f"拷贝计划: {self.copy_plan}")
        
        print("\n" + "="*60)
    
    def run(self):
        """运行交互式数据拷贝工具"""
        print("交互式数据拷贝工具")
        print("="*60)
        print("本工具将引导您完成以下步骤:")
        print("1. 识别所有外接盘")
        print("2. 处理BitLocker解锁（如需要）")
        print("3. 选择Qdrive数据盘（201，203，230，231）")
        print("4. 选择Vector数据盘")
        print("5. 选择Transfer目标盘")
        print("6. 选择Backup目标盘")
        print("7. 检查Vector数据日期")
        print("8. 制定拷贝计划")
        print("9. 执行数据拷贝")
        print("="*60)
        
        try:
            # 1. 显示所有外接盘
            external_drives = self.show_all_drives()
            if not external_drives:
                print("❌ 没有可用的外接盘，程序退出")
                return
            
            # 2. 处理BitLocker解锁（在盘符选择之前）
            if not self.handle_bitlocker_unlock(external_drives):
                print("❌ BitLocker解锁失败，程序退出")
                return
            
            # 3. 选择Qdrive盘
            self.select_qdrive_drives(external_drives)
            
            # 4. 选择Vector盘
            self.select_vector_drive(external_drives)
            
            # 5. 选择Transfer盘
            self.select_transfer_drive(external_drives)
            
            # 6. 选择Backup盘
            self.select_backup_drive(external_drives)
            
            # 7. 检查Vector数据日期（在制定拷贝计划前）
            if self.vector_drive:
                print("\n" + "="*60)
                print("检查Vector数据日期...")
                print("="*60)
                
                is_single_date, dates = self.detector.check_vector_data_dates(self.vector_drive)
                if is_single_date:
                    print(f"✅ Vector数据盘 {self.vector_drive} 包含单个日期数据: {dates[0]}")
                    print("可以继续执行拷贝计划")
                else:
                    print(f"❌ Vector数据盘 {self.vector_drive} 包含多个日期数据: {dates}")
                    print("⚠️ 警告：多日期数据可能导致拷贝问题")
                    print("建议：请手动处理多日期数据，或选择单日期的Vector盘")
                    
                    confirm = input("\n是否仍要继续执行拷贝计划？(y/n): ").lower().strip()
                    if confirm != 'y':
                        print("拷贝计划已取消")
                        return
            
            # 8. 制定拷贝计划
            self.create_copy_plan()
            
            # 9. 确认执行
            print("\n" + "="*60)
            print("所有选择已完成，准备执行拷贝计划")
            self.print_summary()
            
            confirm = input("\n是否开始执行拷贝计划？(y/n): ").lower().strip()
            if confirm == 'y':
                # 10. 执行拷贝计划
                success = self.execute_copy_plan()
                if success:
                    print("\n🎉 数据拷贝任务完成！")
                else:
                    print("\n❌ 数据拷贝任务失败")
            else:
                print("操作已取消")
            
        except KeyboardInterrupt:
            print("\n\n用户中断操作")
        except Exception as e:
            print(f"\n程序执行出错: {e}")
            logger.error(f"程序执行出错: {e}", exc_info=True)
        finally:
            print("\n程序执行完成")

def main():
    """主函数"""
    # 设置拷贝日志记录器
    copy_log_file, filelist_log_file = setup_copy_logger()
    print(f"拷贝日志文件: {copy_log_file}")
    print(f"文件列表日志文件: {filelist_log_file}")
    
    # 创建并运行交互式工具
    tool = InteractiveDataCopyTool()
    tool.run()

if __name__ == "__main__":
    main()
