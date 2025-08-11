"""
WebSocket路由配置
"""
from django.urls import re_path
from . import consumers, consumers_monitor

websocket_urlpatterns = [
    re_path(r'ws/signal-acquisition/$', consumers.SignalAcquisitionConsumer.as_asgi()),
    re_path(r'ws/signal-monitor/$', consumers_monitor.SignalMonitorConsumer.as_asgi()),
]
