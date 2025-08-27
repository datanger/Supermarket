#!/bin/bash

# 🚀 Linux环境下Windows EXE打包脚本
# Windows EXE Build Script for Linux Environment

echo "🚀 开始为Windows系统打包EXE文件..."
echo "=================================================="

# 检查Python环境
echo "🔍 检查Python环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3未安装或不在PATH中"
    exit 1
fi

# 检查pip
echo "🔍 检查pip..."
python3 -m pip --version
if [ $? -ne 0 ]; then
    echo "❌ pip未安装"
    exit 1
fi

# 安装PyInstaller
echo "📦 安装PyInstaller..."
python3 -m pip install pyinstaller
if [ $? -ne 0 ]; then
    echo "❌ PyInstaller安装失败"
    exit 1
fi

echo "✅ PyInstaller安装成功"

# 创建spec文件
echo "📝 创建PyInstaller配置文件..."
cat > DataCopyTool.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

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
EOF

echo "✅ 配置文件创建成功"

# 构建exe文件
echo "🔨 开始构建Windows EXE文件..."
pyinstaller --clean DataCopyTool.spec

if [ $? -eq 0 ]; then
    echo "✅ EXE文件构建成功！"
    
    # 创建Windows启动脚本
    echo "📝 创建Windows启动脚本..."
    cat > "启动数据拷贝工具.bat" << 'EOF'
@echo off
chcp 65001 >nul
echo 数据拷贝工具启动中...
echo.
DataCopyTool.exe
pause
EOF
    
    # 创建Windows安装指南
    echo "📝 创建Windows安装指南..."
    cat > "Windows安装使用指南.md" << 'EOF'
# 🚀 Windows安装使用指南

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
EOF
    
    # 复制必要文件到dist目录
    echo "📋 复制配置文件到dist目录..."
    cp -f config.ini dist/
    cp -f README.md dist/
    cp -f xuqiu.txt dist/
    cp -f COPY_LOGIC_DETAILED.md dist/
    cp -f "启动数据拷贝工具.bat" dist/
    cp -f "Windows安装使用指南.md" dist/
    
    echo ""
    echo "🎉 Windows EXE打包完成！"
    echo "=================================================="
    echo "📁 生成的文件:"
    echo "  - dist/DataCopyTool.exe (主程序)"
    echo "  - dist/启动数据拷贝工具.bat (启动脚本)"
    echo "  - dist/Windows安装使用指南.md (使用说明)"
    echo "  - dist/config.ini (配置文件)"
    echo "  - dist/README.md (说明文档)"
    echo ""
    echo "🚀 现在可以将dist目录打包分发给Windows用户！"
    echo "📦 建议将dist目录压缩为zip文件，方便分发"
    
    # 创建压缩包
    echo "📦 创建Windows分发压缩包..."
    cd dist
    zip -r ../DataCopyTool_Windows.zip ./*
    cd ..
    echo "✅ 创建压缩包: DataCopyTool_Windows.zip"
    
else
    echo "❌ EXE文件构建失败"
    exit 1
fi

echo ""
echo "🎯 打包完成！"
echo "📁 主要文件:"
echo "  - DataCopyTool_Windows.zip (Windows分发包)"
echo "  - dist/ (包含所有Windows文件)"
echo "  - DataCopyTool.spec (PyInstaller配置)"
