# multi/myproject/asgi.py

import os
import sys # 导入 sys 模块，用于路径调试

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

print("\n--- ASGI DEBUG START ---")
print(f"Current working directory: {os.getcwd()}")
print(f"sys.path: {sys.path}")

# 尝试设置 Django settings 模块
settings_module = 'myproject.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
print(f"DJANGO_SETTINGS_MODULE set to: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

# 验证 settings 是否能被找到（可能无法在加载asgi.py时立即完全验证）
try:
    from django.conf import settings
    settings.SECRET_KEY # 尝试访问一个设置，如果能访问到说明 settings 加载成功
    print("Django settings loaded successfully (initial check).")
except Exception as e:
    print(f"Error loading Django settings: {e}")
    # 如果这里报错，说明 settings 路径或文件本身有问题

# 导入 polls.routing
try:
    import polls.routing as polls_routing
    print("Successfully imported polls.routing.")
except ImportError as e:
    print(f"Failed to import polls.routing: {e}")
    # 如果这里报错，说明 Python 找不到 polls 模块，即使 manage.py 运行正常
    # 这可能意味着 Daphne 运行时的 Python 路径与 manage.py 不同
    sys.exit(1) # 如果无法导入，直接退出，因为 WebSocket 也无法工作

# 获取 Django 的 ASGI 应用程序实例
# 注意：get_asgi_application() 内部会初始化 Django 应用
django_asgi_app = get_asgi_application()
print("Django ASGI application instance created.")


class CustomProtocolTypeRouter(ProtocolTypeRouter):
    async def __call__(self, scope, receive, send):
        # 记录请求类型
        print(f"Incoming scope type: {scope['type']}")
        if scope['type'] == 'http':
            print(f"Handling HTTP request. Path: {scope.get('path')}")
            # 调用原始的 http 处理程序
            await super().__call__(scope, receive, send)
        elif scope['type'] == 'websocket':
            print(f"Handling WebSocket request. Path: {scope.get('path')}")
            # 调用原始的 websocket 处理程序
            await super().__call__(scope, receive, send)
        else:
            print(f"Handling unknown protocol type: {scope['type']}")
            await super().__call__(scope, receive, send)

application = CustomProtocolTypeRouter({
    "http": django_asgi_app, # 使用上面创建的实例
    "websocket": AuthMiddlewareStack(
        URLRouter(
            polls_routing.websocket_urlpatterns
        )
    ),
})

print("--- ASGI DEBUG END ---")