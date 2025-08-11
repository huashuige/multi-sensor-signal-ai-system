"""
深度学习模块视图函数
提供深度学习相关的API接口
"""

import json
import logging
import os
import time
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

# 配置日志
logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def deep_learning_dashboard(request):
    """
    深度学习仪表板页面
    """
    try:
        return render(request, 'modules/deep_learning.html')
    except Exception as e:
        logger.error(f"渲染深度学习仪表板失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'渲染深度学习仪表板失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def start_training(request):
    """
    开始模型训练API
    """
    try:
        data = json.loads(request.body)
        task_ids = data.get('task_ids', [])
        channels = data.get('channels', [])
        model_config = data.get('model_config', {})
        
        if not task_ids:
            return JsonResponse({
                'success': False,
                'message': '请选择任务ID'
            }, status=400)
        
        if not channels:
            return JsonResponse({
                'success': False,
                'message': '请选择通道'
            }, status=400)
        
        # 生成训练ID
        training_id = f"training_{int(time.time())}"
        
        # TODO: 实现实际的训练逻辑
        # 这里应该包含：
        # 1. 加载数据
        # 2. 构建模型
        # 3. 开始训练
        # 4. 保存训练状态
        
        return JsonResponse({
            'success': True,
            'message': '模型训练已开始',
            'training_id': training_id,
            'status': 'training'
        })
        
    except Exception as e:
        logger.error(f"开始训练失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'开始训练失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def start_training_from_training_set(request):
    """
    从训练集开始训练API
    """
    try:
        data = json.loads(request.body)
        training_set_id = data.get('training_set_id')
        force_restart = data.get('force_restart', False)  # 添加强制重启参数
        
        if not training_set_id:
            return JsonResponse({
                'success': False,
                'message': '请提供训练集ID'
            }, status=400)
        
        # 检查用户登录状态
        user_email = request.session.get('user_email', '')
        if not user_email:
            return JsonResponse({
                'success': False,
                'message': '用户未登录'
            }, status=401)
        
        # 导入模型
        from .models import TrainingSet
        
        try:
            training_set = TrainingSet.objects.get(
                training_set_id=training_set_id,
                user_email=user_email
            )
        except TrainingSet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '训练集不存在'
            }, status=404)
        
        # 检查训练状态，决定是否启动新训练
        current_status = training_set.training_status
        
        # 如果不是强制重启，则进行状态检查
        if not force_restart:
            if current_status in ['training', 'paused']:
                # 有活跃训练，返回监控信息
                return JsonResponse({
                    'success': True,
                    'message': f"检测到训练集 '{training_set.name}' 正在训练中，正在打开监控界面...",
                    'training_set_id': training_set_id,
                    'action': 'open_monitor',
                    'status': current_status
                })
            
            elif current_status in ['completed', 'failed', 'stopped']:
                # 训练已结束，询问是否重新开始
                status_messages = {
                    'completed': '训练已完成',
                    'failed': '上次训练失败',
                    'stopped': '上次训练已被停止'
                }
                message = f"{status_messages[current_status]}，是否重新开始训练？"
                
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'training_set_id': training_set_id,
                    'action': 'ask_restart',
                    'status': current_status
                })
            
            elif current_status in ['created', 'pending']:
                # 未开始训练，正常启动
                pass  # 继续执行下面的启动逻辑
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'未知的训练状态: {current_status}'
                }, status=400)
        
        # 强制重启或正常启动：更新训练状态
        training_set.training_status = 'training'
        training_set.status = 'training'  # 同步status字段
        training_set.current_epoch = 0
        from django.utils import timezone
        training_set.start_time = timezone.now()
        training_set.save()
        
        # 启动实际的训练进程
        try:
            from .sensor_data_loader import train_multi_channel_model
            import threading
            
            # 获取训练配置
            learning_params = training_set.learning_params or {}
            model_config = {
                'window_size': learning_params.get('window_size', 24),
                'horizon': learning_params.get('horizon', 12),
                'batch_size': learning_params.get('batch_size', 32),
                'hidden_size': learning_params.get('hidden_size', 64),
                'num_layers': learning_params.get('lstmLayers', 2),
                'dropout': learning_params.get('dropout', 0.1),
                'lr': learning_params.get('learning_rate', 0.001),  # 使用lr而不是learning_rate
                'epochs': training_set.total_epochs
            }
            
            # 获取数据源信息
            selected_data_sources = training_set.selected_data_sources
            if isinstance(selected_data_sources, str):
                selected_data_sources = json.loads(selected_data_sources)
            
            # 从选中的数据源中提取任务ID和通道信息
            task_ids = []
            channels = []
            
            print(f"🔍 原始数据源信息: {selected_data_sources}")
            
            if selected_data_sources:
                # 检查是否是包含dataSource字段的对象格式
                if isinstance(selected_data_sources, dict) and 'dataSource' in selected_data_sources:
                    data_source = selected_data_sources['dataSource']
                    print(f"🔍 处理dataSource: {data_source}")
                    
                    if isinstance(data_source, dict):
                        task_id = data_source.get('task_id')
                        enabled_channels = data_source.get('enabled_channels', [])
                        
                        if task_id:
                            task_ids.append(task_id)
                            print(f"🔍 找到任务ID: {task_id}")
                        
                        # 将数字通道转换为字符串格式
                        if enabled_channels:
                            channels = [f'CH{ch}' for ch in enabled_channels]
                            print(f"🔍 转换通道格式: {enabled_channels} -> {channels}")
                
                # 如果是数组格式，保持原有逻辑
                elif isinstance(selected_data_sources, list):
                    for data_source in selected_data_sources:
                        print(f"🔍 处理数据源: {data_source}")
                        if isinstance(data_source, dict):
                            task_id = data_source.get('task_id') or data_source.get('id')
                            task_channels = data_source.get('channels', [])
                            if task_id:
                                task_ids.append(task_id)
                            if task_channels:
                                channels.extend(task_channels)
                        elif isinstance(data_source, str):
                            # 如果是字符串，尝试解析
                            try:
                                parsed = json.loads(data_source)
                                if isinstance(parsed, dict):
                                    task_id = parsed.get('task_id') or parsed.get('id')
                                    task_channels = parsed.get('channels', [])
                                    if task_id:
                                        task_ids.append(task_id)
                                    if task_channels:
                                        channels.extend(task_channels)
                            except Exception as e:
                                print(f"❌ 解析数据源字符串失败: {e}")
            
            # 过滤空值
            task_ids = [tid for tid in task_ids if tid]
            channels = [ch for ch in channels if ch]
            
            print(f"🔍 提取的任务ID: {task_ids}")
            print(f"🔍 提取的通道: {channels}")
            
            # 如果没有有效的数据源，使用默认数据
            if not task_ids or not channels:
                print(f"⚠️ 没有找到有效的数据源，使用默认数据")
                # 获取可用的监控任务作为默认数据源
                from .models import MonitorTask
                try:
                    available_tasks = MonitorTask.objects.filter(
                        user_email=user_email,
                        is_deleted=False
                    ).order_by('-created_at')[:1]
                    
                    if available_tasks:
                        task = available_tasks[0]
                        task_ids = [task.task_id]
                        # 获取该任务的可用通道
                        if task.enabled_channels:
                            channels = [f'CH{ch}' for ch in task.enabled_channels]
                        else:
                            channels = ['CH0', 'CH1']  # 默认通道
                        print(f"🔍 使用默认任务: {task.task_id}, 通道: {channels}")
                    else:
                        print(f"❌ 没有找到可用的监控任务")
                        raise ValueError("没有可用的数据源进行训练")
                except Exception as e:
                    print(f"❌ 获取默认数据源失败: {e}")
                    raise ValueError("无法获取训练数据源")
            
            print(f"🚀 启动训练进程...")
            print(f"📊 训练集ID: {training_set_id}")
            print(f"📊 任务ID: {task_ids}")
            print(f"📊 通道: {channels}")
            print(f"📊 模型配置: {model_config}")
            
            # 定义进度回调函数
            def progress_callback(progress_data):
                try:
                    epoch = progress_data['epoch']
                    total_epochs = progress_data['total_epochs']
                    train_loss = progress_data['train_loss']
                    val_loss = progress_data['val_loss']
                    learning_rate = progress_data['learning_rate']
                    
                    # 检查训练是否被暂停
                    training_set.refresh_from_db()
                    if training_set.training_status == 'paused':
                        print(f"⏸️ 训练已暂停，等待恢复...")
                        # 等待恢复，而不是直接退出
                        while training_set.training_status == 'paused':
                            import time
                            time.sleep(1)  # 每秒检查一次
                            training_set.refresh_from_db()
                        print(f"🔄 训练已恢复，继续训练...")
                    
                    # 更新数据库中的训练进度
                    training_set.current_epoch = epoch
                    training_set.learning_params = {
                        'current_training_loss': train_loss,
                        'current_validation_loss': val_loss,
                        'current_learning_rate': learning_rate
                    }
                    training_set.save()
                    print(f"📊 轮次 {epoch}/{total_epochs} - 训练损失: {train_loss:.6f}, 验证损失: {val_loss:.6f}")
                    
                    # 返回True表示继续训练
                    return True
                except Exception as e:
                    print(f"❌ 更新训练进度失败: {str(e)}")
                    return True  # 即使出错也继续训练
            
            # 在后台线程中启动训练
            def train_in_background():
                try:
                    # 确保models目录存在
                    import os
                    os.makedirs("models", exist_ok=True)
                    
                    trainer, metadata = train_multi_channel_model(
                        task_ids=task_ids,
                        channels=channels,
                        model_config=model_config,
                        save_dir="models",
                        progress_callback=progress_callback,
                        training_set_id=training_set_id  # 传递训练集ID用于检查停止状态
                    )
                    
                    # 检查训练是否被停止
                    if metadata.get('status') == 'stopped':
                        print(f"⏹️ 训练已被停止")
                        training_set.training_status = 'stopped'
                        training_set.status = 'failed'  # 同步status字段
                        training_set.save()
                        return
                    
                    # 训练完成，更新状态和保存模型信息
                    training_set.training_status = 'completed'
                    training_set.status = 'completed'  # 同步status字段
                    training_set.current_epoch = training_set.total_epochs
                    
                    # 保存模型文件路径和元数据到learning_params
                    learning_params = training_set.learning_params or {}
                    learning_params.update({
                        'saved_model_path': metadata.get('model_path', ''),
                        'saved_model_filename': os.path.basename(metadata.get('model_path', '')),
                        'training_metadata': metadata
                    })
                    training_set.learning_params = learning_params
                    training_set.save()
                    
                    print(f"✅ 训练完成！")
                    print(f"📁 模型文件路径: {metadata.get('model_path', '')}")
                    
                except Exception as e:
                    print(f"❌ 训练失败: {str(e)}")
                    training_set.training_status = 'failed'
                    training_set.status = 'failed'  # 同步status字段
                    training_set.save()
            
            # 启动后台训练线程
            train_thread = threading.Thread(target=train_in_background)
            train_thread.daemon = True
            train_thread.start()
            
        except Exception as e:
            print(f"❌ 启动训练进程失败: {str(e)}")
            training_set.training_status = 'failed'
            training_set.status = 'failed'  # 同步status字段
            training_set.save()
            return JsonResponse({
                'success': False,
                'message': f'启动训练失败: {str(e)}'
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'message': '训练已开始',
            'training_set_id': training_set_id
        })
        
    except Exception as e:
        logger.error(f"从训练集开始训练失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'从训练集开始训练失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_training_set_info(request):
    """
    获取训练集信息API
    """
    try:
        training_set_id = request.GET.get('training_set_id')
        
        if not training_set_id:
            return JsonResponse({
                'success': False,
                'message': '请提供训练集ID'
            }, status=400)
        
        # 检查用户登录状态
        user_email = request.session.get('user_email', '')
        if not user_email:
            return JsonResponse({
                'success': False,
                'message': '用户未登录'
            }, status=401)
        
        # 导入模型
        from .models import TrainingSet
        
        try:
            training_set = TrainingSet.objects.get(
                training_set_id=training_set_id,
                user_email=user_email
            )
        except TrainingSet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '训练集不存在'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'training_set': {
                'training_set_id': training_set.training_set_id,
                'name': training_set.name,
                'description': training_set.description,
                'model_type': training_set.model_type,
                'training_mode': training_set.training_mode,
                'current_epoch': training_set.current_epoch,
                'total_epochs': training_set.total_epochs,
                'training_status': training_set.training_status,
                'start_time': training_set.start_time.isoformat() if training_set.start_time else None,
                'learning_params': training_set.learning_params
            }
        })
        
    except Exception as e:
        logger.error(f"获取训练集信息失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'获取训练集信息失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def predict_data(request):
    """
    数据预测API
    """
    try:
        data = json.loads(request.body)
        model_path = data.get('model_path')
        input_data = data.get('input_data')
        
        if not model_path:
            return JsonResponse({
                'success': False,
                'message': '请提供模型路径'
            }, status=400)
        
        if not input_data:
            return JsonResponse({
                'success': False,
                'message': '请提供输入数据'
            }, status=400)
        
        # TODO: 实现实际的预测逻辑
        # 这里应该包含：
        # 1. 加载模型
        # 2. 预处理输入数据
        # 3. 进行预测
        # 4. 返回预测结果
        
        # 模拟预测结果
        prediction_result = {
            'predicted_values': [0.1, 0.2, 0.3, 0.4, 0.5],
            'confidence': 0.85,
            'prediction_time': time.time()
        }
        
        return JsonResponse({
            'success': True,
            'prediction': prediction_result
        })
        
    except Exception as e:
        logger.error(f"数据预测失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'数据预测失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_model_info(request):
    """
    获取模型信息API
    """
    try:
        model_path = request.GET.get('model_path')
        
        if not model_path:
            return JsonResponse({
                'success': False,
                'message': '请提供模型路径'
            }, status=400)
        
        # TODO: 实现获取模型信息的逻辑
        # 这里应该包含：
        # 1. 检查模型文件是否存在
        # 2. 读取模型元数据
        # 3. 返回模型信息
        
        # 模拟模型信息
        model_info = {
            'model_name': 'LSTM_Model_v1',
            'model_type': 'lstm',
            'input_shape': [24, 3],
            'output_shape': [12, 3],
            'parameters': 50000,
            'created_at': '2024-01-15T10:30:00',
            'accuracy': 0.85,
            'file_size_mb': 2.5
        }
        
        return JsonResponse({
            'success': True,
            'model_info': model_info
        })
        
    except Exception as e:
        logger.error(f"获取模型信息失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'获取模型信息失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_available_channels(request):
    """
    获取可用通道API
    """
    try:
        # 检查用户登录状态
        user_email = request.session.get('user_email', '')
        if not user_email:
            return JsonResponse({
                'success': False,
                'message': '用户未登录'
            }, status=401)
        
        # 导入模型
        from .models import MonitorTask
        
        # 获取用户的所有监控任务
        tasks = MonitorTask.objects.filter(
            user_email=user_email,
            is_completed=True,
            is_deleted=False
        )
        
        # 收集所有可用的通道
        available_channels = set()
        for task in tasks:
            if task.enabled_channels:
                for channel in task.enabled_channels:
                    available_channels.add(channel)
        
        return JsonResponse({
            'success': True,
            'channels': list(available_channels)
        })
        
    except Exception as e:
        logger.error(f"获取可用通道失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'获取可用通道失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_recent_data(request):
    """
    获取最近数据API
    """
    try:
        # 检查用户登录状态
        user_email = request.session.get('user_email', '')
        if not user_email:
            return JsonResponse({
                'success': False,
                'message': '用户未登录'
            }, status=401)
        
        # 导入模型
        from .models import MonitorTask
        
        # 获取用户最近的监控任务
        recent_tasks = MonitorTask.objects.filter(
            user_email=user_email,
            is_completed=True,
            is_deleted=False
        ).order_by('-created_at')[:5]
        
        recent_data = []
        for task in recent_tasks:
            recent_data.append({
                'task_id': task.task_id,
                'task_name': task.task_name,
                'created_at': task.created_at.isoformat(),
                'file_size_mb': task.file_size_mb,
                'total_data_points': task.total_data_points,
                'enabled_channels': task.enabled_channels
            })
        
        return JsonResponse({
            'success': True,
            'recent_data': recent_data
        })
        
    except Exception as e:
        logger.error(f"获取最近数据失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'获取最近数据失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def delete_model(request):
    """
    删除模型API
    """
    try:
        data = json.loads(request.body)
        model_path = data.get('model_path')
        
        if not model_path:
            return JsonResponse({
                'success': False,
                'message': '请提供模型路径'
            }, status=400)
        
        # 检查用户登录状态
        user_email = request.session.get('user_email', '')
        if not user_email:
            return JsonResponse({
                'success': False,
                'message': '用户未登录'
            }, status=401)
        
        # TODO: 实现删除模型的逻辑
        # 这里应该包含：
        # 1. 验证模型文件是否存在
        # 2. 检查用户权限
        # 3. 删除模型文件
        # 4. 更新数据库记录
        
        # 模拟删除成功
        return JsonResponse({
            'success': True,
            'message': '模型删除成功'
        })
        
    except Exception as e:
        logger.error(f"删除模型失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'删除模型失败: {str(e)}'
        }, status=500) 

@csrf_exempt
@require_http_methods(["GET"])
def get_training_status_info(request, training_set_id):
    """
    获取训练状态信息API
    用于前端检查训练状态并显示相应的提示信息
    """
    try:
        # 检查用户登录状态
        user_email = request.session.get('user_email', '')
        if not user_email:
            return JsonResponse({
                'success': False,
                'message': '用户未登录'
            }, status=401)
        
        # 导入模型
        from .models import TrainingSet
        
        try:
            training_set = TrainingSet.objects.get(
                training_set_id=training_set_id,
                user_email=user_email
            )
        except TrainingSet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '训练集不存在'
            }, status=404)
        
        # 根据状态返回相应的信息
        status = training_set.training_status
        status_info = {
            'status': status,
            'training_set_name': training_set.name,
            'current_epoch': training_set.current_epoch,
            'total_epochs': training_set.total_epochs,
            'action': None,
            'message': None
        }
        
        if status in ['training', 'paused']:
            status_info['action'] = 'open_monitor'
            status_info['message'] = f"检测到训练集 '{training_set.name}' 正在训练中，正在打开监控界面..."
        elif status in ['failed', 'stopped']:
            status_info['action'] = 'ask_restart'
            status_messages = {
                'failed': '上次训练失败',
                'stopped': '上次训练已被停止'
            }
            status_info['message'] = f"{status_messages[status]}，是否重新开始训练？"
        elif status == 'completed':
            status_info['action'] = 'completed'
            status_info['message'] = f"训练集 '{training_set.name}' 已完成训练"
        elif status in ['pending', 'created']:
            status_info['action'] = 'start_new'
            status_info['message'] = '可以开始新训练'
        else:
            status_info['action'] = 'unknown'
            status_info['message'] = f'未知的训练状态: {status}'
        
        return JsonResponse({
            'success': True,
            'status_info': status_info
        })
        
    except Exception as e:
        logger.error(f"获取训练状态信息失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'获取训练状态信息失败: {str(e)}'
        }, status=500) 