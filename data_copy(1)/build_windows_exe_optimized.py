#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的Windows EXE打包脚本 - 专门针对减小文件大小
Optimized Windows EXE Build Script - Focus on reducing file size
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

def create_optimized_spec_file():
    """创建优化的PyInstaller配置文件 - 专门减小文件大小"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 最小化的数据文件 - 只包含必要的
datas = [
    ('config.ini', '.'),
    ('README.md', '.'),
]

# 精确的隐藏导入 - 只包含实际使用的模块
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
    'pathlib',
    'json',
    'hashlib',
    'stat',
]

# 排除不需要的模块 - 大幅减小文件大小
excludes = [
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    'tkinter',
    'PyQt5',
    'PySide2',
    'wx',
    'pytest',
    'unittest',
    'doctest',
    'pdb',
    'profile',
    'cProfile',
    'trace',
    'pickletools',
    'pydoc',
    'email',
    'http',
    'urllib',
    'xml',
    'html',
    'sqlite3',
    'multiprocessing',
    'asyncio',
    'ssl',
    'socket',
    'ftplib',
    'telnetlib',
    'poplib',
    'imaplib',
    'nntplib',
    'smtplib',
    'smtpd',
    'telnetlib',
    'ftplib',
    'poplib',
    'imaplib',
    'nntplib',
    'smtplib',
    'smtpd',
    'xmlrpc',
    'webbrowser',
    'cgi',
    'cgitb',
    'wsgiref',
    'urllib3',
    'requests',
    'beautifulsoup4',
    'lxml',
    'jinja2',
    'flask',
    'django',
    'sqlalchemy',
    'pymongo',
    'redis',
    'celery',
    'fabric',
    'ansible',
    'salt',
    'chef',
    'puppet',
    'vagrant',
    'docker',
    'kubernetes',
    'openshift',
    'helm',
    'terraform',
    'cloudformation',
    'boto3',
    'azure',
    'gcp',
    'openstack',
    'vsphere',
    'vmware',
    'hyperv',
    'xen',
    'kvm',
    'qemu',
    'virtualbox',
    'vmware',
    'parallels',
    'fusion',
    'workstation',
    'player',
    'esxi',
    'vcenter',
    'nsx',
    'vrealize',
    'vrops',
    'vra',
    'vro',
    'vcd',
    'vcloud',
    'vapp',
    'vdc',
    'org',
    'catalog',
    'template',
    'snapshot',
    'backup',
    'replication',
    'migration',
    'conversion',
    'p2v',
    'v2v',
    'p2p',
    'v2p',
    'p2c',
    'c2p',
    'c2v',
    'v2c',
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
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,  # 禁用归档以减小大小
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
    strip=True,  # 启用strip以减小大小
    upx=True,    # 启用UPX压缩
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
    
    with open('DataCopyTool_optimized.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 创建优化的PyInstaller配置文件: DataCopyTool_optimized.spec")

def install_upx():
    """安装UPX压缩工具"""
    print("🔧 检查UPX压缩工具...")
    try:
        # 检查UPX是否已安装
        result = subprocess.run(['upx', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ UPX已安装")
            return True
    except FileNotFoundError:
        pass
    
    print("📦 正在安装UPX...")
    try:
        # 使用chocolatey安装UPX (Windows)
        subprocess.run(['choco', 'install', 'upx', '-y'], check=True)
        print("✅ UPX安装成功")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ 无法自动安装UPX，将使用PyInstaller内置压缩")
        return False

def build_optimized_exe():
    """构建优化的exe文件"""
    print("🔨 开始构建优化的Windows EXE文件...")
    
    # 使用优化的spec文件构建
    try:
        subprocess.run([
            'pyinstaller',
            '--clean',
            '--distpath', 'dist_optimized',
            '--workpath', 'build_optimized',
            'DataCopyTool_optimized.spec'
        ], check=True)
        print("✅ 优化的EXE文件构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ EXE文件构建失败: {e}")
        return False

def analyze_file_size():
    """分析文件大小"""
    dist_dir = Path("dist_optimized")
    if not dist_dir.exists():
        return
    
    exe_file = dist_dir / "DataCopyTool.exe"
    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"📊 EXE文件大小: {size_mb:.2f} MB")
        
        # 分析目录大小
        total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
        total_mb = total_size / (1024 * 1024)
        print(f"📁 总目录大小: {total_mb:.2f} MB")
        
        # 列出所有文件
        print("\n📋 生成的文件列表:")
        for file in dist_dir.rglob('*'):
            if file.is_file():
                file_size = file.stat().st_size / 1024  # KB
                print(f"  - {file.relative_to(dist_dir)} ({file_size:.1f} KB)")

def create_minimal_launcher():
    """创建最小化的启动脚本"""
    bat_content = '''@echo off
chcp 65001 >nul
DataCopyTool.exe
'''
    
    with open('启动数据拷贝工具.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print("✅ 创建最小化启动脚本: 启动数据拷贝工具.bat")

def main():
    """主函数"""
    print("🚀 优化的Windows EXE打包工具 - 专注减小文件大小")
    print("="*60)
    
    # 1. 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ 无法安装PyInstaller，打包失败")
            return
    
    # 2. 安装UPX压缩工具
    install_upx()
    
    # 3. 创建优化的spec文件
    create_optimized_spec_file()
    
    # 4. 构建优化的exe文件
    if build_optimized_exe():
        # 5. 创建最小化启动脚本
        create_minimal_launcher()
        
        # 6. 分析文件大小
        analyze_file_size()
        
        print("\n🎉 优化的Windows EXE打包完成！")
        print("📁 生成的文件在 dist_optimized/ 目录中")
        print("💡 优化措施:")
        print("  - 排除了大量不需要的模块")
        print("  - 启用了UPX压缩")
        print("  - 启用了strip优化")
        print("  - 禁用了归档功能")
        print("  - 最小化了数据文件")
        
        # 7. 复制必要文件
        dist_dir = Path("dist_optimized")
        if dist_dir.exists():
            print("\n📋 正在复制必要文件...")
            files_to_copy = [
                "config.ini",
                "启动数据拷贝工具.bat"
            ]
            
            for file in files_to_copy:
                if Path(file).exists():
                    shutil.copy2(file, dist_dir)
                    print(f"  ✅ 复制: {file}")
        
        print("\n🚀 现在可以将dist_optimized目录打包分发给Windows用户！")
        print("💾 文件大小已优化到最小！")
    else:
        print("❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main()
