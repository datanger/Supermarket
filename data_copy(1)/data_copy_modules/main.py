#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据拷贝工具主程序
Data Copy Tool Main Program
"""

import logging
import os
try:
    from core.system_detector import CrossPlatformSystemDetector
    from logging_utils.copy_logger import setup_copy_logger
except ImportError:
    from data_copy_modules.core.system_detector import CrossPlatformSystemDetector
    from data_copy_modules.logging_utils.copy_logger import setup_copy_logger

# 配置日志
def setup_main_logger():
    """设置主程序日志记录器"""
    # 创建logs根目录
    logs_root = "logs"
    if not os.path.exists(logs_root):
        os.makedirs(logs_root)
    
    # 创建以运行时间命名的二级目录
    import datetime
    run_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_subdir = os.path.join(logs_root, run_time)
    if not os.path.exists(log_subdir):
        os.makedirs(log_subdir)
    
    # 配置日志
    system_log_file = os.path.join(log_subdir, "system_detector.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(system_log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_main_logger()

def main():
    """主函数 - 演示跨平台系统检测和数据拷贝功能"""
    print("跨平台系统检测与数据拷贝工具")
    print("=" * 50)
    
    # 设置拷贝日志记录器
    copy_log_file, filelist_log_file = setup_copy_logger()
    print(f"拷贝日志文件: {copy_log_file}")
    print(f"文件列表日志文件: {filelist_log_file}")
    
    # 创建系统检测器实例
    detector = CrossPlatformSystemDetector()
    
    try:
        # 1. 检测所有驱动器
        print("\n1. 正在检测所有可用驱动器...")
        drives = detector.detect_all_drives()
        
        if not drives:
            print("未检测到任何驱动器，程序退出")
            return
        
        # 2. 获取系统驱动器
        print("\n2. 正在识别系统驱动器...")
        system_drives = detector.get_system_drives()
        
        # 3. 分类驱动器
        print("\n3. 正在分类驱动器...")
        source_drives, destination_drives = detector.classify_drives()
        
        # 4. 获取驱动器详细信息
        print("\n4. 正在获取驱动器详细信息...")
        drive_info = detector.get_drive_information()
        
        # 5. 检查BitLocker状态（仅Windows）
        if detector.os_type == "windows":
            print("\n5. 正在检查BitLocker状态...")
            locked_drives = [drive for drive, info in drive_info.items() 
                            if info.get('bitlocker_status') == 'Locked']
            
            if locked_drives:
                print(f"发现被BitLocker锁定的驱动器: {locked_drives}")
                print("\n正在解锁BitLocker加密的驱动器...")
                
                # 直接使用密码解锁所有驱动器
                unlock_results = detector.unlock_all_locked_drives(drive_info)
                
                if unlock_results:
                    print("\n解锁结果:")
                    for drive, success in unlock_results.items():
                        status = "成功" if success else "失败"
                        print(f"  {drive}: {status}")
                else:
                    print("解锁操作被取消或失败")
            else:
                print("未发现被BitLocker锁定的驱动器")
        else:
            print("\n5. 跳过BitLocker检查（非Windows系统）")
        
        # 6. 识别数据驱动器
        print("\n6. 正在识别数据驱动器...")
        detector.identify_data_drives()
        
        # 7. 询问是否执行数据拷贝
        print("\n7. 驱动器识别完成")
        response = input("是否要执行数据拷贝计划？(y/n): ").lower().strip()
        
        if response == 'y':
            print("\n开始执行数据拷贝计划...")
            success = detector.execute_data_copy_plan()
            if success:
                print("数据拷贝计划执行完成")
            else:
                print("数据拷贝计划执行失败")
        else:
            print("跳过数据拷贝步骤")
        
        # 8. 打印摘要
        detector.print_summary()
        
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        logger.error(f"程序执行出错: {e}", exc_info=True)
    finally:
        print("\n程序执行完成")

if __name__ == "__main__":
    main() 