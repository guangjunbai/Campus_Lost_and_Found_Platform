# 服务器配置文件
# 可以根据不同的部署环境修改这些配置

# 开发环境配置
DEV_CONFIG = {
    "host": "127.0.0.1",
    "port": 5000,
    "timeout": 10
}

# 生产环境配置
PROD_CONFIG = {
    "host": "your-server-ip.com",  # 替换为实际的服务器IP或域名
    "port": 5000,
    "timeout": 30
}

# 当前使用的配置（可以在这里切换环境）
CURRENT_CONFIG = DEV_CONFIG

# 构建服务器基础URL
SERVER_BASE_URL = f"http://{CURRENT_CONFIG['host']}:{CURRENT_CONFIG['port']}"

# API端点
API_ENDPOINTS = {
    "login": "/api/login",#登录
    "register": "/api/register",#注册
    "logout": "/api/logout",#退出
    "user_info": "/api/user_info",#用户信息
    "post": "/api/post"  # 新增发布接口
}

def get_api_url(endpoint: str) -> str:
    """获取完整的API URL"""
    if endpoint not in API_ENDPOINTS:
        raise ValueError(f"未知的API端点: {endpoint}")#如果API端点不存在，抛出异常
    return f"{SERVER_BASE_URL}{API_ENDPOINTS[endpoint]}"#返回完整的API URL

def get_timeout() -> int:
    """获取请求超时时间"""
    return CURRENT_CONFIG.get("timeout", 10) #返回请求超时时间