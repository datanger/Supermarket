#!/bin/bash

# 脚本：为每个git tag创建独立版本文件夹（保持完整git历史）
# 功能：
# 1. 获取所有tag并为每个tag创建独立版本文件夹
# 2. 保持完整的git历史记录
# 3. 只保留最近的两个tag，删除更早的tag
# 4. 生成requirements文件，包含两个保留tag之间的commit message

set -e  # 遇到错误时退出

# 默认配置变量
SOURCE_DIR="/home/kotei/work/nj/Gen3CamLKASOFF"
TARGET_BASE_DIR="/home/kotei/work/nj/version_folders_corrected"
REPO_NAME="Gen3CamLKASOFF"

# 支持命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--source)
            SOURCE_DIR="$2"
            shift 2
            ;;
        -t|--target)
            TARGET_BASE_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "用法: $0 [选项]"
            echo "选项:"
            echo "  -s, --source DIR    源git仓库目录 (默认: $SOURCE_DIR)"
            echo "  -t, --target DIR    目标基础目录 (默认: $TARGET_BASE_DIR)"
            echo "  -h, --help          显示此帮助信息"
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 -h 或 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

# 验证源目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo "错误: 源目录不存在: $SOURCE_DIR"
    exit 1
fi

# 验证源目录是否是git仓库
if [ ! -d "$SOURCE_DIR/.git" ]; then
    echo "错误: 源目录不是git仓库: $SOURCE_DIR"
    exit 1
fi

# 创建目标基础目录
mkdir -p "$TARGET_BASE_DIR"

echo "=========================================="
echo "Git版本文件夹创建脚本（保持完整历史）"
echo "=========================================="
echo "源目录: $SOURCE_DIR"
echo "目标目录: $TARGET_BASE_DIR"
echo "=========================================="

# 进入源目录
cd "$SOURCE_DIR"

# 获取所有tag，按版本号排序（最新的在前）
TAGS=($(git tag --sort=-version:refname))

if [ ${#TAGS[@]} -eq 0 ]; then
    echo "错误: 没有找到任何git tags"
    exit 1
fi

echo "找到 ${#TAGS[@]} 个tags:"
for tag in "${TAGS[@]}"; do
    echo "  - $tag"
done

echo ""
echo "开始处理每个版本..."

# 为每个tag创建独立版本文件夹
for i in "${!TAGS[@]}"; do
    CURRENT_TAG="${TAGS[$i]}"
    VERSION_FOLDER="$TARGET_BASE_DIR/${CURRENT_TAG}"
    
    echo ""
    echo "----------------------------------------"
    echo "处理版本: $CURRENT_TAG ($((i+1))/${#TAGS[@]})"
    echo "----------------------------------------"
    
    # 创建版本文件夹
    mkdir -p "$VERSION_FOLDER"
    
    # 检出到该tag
    echo "检出到tag: $CURRENT_TAG"
    git checkout "$CURRENT_TAG" > /dev/null 2>&1
    
    # 复制整个git仓库到版本文件夹（包括.git目录）
    echo "复制完整git仓库到版本文件夹..."
    cp -r "$SOURCE_DIR" "$VERSION_FOLDER/"
    
    # 进入版本文件夹
    cd "$VERSION_FOLDER"
    
    # 重命名文件夹，去掉源目录名
    SOURCE_BASENAME=$(basename "$SOURCE_DIR")
    mv "$SOURCE_BASENAME" temp_folder
    mv temp_folder/* .
    mv temp_folder/.* . 2>/dev/null || true
    rm -rf temp_folder
    
    # 获取需要保留的tags（当前tag和下一个tag，如果存在）
    KEEP_TAGS=()
    KEEP_TAGS+=("$CURRENT_TAG")
    
    # 如果有下一个tag，也保留它
    if [ $((i+1)) -lt ${#TAGS[@]} ]; then
        NEXT_TAG="${TAGS[$((i+1))]}"
        KEEP_TAGS+=("$NEXT_TAG")
    fi
    
    echo "保留的tags: ${KEEP_TAGS[*]}"
    
    # 删除不需要的tags（保留最近的两个）
    ALL_TAGS_IN_REPO=($(git tag))
    deleted_count=0
    for tag_to_check in "${ALL_TAGS_IN_REPO[@]}"; do
        should_keep=false
        for keep_tag in "${KEEP_TAGS[@]}"; do
            if [ "$tag_to_check" = "$keep_tag" ]; then
                should_keep=true
                break
            fi
        done
        
        if [ "$should_keep" = false ]; then
            echo "删除tag: $tag_to_check"
            git tag -d "$tag_to_check" > /dev/null 2>&1
            deleted_count=$((deleted_count + 1))
        fi
    done
    
    if [ $deleted_count -gt 0 ]; then
        echo "删除了 $deleted_count 个旧tags"
    fi
    
    # 生成requirements文件
    REQUIREMENTS_FILE="$VERSION_FOLDER/requirements.md"
    echo "生成requirements文件: $REQUIREMENTS_FILE"
    
    echo "# Requirements for $CURRENT_TAG" > "$REQUIREMENTS_FILE"
    echo "" >> "$REQUIREMENTS_FILE"
    echo "## Changes between tags" >> "$REQUIREMENTS_FILE"
    echo "" >> "$REQUIREMENTS_FILE"
    
    # 获取两个保留tag之间的commit messages
    if [ ${#KEEP_TAGS[@]} -eq 2 ]; then
        NEWER_TAG="${KEEP_TAGS[0]}"
        OLDER_TAG="${KEEP_TAGS[1]}"
        
        echo "获取 $OLDER_TAG 到 $NEWER_TAG 之间的commit messages..."
        
        # 获取commit messages
        COMMITS=$(git log --pretty=format:"%s" "$OLDER_TAG..$NEWER_TAG" 2>/dev/null || echo "")
        
        if [ -n "$COMMITS" ]; then
            echo "### Commits between $OLDER_TAG and $NEWER_TAG" >> "$REQUIREMENTS_FILE"
            echo "" >> "$REQUIREMENTS_FILE"
            
            counter=1
            while IFS= read -r commit_msg; do
                if [ -n "$commit_msg" ]; then
                    echo "$counter. $commit_msg" >> "$REQUIREMENTS_FILE"
                    counter=$((counter + 1))
                fi
            done <<< "$COMMITS"
            
            echo "找到 $((counter-1)) 个commits"
        else
            echo "No commits found between $OLDER_TAG and $NEWER_TAG" >> "$REQUIREMENTS_FILE"
            echo "没有找到commits"
        fi
    else
        echo "Only one tag available: $CURRENT_TAG" >> "$REQUIREMENTS_FILE"
        echo "No comparison available." >> "$REQUIREMENTS_FILE"
        echo "只有一个tag，无法比较"
    fi
    
    echo "✓ 完成版本: $CURRENT_TAG"
    
    # 返回源目录
    cd "$SOURCE_DIR"
done

echo ""
echo "=========================================="
echo "所有版本文件夹已创建完成！"
echo "=========================================="
echo "目标目录: $TARGET_BASE_DIR"
echo ""
echo "创建的版本文件夹："
ls -la "$TARGET_BASE_DIR"

echo ""
echo "每个版本文件夹包含："
echo "- 完整的源代码文件"
echo "- 完整的git历史记录"
echo "- 只包含最近的两个tags"
echo "- requirements.md文件（包含commit messages）"
echo ""
echo "脚本执行完成！"
