"""
USB5121数据采集卡驱动封装 - 修正版
支持AI采集和AO输出功能，仅支持CH0-CH3四个通道
"""
import ctypes
from ctypes import *
import numpy as np
import threading
import time
import json
import logging
from typing import Optional, Dict, List, Callable, Any
from pathlib import Path
import math

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class USB5121Driver:
    """USB5121数据采集卡驱动类"""

    # 错误代码映射
    ERROR_CODES = {
        0: "操作成功",
        -1: "设备未找到",
        -2: "设备已打开",
        -3: "设备未打开",
        -4: "参数错误",
        -5: "内存分配失败",
        -6: "设备忙",
        -7: "超时错误",
        -8: "数据溢出",
        -9: "硬件错误"
    }

    # 采集模式
    MODE_CONTINUOUS = 0  # 连续采集
    MODE_ONESHOT = 1  # 单次采集

    # 触发源
    TRIG_SOFTWARE = 0  # 软件触发
    TRIG_EXTERNAL = 1  # 外部触发

    # 时钟源
    CLOCK_INTERNAL = 0  # 内部时钟
    CLOCK_EXTERNAL = 1  # 外部时钟

    # AO输出模式
    AO_MODE_CONTINUOUS = 0  # 连续不循环输出
    AO_MODE_CYCLE = 1  # 循环输出

    def __init__(self, dll_path: str = r"D:\multi\multi\polls\lib\x64\USB5000.dll"):
        """
        初始化USB5121驱动

        Args:
            dll_path: DLL文件路径
        """
        self.dll_path = dll_path
        self.dll: Optional[Any] = None  # 添加类型注解
        self.device_index = ctypes.c_int(0)
        self.is_opened = False
        self.is_acquiring = False
        self.acquisition_thread = None
        self.data_callback = None
        self.trigger_callback = None  # 新增：触发回调函数

        # AI采集参数 - 支持16个通道
        self.ai_channels = [False] * 16  # CH0-CH15通道状态
        self.ai_channel_ranges = [10.0] * 16  # 各通道量程
        self.ai_sample_mode = self.MODE_CONTINUOUS
        self.ai_sample_rate_ns = 1000000  # 采样周期(ns)
        self.ai_oneshot_points = 1000
        self.ai_buffer_size = 16000  # 增加缓冲区大小以支持16个通道
        self.ai_timeout_ms = 1000

        # 单次采集状态
        self.oneshot_triggered = False
        self.oneshot_completed = False
        self.oneshot_progress = 0

        # AO输出参数
        self.ao_channels = [False] * 4  # AO通道状态
        self.ao_voltages = [0.0] * 4  # 各通道直流电压

        # 数据缓冲区
        self.ai_data_buffer = None

        self._load_dll()

    def _load_dll(self):
        """加载DLL库"""
        try:
            if Path(self.dll_path).exists():
                self.dll = windll.LoadLibrary(self.dll_path)
                logger.info(f"成功加载DLL: {self.dll_path}")
            else:
                logger.error(f"DLL文件不存在: {self.dll_path}")
                self.dll = None
        except Exception as e:
            logger.error(f"加载DLL失败: {e}")
            self.dll = None

    def _check_dll_loaded(self) -> bool:
        """检查DLL是否已加载"""
        if self.dll is None:
            logger.error("DLL未加载，无法执行操作")
            return False
        return True

    def _check_result(self, result: int, operation: str) -> bool:
        """
        检查操作结果

        Args:
            result: 操作返回值
            operation: 操作描述

        Returns:
            bool: 操作是否成功
        """
        if result == 0:
            logger.info(f"{operation} - 成功")
            return True
        else:
            error_msg = self.ERROR_CODES.get(result, f"未知错误({result})")
            logger.error(f"{operation} - 失败: {error_msg}")
            return False

    def open_device(self) -> bool:
        """
        打开设备

        Returns:
            bool: 是否成功打开
        """
        if not self._check_dll_loaded():
            return False

        try:
            result = self.dll.USB5OpenDevice(self.device_index)
            success = self._check_result(result, "打开设备")
            if success:
                self.is_opened = True
                # 初始化AI数据缓冲区
                self.ai_data_buffer = np.zeros(self.ai_buffer_size, dtype='float32')

                # 默认关闭所有AI通道
                for i in range(16):
                    self.dll.SetUSB5AiChanSel(self.device_index, ctypes.c_int(i), ctypes.c_char(0))

            return success
        except Exception as e:
            logger.error(f"打开设备异常: {e}")
            return False

    def close_device(self) -> bool:
        """
        关闭设备

        Returns:
            bool: 是否成功关闭
        """
        if not self._check_dll_loaded():
            return False

        try:
            if self.is_acquiring:
                self.stop_ai_acquisition()

            if self.is_opened:
                # 清除AI触发和FIFO
                self.dll.SetUSB5ClrAiTrigger(self.device_index)
                self.dll.SetUSB5ClrAiFifo(self.device_index)

                # 清除AO触发
                for i in range(4):
                    self.dll.SetUSB5ClrAoTrigger(self.device_index, ctypes.c_char(i))
                    self.dll.SetUSB5ClrAoFifo(self.device_index, ctypes.c_char(i))

                result = self.dll.USB5CloseDevice(self.device_index)
                success = self._check_result(result, "关闭设备")
                if success:
                    self.is_opened = False
                return success
            return True
        except Exception as e:
            logger.error(f"关闭设备异常: {e}")
            return False

    def configure_ai_channel(self, channel: int, enabled: bool, voltage_range: float = 10.0) -> bool:
        """
        配置AI通道

        Args:
            channel: 通道号(0-15)
            enabled: 是否启用
            voltage_range: 电压量程

        Returns:
            bool: 配置是否成功
        """
        if not self.is_opened:
            logger.error("设备未打开")
            return False

        if not (0 <= channel <= 15):
            logger.error(f"AI通道号无效: {channel}")
            return False

        if not self._check_dll_loaded():
            return False

        try:
            # 设置通道开关
            chan_sel = ctypes.c_char(1 if enabled else 0)
            result1 = self.dll.SetUSB5AiChanSel(
                self.device_index,
                ctypes.c_int(channel),
                chan_sel
            )

            success1 = self._check_result(result1, f"设置AI通道{channel}开关")

            if enabled:
                # 设置量程
                range_val = ctypes.c_float(voltage_range)
                result2 = self.dll.SetUSB5AiRange(
                    self.device_index,
                    ctypes.c_int(channel),
                    range_val
                )
                success2 = self._check_result(result2, f"设置AI通道{channel}量程")

                if success1 and success2:
                    self.ai_channels[channel] = enabled
                    self.ai_channel_ranges[channel] = voltage_range
                    return True
            else:
                if success1:
                    self.ai_channels[channel] = enabled
                    return True

            return False

        except Exception as e:
            logger.error(f"配置AI通道{channel}异常: {e}")
            return False

    def configure_ai_acquisition(self,
                                 mode: int = MODE_CONTINUOUS,
                                 sample_rate_hz: int = 1000,
                                 oneshot_points: int = 1000,
                                 trigger_source: int = TRIG_SOFTWARE,
                                 clock_source: int = CLOCK_INTERNAL) -> bool:
        """
        配置AI采集参数

        Args:
            mode: 采集模式
            sample_rate_hz: 采样率(Hz)
            oneshot_points: 单次采集点数
            trigger_source: 触发源
            clock_source: 时钟源

        Returns:
            bool: 配置是否成功
        """
        if not self.is_opened:
            logger.error("设备未打开")
            return False

        if not self._check_dll_loaded():
            return False

        try:
            # 转换采样率为ns
            sample_rate_ns = int(1e9 / sample_rate_hz)

            # 设置采集模式
            result1 = self.dll.SetUSB5AiSampleMode(
                self.device_index,
                ctypes.c_char(mode)
            )
            success1 = self._check_result(result1, "设置AI采集模式")

            # 设置单次采集点数(仅在oneshot模式下)
            success2 = True
            if mode == self.MODE_ONESHOT:
                result2 = self.dll.SetUSB5AiOneShotPoints(
                    self.device_index,
                    ctypes.c_uint(oneshot_points)
                )
                success2 = self._check_result(result2, "设置AI单次采集点数")

            # 设置采样率
            result3 = self.dll.SetUSB5AiSampleRate(
                self.device_index,
                ctypes.c_int(sample_rate_ns)
            )
            success3 = self._check_result(result3, "设置AI采样率")

            # 设置触发源
            result4 = self.dll.SetUSB5AiTrigSource(
                self.device_index,
                ctypes.c_char(trigger_source)
            )
            success4 = self._check_result(result4, "设置AI触发源")

            # 设置时钟源
            result5 = self.dll.SetUSB5AiConvSource(
                self.device_index,
                ctypes.c_char(clock_source)
            )
            success5 = self._check_result(result5, "设置AI时钟源")

            if all([success1, success2, success3, success4, success5]):
                self.ai_sample_mode = mode
                self.ai_sample_rate_ns = sample_rate_ns
                self.ai_oneshot_points = oneshot_points
                return True

            return False

        except Exception as e:
            logger.error(f"配置AI采集参数异常: {e}")
            return False

    def trigger_ai_acquisition(self) -> bool:
        """
        触发AI采集（主要用于单次采集模式）

        Returns:
            bool: 触发是否成功
        """
        if not self.is_opened:
            logger.error("设备未打开")
            return False

        if not self._check_dll_loaded():
            return False

        if not self.is_acquiring:
            logger.error("采集未启动")
            return False

        try:
            # 清除之前的触发
            self.dll.SetUSB5ClrAiTrigger(self.device_index)
            
            # 软件触发
            result = self.dll.SetUSB5AiSoftTrig(self.device_index)
            success = self._check_result(result, "AI软件触发")

            if success:
                self.oneshot_triggered = True
                self.oneshot_completed = False
                self.oneshot_progress = 0
                logger.info("AI采集已触发")
                
                # 调用触发回调
                if self.trigger_callback:
                    self.trigger_callback()
                
            return success

        except Exception as e:
            logger.error(f"触发AI采集异常: {e}")
            return False

    def clear_ai_fifo(self) -> bool:
        """
        清除AI FIFO缓冲区

        Returns:
            bool: 清除是否成功
        """
        if not self.is_opened:
            logger.error("设备未打开")
            return False

        if not self._check_dll_loaded():
            return False

        try:
            result = self.dll.SetUSB5ClrAiFifo(self.device_index)
            return self._check_result(result, "清除AI FIFO缓冲区")
        except Exception as e:
            logger.error(f"清除AI FIFO缓冲区异常: {e}")
            return False

    def start_ai_acquisition(self, data_callback: Optional[Callable] = None, trigger_callback: Optional[Callable] = None) -> bool:
        """
        开始AI采集

        Args:
            data_callback: 数据回调函数
            trigger_callback: 触发回调函数

        Returns:
            bool: 是否成功开始
        """
        if not self.is_opened:
            logger.error("设备未打开")
            return False

        if not self._check_dll_loaded():
            return False

        if self.is_acquiring:
            logger.warning("AI采集已在进行中")
            return True

        try:
            # 重置状态
            self.oneshot_triggered = False
            self.oneshot_completed = False
            self.oneshot_progress = 0

            # 清空FIFO缓冲区
            if not self.clear_ai_fifo():
                return False

            self.is_acquiring = True
            self.data_callback = data_callback
            self.trigger_callback = trigger_callback

            # 启动采集线程
            if self.ai_sample_mode == self.MODE_CONTINUOUS:
                self.acquisition_thread = threading.Thread(
                    target=self._ai_continuous_acquisition_loop,
                    daemon=True
                )
                # 连续模式下自动触发
                if not self.trigger_ai_acquisition():
                    self.is_acquiring = False
                    return False
            else:
                self.acquisition_thread = threading.Thread(
                    target=self._ai_oneshot_acquisition,
                    daemon=True
                )

            self.acquisition_thread.start()
            logger.info("AI采集已启动")
            return True

        except Exception as e:
            logger.error(f"启动AI采集异常: {e}")
            self.is_acquiring = False
            return False

    def stop_ai_acquisition(self) -> bool:
        """
        停止AI采集

        Returns:
            bool: 是否成功停止
        """
        if not self._check_dll_loaded():
            return False

        try:
            if self.is_acquiring:
                self.is_acquiring = False

                # 等待采集线程结束
                if self.acquisition_thread and self.acquisition_thread.is_alive():
                    self.acquisition_thread.join(timeout=2.0)

                # 清除触发
                if self.is_opened:
                    self.dll.SetUSB5ClrAiTrigger(self.device_index)
                    self.dll.SetUSB5ClrAiFifo(self.device_index)

                logger.info("AI采集已停止")

            return True

        except Exception as e:
            logger.error(f"停止AI采集异常: {e}")
            return False

    def _ai_continuous_acquisition_loop1(self):
        """AI连续采集循环"""
        logger.info("开始AI连续采集循环")

        # 计算每次读取的点数
        sample_rate_hz = int(1e9 / self.ai_sample_rate_ns)
        
        # 根据采样率动态调整读取点数
        if sample_rate_hz <= 1000:  # 1kHz以下
            points_per_read = max(100, sample_rate_hz // 10)
        elif sample_rate_hz <= 10000:  # 1kHz-10kHz
            points_per_read = max(500, sample_rate_hz // 20)
        elif sample_rate_hz <= 100000:  # 10kHz-100kHz
            points_per_read = max(1000, sample_rate_hz // 50)
        else:  # 100kHz以上
            points_per_read = max(2000, sample_rate_hz // 100)

        # 确保点数不超过缓冲区大小
        points_per_read = min(points_per_read, self.ai_buffer_size)
        
        logger.info(f"采样率: {sample_rate_hz}Hz, 每次读取点数: {points_per_read}")

        while self.is_acquiring:
            try:
                # 获取数据
                remaining_points = self.dll.USB5GetAi(
                    self.device_index,
                    ctypes.c_long(points_per_read),
                    self.ai_data_buffer.ctypes.data_as(POINTER(c_float)),
                    ctypes.c_long(self.ai_timeout_ms)
                )

                if remaining_points >= 0:
                    # 处理数据
                    try:
                        self._process_ai_acquired_data(points_per_read, remaining_points)
                    except Exception as e:
                        logger.error(f"处理数据异常: {e}")
                        # 继续执行，不中断采集
                    
                    # 如果缓冲区剩余点数过多，说明数据处理跟不上，需要调整读取策略
                    if remaining_points > points_per_read * 0.8:
                        points_per_read = max(100, points_per_read // 2)
                        logger.warning(f"缓冲区积压，调整读取点数为: {points_per_read}")
                else:
                    error_msg = self.ERROR_CODES.get(remaining_points, '未知错误')
                    logger.error(f"AI数据获取失败: {error_msg}")
                    if remaining_points == -7:  # 超时错误
                        continue  # 超时错误可以继续尝试
                    break

            except Exception as e:
                logger.error(f"AI连续采集异常: {e}")
                break

        logger.info("AI连续采集循环结束")

    def _continuous_acquisition_loop(self):
        """
        连续采集循环
        """
        try:
            logger.info("连续采集循环开始")
            time.sleep(0.1)
            while self.is_acquiring:
                try:
                    enabled_channels = [i for i, enabled in enumerate(self.ai_channels) if enabled]
                    num_enabled_channels = len(enabled_channels)
                    if num_enabled_channels == 0:
                        logger.warning("没有启用的AI通道，跳过数据获取。")
                        time.sleep(0.1)
                        continue
                    points_per_channel = 100
                    channel_data = self._get_ai_data(points_per_channel)
                    if channel_data is not None:
                        remaining_points = self._get_buffer_remaining()
                        sample_rate_hz = int(1e9 / self.ai_sample_rate_ns) if self.ai_sample_rate_ns > 0 else 0
                        data_packet = {
                            'timestamp': time.time(),
                            'sample_rate': sample_rate_hz,
                            'points_per_channel': points_per_channel,
                            'remaining_points': remaining_points,
                            'channel_data': channel_data,
                            'enabled_channels': enabled_channels,
                        }
                        if self.data_callback:
                            self.data_callback(data_packet)
                    else:
                        time.sleep(0.01)
                    time.sleep(0.01)
                except Exception as e:
                    logger.error(f"连续采集循环异常: {e}")
                    time.sleep(0.1)
            logger.info("连续采集循环结束")
        except Exception as e:
            logger.error(f"连续采集循环严重异常: {e}")

    def _ai_oneshot_acquisition(self):
        """AI单次采集"""
        logger.info("开始AI单次采集")

        if not self._check_dll_loaded():
            return

        try:
            last_data_packet = None  # 修复UnboundLocalError
            # 等待触发
            while self.is_acquiring and not self.oneshot_triggered:
                time.sleep(0.01)

            if not self.is_acquiring:
                logger.info("单次采集已取消")
                return

            logger.info("单次采集已触发，开始获取数据...")
            total_points_acquired = 0
            last_data_packet = None  # 用于存储最后一个有效数据包

            while self.is_acquiring and not self.oneshot_completed:
                # 计算本次需要获取的点数
                points_to_read = min(
                    self.ai_oneshot_points - total_points_acquired,
                    self.ai_buffer_size
                )

                if points_to_read <= 0:
                    self.oneshot_completed = True
                    break

                # 获取数据
                remaining_points = self.dll.USB5GetAi(
                    self.device_index,
                    ctypes.c_long(points_to_read),
                    self.ai_data_buffer.ctypes.data_as(POINTER(c_float)),
                    ctypes.c_long(self.ai_timeout_ms)
                )

                if remaining_points >= 0:
                    # 计算实际获取的点数
                    points_acquired = points_to_read - remaining_points
                    total_points_acquired += points_acquired

                    # 更新进度
                    self.oneshot_progress = min(100, int(total_points_acquired * 100 / self.ai_oneshot_points))
                    
                    # 处理数据
                    if points_acquired > 0:
                        try:
                            # 保存最后一个有效数据包
                            last_data_packet = self._process_ai_acquired_data(points_acquired, remaining_points, is_final=False)
                        except Exception as e:
                            logger.error(f"处理数据异常: {e}")
                    
                    # 检查是否完成
                    if total_points_acquired >= self.ai_oneshot_points:
                        self.oneshot_completed = True
                        logger.info(f"单次采集完成，共获取 {total_points_acquired} 点数据")
                        break

                    # 如果还有剩余点数，继续获取
                    if remaining_points > 0:
                        continue

                elif remaining_points == -7:  # 超时错误
                    logger.warning("获取数据超时，重试...")
                    continue
                else:
                    error_msg = self.ERROR_CODES.get(remaining_points, '未知错误')
                    logger.error(f"单次采集失败: {error_msg}")
                    break

        except Exception as e:
            logger.error(f"单次采集异常: {e}")
        finally:
            # 清理资源
            self.is_acquiring = False
            self.oneshot_triggered = False
            if self.is_opened:
                try:
                    self.dll.SetUSB5ClrAiTrigger(self.device_index)
                    self.dll.SetUSB5ClrAiFifo(self.device_index)
                except Exception as e:
                    logger.error(f"清理资源异常: {e}")

            # 发送最后一个有效数据包，标记为最终状态
            if self.data_callback and last_data_packet is not None:
                try:
                    # 更新数据包为最终状态
                    last_data_packet['is_final'] = True
                    self.data_callback(last_data_packet)
                except Exception as e:
                    logger.error(f"发送最终数据包异常: {e}")

            logger.info("单次采集线程结束")

    def _process_ai_acquired_data(self, points_acquired: int, remaining_points: int, is_final: bool = False) -> Optional[Dict]:
        """
        处理AI采集到的数据
        Args:
            points_acquired: 本次采集的点数（总点数=每通道点数*通道数）
            remaining_points: 缓冲区剩余点数
            is_final: 是否为最终数据包
        Returns:
            Optional[Dict]: 处理后的数据包
        """
        if not self._check_dll_loaded():
            return None
        try:
            enabled_channels = [i for i, enabled in enumerate(self.ai_channels) if enabled]
            num_enabled_channels = len(enabled_channels)
            if num_enabled_channels == 0:
                return None
            points_per_channel = points_acquired // num_enabled_channels if num_enabled_channels > 0 else 0
            if points_per_channel == 0:
                logger.warning(f"采集点数({points_acquired})不足以分配给通道")
                return None
            channel_data = {}
            for i, ch in enumerate(enabled_channels):
                start = i * points_per_channel
                end = start + points_per_channel
                if self.ai_data_buffer is not None and end <= len(self.ai_data_buffer):
                    channel_data[ch] = self.ai_data_buffer[start:end].copy()
                else:
                    channel_data[ch] = np.zeros(points_per_channel, dtype='float32')
            sample_rate_hz = int(1e9 / self.ai_sample_rate_ns)
            data_packet = {
                'timestamp': time.time(),
                'sample_rate': sample_rate_hz,
                'points_per_channel': points_per_channel,
                'remaining_points': remaining_points,
                'channel_data': {str(ch): data.tolist() for ch, data in channel_data.items()},
                'enabled_channels': enabled_channels,
                'oneshot_progress': self.oneshot_progress if self.ai_sample_mode == self.MODE_ONESHOT else None,
                'is_final': is_final,
                'total_points': self.ai_oneshot_points if self.ai_sample_mode == self.MODE_ONESHOT else None
            }
            if self.data_callback:
                self.data_callback(data_packet)
            logger.info(f"原始数据前20个: {self.ai_data_buffer[:20] if self.ai_data_buffer is not None else []}")
            for ch in enabled_channels:
                ch_data = channel_data.get(ch, [])
                logger.info(f"分离后CH{ch}前5个: {ch_data[:5]}")
            return data_packet
        except Exception as e:
            logger.error(f"AI数据处理异常: {e}")
            return None

    def set_ao_dc_voltage(self, channel: int, voltage: float) -> bool:
        """
        设置AO通道直流电压输出

        Args:
            channel: AO通道号(0-3)
            voltage: 输出电压值

        Returns:
            bool: 设置是否成功
        """
        if not self.is_opened:
            logger.error("设备未打开")
            return False

        if not (0 <= channel <= 3):
            logger.error(f"AO通道号无效: {channel}")
            return False

        if not self._check_dll_loaded():
            return False

        try:
            result = self.dll.SetUSB5AoImmediately(
                self.device_index,
                ctypes.c_ubyte(channel),
                ctypes.c_float(voltage)
            )

            success = self._check_result(result, f"设置AO通道{channel}电压为{voltage}V")
            if success:
                self.ao_voltages[channel] = voltage
                self.ao_channels[channel] = True

            return success

        except Exception as e:
            logger.error(f"设置AO通道{channel}电压异常: {e}")
            return False

    def output_ao_waveform(self, channel: int, waveform_data: np.ndarray,
                           sample_rate_hz: int = 10000, cycle_count: int = 0) -> bool:
        """
        AO通道波形输出

        Args:
            channel: AO通道号(0-3)
            waveform_data: 波形数据
            sample_rate_hz: 输出采样率
            cycle_count: 循环次数(0为无限循环)

        Returns:
            bool: 输出是否成功
        """
        if not self.is_opened:
            logger.error("设备未打开")
            return False

        if not (0 <= channel <= 3):
            logger.error(f"AO通道号无效: {channel}")
            return False

        if not self._check_dll_loaded():
            return False

        try:
            chan = ctypes.c_char(channel)
            sample_rate_ns = int(1e9 / sample_rate_hz)

            # 清除AO触发和FIFO
            self.dll.SetUSB5ClrAoTrigger(self.device_index, chan)
            self.dll.SetUSB5ClrAoFifo(self.device_index, chan)

            # 设置AO输出模式
            result1 = self.dll.SetUSB5AoSampleMode(
                self.device_index, chan, ctypes.c_char(self.AO_MODE_CYCLE)
            )
            success1 = self._check_result(result1, f"设置AO通道{channel}输出模式")

            # 设置采样率
            result2 = self.dll.SetUSB5AoSampleRate(
                self.device_index, chan, ctypes.c_uint(sample_rate_ns)
            )
            success2 = self._check_result(result2, f"设置AO通道{channel}采样率")

            # 设置触发源
            result3 = self.dll.SetUSB5AoTrigSource(
                self.device_index, chan, ctypes.c_char(0)
            )
            success3 = self._check_result(result3, f"设置AO通道{channel}触发源")

            # 设置时钟源
            result4 = self.dll.SetUSB5AoConvSource(
                self.device_index, chan, ctypes.c_char(0)
            )
            success4 = self._check_result(result4, f"设置AO通道{channel}时钟源")

            # 设置循环次数
            result5 = self.dll.SetUSB5AoCycle(
                self.device_index, chan, ctypes.c_uint(cycle_count)
            )
            success5 = self._check_result(result5, f"设置AO通道{channel}循环次数")

            # 设置波形数据
            waveform_float32 = waveform_data.astype('float32')
            result6 = self.dll.SetUSB5AoDataFifo(
                self.device_index, chan,
                waveform_float32.ctypes.data_as(POINTER(c_float)),
                ctypes.c_uint(len(waveform_float32))
            )
            success6 = self._check_result(result6, f"设置AO通道{channel}波形数据")

            # 软件触发
            result7 = self.dll.SetUSB5AoSoftTrig(self.device_index, chan)
            success7 = self._check_result(result7, f"AO通道{channel}软件触发")

            return all([success1, success2, success3, success4, success5, success6, success7])

        except Exception as e:
            logger.error(f"AO通道{channel}波形输出异常: {e}")
            return False

    def get_device_status(self) -> Dict:
        """
        获取设备状态

        Returns:
            Dict: 设备状态信息
        """
        return {
            'is_opened': self.is_opened,
            'is_acquiring': self.is_acquiring,
            'ai_sample_mode': 'continuous' if self.ai_sample_mode == self.MODE_CONTINUOUS else 'oneshot',
            'ai_sample_rate_hz': int(1e9 / self.ai_sample_rate_ns),
            'ai_enabled_channels': [i for i, enabled in enumerate(self.ai_channels) if enabled],
            'ai_channel_ranges': self.ai_channel_ranges,
            'ao_channels': self.ao_channels,
            'ao_voltages': self.ao_voltages
        }

    def __del__(self):
        """析构函数"""
        try:
            self.close_device()
        except:
            pass

    def _separate_channel_data(self, raw_data: np.ndarray, points_per_channel: int) -> Dict[str, List[float]]:
        """
        USB5000系列多通道连续采样分离：按物理通道号分段切片
        raw_data = [CH0的N点][CH1的N点]...[CH15的N点]
        enabled_channels = [a, b, c, ...]
        """
        try:
            enabled_channels = [i for i, enabled in enumerate(self.ai_channels) if enabled]
            num_channels = 16
            separated_data = {}
            for ch in enabled_channels:
                start_idx = ch * points_per_channel
                end_idx = start_idx + points_per_channel
                if end_idx <= len(raw_data):
                    separated_data[str(ch)] = raw_data[start_idx:end_idx].tolist()
                else:
                    separated_data[str(ch)] = [0.0] * points_per_channel
            return separated_data
        except Exception as e:
            logger.error(f"数据分离失败: {e}")
            return {}

    def _get_ai_data(self, points_per_channel: int) -> Optional[Dict[str, List[float]]]:
        """
        获取AI数据
        Args:
            points_per_channel: 每个通道需要获取的数据点数
        Returns:
            通道数据字典
        """
        try:
            if not self.is_opened:
                logger.error("设备未打开")
                return None
            enabled_channels = [i for i, enabled in enumerate(self.ai_channels) if enabled]
            num_enabled_channels = len(enabled_channels)
            if num_enabled_channels == 0:
                logger.warning("没有启用的AI通道")
                return {}
            total_points = points_per_channel * num_enabled_channels
            data_buffer = (ctypes.c_float * total_points)()
            # 关键修正：Points参数为每通道点数
            result = self.dll.USB5GetAi(
                self.device_index,
                ctypes.c_uint(points_per_channel),
                ctypes.cast(data_buffer, ctypes.POINTER(ctypes.c_float)),
                ctypes.c_long(self.ai_timeout_ms)
            )
            if result < 0:
                if result == -7:
                    logger.debug(f"获取AI数据超时，可能缓冲区数据不足: {result}")
                    return None
                else:
                    logger.error(f"获取AI数据失败: {result}")
                    return None
            raw_data = np.array(data_buffer, dtype=np.float32)
            # 按文档顺序分离数据
            separated_data = {}
            for i, ch in enumerate(enabled_channels):
                start = i * points_per_channel
                end = start + points_per_channel
                separated_data[str(ch)] = raw_data[start:end].tolist()
            logger.debug(f"获取AI数据成功: 通道数={len(separated_data)}, 每通道点数={points_per_channel}")
            return separated_data
        except Exception as e:
            logger.error(f"获取AI数据异常: {e}")
            return None

    def _get_buffer_remaining(self) -> int:
        """
        获取缓冲区剩余点数
        
        Returns:
            剩余点数
        """
        try:
            # 创建一个小的缓冲区来获取剩余点数
            temp_buffer = (ctypes.c_float * 1)()
            result = self.dll.USB5GetAi(
                self.device_index,
                ctypes.c_uint(0),  # 请求0个点来获取剩余数量
                ctypes.cast(temp_buffer, ctypes.POINTER(ctypes.c_float)),
                ctypes.c_long(1)  # 很短的超时
            )
            
            # 返回值就是剩余点数
            return max(0, result)
            
        except Exception as e:
            logger.error(f"获取缓冲区剩余点数失败: {e}")
            return 0

    def set_ai_sample_mode(self, mode: int) -> bool:
        """
        设置AI采集模式
        
        Args:
            mode: 采集模式 (0=连续, 1=单次)
            
        Returns:
            是否成功
        """
        try:
            if not self.is_opened:
                logger.error("设备未打开")
                return False
            
            if mode not in [0, 1]:
                logger.error(f"无效的采集模式: {mode}")
                return False
            
            result = self.dll.SetUSB5AiSampleMode(self.device_index, ctypes.c_char(mode))
            if result == 0:
                self.ai_sample_mode = mode
                logger.info(f"设置AI采集模式成功: {'连续' if mode == 0 else '单次'}")
                return True
            else:
                logger.error(f"设置AI采集模式失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"设置AI采集模式异常: {e}")
            return False

    def set_ai_sample_rate(self, sample_rate_hz: int) -> bool:
        """
        设置AI采样率
        
        Args:
            sample_rate_hz: 采样率(Hz)
            
        Returns:
            是否成功
        """
        try:
            if not self.is_opened:
                logger.error("设备未打开")
                return False
            
            if sample_rate_hz <= 0:
                logger.error(f"无效的采样率: {sample_rate_hz}")
                return False
            
            # 转换为纳秒周期
            sample_rate_ns = int(1e9 / sample_rate_hz)
            
            result = self.dll.SetUSB5AiSampleRate(self.device_index, ctypes.c_int(sample_rate_ns))
            if result == 0:
                self.ai_sample_rate_ns = sample_rate_ns
                logger.info(f"设置AI采样率成功: {sample_rate_hz}Hz ({sample_rate_ns}ns)")
                return True
            else:
                logger.error(f"设置AI采样率失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"设置AI采样率异常: {e}")
            return False

    def set_ai_oneshot_points(self, points: int) -> bool:
        """
        设置AI单次采集点数
        
        Args:
            points: 采集点数
            
        Returns:
            是否成功
        """
        try:
            if not self.is_opened:
                logger.error("设备未打开")
                return False
            
            if points <= 0:
                logger.error(f"无效的采集点数: {points}")
                return False
            
            result = self.dll.SetUSB5AiOneShotPoints(self.device_index, ctypes.c_uint(points))
            if result == 0:
                self.ai_oneshot_points = points
                logger.info(f"设置AI单次采集点数成功: {points}")
                return True
            else:
                logger.error(f"设置AI单次采集点数失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"设置AI单次采集点数异常: {e}")
            return False

    def stop_continuous_acquisition(self) -> bool:
        """
        停止连续采集
        
        Returns:
            是否成功
        """
        try:
            if not self.is_acquiring:
                logger.warning("采集未在进行中")
                return True
            
            self.is_acquiring = False
            
            # 等待采集线程结束
            if self.acquisition_thread and self.acquisition_thread.is_alive():
                self.acquisition_thread.join(timeout=2.0)
            
            # 清除触发和缓冲区
            if self.is_opened:
                self.dll.SetUSB5ClrAiTrigger(self.device_index)
                self.dll.SetUSB5ClrAiFifo(self.device_index)
            
            logger.info("连续采集已停止")
            return True
            
        except Exception as e:
            logger.error(f"停止连续采集异常: {e}")
            return False

    def _configure_ai_acquisition(self) -> bool:
        """
        配置AI采集参数
        
        Returns:
            是否成功
        """
        try:
            if not self.is_opened:
                logger.error("设备未打开")
                return False
            
            # 设置采集模式
            result = self.dll.SetUSB5AiSampleMode(self.device_index, ctypes.c_char(self.ai_sample_mode))
            if result != 0:
                logger.error(f"设置AI采集模式失败: {result}")
                return False
            
            # 设置采样率
            result = self.dll.SetUSB5AiSampleRate(self.device_index, ctypes.c_int(self.ai_sample_rate_ns))
            if result != 0:
                logger.error(f"设置AI采样率失败: {result}")
                return False
            
            # 如果是单次采集模式，设置点数
            if self.ai_sample_mode == 1:
                result = self.dll.SetUSB5AiOneShotPoints(self.device_index, ctypes.c_uint(self.ai_oneshot_points))
                if result != 0:
                    logger.error(f"设置AI单次采集点数失败: {result}")
                    return False
            
            # 设置触发源（软件触发）
            result = self.dll.SetUSB5AiTrigSource(self.device_index, ctypes.c_char(0))
            if result != 0:
                logger.error(f"设置AI触发源失败: {result}")
                return False
            
            # 设置时钟源（内部时钟）
            result = self.dll.SetUSB5AiConvSource(self.device_index, ctypes.c_char(0))
            if result != 0:
                logger.error(f"设置AI时钟源失败: {result}")
                return False
            
            logger.info("AI采集参数配置成功")
            return True
            
        except Exception as e:
            logger.error(f"配置AI采集参数异常: {e}")
            return False

    def start_continuous_acquisition(self, callback):
        """
        开始连续采集
        Args:
            callback: 数据回调函数，参数为(data_packet)
        Returns:
            是否成功启动
        """
        try:
            if not self.is_opened:
                logger.error("设备未打开")
                return False
            if self.is_acquiring:
                logger.warning("采集已在进行中")
                return False
            enabled_count = sum(self.ai_channels)
            if enabled_count == 0:
                logger.error("没有启用的AI通道")
                return False
            if not self._configure_ai_acquisition():
                return False
            self.dll.SetUSB5ClrAiFifo(self.device_index)
            result = self.dll.SetUSB5AiSoftTrig(self.device_index)
            if result != 0:
                logger.error(f"启动软件触发失败: {result}")
                return False
            self.is_acquiring = True
            self.data_callback = callback
            self.acquisition_thread = threading.Thread(
                target=self._continuous_acquisition_loop,
                daemon=True
            )
            self.acquisition_thread.start()
            logger.info(f"连续采集已启动: 启用通道数={enabled_count}")
            return True
        except Exception as e:
            logger.error(f"启动连续采集失败: {e}")
            return False
