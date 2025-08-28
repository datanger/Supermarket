#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式数据拷贝工具主程序
Interactive Data Copy Tool Main Program
"""

import os
import logging
from typing import List, Dict, Tuple
from core.system_detector import CrossPlatformSystemDetector
from data_copy.qdrive_data_handler import QdriveDataHandler
from logging_utils.copy_logger import setup_copy_logger

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
                    total_gb = info.get('total', 0) / (1024**3)
                    free_gb = info.get('free', 0) / (1024**3)
                    volume_name = info.get('volume_name', 'Unknown')
                    print(f"{i:2d}. {drive} - {volume_name} - 总容量: {total_gb:.2f}GB - 可用: {free_gb:.2f}GB")
                else:
                    print(f"{i:2d}. {drive} - 错误: {info['error']}")
            except Exception as e:
                print(f"{i:2d}. {drive} - 无法获取信息: {e}")
        
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
        
        while len(selected_drives) < 4:
            print(f"\n当前已选择: {selected_drives}")
            print(f"还需要选择: {[num for num in expected_numbers if not any(num in drive for drive in selected_drives)]}")
            
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
            
            choice = input(f"\n请选择第{len(selected_drives)+1}个Qdrive盘 (输入数字编号或输入'done'完成): ").strip()
            
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
        print(f"\n✅ Qdrive盘选择完成: {selected_drives}")
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
        
        print("可选的拷贝操作:")
        print("1. Qdrive数据 → Transfer盘（保持原始结构）")
        print("2. Vector数据 → Transfer盘（保持原始结构）")
        print("3. Vector数据 → Backup盘（保持原始结构）")
        print("4. Qdrive数据 → Backup盘（重新组织目录结构）")
        
        for operation in copy_plan.keys():
            while True:
                choice = input(f"\n是否执行 {operation}？(y/n): ").lower().strip()
                if choice in ['y', 'n']:
                    copy_plan[operation] = (choice == 'y')
                    break
                else:
                    print("请输入 y 或 n")
        
        self.copy_plan = copy_plan
        print(f"\n✅ 拷贝计划已确定: {copy_plan}")
        return copy_plan
    
    def handle_bitlocker_unlock(self, external_drives: List[str]) -> bool:
        """处理BitLocker解锁（人工确认解密密钥）"""
        if self.detector.os_type != "windows":
            print("\n跳过BitLocker检查（非Windows系统）")
            return True
        
        print("\n" + "="*60)
        print("BitLocker状态检查:")
        print("="*60)
        
        # 检查所有外接盘
        locked_drives = []
        for drive in external_drives:
            try:
                status = self.detector.bitlocker_manager.check_bitlocker_status(drive)
                if status == 'Locked':
                    locked_drives.append(drive)
                    print(f"🔒 {drive}: BitLocker已锁定")
                else:
                    print(f"🔓 {drive}: BitLocker状态正常")
            except Exception as e:
                print(f"❓ {drive}: 无法检查BitLocker状态: {e}")
        
        if not locked_drives:
            print("✅ 所有外接盘BitLocker状态正常")
            return True
        
        print(f"\n发现 {len(locked_drives)} 个被锁定的驱动器")
        print("需要解锁这些驱动器才能进行数据拷贝")
        
        while True:
            choice = input("是否现在解锁这些驱动器？(y/n): ").lower().strip()
            if choice == 'y':
                # 获取恢复密钥
                recovery_key = input("请输入BitLocker恢复密钥: ").strip()
                if recovery_key:
                    try:
                        unlock_results = self.detector.unlock_all_locked_drives(recovery_key)
                        if unlock_results:
                            print("\n解锁结果:")
                            for drive, success in unlock_results.items():
                                status = "✅ 成功" if success else "❌ 失败"
                                print(f"  {drive}: {status}")
                            
                            # 检查是否所有驱动器都解锁成功
                            all_unlocked = all(unlock_results.values())
                            if all_unlocked:
                                print("✅ 所有驱动器解锁成功")
                                return True
                            else:
                                print("⚠️ 部分驱动器解锁失败，可能影响数据拷贝")
                                confirm = input("是否继续？(y/n): ").lower().strip()
                                return confirm == 'y'
                        else:
                            print("❌ 解锁操作失败")
                            return False
                    except Exception as e:
                        print(f"❌ 解锁过程中出错: {e}")
                        return False
                else:
                    print("❌ 未输入恢复密钥")
                    return False
            elif choice == 'n':
                print("❌ 无法解锁驱动器，无法进行数据拷贝")
                return False
            else:
                print("请输入 y 或 n")
    
    def execute_copy_plan(self) -> bool:
        """执行拷贝计划"""
        print("\n" + "="*60)
        print("开始执行数据拷贝计划:")
        print("="*60)
        
        try:
            # 1. Qdrive数据 → Transfer盘
            if self.copy_plan['qdrive_to_transfer'] and self.qdrive_drives and self.transfer_drive:
                print(f"\n📁 拷贝Qdrive数据到Transfer盘...")
                for qdrive_drive in self.qdrive_drives:
                    success = self.detector.copy_qdrive_data_to_transfer(qdrive_drive, self.transfer_drive)
                    if success:
                        print(f"✅ {qdrive_drive} → {self.transfer_drive} 拷贝成功")
                    else:
                        print(f"❌ {qdrive_drive} → {self.transfer_drive} 拷贝失败")
            
            # 2. Vector数据 → Transfer盘
            if self.copy_plan['vector_to_transfer'] and self.vector_drive and self.transfer_drive:
                print(f"\n📁 拷贝Vector数据到Transfer盘...")
                success = self.detector.copy_vector_data_to_transfer(self.vector_drive, self.transfer_drive)
                if success:
                    print(f"✅ {self.vector_drive} → {self.transfer_drive} 拷贝成功")
                else:
                    print(f"❌ {self.vector_drive} → {self.transfer_drive} 拷贝失败")
            
            # 3. Vector数据 → Backup盘
            if self.copy_plan['vector_to_backup'] and self.vector_drive and self.backup_drive:
                print(f"\n📁 拷贝Vector数据到Backup盘...")
                success = self.detector.copy_vector_data_to_backup(self.vector_drive, self.backup_drive)
                if success:
                    print(f"✅ {self.vector_drive} → {self.backup_drive} 拷贝成功")
                else:
                    print(f"❌ {self.vector_drive} → {self.backup_drive} 拷贝失败")
            
            # 4. Qdrive数据 → Backup盘（需要重新组织目录结构）
            if self.copy_plan['qdrive_to_backup'] and self.qdrive_drives and self.backup_drive:
                print(f"\n📁 拷贝Qdrive数据到Backup盘（重新组织目录结构）...")
                
                # 创建QdriveDataHandler实例
                qdrive_handler = QdriveDataHandler()
                
                # 创建backup目录结构
                if qdrive_handler.create_backup_directory_structure(self.backup_drive, self.qdrive_drives):
                    # 拷贝数据到新结构
                    for qdrive_drive in self.qdrive_drives:
                        success = self.detector.copy_qdrive_data_to_backup(qdrive_drive, self.backup_drive, qdrive_handler)
                        if success:
                            print(f"✅ {qdrive_drive} → {self.backup_drive} 拷贝成功")
                        else:
                            print(f"❌ {qdrive_drive} → {self.backup_drive} 拷贝失败")
                else:
                    print(f"❌ 创建Backup盘目录结构失败")
            
            print("\n✅ 数据拷贝计划执行完成")
            return True
            
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
        print(f"Qdrive盘: {self.qdrive_drives}")
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
