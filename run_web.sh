#!/bin/bash
# 启动 The Matrix Web UI

cd "$(dirname "$0")"

# 激活 conda 环境
source ~/anaconda3/etc/profile.d/conda.sh
conda activate base

# 启动 FastAPI 服务
python -m uvicorn web.main:app --host 0.0.0.0 --port 8000 --reload
