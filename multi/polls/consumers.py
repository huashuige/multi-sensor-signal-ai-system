"""
WebSocket消费者 - 添加详细数据日志
"""
import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from .dap_driver import USB5121Driver
import threading
from typing import Dict, Any, List
import numpy as np
from collections import deque
import time

logger = logging.getLogger(__name__)


class SignalAcquisitionConsumer(AsyncWebsocketConsumer):
    """信号采集WebSocket消费者"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = None
        self.group_name = "signal_acquisition"
        self.data_packet_count = 0
        self.data_queue = deque(maxlen=100)  # 限制队列大小，避免内存溢出
        self.processing_task = None
        self.global_time_offset = 0  # 全局时间偏移量
        self.last_data_packet = None  # 用于存储最后一个有效数据包
        self.enabled_channels = []  # 存储启用的通道列表
        self.global_point_index = 0  # 新增：全局采集点计数器

    async def connect(self):
        """WebSocket连接"""
        try:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.initialize_driver()
            # 启动数据处理任务
            self.processing_task = asyncio.create_task(self.process_data_queue())
            logger.info(f"WebSocket连接已建立: {self.channel_name}")
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            await self.close()

    async def disconnect(self, close_code):
        """WebSocket断开连接"""
        try:
            if self.processing_task:
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            if self.driver:
                await asyncio.get_event_loop().run_in_executor(None, self.driver.close_device)
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info(f"WebSocket连接已断开: {self.channel_name}")
        except Exception as e:
            logger.error(f"WebSocket断开异常: {e}")

    async def process_data_queue(self):
        """处理数据队列的任务"""
        try:
            while True:
                if self.data_queue:
                    data_packet = self.data_queue.popleft()
                    try:
                        await self.send_acquisition_data(data_packet)
                        logger.info(f"发送数据包 #{data_packet.get('packet_id', 0)}")
                    except Exception as e:
                        logger.error(f"发送数据包异常: {e}")
                else:
                    await asyncio.sleep(0.001)  # 避免CPU空转
        except asyncio.CancelledError:
            logger.info("数据处理任务已取消")
        except Exception as e:
            logger.error(f"数据处理任务异常: {e}")

    async def receive(self, text_data):
        """接收WebSocket消息"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            # 消息路由
            handlers = {
                'open_device': self.handle_open_device,
                'close_device': self.handle_close_device,
                'configure_channels': self.handle_configure_channels,
                'configure_acquisition': self.handle_configure_acquisition,
                'start_acquisition': self.handle_start_acquisition,
                'stop_acquisition': self.handle_stop_acquisition,
                'get_status': self.handle_get_status
            }

            handler = handlers.get(message_type)
            if handler:
                await handler(data)
            else:
                await self.send_error(f"未知消息类型: {message_type}")

        except json.JSONDecodeError:
            await self.send_error("JSON解析错误")
        except Exception as e:
            logger.error(f"处理消息异常: {e}")
            await self.send_error(f"处理消息异常: {str(e)}")

    async def initialize_driver(self):
        """初始化驱动"""
        try:
            self.driver = await asyncio.get_event_loop().run_in_executor(None, USB5121Driver)
            logger.info("驱动初始化成功")
        except Exception as e:
            logger.error(f"驱动初始化失败: {str(e)}")

    async def handle_open_device(self, data: Dict[str, Any]):
        """处理打开设备请求"""
        try:
            if not self.driver:
                logger.error("驱动未初始化")
                return

            logger.info("正在打开设备...")
            success = await asyncio.get_event_loop().run_in_executor(None, self.driver.open_device)

            if success:
                logger.info("设备打开成功")
                await self.send_success("设备打开成功")
            else:
                logger.error("设备打开失败")
                await self.send_error("设备打开失败")
        except Exception as e:
            logger.error(f"打开设备异常: {str(e)}")
            await self.send_error(f"打开设备异常: {str(e)}")

    async def handle_close_device(self, data: Dict[str, Any]):
        """处理关闭设备请求"""
        try:
            if not self.driver:
                logger.error("驱动未初始化")
                return

            logger.info("正在关闭设备...")
            success = await asyncio.get_event_loop().run_in_executor(None, self.driver.close_device)

            if success:
                logger.info("设备关闭成功")
                await self.send_success("设备关闭成功")
            else:
                logger.error("设备关闭失败")
                await self.send_error("设备关闭失败")
        except Exception as e:
            logger.error(f"关闭设备异常: {str(e)}")
            await self.send_error(f"关闭设备异常: {str(e)}")

    async def handle_configure_channels(self, data: Dict[str, Any]):
        """处理通道配置请求"""
        try:
            if not self.driver:
                logger.error("驱动未初始化")
                return

            channels_config = data.get('channels', [])
            results = []

            logger.info("开始配置AI通道...")

            # 先关闭所有通道
            for i in range(16):
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.driver.configure_ai_channel,
                    i, False, 10.0
                )

            # 配置启用的通道
            for config in channels_config:
                channel = config.get('channel')
                enabled = config.get('enabled', False)
                voltage_range = config.get('range', 10.0)

                if not (0 <= channel <= 15):
                    logger.error(f"无效的通道号: {channel}")
                    results.append({
                        'channel': channel,
                        'success': False
                    })
                    continue

                success = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.driver.configure_ai_channel,
                    channel, enabled, voltage_range
                )

                if enabled:
                    if success:
                        logger.info(f"AI通道{channel}配置成功 (±{voltage_range}V)")
                    else:
                        logger.error(f"AI通道{channel}配置失败")

                results.append({
                    'channel': channel,
                    'success': success
                })

            enabled_count = sum(1 for config in channels_config if config.get('enabled', False))
            logger.info(f"通道配置完成，已启用{enabled_count}个通道")

            await self.send_response('configure_channels_result', {'results': results})

        except Exception as e:
            logger.error(f"配置通道异常: {str(e)}")
            await self.send_error(f"配置通道异常: {str(e)}")

    async def handle_configure_acquisition(self, data: Dict[str, Any]):
        """处理采集配置请求"""
        try:
            if not self.driver:
                logger.error("驱动未初始化")
                return

            config = data.get('config', {})
            mode = config.get('mode', 0)
            sample_rate = config.get('sample_rate', 10000)
            oneshot_points = config.get('oneshot_points', 1000)

            logger.info(f"配置采集参数: 模式={mode}, 采样率={sample_rate}Hz, 单次点数={oneshot_points}")

            # 设置采集模式
            success = await asyncio.get_event_loop().run_in_executor(
                None,
                self.driver.set_ai_sample_mode,
                mode
            )

            if not success:
                logger.error("设置采集模式失败")
                await self.send_error("设置采集模式失败")
                return

            # 设置采样率
            success = await asyncio.get_event_loop().run_in_executor(
                None,
                self.driver.set_ai_sample_rate,
                sample_rate
            )

            if not success:
                logger.error("设置采样率失败")
                await self.send_error("设置采样率失败")
                return

            # 如果是单次采集模式，设置点数
            if mode == 1:
                success = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.driver.set_ai_oneshot_points,
                    oneshot_points
                )

                if not success:
                    logger.error("设置单次采集点数失败")
                    await self.send_error("设置单次采集点数失败")
                    return

            logger.info("采集参数配置成功")
            await self.send_success("采集参数配置成功")

        except Exception as e:
            logger.error(f"配置采集参数异常: {str(e)}")
            await self.send_error(f"配置采集参数异常: {str(e)}")

    def data_callback(self, data_packet: Dict[str, Any]):
        """数据回调函数 - 只接收 data_packet 字典"""
        try:
            self.data_packet_count += 1

            # 从 data_packet 读取必要信息
            channel_data = data_packet.get('channel_data', {})
            points_per_channel = data_packet.get('points_per_channel', 0)
            sample_rate = data_packet.get('sample_rate', 0)
            remaining_points = data_packet.get('remaining_points', 0)
            enabled_channels = data_packet.get('enabled_channels', [])
            timestamp = data_packet.get('timestamp', time.time())

            # 全局时间轴递增
            time_step = 1.0 / sample_rate if sample_rate else 0
            start_idx = self.global_point_index
            end_idx = self.global_point_index + points_per_channel
            time_axis = [i * time_step for i in range(start_idx, end_idx)]
            self.global_point_index += points_per_channel

            # 调试日志：检查时间轴是否正常
            logger.info(f"时间轴生成: sample_rate={sample_rate}Hz, time_step={time_step}s, 前5个值={time_axis[:5]}")

            # 构建新的数据包，加入时间轴和 packet_id
            data_packet_out = dict(data_packet)
            data_packet_out.update({
                'packet_id': self.data_packet_count,
                'time_axis': time_axis,
                'enabled_channels': enabled_channels,
            })

            # 将数据包加入队列
            self.data_queue.append(data_packet_out)

            # 详细的本地日志
            logger.info(f"数据包 #{self.data_packet_count}: 通道数={len(channel_data)}, 剩余点数={remaining_points}")

            # 记录每个通道的数据统计
            for ch_str, ch_data in channel_data.items():
                if ch_data:
                    ch = int(ch_str)
                    v_min = min(ch_data)
                    v_max = max(ch_data)
                    v_avg = sum(ch_data) / len(ch_data)
                    v_rms = (sum(v*v for v in ch_data) / len(ch_data)) ** 0.5
                    logger.info(f"  CH{ch}: 最小={v_min:.4f}V, 最大={v_max:.4f}V, 平均={v_avg:.4f}V, RMS={v_rms:.4f}V")

        except Exception as e:
            logger.error(f"数据回调函数异常: {e}")

    async def handle_start_acquisition(self, data: Dict[str, Any]):
        """处理开始采集请求"""
        try:
            if not self.driver:
                logger.error("驱动未初始化")
                return

            # 检查是否有启用的通道
            self.enabled_channels = [i for i, enabled in enumerate(self.driver.ai_channels) if enabled]
            if not self.enabled_channels:
                logger.error("没有启用的AI通道")
                await self.send_error("没有启用的AI通道")
                return

            logger.info(f"开始采集，启用通道: {self.enabled_channels}")

            # 重置数据包计数和全局点数
            self.data_packet_count = 0
            self.global_point_index = 0

            # 启动连续采集
            success = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.driver.start_continuous_acquisition(self.data_callback)
            )

            if success:
                logger.info("连续采集启动成功")
                await self.send_success("连续采集启动成功")
            else:
                logger.error("连续采集启动失败")
                await self.send_error("连续采集启动失败")

        except Exception as e:
            logger.error(f"开始采集异常: {str(e)}")
            await self.send_error(f"开始采集异常: {str(e)}")

    async def handle_stop_acquisition(self, data: Dict[str, Any]):
        """处理停止采集请求"""
        try:
            if not self.driver:
                logger.error("驱动未初始化")
                return

            logger.info("停止采集...")

            # 停止连续采集
            success = await asyncio.get_event_loop().run_in_executor(
                None,
                self.driver.stop_continuous_acquisition
            )

            if success:
                logger.info(f"采集已停止，本次共采集 {self.data_packet_count} 个数据包")
                await self.send_success(f"采集已停止，本次共采集 {self.data_packet_count} 个数据包")
            else:
                logger.error("停止采集失败")
                await self.send_error("停止采集失败")

        except Exception as e:
            logger.error(f"停止采集异常: {str(e)}")
            await self.send_error(f"停止采集异常: {str(e)}")

    async def handle_get_status(self, data: Dict[str, Any]):
        """处理获取状态请求"""
        try:
            if not self.driver:
                await self.send_response('device_status', {
                    'opened': False,
                    'acquiring': False,
                    'enabled_channels': [],
                    'sample_rate': 0,
                    'buffer_remaining': 0
                })
                return

            # 获取设备状态
            enabled_channels = [i for i, enabled in enumerate(self.driver.ai_channels) if enabled]
            sample_rate = self.driver.ai_sample_rate_ns / 1e9 if self.driver.ai_sample_rate_ns > 0 else 0
            
            # 获取缓冲区剩余点数
            buffer_remaining = 0
            if self.driver.is_opened:
                buffer_remaining = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.driver._get_buffer_remaining
                )

            status_data = {
                'opened': self.driver.is_opened,
                'acquiring': self.driver.is_acquiring,
                'enabled_channels': enabled_channels,
                'sample_rate': sample_rate,
                'buffer_remaining': buffer_remaining
            }

            await self.send_response('device_status', status_data)

        except Exception as e:
            logger.error(f"获取状态异常: {str(e)}")
            await self.send_error(f"获取状态异常: {str(e)}")

    async def send_acquisition_data(self, data_packet: Dict[str, Any]):
        """发送采集数据"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'acquisition_data',
                'data': data_packet
            }))
        except Exception as e:
            logger.error(f"发送采集数据异常: {e}")

    async def send_success(self, message: str):
        """发送成功消息"""
        await self.send(text_data=json.dumps({
            'type': 'success',
            'message': message
        }))

    async def send_error(self, message: str):
        """发送错误消息"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    async def send_response(self, response_type: str, data: Dict[str, Any]):
        """发送响应消息"""
        await self.send(text_data=json.dumps({
            'type': response_type,
            'data': data
        }))
