#!/bin/bash
# The Matrix 运行脚本

# 激活conda环境
eval "$(conda shell.bash hook)"
conda activate TheMatrix

# 切换到项目目录
cd "$(dirname "$0")"

# 运行
if [ $# -eq 0 ]; then
    python main.py
else
    python main.py "$@"
fi
