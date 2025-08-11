import numpy as np
import pandas as pd
import os
from datetime import datetime

def generate_simulated_data():
    """生成模拟的传感器数据"""
    
    # 参数设置
    sample_rate = 10000  # 采样率 10kHz
    duration = 2.0  # 持续时间 2秒
    num_samples = int(sample_rate * duration)
    
    # 时间轴
    time = np.linspace(0, duration, num_samples)
    
    # 通道1: 正弦波 + 噪声
    frequency = 5.0  # 5Hz正弦波
    amplitude = 2.0
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * time)
    noise_level = 0.1
    noise = np.random.normal(0, noise_level, num_samples)
    ch0_data = sine_wave + noise
    
    # 通道2: PWM波 + 噪声
    pwm_frequency = 10.0  # 10Hz PWM
    duty_cycle = 0.3  # 30%占空比
    
    # 生成PWM波
    pwm_period = 1.0 / pwm_frequency
    samples_per_period = int(sample_rate / pwm_frequency)
    
    pwm_wave = np.zeros(num_samples)
    for i in range(0, num_samples, samples_per_period):
        # 计算当前周期内的样本数
        period_samples = min(samples_per_period, num_samples - i)
        high_samples = int(period_samples * duty_cycle)
        
        # 设置高电平和低电平
        pwm_wave[i:i+high_samples] = 3.0  # 高电平
        pwm_wave[i+high_samples:i+period_samples] = 0.0  # 低电平
    
    # 添加噪声
    pwm_noise = np.random.normal(0, 0.05, num_samples)
    ch1_data = pwm_wave + pwm_noise
    
    # 创建DataFrame
    df = pd.DataFrame({
        'Time(s)': time,
        'CH0': ch0_data,
        'CH1': ch1_data
    })
    
    return df

def save_simulated_data():
    """保存模拟数据到CSV文件"""
    
    # 生成数据
    df = generate_simulated_data()
    
    # 创建保存目录
    save_dir = "multi/myproject/media/monitor_data"
    os.makedirs(save_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"simulated_data_{timestamp}.csv"
    filepath = os.path.join(save_dir, filename)
    
    # 保存数据
    df.to_csv(filepath, index=False)
    
    print(f"✅ 模拟数据已保存到: {filepath}")
    print(f"📊 数据形状: {df.shape}")
    print(f"📈 通道0 (正弦波): 范围=[{df['CH0'].min():.3f}, {df['CH0'].max():.3f}], 均值={df['CH0'].mean():.3f}")
    print(f"📈 通道1 (PWM波): 范围=[{df['CH1'].min():.3f}, {df['CH1'].max():.3f}], 均值={df['CH1'].mean():.3f}")
    
    return filepath

if __name__ == "__main__":
    filepath = save_simulated_data()
    print(f"\n🎯 文件路径: {filepath}")
    print("💡 现在可以在训练界面中使用这个文件进行训练了！") 
import pandas as pd
import os
from datetime import datetime

def generate_simulated_data():
    """生成模拟的传感器数据"""
    
    # 参数设置
    sample_rate = 10000  # 采样率 10kHz
    duration = 2.0  # 持续时间 2秒
    num_samples = int(sample_rate * duration)
    
    # 时间轴
    time = np.linspace(0, duration, num_samples)
    
    # 通道1: 正弦波 + 噪声
    frequency = 5.0  # 5Hz正弦波
    amplitude = 2.0
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * time)
    noise_level = 0.1
    noise = np.random.normal(0, noise_level, num_samples)
    ch0_data = sine_wave + noise
    
    # 通道2: PWM波 + 噪声
    pwm_frequency = 10.0  # 10Hz PWM
    duty_cycle = 0.3  # 30%占空比
    
    # 生成PWM波
    pwm_period = 1.0 / pwm_frequency
    samples_per_period = int(sample_rate / pwm_frequency)
    
    pwm_wave = np.zeros(num_samples)
    for i in range(0, num_samples, samples_per_period):
        # 计算当前周期内的样本数
        period_samples = min(samples_per_period, num_samples - i)
        high_samples = int(period_samples * duty_cycle)
        
        # 设置高电平和低电平
        pwm_wave[i:i+high_samples] = 3.0  # 高电平
        pwm_wave[i+high_samples:i+period_samples] = 0.0  # 低电平
    
    # 添加噪声
    pwm_noise = np.random.normal(0, 0.05, num_samples)
    ch1_data = pwm_wave + pwm_noise
    
    # 创建DataFrame
    df = pd.DataFrame({
        'Time(s)': time,
        'CH0': ch0_data,
        'CH1': ch1_data
    })
    
    return df

def save_simulated_data():
    """保存模拟数据到CSV文件"""
    
    # 生成数据
    df = generate_simulated_data()
    
    # 创建保存目录
    save_dir = "multi/myproject/media/monitor_data"
    os.makedirs(save_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"simulated_data_{timestamp}.csv"
    filepath = os.path.join(save_dir, filename)
    
    # 保存数据
    df.to_csv(filepath, index=False)
    
    print(f"✅ 模拟数据已保存到: {filepath}")
    print(f"📊 数据形状: {df.shape}")
    print(f"📈 通道0 (正弦波): 范围=[{df['CH0'].min():.3f}, {df['CH0'].max():.3f}], 均值={df['CH0'].mean():.3f}")
    print(f"📈 通道1 (PWM波): 范围=[{df['CH1'].min():.3f}, {df['CH1'].max():.3f}], 均值={df['CH1'].mean():.3f}")
    
    return filepath

if __name__ == "__main__":
    filepath = save_simulated_data()
    print(f"\n🎯 文件路径: {filepath}")
    print("💡 现在可以在训练界面中使用这个文件进行训练了！") 
 
 