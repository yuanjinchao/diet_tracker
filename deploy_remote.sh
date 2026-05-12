#!/bin/bash
# 减肥打卡应用部署脚本
# 用途：更新应用程序版本，不修改数据库文件

set -e

# 配置
APP_DIR="/var/www/diet_tracker"
VENV_DIR="$APP_DIR/venv"

# 默认分支
DEFAULT_BRANCH="dev20260509"
BRANCH="${1:-$DEFAULT_BRANCH}"

echo "=========================================="
echo "减肥打卡应用部署脚本"
echo "分支: $BRANCH"
echo "=========================================="
echo ""

# 1. 检查目录
if [ ! -d "$APP_DIR" ]; then
    echo "错误: 应用目录不存在 $APP_DIR"
    exit 1
fi

# 2. 进入应用目录
cd "$APP_DIR"
echo "进入应用目录: $APP_DIR"

# 3. 拉取最新代码
echo ""
echo "正在拉取最新代码..."
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

# 4. 更新依赖（如果 requirements.txt 有变化）
echo ""
echo "检查依赖更新..."
$VENV_DIR/bin/pip install -r requirements.txt -q

# 5. 重启服务
echo ""
echo "重启 gunicorn 服务..."

# 查找并重启 gunicorn
MAIN_PID=$(ps aux | grep "gunicorn.*app:app" | grep -v grep | head -1 | awk '{print $2}')
if [ -n "$MAIN_PID" ]; then
    echo "找到 gunicorn 主进程: $MAIN_PID"
    kill -HUP "$MAIN_PID"
    echo "发送 HUP 信号给进程 $MAIN_PID"
else
    echo "警告: 未找到运行中的 gunicorn 进程，尝试启动..."
    $VENV_DIR/bin/gunicorn --workers=3 --bind=0.0.0.0:8000 --daemon --pid=/var/www/diet_tracker/gunicorn.pid app:app
fi

# 等待服务重启
sleep 3

# 6. 验证部署
echo ""
echo "验证部署..."
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo "服务启动成功"
else
    echo "服务启动失败，请检查日志"
    exit 1
fi

echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
