"""
信号监控WebSocket消费者 - 支持定时采集功能
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
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SignalMonitorConsumer(AsyncWebsocketConsumer):
    """信号监控WebSocket消费者"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = None
        self.group_name = "signal_monitor"
        self.data_packet_count = 0
        self.data_queue = deque(maxlen=100)
        self.processing_task = None
        self.monitoring_task = None
        self.enabled_channels = []
        self.channel_configs = {}
        self.global_point_index = 0  # 全局采集点计数器
        
        # 监控配置
        self.monitor_config = {
            'interval_seconds': 5,  # 采集间隔（秒）
            'points_per_acquisition': 1000,  # 每次采集点数
            'total_duration_minutes': 60,  # 总监控时长（分钟）
            'sample_rate': 10000  # 采样率
        }
        
        # 监控状态
        self.is_monitoring = False
        self.is_paused = False  # 新增：暂停状态
        self.monitor_start_time = None
        self.monitor_end_time = None
        self.next_acquisition_time = None
        self.acquisition_count = 0
        self.total_acquisitions = 0
        self.paused_time_total = 0  # 新增：累计暂停时长（秒）
        self.paused_time_start = None  # 新增：本次暂停开始时间
        
        # 数据存储
        self.all_time_axis = []
        self.all_channel_data = {}
        self.monitor_data_ready = False

    async def connect(self):
        """WebSocket连接"""
        try:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.initialize_driver()
            # 启动数据处理任务
            self.processing_task = asyncio.create_task(self.process_data_queue())
            logger.info(f"信号监控WebSocket连接已建立: {self.channel_name}")
        except Exception as e:
            logger.error(f"信号监控WebSocket连接失败: {e}")
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
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
                
            if self.driver:
                await asyncio.get_event_loop().run_in_executor(None, self.driver.close_device)
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info(f"信号监控WebSocket连接已断开: {self.channel_name}")
        except Exception as e:
            logger.error(f"信号监控WebSocket断开异常: {e}")

    async def process_data_queue(self):
        """处理数据队列的任务"""
        try:
            while True:
                if self.data_queue:
                    data_packet = self.data_queue.popleft()
                    try:
                        await self.send_monitor_data(data_packet)
                        logger.info(f"发送监控数据包 #{data_packet.get('packet_id', 0)}")
                    except Exception as e:
                        logger.error(f"发送监控数据包异常: {e}")
                else:
                    await asyncio.sleep(0.001)
        except asyncio.CancelledError:
            logger.info("监控数据处理任务已取消")
        except Exception as e:
            logger.error(f"监控数据处理任务异常: {e}")

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
                'configure_monitor': self.handle_configure_monitor,
                'start_monitoring': self.handle_start_monitoring,
                'stop_monitoring': self.handle_stop_monitoring,
                'pause_monitoring': self.handle_pause_monitoring,
                'get_monitor_status': self.handle_get_monitor_status,
                'acquire_data': self.handle_acquire_data,
                'reset_monitor': self.handle_reset_monitor,
                'stop_monitoring_and_reset': self.handle_stop_monitoring_and_reset,
                'save_monitor_data': self.handle_save_monitor_data,
            }

            handler = handlers.get(message_type)
            if handler:
                await handler(data)
            else:
                await self.send_error(f"未知消息类型: {message_type}")

        except json.JSONDecodeError:
            await self.send_error("JSON解析错误")
        except Exception as e:
            logger.error(f"处理监控消息异常: {e}")
            await self.send_error(f"处理监控消息异常: {str(e)}")

    async def initialize_driver(self):
        """初始化驱动"""
        try:
            self.driver = await asyncio.get_event_loop().run_in_executor(None, USB5121Driver)
            logger.info("监控驱动初始化成功")
        except Exception as e:
            logger.error(f"监控驱动初始化失败: {str(e)}")

    async def handle_open_device(self, data: Dict[str, Any]):
        """处理打开设备请求"""
        try:
            if not self.driver:
                logger.error("驱动未初始化")
                return

            logger.info("正在打开监控设备...")
            success = await asyncio.get_event_loop().run_in_executor(None, self.driver.open_device)

            if success:
                logger.info("监控设备打开成功")
                await self.send_success("监控设备打开成功")
            else:
                logger.error("监控设备打开失败")
                await self.send_error("监控设备打开失败")
        except Exception as e:
            logger.error(f"打开监控设备异常: {str(e)}")
            await self.send_error(f"打开监控设备异常: {str(e)}")

    async def handle_close_device(self, data: Dict[str, Any]):
        """处理关闭设备请求"""
        try:
            if not self.driver:
                logger.error("驱动未初始化")
                return

            # 停止监控
            if self.is_monitoring:
                await self.stop_monitoring()

            logger.info("正在关闭监控设备...")
            success = await asyncio.get_event_loop().run_in_executor(None, self.driver.close_device)

            if success:
                logger.info("监控设备关闭成功")
                await self.send_success("监控设备关闭成功")
            else:
                logger.error("监控设备关闭失败")
                await self.send_error("监控设备关闭失败")
        except Exception as e:
            logger.error(f"关闭监控设备异常: {str(e)}")
            await self.send_error(f"关闭监控设备异常: {str(e)}")

    async def handle_configure_channels(self, data: Dict[str, Any]):
        """处理通道配置请求"""
        try:
            if not self.driver:
                logger.error("驱动未初始化")
                return

            channels_config = data.get('channels', [])
            results = []
            self.enabled_channels = []
            self.channel_configs = {}

            logger.info("开始配置监控AI通道...")

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
                sensitivity = config.get('sensitivity', 1.0)

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
                        self.enabled_channels.append(channel)
                        self.channel_configs[channel] = {
                            'range': voltage_range,
                            'sensitivity': sensitivity
                        }
                        logger.info(f"监控AI通道{channel}配置成功 (±{voltage_range}V, 灵敏度:{sensitivity})")
                    else:
                        logger.error(f"监控AI通道{channel}配置失败")
                    results.append({
                        'channel': channel,
                        'success': success
                    })

            logger.info(f"监控通道配置完成: 启用{len(self.enabled_channels)}个通道")
            await self.send_response('configure_channels_result', {
                'results': results,
                'enabled_channels': self.enabled_channels
            })

        except Exception as e:
            logger.error(f"配置监控通道异常: {str(e)}")
            await self.send_error(f"配置监控通道异常: {str(e)}")

    async def handle_configure_monitor(self, data: Dict[str, Any]):
        """处理监控配置请求"""
        try:
            config = data.get('config', {})
            
            # 更新监控配置
            self.monitor_config.update({
                'interval_seconds': config.get('interval_seconds', 5),
                'points_per_acquisition': config.get('points_per_acquisition', 1000),
                'total_duration_minutes': config.get('total_duration_minutes', 60),
                'sample_rate': config.get('sample_rate', 10000)
            })

            # 计算总采集次数（考虑采集时间）
            # 每次采集的总时间 = 采集时间 + 间隔时间
            acquisition_time = self.monitor_config['points_per_acquisition'] / self.monitor_config['sample_rate']
            total_time_per_acquisition = acquisition_time + self.monitor_config['interval_seconds']
            total_duration_seconds = self.monitor_config['total_duration_minutes'] * 60
            
            # 总采集次数 = 总时长 / 每次采集的总时间
            self.total_acquisitions = int(total_duration_seconds / total_time_per_acquisition)

            logger.info(f"监控配置更新: 间隔{self.monitor_config['interval_seconds']}秒, "
                       f"每次{self.monitor_config['points_per_acquisition']}点, "
                       f"采集时间{acquisition_time:.3f}秒, "
                       f"每次总时间{total_time_per_acquisition:.3f}秒, "
                       f"总时长{self.monitor_config['total_duration_minutes']}分钟, "
                       f"总采集次数{self.total_acquisitions}")

            await self.send_success("监控配置已更新")

        except Exception as e:
            logger.error(f"配置监控参数异常: {str(e)}")
            await self.send_error(f"配置监控参数异常: {str(e)}")

    async def handle_start_monitoring(self, data: Dict[str, Any]):
        """处理开始监控请求"""
        try:
            if not self.driver:
                await self.send_error("设备未连接")
                return

            if not self.enabled_channels:
                await self.send_error("请先配置通道")
                return

            if self.is_monitoring:
                await self.send_error("监控已在进行中")
                return

            # 启动监控任务
            self.monitoring_task = asyncio.create_task(self.monitoring_loop())
            await self.send_success("监控已开始")

        except Exception as e:
            logger.error(f"开始监控异常: {str(e)}")
            await self.send_error(f"开始监控异常: {str(e)}")

    async def handle_stop_monitoring(self, data: Dict[str, Any]):
        """处理停止监控请求"""
        try:
            await self.stop_monitoring()
            await self.send_success("监控已停止")
        except Exception as e:
            logger.error(f"停止监控异常: {str(e)}")
            await self.send_error(f"停止监控异常: {str(e)}")

    async def handle_pause_monitoring(self, data: Dict[str, Any]):
        """处理暂停/继续监控请求"""
        try:
            if not self.is_monitoring:
                await self.send_error("监控未在进行中")
                return
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.paused_time_start = datetime.now()
                await self.send_success("监控已暂停")
            else:
                if self.paused_time_start:
                    self.paused_time_total += (datetime.now() - self.paused_time_start).total_seconds()
                self.paused_time_start = None
                await self.send_success("监控已继续")
        except Exception as e:
            logger.error(f"暂停监控异常: {str(e)}")
            await self.send_error(f"暂停监控异常: {str(e)}")

    async def handle_acquire_data(self, data: Dict[str, Any]):
        """处理单次数据采集请求"""
        try:
            if not self.driver:
                await self.send_error("设备未连接")
                return

            if not self.enabled_channels:
                await self.send_error("请先配置通道")
                return

            # 执行单次采集
            await self.perform_single_acquisition()

        except Exception as e:
            logger.error(f"单次采集异常: {str(e)}")
            await self.send_error(f"单次采集异常: {str(e)}")

    async def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("监控已停止")

    async def monitoring_loop(self):
        """监控循环"""
        try:
            self.is_monitoring = True
            self.is_paused = False
            self.monitor_start_time = datetime.now()
            self.monitor_end_time = self.monitor_start_time + timedelta(minutes=self.monitor_config['total_duration_minutes'])
            self.acquisition_count = 0
            self.global_point_index = 0
            self.paused_time_total = 0
            self.paused_time_start = None
            logger.info(f"开始监控循环: 预计结束时间 {self.monitor_end_time}")
            
            while self.is_monitoring:
                current_time = datetime.now()
                # 检查是否超时
                if current_time >= self.monitor_end_time:
                    logger.info("监控时间已到，自动停止")
                    break
                
                # 暂停时不采集，只发状态
                if self.is_paused:
                    await self.send_monitor_status()
                    await asyncio.sleep(0.2)
                    continue
                
                # 执行单次采集
                logger.info(f"开始第{self.acquisition_count + 1}次采集")
                await self.perform_single_acquisition()
                self.acquisition_count += 1
                
                # 发送监控状态
                await self.send_monitor_status()
                
                # 等待间隔时间（采集完成后）
                if self.is_monitoring:  # 再次检查，避免在间隔期间被停止
                    logger.info(f"第{self.acquisition_count}次采集完成，等待{self.monitor_config['interval_seconds']}秒间隔...")
                    await asyncio.sleep(self.monitor_config['interval_seconds'])
            
            logger.info(f"监控循环结束: 共完成{self.acquisition_count}次采集")
            self.is_monitoring = False
            self.paused_time_total = 0
            self.paused_time_start = None
            
            # 发送采集完成消息
            await self.send_acquisition_complete()
            
        except asyncio.CancelledError:
            logger.info("监控循环被取消")
            self.paused_time_total = 0
            self.paused_time_start = None
        except Exception as e:
            logger.error(f"监控循环异常: {e}")
            self.is_monitoring = False
            self.paused_time_total = 0
            self.paused_time_start = None

    async def perform_single_acquisition(self):
        """执行单次采集"""
        try:
            logger.info(f"执行第{self.acquisition_count + 1}次采集...")

            # 配置采集参数
            success = await asyncio.get_event_loop().run_in_executor(
                None,
                self.driver.configure_ai_acquisition,
                1,  # 单次采集模式
                self.monitor_config['sample_rate'],
                self.monitor_config['points_per_acquisition']
            )

            if not success:
                logger.error("配置采集参数失败")
                return

            # 开始采集
            success = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.driver.start_ai_acquisition(self.data_callback)
            )

            if not success:
                logger.error("开始采集失败")
                return

            # 触发单次采集
            success = await asyncio.get_event_loop().run_in_executor(
                None,
                self.driver.trigger_ai_acquisition
            )

            if not success:
                logger.error("触发采集失败")
                return

            # 等待采集完成
            # 计算理论采集时间：点数/采样率，再加上一些缓冲时间
            theoretical_time = self.monitor_config['points_per_acquisition'] / self.monitor_config['sample_rate']
            wait_time = max(theoretical_time + 0.5, 1.0)  # 至少等待1秒，确保采集完成
            logger.info(f"等待采集完成，理论时间: {theoretical_time:.3f}秒，实际等待: {wait_time:.3f}秒")
            await asyncio.sleep(wait_time)

            # 停止采集
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.driver.stop_ai_acquisition
            )

            logger.info(f"第{self.acquisition_count + 1}次采集完成")

        except Exception as e:
            logger.error(f"执行采集异常: {e}")

    def data_callback(self, data_packet: Dict[str, Any]):
        """数据回调函数"""
        try:
            self.data_packet_count += 1

            # 从 data_packet 读取必要信息
            channel_data = data_packet.get('channel_data', {})
            points_per_channel = data_packet.get('points_per_channel', 0)
            sample_rate = data_packet.get('sample_rate', 0)
            remaining_points = data_packet.get('remaining_points', 0)
            enabled_channels = data_packet.get('enabled_channels', [])
            timestamp = data_packet.get('timestamp', time.time())

            # 本地详细打印数据内容，便于调试
            logger.info(f"[DEBUG] 数据包时间戳: {timestamp}")
            logger.info(f"[DEBUG] 启用通道: {enabled_channels}")
            logger.info(f"[DEBUG] 通道数据键: {list(channel_data.keys())}")
            
            for ch_str, ch_data in channel_data.items():
                if ch_data and len(ch_data) > 0:
                    logger.info(f"[DEBUG] CH{ch_str} 前5个点: {ch_data[:5]}")
                    logger.info(f"[DEBUG] CH{ch_str} 数据长度: {len(ch_data)}")
                    logger.info(f"[DEBUG] CH{ch_str} 数据范围: {min(ch_data):.4f} ~ {max(ch_data):.4f}")
                else:
                    logger.info(f"[DEBUG] CH{ch_str} 数据为空或None")

            # 全局时间轴递增
            time_step = 1.0 / sample_rate if sample_rate else 0
            start_idx = self.global_point_index
            end_idx = self.global_point_index + points_per_channel
            time_axis = [i * time_step for i in range(start_idx, end_idx)]
            self.global_point_index += points_per_channel

            # 累积数据用于保存
            self.all_time_axis.extend(time_axis)
            
            # 确保所有启用的通道都有数据存储
            # 使用传入的enabled_channels参数，而不是self.enabled_channels
            for ch in enabled_channels:
                if ch not in self.all_channel_data:
                    self.all_channel_data[ch] = []
                
                # 如果当前数据包中有这个通道的数据，则添加
                ch_str = str(ch)
                if ch_str in channel_data and channel_data[ch_str]:
                    self.all_channel_data[ch].extend(channel_data[ch_str])
                    logger.info(f"累积CH{ch}数据: {len(channel_data[ch_str])}个点, 值范围: {min(channel_data[ch_str]):.4f}~{max(channel_data[ch_str]):.4f}")
                else:
                    # 如果没有数据，用NaN填充
                    self.all_channel_data[ch].extend([float('nan')] * len(time_axis))
                    logger.info(f"CH{ch}无数据，用NaN填充: {len(time_axis)}个点")
            
            # 标记数据已准备好
            if len(self.all_time_axis) > 0:
                self.monitor_data_ready = True
                logger.info(f"数据累积状态: 时间轴{len(self.all_time_axis)}点, 通道数据{list(self.all_channel_data.keys())}")
                # 打印每个通道的累积数据统计
                for ch in self.all_channel_data:
                    if self.all_channel_data[ch]:
                        valid_data = [x for x in self.all_channel_data[ch] if not np.isnan(x)]
                        if valid_data:
                            logger.info(f"  累积CH{ch}: {len(valid_data)}个有效数据点, 范围: {min(valid_data):.4f}~{max(valid_data):.4f}")
                        else:
                            logger.info(f"  累积CH{ch}: 只有NaN数据")
                    else:
                        logger.info(f"  累积CH{ch}: 无数据")

            # 构建新的数据包，加入时间轴和 packet_id
            data_packet_out = dict(data_packet)
            data_packet_out.update({
                'packet_id': self.data_packet_count,
                'time_axis': time_axis,
                'enabled_channels': enabled_channels,
                'acquisition_id': self.acquisition_count + 1,
                'channel_configs': self.channel_configs
            })

            # 将数据包加入队列
            self.data_queue.append(data_packet_out)

            # 详细的本地日志
            logger.info(f"监控数据包 #{self.data_packet_count}: 通道数={len(channel_data)}, 剩余点数={remaining_points}")

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
            logger.error(f"监控数据回调函数异常: {e}")

    async def handle_get_monitor_status(self, data: Dict[str, Any]):
        """处理获取监控状态请求"""
        try:
            await self.send_monitor_status()
        except Exception as e:
            logger.error(f"获取监控状态异常: {str(e)}")
            await self.send_error(f"获取监控状态异常: {str(e)}")

    async def send_monitor_status(self):
        """发送监控状态"""
        try:
            current_time = datetime.now()
            remaining_time = 0
            progress = 0
            if self.monitor_start_time and self.monitor_end_time:
                # 计算实际已用时（减去累计暂停时长）
                paused_seconds = self.paused_time_total
                if self.is_paused and self.paused_time_start:
                    paused_seconds += (current_time - self.paused_time_start).total_seconds()
                elapsed_time = (current_time - self.monitor_start_time).total_seconds() - paused_seconds
                total_time = self.monitor_config['total_duration_minutes'] * 60
                if elapsed_time < 0:
                    elapsed_time = 0
                if elapsed_time < total_time:
                    remaining_time = total_time - elapsed_time
                    progress = min(100, (elapsed_time / total_time) * 100)
                else:
                    remaining_time = 0
                    progress = 100
            status_data = {
                'is_monitoring': self.is_monitoring,
                'is_paused': self.is_paused,  # 新增
                'acquisition_count': self.acquisition_count,
                'total_acquisitions': self.total_acquisitions,
                'remaining_time_seconds': int(remaining_time),
                'progress_percent': round(progress, 1),
                'next_acquisition_time': None,  # 不再使用固定时间，改为采集完成后等待间隔
                'enabled_channels': self.enabled_channels,
                'monitor_config': self.monitor_config
            }
            await self.send_response('monitor_status', status_data)
        except Exception as e:
            logger.error(f"发送监控状态异常: {e}")

    async def send_monitor_data(self, data_packet: Dict[str, Any]):
        """发送监控数据"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'monitor_data',
                'data': data_packet
            }))
        except Exception as e:
            logger.error(f"发送监控数据异常: {e}")

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

    async def handle_reset_monitor(self, data):
        """处理清空/重置监控请求"""
        try:
            # 停止监控任务
            self.is_monitoring = False
            self.is_paused = False
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except Exception:
                    pass
                self.monitoring_task = None
            # 重置所有状态
            self.acquisition_count = 0
            self.total_acquisitions = 0
            self.paused_time_total = 0
            self.paused_time_start = None
            self.monitor_start_time = None
            self.monitor_end_time = None
            self.next_acquisition_time = None
            self.global_point_index = 0
            self.data_queue.clear()
            
            # 清空数据存储
            self.all_time_axis = []
            self.all_channel_data = {}
            self.monitor_data_ready = False
            
            await self.send_success("监控已重置")
            await self.send_monitor_status()
        except Exception as e:
            logger.error(f"重置监控异常: {str(e)}")
            await self.send_error(f"重置监控异常: {str(e)}")

    async def handle_stop_monitoring_and_reset(self, data):
        """处理停止监控并重置请求"""
        try:
            # 停止监控任务
            self.is_monitoring = False
            self.is_paused = False
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except Exception:
                    pass
                self.monitoring_task = None
            # 重置采集次数、时间、进度等（不清空通道配置）
            self.acquisition_count = 0
            self.total_acquisitions = 0
            self.paused_time_total = 0
            self.paused_time_start = None
            self.monitor_start_time = None
            self.monitor_end_time = None
            self.next_acquisition_time = None
            self.global_point_index = 0
            
            # 清空数据存储
            self.all_time_axis = []
            self.all_channel_data = {}
            self.monitor_data_ready = False
            
            await self.send_success("监控已停止并重置")
            await self.send_monitor_status()
        except Exception as e:
            logger.error(f"停止监控并重置异常: {str(e)}")
            await self.send_error(f"停止监控并重置异常: {str(e)}")

    async def handle_save_monitor_data(self, data):
        """处理保存监控数据请求"""
        try:
            if not self.monitor_data_ready:
                await self.send_error("没有可保存的监控数据")
                return
            
            # 添加调试信息
            logger.info(f"准备保存监控数据:")
            logger.info(f"  时间轴长度: {len(self.all_time_axis)}")
            logger.info(f"  启用的通道: {self.enabled_channels}")
            logger.info(f"  累积的通道数据: {list(self.all_channel_data.keys())}")
            
            for ch in self.enabled_channels:
                if ch in self.all_channel_data:
                    data_length = len(self.all_channel_data[ch])
                    logger.info(f"  CH{ch} 数据长度: {data_length}")
                    if data_length > 0:
                        # 检查有效数据（非NaN）
                        valid_data = [x for x in self.all_channel_data[ch] if not np.isnan(x)]
                        logger.info(f"  CH{ch} 有效数据点: {len(valid_data)}")
                        if valid_data:
                            logger.info(f"  CH{ch} 前5个有效值: {valid_data[:5]}")
                            logger.info(f"  CH{ch} 数据范围: {min(valid_data):.4f}~{max(valid_data):.4f}")
                        else:
                            logger.info(f"  CH{ch} 只有NaN数据")
                    else:
                        logger.info(f"  CH{ch} 数据为空")
                else:
                    logger.info(f"  CH{ch} 没有数据")
            
            # 准备保存的数据
            save_data = {
                'task_name': data.get('task_name', '未命名任务'),
                'task_description': data.get('task_description', ''),
                'start_time': self.monitor_start_time.isoformat() if self.monitor_start_time else None,
                'end_time': self.monitor_end_time.isoformat() if self.monitor_end_time else None,
                'monitor_config': self.monitor_config,
                'channel_configs': self.channel_configs,
                'enabled_channels': self.enabled_channels,
                'monitor_data': {
                    'time_axis': self.all_time_axis,
                    'channel_data': self.all_channel_data
                },
                'total_acquisitions': self.total_acquisitions
            }
            
            # 发送保存成功消息
            await self.send_success(f"监控数据已准备保存，任务名称: {save_data['task_name']}")
            
            # 返回数据供前端调用API保存
            await self.send_response('monitor_data_ready', save_data)
            
        except Exception as e:
            logger.error(f"准备保存监控数据异常: {str(e)}")
            await self.send_error(f"准备保存监控数据异常: {str(e)}") 

    async def send_acquisition_complete(self):
        """发送采集完成消息"""
        try:
            # 计算采集统计信息
            duration_minutes = 0
            if self.monitor_start_time and self.monitor_end_time:
                duration_seconds = (self.monitor_end_time - self.monitor_start_time).total_seconds() - self.paused_time_total
                duration_minutes = int(duration_seconds / 60)
            
            complete_data = {
                'acquisition_count': self.acquisition_count,
                'total_acquisitions': self.total_acquisitions,
                'data_points': len(self.all_time_axis),
                'enabled_channels': len(self.enabled_channels),
                'duration_minutes': duration_minutes,
                'sample_rate': self.monitor_config.get('sample_rate', 0)
            }
            
            await self.send_response('acquisition_complete', complete_data)
            logger.info("发送采集完成消息")
            
        except Exception as e:
            logger.error(f"发送采集完成消息异常: {e}") 