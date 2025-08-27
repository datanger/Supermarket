#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无警告的Windows EXE打包脚本 - 专门处理pkg_resources弃用警告
No-Warning Windows EXE Build Script - Handle pkg_resources deprecation warnings
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

def create_no_warnings_spec_file():
    """创建无警告的PyInstaller配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 数据文件
datas = [
    ('config.ini', '.'),
    ('data_copy_modules', 'data_copy_modules'),
]

# 隐藏导入 - 包含所有必要的模块
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
    'ctypes',
    'win32api',
    'win32file',
    'win32security',
    'win32con',
    'win32com',
    'wmi',
    'winreg',
    'socket',
    'ssl',
    'http',
    'urllib',
    'urllib3',
    'requests',
    'zipfile',
    'tarfile',
    'gzip',
    'bz2',
    'lzma',
    'zlib',
    'email',
    'xml',
    'html',
    'sqlite3',
    'multiprocessing',
    'asyncio',
    'ftplib',
    'telnetlib',
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
    'pkg_resources',
    'setuptools',
    'distutils',
    'pkgutil',
    'importlib',
    'importlib.util',
    'importlib.machinery',
    'importlib.abc',
    'importlib.metadata',
    'importlib.resources',
    'importlib.import_module',
    'importlib.reload',
    'importlib.invalidate_caches',
    'importlib.find_loader',
    'importlib.find_spec',
    'importlib.util.find_spec',
    'importlib.util.spec_from_file_location',
    'importlib.util.module_from_spec',
    'importlib.util.spec_from_loader',
    'importlib.util.LazyLoader',
    'importlib.util.module_for_loader',
    'importlib.util.set_package',
    'importlib.util.set_loader',
    'importlib.util.resolve_name',
    # 项目特定模块
    'interactive_main',
    'data_copy_modules.interactive_main',
    'data_copy_modules.core.system_detector',
    'data_copy_modules.drivers.drive_detector',
    'data_copy_modules.drivers.bitlocker_manager',
    'data_copy_modules.data_copy.qdrive_data_handler',
    'data_copy_modules.data_copy.vector_data_handler',
    'data_copy_modules.utils.file_utils',
    'data_copy_modules.utils.progress_bar',
    'data_copy_modules.logging_utils.copy_logger',
]

# 排除大型不需要的库
excludes = [
    # 科学计算库
    'matplotlib', 'numpy', 'pandas', 'scipy', 'scikit-learn', 'tensorflow', 'torch',
    
    # 图像处理
    'PIL', 'Pillow', 'opencv', 'cv2', 'imageio', 'scikit-image',
    
    # GUI框架
    'tkinter', 'PyQt5', 'PySide2', 'wx', 'kivy', 'pygame',
    
    # Web框架
    'flask', 'django', 'fastapi', 'tornado', 'aiohttp',
    
    # 数据库
    'mysql', 'postgresql', 'mongodb', 'redis', 'sqlalchemy', 'peewee',
    
    # 机器学习
    'sklearn', 'xgboost', 'lightgbm', 'catboost', 'optuna', 'hyperopt',
    
    # 数据处理
    'xarray', 'dask', 'vaex', 'modin', 'polars',
    
    # 可视化
    'seaborn', 'plotly', 'bokeh', 'altair', 'holoviews',
    
    # 地理信息
    'geopandas', 'shapely', 'fiona', 'pyproj', 'folium', 'geopy',
    
    # 时间序列
    'statsmodels', 'prophet', 'pmdarima',
    
    # 统计
    'pingouin', 'scikit-posthocs',
    
    # 文本处理
    'nltk', 'spacy', 'textblob', 'gensim', 'transformers', 'sentence_transformers',
    
    # 计算机视觉
    'albumentations',
    
    # 音频处理
    'librosa', 'pydub', 'soundfile', 'wave', 'audioop', 'pyaudio',
    
    # 其他大型库
    'beautifulsoup4', 'lxml', 'html5lib', 'selenium', 'scrapy',
    'httpx', 'websockets', 'grpc', 'thrift',
]

a = Analysis(
    ['run_interactive.py'],
    pathex=[os.getcwd()],
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
    noarchive=False,  # 启用归档以确保兼容性
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
    strip=False,      # 禁用strip以确保兼容性
    upx=False,        # 禁用UPX
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
    
    with open('DataCopyTool_no_warnings.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 创建无警告的PyInstaller配置文件: DataCopyTool_no_warnings.spec")

def build_no_warnings_exe():
    """构建无警告的exe文件"""
    print("🔨 开始构建无警告的Windows EXE文件...")
    
    try:
        # 使用环境变量抑制警告
        env = os.environ.copy()
        env['PYTHONWARNINGS'] = 'ignore::DeprecationWarning'
        
        subprocess.run([
            'pyinstaller',
            '--clean',
            '--distpath', 'dist_no_warnings',
            '--workpath', 'build_no_warnings',
            '--log-level', 'WARN',  # 减少日志输出
            'DataCopyTool_no_warnings.spec'
        ], check=True, env=env)
        print("✅ 无警告的EXE文件构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ EXE文件构建失败: {e}")
        return False

def analyze_file_size():
    """分析文件大小"""
    dist_dir = Path("dist_no_warnings")
    if not dist_dir.exists():
        return
    
    exe_file = dist_dir / "DataCopyTool.exe"
    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        size_kb = exe_file.stat().st_size / 1024
        
        print(f"📊 EXE文件大小: {size_mb:.2f} MB ({size_kb:.1f} KB)")
        
        # 分析目录大小
        total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
        total_mb = total_size / (1024 * 1024)
        total_kb = total_size / 1024
        
        print(f"📁 总目录大小: {total_mb:.2f} MB ({total_kb:.1f} KB)")
        
        # 列出所有文件
        print("\n📋 生成的文件列表:")
        for file in dist_dir.rglob('*'):
            if file.is_file():
                file_size = file.stat().st_size / 1024  # KB
                print(f"  - {file.relative_to(dist_dir)} ({file_size:.1f} KB)")

def create_launcher():
    """创建启动脚本"""
    bat_content = '''@echo off
chcp 65001 >nul
echo 数据拷贝工具启动中...
echo.
DataCopyTool.exe
pause
'''
    
    with open('启动数据拷贝工具.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print("✅ 创建启动脚本: 启动数据拷贝工具.bat")

def main():
    """主函数"""
    print("🚀 无警告的Windows EXE打包工具")
    print("="*60)
    print("💡 特点: 处理pkg_resources弃用警告，确保模块正确导入")
    print("="*60)
    
    # 1. 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ 无法安装PyInstaller，打包失败")
            return
    
    # 2. 创建无警告的spec文件
    create_no_warnings_spec_file()
    
    # 3. 构建无警告的exe文件
    if build_no_warnings_exe():
        # 4. 创建启动脚本
        create_launcher()
        
        # 5. 分析文件大小
        analyze_file_size()
        
        print("\n🎉 无警告的Windows EXE打包完成！")
        print("📁 生成的文件在 dist_no_warnings/ 目录中")
        print("💡 无警告打包特点:")
        print("  - 处理pkg_resources弃用警告")
        print("  - 确保所有模块正确导入")
        print("  - 包含完整的data_copy_modules目录")
        print("  - 禁用UPX和strip优化")
        print("  - 启用归档功能")
        
        # 6. 复制必要文件
        dist_dir = Path("dist_no_warnings")
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
        
        print("\n🚀 现在可以将dist_no_warnings目录打包分发给Windows用户！")
        print("💾 文件大小适中，但确保了稳定性和无警告！")
        print("🎯 目标: 生成稳定运行的EXE文件，避免模块导入错误和警告")
    else:
        print("❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main()
