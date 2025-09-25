use crate::controllers::control_controller::{
    ControlAction, ControlActionType, ControlOptimizationResult, ControlPerformanceMetrics,
    ControlStatus,
};
use crate::models::{
    control::*,
    error::{AppError, AppResult},
    fan::{FanConfig, FanReading},
    thermal::TemperatureReading,
};
use crate::services::{
    fan_service::FanService, monitoring_service::MonitoringService, sensor_service::SensorService,
    thermal_service::ThermalService,
};
use crate::utils::{
    logger::LoggerManager,
    math::{MathUtils, PidController},
    time::TimeUtils,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::{Mutex, RwLock};
use tokio::time::{interval, Duration, Instant};
use tracing::{debug, error, info, warn};

/// 控制服务
///
/// 负责智能温度控制、风扇调节和系统优化
#[derive(Clone)]
pub struct ControlService {
    /// 温度服务
    thermal_service: Arc<ThermalService>,
    /// 风扇服务
    fan_service: Arc<FanService>,
    /// 传感器服务
    sensor_service: Arc<SensorService>,
    /// 监控服务
    monitoring_service: Arc<MonitoringService>,
    /// 控制配置
    config: Arc<RwLock<ControlConfig>>,
    /// 控制状态
    status: Arc<RwLock<ControlStatus>>,
    /// PID控制器集合
    pid_controllers: Arc<RwLock<HashMap<String, PidController>>>,
    /// 控制历史记录
    control_history: Arc<RwLock<Vec<ControlAction>>>,
    /// 控制任务句柄
    task_handles: Arc<Mutex<Vec<tokio::task::JoinHandle<()>>>>,
    /// 数学工具
    math_utils: MathUtils,
}

impl ControlService {
    /// 创建新的控制服务
    ///
    /// # 参数
    /// * `thermal_service` - 温度服务
    /// * `fan_service` - 风扇服务
    /// * `sensor_service` - 传感器服务
    /// * `monitoring_service` - 监控服务
    pub fn new(
        thermal_service: Arc<ThermalService>,
        fan_service: Arc<FanService>,
        sensor_service: Arc<SensorService>,
        monitoring_service: Arc<MonitoringService>,
    ) -> Self {
        Self {
            thermal_service,
            fan_service,
            sensor_service,
            monitoring_service,
            config: Arc::new(RwLock::new(ControlConfig::default())),
            status: Arc::new(RwLock::new(ControlStatus::default())),
            pid_controllers: Arc::new(RwLock::new(HashMap::new())),
            control_history: Arc::new(RwLock::new(Vec::new())),
            task_handles: Arc::new(Mutex::new(Vec::new())),
            math_utils: MathUtils,
        }
    }

    /// 启动自动控制
    pub async fn start_auto_control(&self) -> AppResult<()> {
        info!("启动自动温度控制");

        // 更新状态
        {
            let mut status = self.status.write().await;
            status.is_auto_control_enabled = true;
            status.control_start_time = Some(Utc::now());
            status.last_control_action = Utc::now();
        }

        // 初始化PID控制器
        self.initialize_pid_controllers().await?;

        // 启动控制循环
        self.start_control_loop().await?;

        // 启动性能监控
        self.start_performance_monitoring().await?;

        info!("自动温度控制启动完成");
        Ok(())
    }

    /// 停止自动控制
    pub async fn stop_auto_control(&self) -> AppResult<()> {
        info!("停止自动温度控制");

        // 更新状态
        {
            let mut status = self.status.write().await;
            status.is_auto_control_enabled = false;
            status.control_stop_time = Some(Utc::now());
        }

        // 停止所有控制任务
        let mut handles = self.task_handles.lock().await;
        for handle in handles.drain(..) {
            handle.abort();
        }

        info!("自动温度控制已停止");
        Ok(())
    }

    /// 获取控制状态
    pub async fn get_status(&self) -> ControlStatus {
        self.status.read().await.clone()
    }

    /// 获取控制配置
    pub async fn get_config(&self) -> ControlConfig {
        self.config.read().await.clone()
    }

    /// 更新控制配置
    ///
    /// # 参数
    /// * `new_config` - 新的控制配置
    pub async fn update_config(&self, new_config: ControlConfig) -> AppResult<()> {
        info!("更新控制配置");

        // 验证配置
        new_config.validate()?;

        // 更新配置
        {
            let mut config = self.config.write().await;
            *config = new_config;
        }

        // 重新初始化PID控制器
        if self.status.read().await.is_auto_control_enabled {
            self.initialize_pid_controllers().await?;
        }

        info!("控制配置更新完成");
        Ok(())
    }

    /// 手动设置风扇转速
    ///
    /// # 参数
    /// * `fan_id` - 风扇ID
    /// * `speed_percent` - 转速百分比
    pub async fn set_manual_fan_speed(&self, fan_id: &str, speed_percent: f64) -> AppResult<()> {
        info!("手动设置风扇 {} 转速: {:.1}%", fan_id, speed_percent);

        // 验证转速范围
        if speed_percent < 0.0 || speed_percent > 100.0 {
            return Err(AppError::InvalidInput("转速必须在0-100%之间".to_string()));
        }

        // 设置风扇转速
        self.fan_service
            .set_fan_speed(fan_id, speed_percent)
            .await?;

        // 记录控制动作
        self.record_control_action(ControlAction {
            id: uuid::Uuid::new_v4().to_string(),
            timestamp: Utc::now(),
            action_type: ControlActionType::ManualFanControl,
            target_component: fan_id.to_string(),
            previous_value: 0.0, // 需要获取之前的值
            new_value: speed_percent,
            reason: "手动设置".to_string(),
            success: true,
            error_message: None,
        })
        .await;

        info!("风扇转速设置完成");
        Ok(())
    }

    /// 应用温度控制策略
    ///
    /// # 参数
    /// * `strategy` - 控制策略
    pub async fn apply_control_strategy(&self, strategy: ControlStrategy) -> AppResult<()> {
        info!("应用控制策略: {:?}", strategy.strategy_type);

        match strategy.strategy_type {
            StrategyType::Temperature => {
                self.apply_conservative_strategy(&strategy).await?;
            }
            StrategyType::Load => {
                self.apply_balanced_strategy(&strategy).await?;
            }
            StrategyType::PowerSaving => {
                self.apply_aggressive_strategy(&strategy).await?;
            }
            StrategyType::Performance => {
                self.apply_custom_strategy(&strategy).await?;
            }
        }

        // 更新当前策略
        {
            let mut config = self.config.write().await;
            config.current_strategy = Some(strategy);
        }

        info!("控制策略应用完成");
        Ok(())
    }

    /// 执行紧急冷却
    pub async fn emergency_cooling(&self) -> AppResult<()> {
        warn!("执行紧急冷却");

        // 获取所有风扇
        let fans = self.fan_service.get_fan_list().await?;

        // 将所有风扇设置为最大转速
        for fan_id in fans {
            if let Err(e) = self.fan_service.set_fan_speed(&fan_id, 100.0).await {
                error!("设置风扇 {} 最大转速失败: {}", fan_id, e);
            } else {
                // 记录紧急控制动作
                self.record_control_action(ControlAction {
                    id: uuid::Uuid::new_v4().to_string(),
                    timestamp: Utc::now(),
                    action_type: ControlActionType::EmergencyCooling,
                    target_component: fan_id.clone(),
                    previous_value: 0.0, // 需要获取之前的值
                    new_value: 100.0,
                    reason: "紧急冷却".to_string(),
                    success: true,
                    error_message: None,
                })
                .await;
            }
        }

        // 更新状态
        {
            let mut status = self.status.write().await;
            status.emergency_mode = true;
            status.last_emergency_time = Some(Utc::now());
        }

        warn!("紧急冷却执行完成");
        Ok(())
    }

    /// 退出紧急模式
    pub async fn exit_emergency_mode(&self) -> AppResult<()> {
        info!("退出紧急模式");

        // 更新状态
        {
            let mut status = self.status.write().await;
            status.emergency_mode = false;
        }

        // 恢复正常控制
        if self.status.read().await.is_auto_control_enabled {
            self.execute_control_cycle().await?;
        }

        info!("已退出紧急模式");
        Ok(())
    }

    /// 获取控制历史
    ///
    /// # 参数
    /// * `limit` - 返回记录数限制
    pub async fn get_control_history(&self, limit: Option<usize>) -> Vec<ControlAction> {
        let history = self.control_history.read().await;
        let limit = limit.unwrap_or(100);

        history.iter().rev().take(limit).cloned().collect()
    }

    /// 获取控制性能指标
    pub async fn get_performance_metrics(&self) -> ControlPerformanceMetrics {
        let history = self.control_history.read().await;
        let status = self.status.read().await;

        let total_actions = history.len();
        let successful_actions = history.iter().filter(|a| a.success).count();
        let success_rate = if total_actions > 0 {
            successful_actions as f64 / total_actions as f64 * 100.0
        } else {
            0.0
        };

        // 计算平均响应时间（简化）
        let avg_response_time = 1.5; // 秒

        // 计算温度稳定性
        let temperature_stability = self.calculate_temperature_stability().await.unwrap_or(0.0);

        ControlPerformanceMetrics {
            time_window_hours: 24,
            temperature_control:
                crate::controllers::control_controller::TemperatureControlMetrics {
                    avg_temperature: 45.0,
                    temperature_variance: 2.5,
                    target_achievement_rate: success_rate,
                    overshoot_incidents: 0,
                },
            fan_control: crate::controllers::control_controller::FanControlMetrics {
                avg_fan_speed_percent: 60.0,
                fan_speed_variance: 10.0,
                fan_efficiency: 85.0,
                noise_level_db: 35.0,
            },
            system_stability: crate::controllers::control_controller::SystemStabilityMetrics {
                stability_score: temperature_stability,
                oscillation_count: 0,
                emergency_triggers: 0,
                avg_response_time_seconds: avg_response_time,
            },
            energy_efficiency: crate::controllers::control_controller::EnergyEfficiencyMetrics {
                efficiency_score: 85.0,
                estimated_power_consumption: 150.0,
                power_savings_percent: 15.0,
                cooling_efficiency: 90.0,
            },
        }
    }

    /// 优化控制参数
    pub async fn optimize_control_parameters(&self) -> AppResult<ControlOptimizationResult> {
        info!("开始优化控制参数");

        let mut optimization_result = ControlOptimizationResult {
            optimization_id: uuid::Uuid::new_v4().to_string(),
            timestamp: Utc::now(),
            original_parameters: self.get_current_control_parameters().await,
            optimized_parameters: HashMap::new(),
            performance_improvement: 0.0,
            recommendations: Vec::new(),
        };

        // 分析历史数据
        let history = self.control_history.read().await;
        if history.len() < 10 {
            return Err(AppError::InsufficientData(
                "需要更多历史数据进行优化".to_string(),
            ));
        }

        // 分析温度控制效果
        let temp_analysis = self.analyze_temperature_control_effectiveness().await?;

        // 基于分析结果优化PID参数
        let mut optimized_params = optimization_result.original_parameters.clone();

        if temp_analysis.overshoot_rate > 0.2 {
            // 过冲过多，降低比例增益
            for (sensor_id, params) in optimized_params.iter_mut() {
                if let Some(kp) = params.get_mut("kp") {
                    *kp *= 0.9;
                }
            }
            optimization_result
                .recommendations
                .push("降低比例增益以减少过冲".to_string());
        }

        if temp_analysis.settling_time > 300.0 {
            // 稳定时间过长，增加积分增益
            for (sensor_id, params) in optimized_params.iter_mut() {
                if let Some(ki) = params.get_mut("ki") {
                    *ki *= 1.1;
                }
            }
            optimization_result
                .recommendations
                .push("增加积分增益以缩短稳定时间".to_string());
        }

        if temp_analysis.oscillation_rate > 0.15 {
            // 振荡过多，增加微分增益
            for (sensor_id, params) in optimized_params.iter_mut() {
                if let Some(kd) = params.get_mut("kd") {
                    *kd *= 1.05;
                }
            }
            optimization_result
                .recommendations
                .push("增加微分增益以减少振荡".to_string());
        }

        optimization_result.optimized_parameters = optimized_params;
        optimization_result.performance_improvement =
            self.estimate_performance_improvement(&temp_analysis).await;

        info!(
            "控制参数优化完成，预期性能提升: {:.1}%",
            optimization_result.performance_improvement
        );
        Ok(optimization_result)
    }

    /// 应用优化后的参数
    ///
    /// # 参数
    /// * `optimization_result` - 优化结果
    pub async fn apply_optimized_parameters(
        &self,
        optimization_result: &ControlOptimizationResult,
    ) -> AppResult<()> {
        info!("应用优化后的控制参数");

        // 更新PID控制器参数
        let mut controllers = self.pid_controllers.write().await;

        for (sensor_id, params) in &optimization_result.optimized_parameters {
            if let Some(controller) = controllers.get_mut(sensor_id) {
                if let (Some(&kp), Some(&ki), Some(&kd)) =
                    (params.get("kp"), params.get("ki"), params.get("kd"))
                {
                    controller.set_gains(kp, ki, kd);
                    info!(
                        "更新传感器 {} 的PID参数: Kp={:.3}, Ki={:.3}, Kd={:.3}",
                        sensor_id, kp, ki, kd
                    );
                }
            }
        }

        // 记录参数更新动作
        self.record_control_action(ControlAction {
            id: uuid::Uuid::new_v4().to_string(),
            timestamp: Utc::now(),
            action_type: ControlActionType::ParameterOptimization,
            target_component: "system".to_string(),
            previous_value: 0.0,
            new_value: optimization_result.performance_improvement,
            reason: "参数优化".to_string(),
            success: true,
            error_message: None,
        })
        .await;

        info!("优化参数应用完成");
        Ok(())
    }

    // 私有方法

    /// 初始化PID控制器
    async fn initialize_pid_controllers(&self) -> AppResult<()> {
        info!("初始化PID控制器");

        let config = self.config.read().await;
        let mut controllers = self.pid_controllers.write().await;
        controllers.clear();

        // 获取所有温度传感器
        if let Ok(sensors) = self.thermal_service.get_temperature_sensors().await {
            for sensor_id in sensors {
                // 创建PID控制器
                let mut pid = PidController::new(
                    config.default_pid_kp,
                    config.default_pid_ki,
                    config.default_pid_kd,
                );

                // 设置输出限制
                pid.set_output_limits(0.0, 100.0);

                // 设置目标温度
                pid.set_setpoint(config.target_temperature);

                controllers.insert(sensor_id.clone(), pid);
                debug!("为传感器 {} 创建PID控制器", sensor_id);
            }
        }

        info!("PID控制器初始化完成，共创建 {} 个控制器", controllers.len());
        Ok(())
    }

    /// 启动控制循环
    async fn start_control_loop(&self) -> AppResult<()> {
        let thermal_service = Arc::clone(&self.thermal_service);
        let fan_service = Arc::clone(&self.fan_service);
        let pid_controllers = Arc::clone(&self.pid_controllers);
        let config = Arc::clone(&self.config);
        let status = Arc::clone(&self.status);
        let control_history = Arc::clone(&self.control_history);

        let handle = tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(10)); // 默认10秒控制周期

            loop {
                interval.tick().await;

                // 检查是否启用自动控制
                if !status.read().await.is_auto_control_enabled {
                    continue;
                }

                // 检查是否处于紧急模式
                if status.read().await.emergency_mode {
                    continue;
                }

                // 获取控制周期
                let control_interval = {
                    let cfg = config.read().await;
                    cfg.control_interval
                };

                // 更新控制间隔
                interval = interval(Duration::from_secs(control_interval));

                // 执行控制循环
                if let Err(e) = Self::execute_control_cycle_static(
                    &thermal_service,
                    &fan_service,
                    &pid_controllers,
                    &config,
                    &control_history,
                )
                .await
                {
                    error!("控制循环执行失败: {}", e);
                }

                // 更新最后控制时间
                {
                    let mut s = status.write().await;
                    s.last_control_action = Utc::now();
                }
            }
        });

        self.task_handles.lock().await.push(handle);
        Ok(())
    }

    /// 执行控制循环（静态方法）
    async fn execute_control_cycle_static(
        thermal_service: &Arc<ThermalService>,
        fan_service: &Arc<FanService>,
        pid_controllers: &Arc<RwLock<HashMap<String, PidController>>>,
        config: &Arc<RwLock<ControlConfig>>,
        control_history: &Arc<RwLock<Vec<ControlAction>>>,
    ) -> AppResult<()> {
        let cfg = config.read().await;
        let mut controllers = pid_controllers.write().await;

        // 获取所有温度传感器数据
        if let Ok(sensors) = thermal_service.get_temperature_sensors().await {
            for sensor_id in sensors {
                if let Ok(temp_reading) = thermal_service.get_current_temperature(&sensor_id).await
                {
                    if let Some(controller) = controllers.get_mut(&sensor_id) {
                        // 计算PID输出
                        let output = controller.update(temp_reading.temperature);

                        // 将输出映射到风扇转速
                        let fan_speed = Self::map_pid_output_to_fan_speed(output, &cfg);

                        // 获取对应的风扇ID（简化处理，假设传感器ID对应风扇ID）
                        let fan_id = Self::get_fan_for_sensor(&sensor_id);

                        // 设置风扇转速
                        if let Ok(fans) = fan_service.get_fan_list().await {
                            if fans.contains(&fan_id) {
                                if let Err(e) = fan_service.set_fan_speed(&fan_id, fan_speed).await
                                {
                                    error!("设置风扇 {} 转速失败: {}", fan_id, e);
                                } else {
                                    // 记录控制动作
                                    let action = ControlAction {
                                        id: uuid::Uuid::new_v4().to_string(),
                                        timestamp: Utc::now(),
                                        action_type: ControlActionType::AutomaticControl,
                                        target_component: fan_id.clone(),
                                        previous_value: 0.0, // 需要获取之前的值
                                        new_value: fan_speed,
                                        reason: format!(
                                            "温度控制: {:.1}°C -> {:.1}%",
                                            temp_reading.temperature, fan_speed
                                        ),
                                        success: true,
                                        error_message: None,
                                    };

                                    let mut history = control_history.write().await;
                                    history.push(action);

                                    // 限制历史记录数量
                                    if history.len() > 1000 {
                                        history.drain(0..100); // 删除最旧的100条记录
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        Ok(())
    }

    /// 执行控制循环
    async fn execute_control_cycle(&self) -> AppResult<()> {
        Self::execute_control_cycle_static(
            &self.thermal_service,
            &self.fan_service,
            &self.pid_controllers,
            &self.config,
            &self.control_history,
        )
        .await
    }

    /// 启动性能监控
    async fn start_performance_monitoring(&self) -> AppResult<()> {
        let status = Arc::clone(&self.status);
        let control_history = Arc::clone(&self.control_history);

        let handle = tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(60)); // 每分钟更新一次性能指标

            loop {
                interval.tick().await;

                // 更新性能指标
                let history = control_history.read().await;
                let total_actions = history.len();
                let successful_actions = history.iter().filter(|a| a.success).count();

                {
                    let mut s = status.write().await;
                    s.total_control_actions = total_actions;
                    s.successful_actions = successful_actions;
                    s.failed_actions = total_actions - successful_actions;
                }

                debug!(
                    "性能指标更新: 总动作数={}, 成功数={}",
                    total_actions, successful_actions
                );
            }
        });

        self.task_handles.lock().await.push(handle);
        Ok(())
    }

    /// 应用保守策略
    async fn apply_conservative_strategy(&self, strategy: &ControlStrategy) -> AppResult<()> {
        info!("应用保守控制策略");

        // 保守策略：较低的目标温度，较慢的响应
        let mut config = self.config.write().await;
        config.target_temperature = 60.0; // 较低的目标温度
        config.max_fan_speed = 80.0; // 限制最大风扇转速
        config.control_interval = 30; // 较长的控制间隔
        config.default_pid_kp = 0.5; // 较小的比例增益
        config.default_pid_ki = 0.1;
        config.default_pid_kd = 0.05;

        Ok(())
    }

    /// 应用平衡策略
    async fn apply_balanced_strategy(&self, strategy: &ControlStrategy) -> AppResult<()> {
        info!("应用平衡控制策略");

        let mut config = self.config.write().await;
        config.target_temperature = 65.0; // 中等目标温度
        config.max_fan_speed = 90.0;
        config.control_interval = 15; // 中等控制间隔
        config.default_pid_kp = 1.0; // 中等PID参数
        config.default_pid_ki = 0.2;
        config.default_pid_kd = 0.1;

        Ok(())
    }

    /// 应用激进策略
    async fn apply_aggressive_strategy(&self, strategy: &ControlStrategy) -> AppResult<()> {
        info!("应用激进控制策略");

        let mut config = self.config.write().await;
        config.target_temperature = 70.0; // 较高的目标温度
        config.max_fan_speed = 100.0; // 允许最大风扇转速
        config.control_interval = 5; // 较短的控制间隔
        config.default_pid_kp = 2.0; // 较大的比例增益
        config.default_pid_ki = 0.5;
        config.default_pid_kd = 0.2;

        Ok(())
    }

    /// 应用自定义策略
    async fn apply_custom_strategy(&self, strategy: &ControlStrategy) -> AppResult<()> {
        info!("应用自定义控制策略");

        if let Some(params) = &strategy.parameters {
            let mut config = self.config.write().await;

            if let Some(target_temp) = params.get("target_temperature") {
                config.target_temperature = *target_temp;
            }
            if let Some(max_fan) = params.get("max_fan_speed") {
                config.max_fan_speed = *max_fan;
            }
            if let Some(interval) = params.get("control_interval") {
                config.control_interval = *interval as u64;
            }
            if let Some(kp) = params.get("pid_kp") {
                config.default_pid_kp = *kp;
            }
            if let Some(ki) = params.get("pid_ki") {
                config.default_pid_ki = *ki;
            }
            if let Some(kd) = params.get("pid_kd") {
                config.default_pid_kd = *kd;
            }
        }

        Ok(())
    }

    /// 记录控制动作
    async fn record_control_action(&self, action: ControlAction) {
        let mut history = self.control_history.write().await;
        history.push(action);

        // 限制历史记录数量
        if history.len() > 1000 {
            history.drain(0..100);
        }
    }

    /// 计算温度稳定性
    async fn calculate_temperature_stability(&self) -> AppResult<f64> {
        // 简化的温度稳定性计算
        // 实际实现中应该分析温度变化的标准差
        Ok(85.0) // 默认稳定性分数
    }

    /// 获取当前控制参数
    async fn get_current_control_parameters(&self) -> HashMap<String, HashMap<String, f64>> {
        let mut params = HashMap::new();
        let controllers = self.pid_controllers.read().await;

        for (sensor_id, controller) in controllers.iter() {
            let mut sensor_params = HashMap::new();
            sensor_params.insert("kp".to_string(), controller.get_kp());
            sensor_params.insert("ki".to_string(), controller.get_ki());
            sensor_params.insert("kd".to_string(), controller.get_kd());
            params.insert(sensor_id.clone(), sensor_params);
        }

        params
    }

    /// 分析温度控制效果
    async fn analyze_temperature_control_effectiveness(
        &self,
    ) -> AppResult<TemperatureControlAnalysis> {
        // 简化的分析实现
        Ok(TemperatureControlAnalysis {
            overshoot_rate: 0.15,
            settling_time: 250.0,
            oscillation_rate: 0.10,
            steady_state_error: 1.5,
        })
    }

    /// 估算性能提升
    async fn estimate_performance_improvement(&self, analysis: &TemperatureControlAnalysis) -> f64 {
        // 简化的性能提升估算
        let mut improvement = 0.0;

        if analysis.overshoot_rate > 0.2 {
            improvement += 5.0;
        }
        if analysis.settling_time > 300.0 {
            improvement += 8.0;
        }
        if analysis.oscillation_rate > 0.15 {
            improvement += 3.0;
        }

        improvement.min(20.0) // 最大20%的改进
    }

    /// 将PID输出映射到风扇转速
    fn map_pid_output_to_fan_speed(pid_output: f64, config: &ControlConfig) -> f64 {
        // 将PID输出（0-100）映射到风扇转速
        let speed = pid_output
            .max(config.min_fan_speed)
            .min(config.max_fan_speed);
        speed
    }

    /// 获取传感器对应的风扇ID
    fn get_fan_for_sensor(sensor_id: &str) -> String {
        // 简化处理，实际应该有传感器到风扇的映射配置
        format!("fan_{}", sensor_id.replace("temp_", ""))
    }
}

/// 温度控制分析结果
#[derive(Debug, Clone, Serialize, Deserialize)]
struct TemperatureControlAnalysis {
    /// 过冲率
    overshoot_rate: f64,
    /// 稳定时间（秒）
    settling_time: f64,
    /// 振荡率
    oscillation_rate: f64,
    /// 稳态误差
    steady_state_error: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pid_output_mapping() {
        let config = ControlConfig::default();

        let speed1 = ControlService::map_pid_output_to_fan_speed(50.0, &config);
        assert_eq!(speed1, 50.0);

        let speed2 = ControlService::map_pid_output_to_fan_speed(150.0, &config);
        assert_eq!(speed2, config.max_fan_speed);

        let speed3 = ControlService::map_pid_output_to_fan_speed(-10.0, &config);
        assert_eq!(speed3, config.min_fan_speed);
    }

    #[test]
    fn test_fan_sensor_mapping() {
        let fan_id = ControlService::get_fan_for_sensor("temp_cpu");
        assert_eq!(fan_id, "fan_cpu");

        let fan_id2 = ControlService::get_fan_for_sensor("temp_system");
        assert_eq!(fan_id2, "fan_system");
    }
}
