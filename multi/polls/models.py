from django.db import models
from django.db import models
import  uuid
# Create your models here.

def generate_user_id():
    return str(uuid.uuid4())

class Userinformation(models.Model):
    user_id = models.CharField(
        primary_key=True,
        max_length=36,
        default=generate_user_id,  # 使用UUID生成用户ID
        editable=False  # 不允许编辑该字段
    )
    user_name = models.CharField(max_length=100)  # 用户名字段
    user_email = models.EmailField(unique=True)  # 用户邮箱，唯一
    user_pwd = models.CharField(max_length=20)  # 存储密码（明文）

    def __str__(self):
        return self.user_email  # 返回邮箱作为模型的字符串表示，方便查看

    class Meta:
        db_table = 'user_information'  # 设置数据库表名


class MonitorTask(models.Model):
    """监控任务数据模型"""
    task_id = models.CharField(
        primary_key=True,
        max_length=36,
        default=generate_user_id,
        editable=False
    )
    task_name = models.CharField(max_length=200, verbose_name="任务名称")
    task_description = models.TextField(blank=True, null=True, verbose_name="任务备注")
    
    # 时间信息
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(verbose_name="结束时间")
    interval_seconds = models.IntegerField(verbose_name="采集间隔(秒)")
    total_duration_minutes = models.IntegerField(verbose_name="总时长(分钟)")
    
    # 采集配置
    sample_rate = models.IntegerField(verbose_name="采样率(Hz)")
    points_per_acquisition = models.IntegerField(verbose_name="单次采集点数")
    enabled_channels = models.JSONField(verbose_name="启用的通道列表")
    channel_configs = models.JSONField(verbose_name="通道配置信息")
    
    # 数据文件信息
    csv_file_path = models.CharField(max_length=500, verbose_name="CSV文件路径")
    data_file_size = models.BigIntegerField(default=0, verbose_name="数据文件大小(字节)")
    
    # 统计信息
    total_acquisitions = models.IntegerField(default=0, verbose_name="总采集次数")
    total_data_points = models.BigIntegerField(default=0, verbose_name="总数据点数")
    
    # 用户信息
    user_email = models.CharField(max_length=100, verbose_name="用户邮箱")
    user_name = models.CharField(max_length=100, verbose_name="用户姓名")
    
    # 创建和更新时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 状态信息
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    def __str__(self):
        return f"{self.task_name} ({self.task_id})"

    class Meta:
        db_table = 'monitor_tasks'
        verbose_name = "监控任务"
        verbose_name_plural = "监控任务"
        ordering = ['-created_at']

    @property
    def duration_seconds(self):
        """计算实际监控时长（秒）"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds())
        return 0

    @property
    def file_size_mb(self):
        """返回文件大小（MB）"""
        if self.data_file_size:
            return round(self.data_file_size / (1024 * 1024), 2)
        return 0.0


class TrainingSet(models.Model):
    """训练集数据模型"""
    training_set_id = models.CharField(
        primary_key=True,
        max_length=36,
        default=generate_user_id,
        editable=False
    )
    
    # 基本信息
    name = models.CharField(max_length=200, verbose_name="训练集名称")
    description = models.TextField(blank=True, null=True, verbose_name="训练集描述")
    start_time = models.DateTimeField(verbose_name="训练开始时间")
    
    # 训练模式配置
    model_type = models.CharField(max_length=50, verbose_name="模型类型")
    training_mode = models.CharField(max_length=20, verbose_name="训练模式")  # basic/expert
    
    # 数据选择
    selected_data_sources = models.JSONField(verbose_name="选中的数据源")
    
    # 学习参数
    learning_params = models.JSONField(verbose_name="学习参数配置")
    
    # 用户信息
    user_email = models.CharField(max_length=100, verbose_name="用户邮箱")
    user_name = models.CharField(max_length=100, verbose_name="用户姓名")
    
    # 创建和更新时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 状态信息
    status = models.CharField(max_length=20, default='created', verbose_name="状态")  # created, training, completed, failed
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    # 训练进度信息
    current_epoch = models.IntegerField(default=0, verbose_name="当前轮数")
    total_epochs = models.IntegerField(default=0, verbose_name="总轮数")
    training_status = models.CharField(max_length=20, default='created', verbose_name="训练状态")  # created, training, paused, completed, failed, stopped
    is_paused = models.BooleanField(default=False, verbose_name="是否暂停")
    pause_requested = models.BooleanField(default=False, verbose_name="是否请求暂停")
    
    # 训练对象和元数据（非数据库字段，用于运行时存储）
    trainer_object = None  # 训练器对象
    metadata = None  # 训练元数据
    


    def __str__(self):
        return f"{self.name} ({self.training_set_id})"

    class Meta:
        db_table = 'training_sets'
        verbose_name = "训练集"
        verbose_name_plural = "训练集"
        ordering = ['-created_at']


class SavedModel(models.Model):
    """已保存的模型数据模型"""
    model_id = models.CharField(
        primary_key=True,
        max_length=36,
        default=generate_user_id,
        editable=False
    )
    
    # 基本信息
    name = models.CharField(max_length=200, verbose_name="模型名称")
    model_type = models.CharField(max_length=50, verbose_name="模型类型")  # LSTM, CNN, etc.
    description = models.TextField(blank=True, null=True, verbose_name="模型描述")
    
    # 文件信息
    model_file_path = models.CharField(max_length=500, verbose_name="模型文件路径")
    model_file_size = models.BigIntegerField(default=0, verbose_name="模型文件大小(字节)")
    
    # 训练信息
    training_set = models.ForeignKey(TrainingSet, on_delete=models.CASCADE, verbose_name="关联训练集")
    training_set_name = models.CharField(max_length=200, verbose_name="训练集名称")
    
    # 性能指标
    final_training_loss = models.FloatField(null=True, blank=True, verbose_name="最终训练损失")
    final_validation_loss = models.FloatField(null=True, blank=True, verbose_name="最终验证损失")
    accuracy = models.FloatField(null=True, blank=True, verbose_name="准确率")
    
    # 模型参数
    model_params = models.JSONField(verbose_name="模型参数")  # 存储模型配置信息
    
    # 用户信息
    user_email = models.CharField(max_length=100, verbose_name="用户邮箱")
    user_name = models.CharField(max_length=100, verbose_name="用户姓名")
    
    # 创建和更新时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 状态信息
    is_deployed = models.BooleanField(default=False, verbose_name="是否已部署")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    def __str__(self):
        return f"{self.name} ({self.model_type})"

    class Meta:
        db_table = 'saved_models'
        verbose_name = "已保存模型"
        verbose_name_plural = "已保存模型"
        ordering = ['-created_at']

    @property
    def file_size_mb(self):
        """返回文件大小（MB）"""
        if self.model_file_size:
            return round(self.model_file_size / (1024 * 1024), 2)
        return 0.0
    trainer_object = None  # 训练器对象
    metadata = None  # 训练元数据
    


    def __str__(self):
        return f"{self.name} ({self.training_set_id})"

    class Meta:
        db_table = 'training_sets'
        verbose_name = "训练集"
        verbose_name_plural = "训练集"
        ordering = ['-created_at']
class SavedModel(models.Model):
    """已保存的模型数据模型"""
    model_id = models.CharField(
        primary_key=True,
        max_length=36,
        default=generate_user_id,
        editable=False
    )
    
    # 基本信息
    name = models.CharField(max_length=200, verbose_name="模型名称")
    model_type = models.CharField(max_length=50, verbose_name="模型类型")  # LSTM, CNN, etc.
    description = models.TextField(blank=True, null=True, verbose_name="模型描述")
    
    # 文件信息
    model_file_path = models.CharField(max_length=500, verbose_name="模型文件路径")
    model_file_size = models.BigIntegerField(default=0, verbose_name="模型文件大小(字节)")
    
    # 训练信息
    training_set = models.ForeignKey(TrainingSet, on_delete=models.CASCADE, verbose_name="关联训练集")
    training_set_name = models.CharField(max_length=200, verbose_name="训练集名称")
    
    # 性能指标
    final_training_loss = models.FloatField(null=True, blank=True, verbose_name="最终训练损失")
    final_validation_loss = models.FloatField(null=True, blank=True, verbose_name="最终验证损失")
    accuracy = models.FloatField(null=True, blank=True, verbose_name="准确率")
    
    # 模型参数
    model_params = models.JSONField(verbose_name="模型参数")  # 存储模型配置信息
    
    # 用户信息
    user_email = models.CharField(max_length=100, verbose_name="用户邮箱")
    user_name = models.CharField(max_length=100, verbose_name="用户姓名")
    
    # 创建和更新时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 状态信息
    is_deployed = models.BooleanField(default=False, verbose_name="是否已部署")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    def __str__(self):
        return f"{self.name} ({self.model_type})"

    class Meta:
        db_table = 'saved_models'
        verbose_name = "已保存模型"
        verbose_name_plural = "已保存模型"
        ordering = ['-created_at']

    @property
    def file_size_mb(self):
        """返回文件大小（MB）"""
        if self.model_file_size:
            return round(self.model_file_size / (1024 * 1024), 2)
        return 0.0

