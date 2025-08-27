#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
极致优化的Windows EXE打包脚本 - 追求最小文件大小
Ultra-optimized Windows EXE Build Script - Pursue minimal file size
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

def create_minimal_spec_file():
    """创建极致优化的PyInstaller配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 绝对最小化的数据文件 - 只包含核心配置
datas = [
    ('config.ini', '.'),
]

# 精确的隐藏导入 - 只包含实际使用的核心模块
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
]

# 极致的排除列表 - 排除所有不需要的模块
excludes = [
    # 科学计算库
    'matplotlib', 'numpy', 'pandas', 'scipy', 'scikit-learn', 'tensorflow', 'torch',
    
    # 图像处理
    'PIL', 'Pillow', 'opencv', 'cv2', 'imageio', 'scikit-image',
    
    # GUI框架
    'tkinter', 'PyQt5', 'PySide2', 'wx', 'kivy', 'pygame',
    
    # Web框架
    'flask', 'django', 'fastapi', 'tornado', 'aiohttp', 'requests', 'urllib3',
    
    # 数据库
    'sqlite3', 'mysql', 'postgresql', 'mongodb', 'redis', 'sqlalchemy', 'peewee',
    
    # 网络和通信
    'socket', 'ssl', 'http', 'urllib', 'ftplib', 'telnetlib', 'poplib', 'imaplib',
    'nntplib', 'smtplib', 'smtpd', 'xmlrpc', 'webbrowser', 'cgi', 'cgitb',
    
    # 测试框架
    'pytest', 'unittest', 'doctest', 'nose', 'tox', 'coverage',
    
    # 调试工具
    'pdb', 'profile', 'cProfile', 'trace', 'pickletools', 'pydoc',
    
    # 文档处理
    'docx', 'openpyxl', 'xlrd', 'xlwt', 'reportlab', 'jinja2', 'markdown',
    
    # 压缩和归档
    'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma', 'zlib', 'rarfile',
    
    # 加密和安全
    'cryptography', 'pycryptodome', 'bcrypt', 'passlib', 'hashlib',
    
    # 多媒体
    'moviepy', 'pydub', 'librosa', 'soundfile', 'wave', 'audioop',
    
    # 机器学习
    'sklearn', 'xgboost', 'lightgbm', 'catboost', 'optuna', 'hyperopt',
    
    # 数据处理
    'pandas', 'numpy', 'xarray', 'dask', 'vaex', 'modin', 'polars',
    
    # 可视化
    'matplotlib', 'seaborn', 'plotly', 'bokeh', 'altair', 'holoviews',
    
    # 地理信息
    'geopandas', 'shapely', 'fiona', 'pyproj', 'folium', 'geopy',
    
    # 时间序列
    'pandas', 'numpy', 'statsmodels', 'prophet', 'pmdarima',
    
    # 统计
    'scipy', 'statsmodels', 'pingouin', 'scikit-posthocs',
    
    # 文本处理
    'nltk', 'spacy', 'textblob', 'gensim', 'transformers', 'sentence_transformers',
    
    # 自然语言处理
    'nltk', 'spacy', 'textblob', 'gensim', 'transformers', 'sentence_transformers',
    
    # 计算机视觉
    'opencv', 'cv2', 'imageio', 'scikit-image', 'albumentations',
    
    # 音频处理
    'librosa', 'pydub', 'soundfile', 'wave', 'audioop', 'pyaudio',
    
    # 并行计算
    'multiprocessing', 'asyncio', 'concurrent.futures', 'threading',
    
    # 系统管理
    'psutil', 'pywin32', 'wmi', 'winreg', 'win32com',
    
    # 其他常用库
    'beautifulsoup4', 'lxml', 'html5lib', 'selenium', 'scrapy', 'requests',
    'urllib3', 'httpx', 'aiohttp', 'websockets', 'grpc', 'thrift',
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
    noarchive=True,  # 禁用归档
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
    strip=True,      # 启用strip
    upx=True,        # 启用UPX
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
    
    with open('DataCopyTool_minimal.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 创建极致优化的PyInstaller配置文件: DataCopyTool_minimal.spec")

def install_upx():
    """安装UPX压缩工具"""
    print("🔧 检查UPX压缩工具...")
    try:
        result = subprocess.run(['upx', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ UPX已安装")
            return True
    except FileNotFoundError:
        pass
    
    print("📦 正在安装UPX...")
    try:
        # 尝试多种安装方式
        install_methods = [
            ['choco', 'install', 'upx', '-y'],
            ['winget', 'install', 'upx.upx'],
            ['scoop', 'install', 'upx'],
        ]
        
        for method in install_methods:
            try:
                subprocess.run(method, check=True)
                print(f"✅ UPX安装成功 (使用 {method[0]})")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        print("⚠️ 无法自动安装UPX，将使用PyInstaller内置压缩")
        return False
    except Exception as e:
        print(f"⚠️ UPX安装失败: {e}")
        return False

def build_minimal_exe():
    """构建极致优化的exe文件"""
    print("🔨 开始构建极致优化的Windows EXE文件...")
    
    try:
        subprocess.run([
            'pyinstaller',
            '--clean',
            '--distpath', 'dist_minimal',
            '--workpath', 'build_minimal',
            '--log-level', 'WARN',  # 减少日志输出
            'DataCopyTool_minimal.spec'
        ], check=True)
        print("✅ 极致优化的EXE文件构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ EXE文件构建失败: {e}")
        return False

def analyze_file_size():
    """分析文件大小"""
    dist_dir = Path("dist_minimal")
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
        
        # 大小对比
        print(f"\n💾 优化效果:")
        print(f"  - EXE文件: {size_mb:.2f} MB")
        print(f"  - 总大小: {total_mb:.2f} MB")
        if size_mb < 10:
            print(f"  - 🎯 目标达成: 文件大小 < 10MB")
        else:
            print(f"  - ⚠️ 文件仍然较大，可能需要进一步优化")

def create_ultra_minimal_launcher():
    """创建超最小化启动脚本"""
    bat_content = '''@echo off
DataCopyTool.exe
'''
    
    with open('启动数据拷贝工具.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print("✅ 创建超最小化启动脚本: 启动数据拷贝工具.bat")

def main():
    """主函数"""
    print("🚀 极致优化的Windows EXE打包工具 - 追求最小文件大小")
    print("="*70)
    
    # 1. 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ 无法安装PyInstaller，打包失败")
            return
    
    # 2. 安装UPX压缩工具
    install_upx()
    
    # 3. 创建极致优化的spec文件
    create_minimal_spec_file()
    
    # 4. 构建极致优化的exe文件
    if build_minimal_exe():
        # 5. 创建超最小化启动脚本
        create_ultra_minimal_launcher()
        
        # 6. 分析文件大小
        analyze_file_size()
        
        print("\n🎉 极致优化的Windows EXE打包完成！")
        print("📁 生成的文件在 dist_minimal/ 目录中")
        print("💡 极致优化措施:")
        print("  - 排除了所有不需要的模块 (100+ 模块)")
        print("  - 启用了UPX压缩")
        print("  - 启用了strip优化")
        print("  - 禁用了归档功能")
        print("  - 最小化了数据文件")
        print("  - 精确控制隐藏导入")
        
        # 7. 复制必要文件
        dist_dir = Path("dist_minimal")
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
        
        print("\n🚀 现在可以将dist_minimal目录打包分发给Windows用户！")
        print("💾 文件大小已优化到极致！")
        print("🎯 目标: 生成 < 10MB 的EXE文件")
    else:
        print("❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main()
