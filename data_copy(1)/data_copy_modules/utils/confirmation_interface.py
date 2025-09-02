#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式确认界面模块
Interactive Confirmation Interface Module
"""

import os
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfirmationInterface:
    """交互式确认界面类"""
    
    def __init__(self):
        """初始化确认界面"""
        self.line_width = 80
        self.section_separator = "=" * self.line_width
        self.subsection_separator = "-" * 50
    
    def display_identification_results(self, 
                                     qdrive_drives: List[str], 
                                     vector_drives: List[str], 
                                     transfer_drives: List[str], 
                                     backup_drives: List[str],
                                     analyzer) -> str:
        """
        显示识别结果并等待用户确认
        
        Args:
            qdrive_drives: Qdrive驱动器列表
            vector_drives: Vector驱动器列表
            transfer_drives: Transfer驱动器列表
            backup_drives: Backup驱动器列表
            analyzer: 目录结构分析器实例
            
        Returns:
            str: 用户选择 (Y/N/M/Q)
        """
        print("\n" + self.section_separator)
        print("🔍 AUTOMATED DRIVE IDENTIFICATION RESULTS")
        print(self.section_separator)
        
        # 显示Qdrive识别结果
        if qdrive_drives:
            self._display_qdrive_results(qdrive_drives, analyzer)
        
        # 显示Vector识别结果
        if vector_drives:
            self._display_vector_results(vector_drives, analyzer)
        
        # 显示Transfer识别结果
        if transfer_drives:
            self._display_transfer_results(transfer_drives, analyzer)
        
        # 显示Backup识别结果
        if backup_drives:
            self._display_backup_results(backup_drives, analyzer)
        
        # 显示总结信息
        self._display_summary(qdrive_drives, vector_drives, transfer_drives, backup_drives)
        
        # 用户确认选项
        return self._get_user_confirmation()
    
    def _display_qdrive_results(self, qdrive_drives: List[str], analyzer):
        """显示Qdrive识别结果"""
        print(f"\n🚗 QDRIVE DATA DRIVES ({len(qdrive_drives)} drives):")
        print(self.subsection_separator)
        
        for i, drive in enumerate(qdrive_drives, 1):
            print(f"\n🔹 Qdrive {i}: {drive}")
            
            # 分析驱动器结构
            structure = analyzer.analyze_drive_structure(drive)
            tree_lines = analyzer.generate_simple_directory_tree(structure)
            
            # 显示目录树
            for line in tree_lines:
                print(f"   {line}")
            
            # 显示分析时间
            if 'analysis_time' in structure:
                print(f"   ⏰ Analyzed at: {structure['analysis_time']}")
    
    def _display_vector_results(self, vector_drives: List[str], analyzer):
        """显示Vector识别结果"""
        print(f"\n📊 VECTOR DATA DRIVES ({len(vector_drives)} drives):")
        print(self.subsection_separator)
        
        for i, drive in enumerate(vector_drives, 1):
            print(f"\n🔹 Vector {i}: {drive}")
            
            # 分析驱动器结构
            structure = analyzer.analyze_drive_structure(drive)
            tree_lines = analyzer.generate_simple_directory_tree(structure)
            
            # 显示目录树
            for line in tree_lines:
                print(f"   {line}")
            
            # 显示分析时间
            if 'analysis_time' in structure:
                print(f"   ⏰ Analyzed at: {structure['analysis_time']}")
    
    def _display_transfer_results(self, transfer_drives: List[str], analyzer):
        """显示Transfer识别结果"""
        print(f"\n🔄 TRANSFER DRIVES ({len(transfer_drives)} drives):")
        print(self.subsection_separator)
        
        for i, drive in enumerate(transfer_drives, 1):
            print(f"\n🔹 Transfer {i}: {drive}")
            
            # 分析驱动器结构
            structure = analyzer.analyze_drive_structure(drive)
            tree_lines = analyzer.generate_simple_directory_tree(structure)
            
            # 显示目录树
            for line in tree_lines:
                print(f"   {line}")
            
            # 显示分析时间
            if 'analysis_time' in structure:
                print(f"   ⏰ Analyzed at: {structure['analysis_time']}")
    
    def _display_backup_results(self, backup_drives: List[str], analyzer):
        """显示Backup识别结果"""
        print(f"\n💾 BACKUP DRIVES ({len(backup_drives)} drives):")
        print(self.subsection_separator)
        
        for i, drive in enumerate(backup_drives, 1):
            print(f"\n🔹 Backup {i}: {drive}")
            
            # 分析驱动器结构
            structure = analyzer.analyze_drive_structure(drive)
            tree_lines = analyzer.generate_simple_directory_tree(structure)
            
            # 显示目录树
            for line in tree_lines:
                print(f"   {line}")
            
            # 显示分析时间
            if 'analysis_time' in structure:
                print(f"   ⏰ Analyzed at: {structure['analysis_time']}")
    
    def _display_summary(self, qdrive_drives: List[str], vector_drives: List[str], 
                        transfer_drives: List[str], backup_drives: List[str]):
        """显示总结信息"""
        print(f"\n📋 IDENTIFICATION SUMMARY:")
        print(self.subsection_separator)
        
        total_drives = len(qdrive_drives) + len(vector_drives) + len(transfer_drives) + len(backup_drives)
        
        print(f"   🚗 Qdrive Data Drives: {len(qdrive_drives)}")
        print(f"   📊 Vector Data Drives: {len(vector_drives)}")
        print(f"   🔄 Transfer Drives: {len(transfer_drives)}")
        print(f"   💾 Backup Drives: {len(backup_drives)}")
        print(f"   📈 Total Drives: {total_drives}")
        
        # 显示识别时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"   ⏰ Identification Time: {current_time}")
    
    def _get_user_confirmation(self) -> str:
        """获取用户确认"""
        print(f"\n{self.section_separator}")
        print("❓ CONFIRMATION REQUIRED")
        print(self.section_separator)
        print("Please review the identification results above.")
        print("Options:")
        print("  [Y] Yes, proceed with data copy")
        print("  [N] No, re-identify drives")
        print("  [M] Manual adjustment")
        print("  [Q] Quit")
        
        while True:
            try:
                choice = input("\nYour choice (Y/N/M/Q): ").strip().upper()
                if choice in ['Y', 'N', 'M', 'Q']:
                    return choice
                else:
                    print("❌ Invalid choice. Please enter Y, N, M, or Q.")
            except KeyboardInterrupt:
                print("\n\n👋 Operation cancelled by user.")
                return 'Q'
            except Exception as e:
                print(f"❌ Input error: {e}")
                print("Please try again.")
    
    def handle_user_confirmation(self, choice: str, detector) -> Tuple[bool, List[str], List[str], List[str], List[str]]:
        """
        处理用户确认选择
        
        Args:
            choice: 用户选择
            detector: 驱动器检测器实例
            
        Returns:
            Tuple[bool, List[str], List[str], List[str], List[str]]: 
            (是否继续, qdrive_drives, vector_drives, transfer_drives, backup_drives)
        """
        if choice == 'Y':
            print("✅ Proceeding with data copy...")
            return True, None, None, None, None
        elif choice == 'N':
            print("🔄 Re-identifying drives...")
            # 重新识别驱动器
            qdrive_drives, vector_drives, transfer_drives, backup_drives = detector.identify_data_drives()
            return False, qdrive_drives, vector_drives, transfer_drives, backup_drives
        elif choice == 'M':
            print("🔧 Manual adjustment mode...")
            return self._manual_drive_adjustment(detector)
        elif choice == 'Q':
            print("👋 Exiting...")
            return False, [], [], [], []
    
    def _manual_drive_adjustment(self, detector) -> Tuple[bool, List[str], List[str], List[str], List[str]]:
        """
        手动调整驱动器分类
        
        Args:
            detector: 驱动器检测器实例
            
        Returns:
            Tuple[bool, List[str], List[str], List[str], List[str]]: 
            (是否继续, qdrive_drives, vector_drives, transfer_drives, backup_drives)
        """
        print("\n🔧 MANUAL DRIVE ADJUSTMENT")
        print(self.subsection_separator)
        print("This feature allows you to manually adjust drive classifications.")
        print("For now, this will re-run the automatic identification.")
        print("Future versions will support manual drive type assignment.")
        
        # 重新识别驱动器
        qdrive_drives, vector_drives, transfer_drives, backup_drives = detector.identify_data_drives()
        return False, qdrive_drives, vector_drives, transfer_drives, backup_drives
    
    def display_confirmation_result(self, choice: str):
        """显示确认结果"""
        if choice == 'Y':
            print("✅ User confirmed identification results. Proceeding with data copy...")
        elif choice == 'N':
            print("🔄 User requested re-identification. Re-analyzing drives...")
        elif choice == 'M':
            print("🔧 User requested manual adjustment. Entering adjustment mode...")
        elif choice == 'Q':
            print("👋 User chose to quit. Exiting program...")
    
    def display_error_message(self, message: str):
        """显示错误消息"""
        print(f"\n❌ ERROR: {message}")
        print(self.subsection_separator)
    
    def display_success_message(self, message: str):
        """显示成功消息"""
        print(f"\n✅ SUCCESS: {message}")
        print(self.subsection_separator)
    
    def display_warning_message(self, message: str):
        """显示警告消息"""
        print(f"\n⚠️ WARNING: {message}")
        print(self.subsection_separator)
