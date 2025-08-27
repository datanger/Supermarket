#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows EXE打包脚本
Windows EXE Build Script
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller已安装，版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("📦 正在安装PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller安装失败: {e}")
        return False

def create_spec_file():
    """创建PyInstaller配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 数据文件
datas = [
    ('data_copy_modules', 'data_copy_modules'),
    ('config.ini', '.'),
    ('requirements.txt', '.'),
    ('README.md', '.'),
    ('xuqiu.txt', '.'),
    ('COPY_LOGIC_DETAILED.md', '.'),
]

# 隐藏导入
hiddenimports = [
    'psutil',
    'tqdm',
    'concurrent.futures',
    'platform',
    'subprocess',
    'logging',
    'os',
    'sys',
    'shutil',
    'datetime',
    're',
    'typing',
    'threading',
    'time',
]

a = Analysis(
    ['run_interactive.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DataCopyTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('DataCopyTool.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 创建PyInstaller配置文件: DataCopyTool.spec")

def build_exe():
    """构建exe文件"""
    print("🔨 开始构建Windows EXE文件...")
    
    # 使用spec文件构建
    try:
        subprocess.run([
            'pyinstaller',
            '--clean',
            'DataCopyTool.spec'
        ], check=True)
        print("✅ EXE文件构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ EXE文件构建失败: {e}")
        return False

def create_windows_launcher():
    """创建Windows启动脚本"""
    bat_content = '''@echo off
chcp 65001 >nul
echo 数据拷贝工具启动中...
echo.
DataCopyTool.exe
pause
'''
    
    with open('启动数据拷贝工具.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print("✅ 创建Windows启动脚本: 启动数据拷贝工具.bat")

def create_install_guide():
    """创建Windows安装指南"""
    guide_content = '''# 🚀 Windows安装使用指南

## 📋 系统要求
- Windows 7/8/10/11 (64位)
- 无需安装Python
- 无需安装任何依赖包

## 🎯 使用方法

### 方法1：直接运行
1. 双击 `DataCopyTool.exe`
2. 按照提示操作

### 方法2：使用启动脚本
1. 双击 `启动数据拷贝工具.bat`
2. 工具会自动启动

### 方法3：命令行运行
1. 打开命令提示符
2. 切换到工具目录
3. 运行 `DataCopyTool.exe`

## 🔧 功能特性
- ✅ 自动识别所有外接驱动器
- ✅ 支持BitLocker加密驱动器解锁
- ✅ 智能分类Qdrive、Vector等数据盘
- ✅ 自动处理同名文件
- ✅ 支持A/B盘选择
- ✅ 完整的拷贝进度显示

## 📁 文件说明
- `DataCopyTool.exe` - 主程序文件
- `启动数据拷贝工具.bat` - Windows启动脚本
- `config.ini` - 配置文件
- `README.md` - 详细说明文档

## ⚠️ 注意事项
1. 首次运行可能需要Windows Defender允许
2. 确保有足够的磁盘空间
3. 建议以管理员身份运行（处理BitLocker时）

## 🆘 常见问题
Q: 运行时提示"Windows已保护你的电脑"
A: 点击"仍要运行"，这是正常的Windows安全提示

Q: 无法识别外接驱动器
A: 确保驱动器已正确连接并被Windows识别

Q: BitLocker解锁失败
A: 确保输入了正确的恢复密钥
'''
    
    with open('Windows安装使用指南.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ 创建Windows安装指南: Windows安装使用指南.md")

def main():
    """主函数"""
    print("🚀 Windows EXE打包工具")
    print("="*50)
    
    # 1. 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ 无法安装PyInstaller，打包失败")
            return
    
    # 2. 创建spec文件
    create_spec_file()
    
    # 3. 构建exe文件
    if build_exe():
        # 4. 创建Windows启动脚本
        create_windows_launcher()
        
        # 5. 创建安装指南
        create_install_guide()
        
        print("\n🎉 Windows EXE打包完成！")
        print("📁 生成的文件:")
        print("  - dist/DataCopyTool.exe (主程序)")
        print("  - 启动数据拷贝工具.bat (启动脚本)")
        print("  - Windows安装使用指南.md (使用说明)")
        
        # 6. 复制必要文件到dist目录
        dist_dir = Path("dist")
        if dist_dir.exists():
            print("\n📋 正在复制配置文件...")
            files_to_copy = [
                "config.ini",
                "README.md", 
                "xuqiu.txt",
                "COPY_LOGIC_DETAILED.md",
                "启动数据拷贝工具.bat",
                "Windows安装使用指南.md"
            ]
            
            for file in files_to_copy:
                if Path(file).exists():
                    shutil.copy2(file, dist_dir)
                    print(f"  ✅ 复制: {file}")
                else:
                    print(f"  ⚠️ 文件不存在: {file}")
        
        print("\n🚀 现在可以将dist目录打包分发给Windows用户！")
    else:
        print("❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main()
