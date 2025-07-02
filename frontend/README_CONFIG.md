# 服务器配置说明

## 问题背景

原始的 `login_app.py` 中硬编码了服务器地址 `http://127.0.0.1:5000`，这会导致在不同环境下运行时出现连接问题。

## 解决方案

我们创建了 `config.py` 配置文件来管理服务器连接设置，使应用程序更加灵活和可移植。

## 配置文件说明

### 1. 开发环境配置
```python
DEV_CONFIG = {
    "host": "127.0.0.1",  # 本地开发服务器
    "port": 5000,         # Flask默认端口
    "timeout": 10         # 10秒超时
}
```

### 2. 生产环境配置
```python
PROD_CONFIG = {
    "host": "your-server-ip.com",  # 生产服务器地址
    "port": 5000,                  # 服务器端口
    "timeout": 30                  # 30秒超时
}
```

## 如何修改配置

### 方法1：修改配置文件
1. 打开 `frontend/config.py`
2. 修改 `CURRENT_CONFIG` 的值：
   - 使用 `DEV_CONFIG` 进行本地开发
   - 使用 `PROD_CONFIG` 连接远程服务器
3. 如果使用生产配置，记得修改 `PROD_CONFIG` 中的 `host` 为实际的服务器地址

### 方法2：环境变量配置（推荐）
可以进一步改进，使用环境变量来配置：

```python
import os

# 从环境变量读取配置
SERVER_HOST = os.getenv('SERVER_HOST', '127.0.0.1')
SERVER_PORT = int(os.getenv('SERVER_PORT', '5000'))
```

## 常见部署场景

### 1. 本地开发
- 服务器运行在同一台电脑上
- 使用 `DEV_CONFIG`
- 地址：`http://127.0.0.1:5000`

### 2. 局域网部署
- 服务器运行在局域网内的其他电脑上
- 修改 `host` 为服务器的局域网IP（如：`192.168.1.100`）
- 确保防火墙允许5000端口访问

### 3. 公网部署
- 服务器运行在云服务器上
- 修改 `host` 为公网IP或域名
- 确保服务器防火墙开放相应端口

## 测试连接

在运行客户端之前，可以通过以下方式测试服务器连接：

```bash
# 使用curl测试
curl http://your-server-ip:5000/api/login

# 使用Python测试
python -c "import requests; print(requests.get('http://your-server-ip:5000/api/login').status_code)"
```

## 错误处理

新的代码增加了更详细的错误处理：
- 连接错误：服务器未启动或地址错误
- 超时错误：网络连接超时
- 其他网络错误：详细的错误信息

## 注意事项

1. **安全性**：生产环境中建议使用HTTPS
2. **防火墙**：确保服务器防火墙允许客户端连接
3. **网络**：确保客户端和服务器之间的网络连通性
4. **端口**：避免端口冲突，确保服务器端口未被占用 