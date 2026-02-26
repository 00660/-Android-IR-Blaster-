#!/bin/bash

# IREXT 红外网关一键部署脚本（8081云端 + 8082本地解码）
# 用法: curl -fsSL https://raw.githubusercontent.com/00660/Android-IR-Blaster/main/install.sh | sudo bash

set -e

RAW_URL="https://raw.githubusercontent.com/00660/Android-IR-Blaster/main"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🚀 IREXT 红外网关部署脚本 (8081云端 + 8082本地解码)${NC}"
echo "======================================================"

# 检查架构
ARCH=$(uname -m)
echo -e "${BLUE}📋 系统架构: ${ARCH}${NC}"

if [[ "$ARCH" == "x86_64" ]]; then
    echo -e "${GREEN}✅ 支持 8081 云端解码 + 8082 本地解码${NC}"
    DEPLOY_LOCAL=true
else
    echo -e "${YELLOW}⚠️ 当前架构 ${ARCH} 只支持 8081 云端解码（本地解码仅支持 x86_64）${NC}"
    DEPLOY_LOCAL=false
fi

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️ 需要 root 权限，尝试 sudo...${NC}"
    if ! sudo -n true 2>/dev/null; then
        echo -e "${RED}❌ 需要 root 权限，请使用: sudo bash install.sh${NC}"
        exit 1
    fi
fi

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    echo "安装命令: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# 检查端口
check_port() {
    netstat -tuln 2>/dev/null | grep -q ":$1 " || ss -tuln 2>/dev/null | grep -q ":$1 "
}

echo -e "${YELLOW}🔍 检查端口占用...${NC}"

for port in 8080 8081 8082; do
    if check_port $port; then
        echo -e "${YELLOW}⚠️ 端口 ${port} 被占用，尝试释放...${NC}"
        fuser -k ${port}/tcp 2>/dev/null || true
        sleep 1
    fi
done

# 创建工作目录
INSTALL_DIR="/opt/irext"
echo -e "${YELLOW}📁 创建工作目录: ${INSTALL_DIR}${NC}"
mkdir -p "${INSTALL_DIR}"
cd "${INSTALL_DIR}"

# ==================== 部署 8081 云端解码 ====================
echo -e "${GREEN}🌐 部署 8081 云端解码服务...${NC}"

# 下载并解压数据包
if [ ! -d "/data" ]; then
    echo -e "${YELLOW}⬇️ 下载 irext-private-data...${NC}"
    wget -q --show-progress https://irext-lib-release.oss-cn-hangzhou.aliyuncs.com/pc-docker-image/1.5.2/irext-private-data_1.5.2.tar.gz -O data.tar.gz
    echo -e "${YELLOW}📦 解压数据包...${NC}"
    tar -xf data.tar.gz
    mv data /
    rm -f data.tar.gz
    echo -e "${GREEN}✅ 数据包已部署到 /data${NC}"
else
    echo -e "${YELLOW}⚠️ /data 已存在，跳过下载${NC}"
fi

# 拉取镜像
echo -e "${YELLOW}🐳 拉取云端解码镜像...${NC}"
docker pull crpi-r0wi5w1pz8m6ceho.cn-hangzhou.personal.cr.aliyuncs.com/irext-private/irext-private-cloud:1.5.2

# 停止旧容器
docker rm -f irext-private 2>/dev/null || true

# 启动 8081
echo -e "${YELLOW}🚀 启动 8081 云端解码...${NC}"
docker run -itd --restart unless-stopped \
    --name irext-private \
    -v /data:/data \
    -p 8080:8301 \
    -p 8081:8081 \
    crpi-r0wi5w1pz8m6ceho.cn-hangzhou.personal.cr.aliyuncs.com/irext-private/irext-private-cloud:1.5.2 \
    /data/start_irext.sh

# ==================== 部署 8082 本地解码（仅 x86）====================
if [ "$DEPLOY_LOCAL" = true ]; then
    echo -e "${GREEN}🖥️ 部署 8082 本地解码服务...${NC}"
    
    # 创建 8082 目录
    mkdir -p "${INSTALL_DIR}/decoder"
    cd "${INSTALL_DIR}/decoder"
    
    # 下载文件
    echo -e "${YELLOW}⬇️ 下载本地解码文件...${NC}"
    wget -q --show-progress "${RAW_URL}/ir_decoder_service.py" -O ir_decoder_service.py
    wget -q --show-progress "${RAW_URL}/libirdecode_jni_1.5.2_x86_64.so" -O libirdecode_jni_1.5.2_x86_64.so
    wget -q --show-progress "${RAW_URL}/Dockerfile" -O Dockerfile
    wget -q --show-progress "${RAW_URL}/docker-compose.yml" -O docker-compose.yml 2>/dev/null || true
    
    # 如果没有 docker-compose.yml，创建一个简单的
    if [ ! -f "docker-compose.yml" ]; then
        cat > docker-compose.yml << 'EOF'
version: '3'
services:
  decoder:
    build: .
    container_name: irext-decoder
    restart: unless-stopped
    ports:
      - "8082:8082"
    volumes:
      - ./:/app
EOF
    fi
    
    # 修改 Dockerfile 暴露 8082
    if ! grep -q "EXPOSE 8082" Dockerfile; then
        echo "EXPOSE 8082" >> Dockerfile
    fi
    
    # 构建并启动
    echo -e "${YELLOW}🔨 构建本地解码镜像...${NC}"
    docker-compose down 2>/dev/null || true
    docker-compose build --no-cache
    docker-compose up -d
    
    cd "${INSTALL_DIR}"
fi

# ==================== 检查状态 ====================
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 5

echo -e "${GREEN}📊 部署状态检查:${NC}"

# 检查 8081
if docker ps | grep -q "irext-private"; then
    echo -e "${GREEN}  ✅ 8081 云端解码: 运行中${NC}"
    echo -e "${BLUE}     访问: http://$(hostname -I | awk '{print $1}'):8081${NC}"
else
    echo -e "${RED}  ❌ 8081 云端解码: 启动失败${NC}"
    docker logs irext-private 2>/dev/null || true
fi

# 检查 8080（管理端口）
if check_port 8080; then
    echo -e "${GREEN}  ✅ 8080 管理端口: 正常${NC}"
fi

# 检查 8082
if [ "$DEPLOY_LOCAL" = true ]; then
    if docker ps | grep -q "irext-decoder"; then
        echo -e "${GREEN}  ✅ 8082 本地解码: 运行中${NC}"
        echo -e "${BLUE}     访问: http://$(hostname -I | awk '{print $1}'):8082${NC}"
    else
        echo -e "${RED}  ❌ 8082 本地解码: 启动失败${NC}"
        cd "${INSTALL_DIR}/decoder" && docker-compose logs 2>/dev/null || true
    fi
else
    echo -e "${YELLOW}  ⏭️  8082 本地解码: 跳过（仅支持 x86_64）${NC}"
fi

# 获取 IP
IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "======================================================"
echo -e "${YELLOW}📱 Android APP 配置:${NC}"
echo -e "  Docker IP:8081: ${BLUE}http://${IP}:8081${NC}"
if [ "$DEPLOY_LOCAL" = true ]; then
    echo -e "  本地解码器:     ${BLUE}http://${IP}:8082${NC}"
else
    echo -e "  本地解码器:     ${YELLOW}当前架构不支持${NC}"
fi
echo ""
echo -e "${YELLOW}🛠️ 常用命令:${NC}"
echo "  查看 8081 日志: docker logs -f irext-private"
if [ "$DEPLOY_LOCAL" = true ]; then
    echo "  查看 8082 日志: cd ${INSTALL_DIR}/decoder && docker-compose logs -f"
    echo "  重启 8082:      cd ${INSTALL_DIR}/decoder && docker-compose restart"
fi
echo "  停止所有:       docker stop irext-private && docker rm irext-private"
echo ""
echo -e "${YELLOW}📁 安装目录: ${INSTALL_DIR}${NC}"
