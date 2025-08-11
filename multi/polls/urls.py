from django.urls import path

from . import views
from . import deep_learning_views
urlpatterns = [
    # 登录注册相关路由
    path('', views.toLogin_view, name='toLogin'),
    path('index/', views.Login0, name='Login0'),
    path('toRegister/', views.toRegister_view, name='toRegister'),
    path('Register/', views.Register_view, name='Register'),

    # 主页面路由（登录后访问）
    path('home/', views.home_view, name='home'),

    # 核心功能模块路由
    path('signal-acquisition/', views.all_acquire, name='all_acquire'),  # 信号采集模块主页面
    path('multi-channel-acquisition/', views.signal_acquisition, name='signal_acquisition'),  # 多通道传感采集
    path('monitor/', views.monitor, name='monitor'),  # 信号数据监控
    path('pointer/', views.pointer, name='pointer'),  # 指针信号收集
    #path('time-frequency-analysis/', views.time_frequency_analysis, name='time_frequency_analysis'),
    #由于功能需要升级，但是为了测验不能剔除原本的程序，所以在这里简单注解，最后home.html复原即可
    path('signal_analysis_dashboard/', views.signal_analysis_dashboard, name='signal_analysis_dashboard'),
    path('deep-learning/', views.deep_learning, name='deep_learning'),
    path('device-management/', views.device_management, name='device_management'),

    # 三大应用场景路由
    path('signal-analysis/', views.signal_analysis, name='signal_analysis'),
    path('power-signal/', views.power_signal, name='power_signal'),
    path('pointer-detection/', views.pointer_detection, name='pointer_detection'),
    path('system-integration/', views.system_integration, name='system_integration'),
    # API路由
    path('api/upload-data/', views.upload_data_file, name='upload_data_file'),
    path('api/perform-fft/', views.perform_fft, name='perform_fft'),
    path('api/perform-transform/', views.perform_transform, name='perform_transform'),
    path('api/calculate-time-features/', views.calculate_time_features, name='calculate_time_features'),
    path('api/time-average/', views.time_average_processing, name='time_average_processing'),
    
    # 监控数据管理API
    path('api/save-monitor-data/', views.save_monitor_data, name='save_monitor_data'),
    path('api/get-monitor-tasks/', views.get_monitor_tasks, name='get_monitor_tasks'),
    path('api/delete-monitor-task/<str:task_id>/', views.delete_monitor_task, name='delete_monitor_task'),
    
    # 深度学习模块API
    path('api/get-monitor-data-for-dl/', views.get_monitor_data_for_dl, name='get_monitor_data_for_dl'),
    path('api/create-dataset/', views.create_dataset, name='create_dataset'),
    path('api/start-training/', views.start_training, name='start_training'),
    path('api/get-training-status/', views.get_training_status, name='get_training_status'),
    path('api/start-prediction/', views.start_prediction, name='start_prediction'),
    path('api/get-trained-models/', views.get_trained_models, name='get_trained_models'),
    
    # 新的深度学习API
    path('deep-learning-dashboard/', deep_learning_views.deep_learning_dashboard, name='deep_learning_dashboard'),
    path('api/start-model-training/', deep_learning_views.start_training, name='start_model_training'),
    path('api/start-training-from-set/', deep_learning_views.start_training_from_training_set, name='start_training_from_set'),
    path('api/get-training-status-info/<str:training_set_id>/', deep_learning_views.get_training_status_info, name='get_training_status_info'),
    path('api/get-training-set-info/', deep_learning_views.get_training_set_info, name='get_training_set_info'),
    path('api/predict-data/', deep_learning_views.predict_data, name='predict_data'),
    path('api/get-model-info/', deep_learning_views.get_model_info, name='get_model_info'),
    path('api/get-available-channels/', deep_learning_views.get_available_channels, name='get_available_channels'),
    path('api/get-recent-data/', deep_learning_views.get_recent_data, name='get_recent_data'),
    path('api/delete-model/<str:model_id>/', views.delete_saved_model, name='delete_saved_model'),
    
    # 新增训练集管理API
    path('api/create-training-set/', views.create_training_set, name='create_training_set'),
    path('api/get-training-sets/', views.get_training_sets, name='get_training_sets'),
    path('api/delete-training-set/<str:training_set_id>/', views.delete_training_set, name='delete_training_set'),

    path('api/get-completed-training/', views.get_completed_training, name='get_completed_training'),
    path('api/get-deployed-models/', views.get_deployed_models, name='get_deployed_models'),
    
    # 训练监控相关API
    path('api/get-training-set/<str:training_set_id>/', views.get_training_set, name='get_training_set'),
    path('api/training-status/<str:training_set_id>/', views.training_status, name='training_status'),
    path('api/pause-training/<str:training_set_id>/', views.pause_training, name='pause_training'),
    path('api/resume-training/<str:training_set_id>/', views.resume_training, name='resume_training'),
    path('api/stop-training/<str:training_set_id>/', views.stop_training, name='stop_training'),
    path('api/save-model/<str:training_set_id>/', views.save_model, name='save_model'),
    path('api/get-saved-models/', views.get_saved_models, name='get_saved_models'),
    path('api/get-test-evaluation/<str:training_set_id>/', views.get_test_evaluation, name='get_test_evaluation'),
    
    # 预测评估相关API
    path('prediction-evaluation/<str:training_set_id>/', views.prediction_evaluation, name='prediction_evaluation'),
    path('api/predict-evaluation/<str:training_set_id>/', views.predict_evaluation, name='predict_evaluation'),
    path('api/export-prediction-results/<str:training_set_id>/', views.export_prediction_results, name='export_prediction_results'),
    
    # 模型预测相关API
    path('model-prediction/<str:model_id>/', views.model_prediction, name='model_prediction'),
    path('api/get-saved-model/<str:model_id>/', views.get_saved_model, name='get_saved_model'),
    path('api/get-data-sources/', views.get_data_sources, name='get_data_sources'),
    path('api/delete-data-source/<str:task_id>/', views.delete_data_source, name='delete_data_source'),
    path('api/model-predict/<str:model_id>/', views.model_predict, name='model_predict'),
    path('api/export-model-prediction-results/<str:model_id>/', views.export_model_prediction_results, name='export_model_prediction_results'),
    
    # 训练监控页面
    path('training-monitor/', views.training_monitor, name='training_monitor'),
    
    #websocket测试
    path('daq/', views.daq_control_view, name='daq_control'),

    # 添加指针识别API路由
    path('api/camera/enable/', views.camera_enable, name='camera_enable'),
    path('api/camera/disable/', views.camera_disable, name='camera_disable'),
    path('api/camera/status/', views.camera_status, name='camera_status'),
    path('api/camera/image/', views.camera_image, name='camera_image'),
    path('api/camera/available/', views.get_available_cameras, name='get_available_cameras'),
    path('api/camera/update_parameters/', views.update_parameters, name='update_parameters'),
    path('api/camera/start_collection/', views.start_collection, name='start_collection'),
    path('api/camera/stop_collection/', views.stop_collection, name='stop_collection'),
    path('api/camera/collect_data/', views.collect_data, name='collect_data'),
]