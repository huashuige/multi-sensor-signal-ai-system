import pandas as pd
import os

# 检查最新的CSV文件 - 修正路径
csv_dir = "D:/multi/multi/myproject/media/monitor_data"
if os.path.exists(csv_dir):
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    if csv_files:
        # 按修改时间排序，获取最新的文件
        csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(csv_dir, x)), reverse=True)
        latest_file = os.path.join(csv_dir, csv_files[0])
        
        print(f"检查文件: {latest_file}")
        print(f"文件大小: {os.path.getsize(latest_file)} 字节")
        
        # 读取CSV文件
        df = pd.read_csv(latest_file)
        print(f"DataFrame形状: {df.shape}")
        print(f"DataFrame列: {df.columns.tolist()}")
        
        # 显示前几行数据
        print("\n前5行数据:")
        print(df.head())
        
        # 显示每列的数据统计
        print("\n数据统计:")
        for col in df.columns:
            if col != 'Time(s)':
                print(f"{col}:")
                print(f"  最小值: {df[col].min()}")
                print(f"  最大值: {df[col].max()}")
                print(f"  平均值: {df[col].mean()}")
                print(f"  标准差: {df[col].std()}")
                print(f"  非空值数量: {df[col].count()}")
                print(f"  前5个值: {df[col].head().tolist()}")
                print()
        
        # 检查是否有NaN值
        print("NaN值检查:")
        for col in df.columns:
            nan_count = df[col].isna().sum()
            print(f"{col}: {nan_count} 个NaN值")
            
    else:
        print("没有找到CSV文件")
else:
    print(f"目录不存在: {csv_dir}")
    # 尝试列出父目录内容
    parent_dir = "D:/multi/multi/myproject/media"
    if os.path.exists(parent_dir):
        print(f"父目录存在，内容: {os.listdir(parent_dir)}")
    else:
        print(f"父目录也不存在: {parent_dir}") 