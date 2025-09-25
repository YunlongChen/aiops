use crate::models::{
    analytics::*,
    thermal::{TemperatureReading, TemperatureStats},
    fan::{FanReading, FanStats},
    sensor::{SensorReading, SensorStats},
    error::{AppError, AppResult},
};
use crate::utils::{
    math::MathUtils,
    time::TimeUtils,
};
use crate::services::{
    thermal_service::ThermalService,
    fan_service::FanService,
    sensor_service::SensorService,
};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use chrono::{DateTime, Utc, Duration};
use serde::{Deserialize, Serialize};

/// 分析服务
/// 
/// 负责数据分析、趋势预测和性能优化
#[derive(Clone)]
pub struct AnalyticsService {
    /// 温度服务
    thermal_service: Arc<ThermalService>,
    /// 风扇服务
    fan_service: Arc<FanService>,
    /// 传感器服务
    sensor_service: Arc<SensorService>,
    /// 分析结果缓存
    analysis_cache: Arc<RwLock<HashMap<String, AnalyticsResult>>>,
    /// 数学工具
    math_utils: MathUtils,
}

impl AnalyticsService {
    /// 创建新的分析服务
    /// 
    /// # 参数
    /// * `thermal_service` - 温度服务
    /// * `fan_service` - 风扇服务
    /// * `sensor_service` - 传感器服务
    pub fn new(
        thermal_service: Arc<ThermalService>,
        fan_service: Arc<FanService>,
        sensor_service: Arc<SensorService>,
    ) -> Self {
        Self {
            thermal_service,
            fan_service,
            sensor_service,
            analysis_cache: Arc::new(RwLock::new(HashMap::new())),
            math_utils: MathUtils,
        }
    }

    /// 执行温度趋势分析
    /// 
    /// # 参数
    /// * `sensor_id` - 传感器ID
    /// * `duration_hours` - 分析时间范围（小时）
    pub async fn analyze_temperature_trend(&self, sensor_id: &str, duration_hours: u64) -> AppResult<AnalyticsResult> {
        let trend = self.thermal_service.get_temperature_trend(sensor_id, duration_hours).await?;
        let stats = self.thermal_service.get_temperature_stats(sensor_id, duration_hours).await?;

        // 分析趋势方向
        let trend_direction = if trend.slope > 0.1 {
            TrendDirection::Increasing
        } else if trend.slope < -0.1 {
            TrendDirection::Decreasing
        } else {
            TrendDirection::Stable
        };

        // 计算置信度
        let confidence = (trend.r_squared * 100.0).min(100.0).max(0.0);

        // 生成预测
        let predictions = trend.predictions.into_iter()
            .map(|(time, temp)| TemperaturePrediction {
                timestamp: time,
                predicted_temperature: temp,
                confidence_interval: (temp - 2.0, temp + 2.0), // 简化的置信区间
                probability: confidence / 100.0,
            })
            .collect();

        let analysis = TemperatureTrendAnalysis {
            sensor_id: sensor_id.to_string(),
            trend_direction,
            slope: trend.slope,
            confidence,
            predictions,
            analysis_period: Duration::hours(duration_hours as i64),
            recommendations: self.generate_temperature_recommendations(&trend, &stats).await,
        };

        let result = AnalyticsResult::new(
            AnalysisType::TemperatureTrend,
            serde_json::to_value(analysis)?,
        );

        // 缓存结果
        self.cache_result(format!("temp_trend_{}_{}", sensor_id, duration_hours), result.clone()).await;

        Ok(result)
    }

    /// 执行风扇效率分析
    /// 
    /// # 参数
    /// * `fan_id` - 风扇ID
    /// * `duration_hours` - 分析时间范围（小时）
    pub async fn analyze_fan_efficiency(&self, fan_id: &str, duration_hours: u64) -> AppResult<AnalyticsResult> {
        let fan_stats = self.fan_service.get_fan_stats(fan_id, duration_hours).await?;
        
        // 计算效率指标
        let efficiency_score = self.calculate_fan_efficiency_score(&fan_stats).await?;
        
        // 分析噪音水平
        let noise_level = self.estimate_noise_level(fan_stats.avg_speed_percent);
        
        // 找到最优转速点
        let optimal_speed = self.find_optimal_fan_speed(fan_id, duration_hours).await?;

        let analysis = FanEfficiencyAnalysis {
            fan_id: fan_id.to_string(),
            efficiency_score,
            noise_level,
            optimal_speed_point: optimal_speed,
            power_consumption_estimate: self.estimate_power_consumption(fan_stats.avg_speed_percent),
            recommendations: self.generate_fan_recommendations(&fan_stats, efficiency_score).await,
        };

        let result = AnalyticsResult::new(
            AnalysisType::FanEfficiency,
            serde_json::to_value(analysis)?,
        );

        // 缓存结果
        self.cache_result(format!("fan_efficiency_{}_{}", fan_id, duration_hours), result.clone()).await;

        Ok(result)
    }

    /// 执行异常检测
    /// 
    /// # 参数
    /// * `duration_hours` - 分析时间范围（小时）
    pub async fn detect_anomalies(&self, duration_hours: u64) -> AppResult<AnalyticsResult> {
        let mut detected_anomalies = Vec::new();

        // 检测温度异常
        let temp_sensors = self.thermal_service.get_temperature_sensors().await?;
        for sensor_id in temp_sensors {
            if let Ok(anomalies) = self.detect_temperature_anomalies(&sensor_id, duration_hours).await {
                detected_anomalies.extend(anomalies);
            }
        }

        // 检测风扇异常
        let fan_list = self.fan_service.get_fan_list().await?;
        for fan_id in fan_list {
            if let Ok(anomalies) = self.detect_fan_anomalies(&fan_id, duration_hours).await {
                detected_anomalies.extend(anomalies);
            }
        }

        // 检测传感器异常
        if let Ok(sensor_anomalies) = self.sensor_service.detect_sensor_anomalies().await {
            for sensor_anomaly in sensor_anomalies {
                let anomaly = DetectedAnomaly {
                    id: sensor_anomaly.id,
                    anomaly_type: match sensor_anomaly.anomaly_type {
                        crate::services::sensor_service::AnomalyType::Warning => AnomalyType::TemperatureSpike,
                        crate::services::sensor_service::AnomalyType::Critical => AnomalyType::SystemFailure,
                        _ => AnomalyType::DataInconsistency,
                    },
                    severity: match sensor_anomaly.severity {
                        crate::services::sensor_service::AnomalySeverity::Low => AnomalySeverity::Low,
                        crate::services::sensor_service::AnomalySeverity::Medium => AnomalySeverity::Medium,
                        crate::services::sensor_service::AnomalySeverity::High => AnomalySeverity::High,
                    },
                    description: sensor_anomaly.description,
                    affected_component: sensor_anomaly.sensor_id,
                    detection_time: sensor_anomaly.timestamp,
                    confidence: 0.85, // 默认置信度
                    recommended_action: "检查传感器状态和连接".to_string(),
                };
                detected_anomalies.push(anomaly);
            }
        }

        let analysis = AnomalyDetectionResult {
            total_anomalies: detected_anomalies.len(),
            high_severity_count: detected_anomalies.iter().filter(|a| a.severity == AnomalySeverity::High).count(),
            medium_severity_count: detected_anomalies.iter().filter(|a| a.severity == AnomalySeverity::Medium).count(),
            low_severity_count: detected_anomalies.iter().filter(|a| a.severity == AnomalySeverity::Low).count(),
            anomalies: detected_anomalies,
            analysis_period: Duration::hours(duration_hours as i64),
            detection_accuracy: 0.85, // 估计的检测准确率
        };

        let result = AnalyticsResult::new(
            AnalysisType::AnomalyDetection,
            serde_json::to_value(analysis)?,
        );

        // 缓存结果
        self.cache_result(format!("anomaly_detection_{}", duration_hours), result.clone()).await;

        Ok(result)
    }

    /// 计算性能指标
    /// 
    /// # 参数
    /// * `duration_hours` - 分析时间范围（小时）
    pub async fn calculate_performance_metrics(&self, duration_hours: u64) -> AppResult<AnalyticsResult> {
        let mut metrics = Vec::new();

        // 系统温度指标
        if let Ok(temp_sensors) = self.thermal_service.get_temperature_sensors().await {
            for sensor_id in temp_sensors {
                if let Ok(stats) = self.thermal_service.get_temperature_stats(&sensor_id, duration_hours).await {
                    metrics.push(PerformanceMetrics::new(
                        MetricType::Temperature,
                        sensor_id.clone(),
                        stats.avg_temperature,
                        Some(format!("平均温度: {:.1}°C, 最高: {:.1}°C", stats.avg_temperature, stats.max_temperature)),
                    ));
                }
            }
        }

        // 风扇性能指标
        if let Ok(fan_list) = self.fan_service.get_fan_list().await {
            for fan_id in fan_list {
                if let Ok(stats) = self.fan_service.get_fan_stats(&fan_id, duration_hours).await {
                    metrics.push(PerformanceMetrics::new(
                        MetricType::FanSpeed,
                        fan_id.clone(),
                        stats.avg_speed_percent,
                        Some(format!("平均转速: {:.1}%, 平均RPM: {}", stats.avg_speed_percent, stats.avg_rpm)),
                    ));
                }
            }
        }

        // 系统稳定性指标
        let stability_score = self.calculate_system_stability_score(duration_hours).await?;
        metrics.push(PerformanceMetrics::new(
            MetricType::SystemStability,
            "system".to_string(),
            stability_score,
            Some(format!("系统稳定性评分: {:.1}/100", stability_score)),
        ));

        // 能效指标
        let efficiency_score = self.calculate_energy_efficiency_score(duration_hours).await?;
        metrics.push(PerformanceMetrics::new(
            MetricType::EnergyEfficiency,
            "system".to_string(),
            efficiency_score,
            Some(format!("能效评分: {:.1}/100", efficiency_score)),
        ));

        let result = AnalyticsResult::new(
            AnalysisType::PerformanceMetrics,
            serde_json::to_value(metrics)?,
        );

        // 缓存结果
        self.cache_result(format!("performance_metrics_{}", duration_hours), result.clone()).await;

        Ok(result)
    }

    /// 执行数据聚合
    /// 
    /// # 参数
    /// * `aggregation_type` - 聚合类型
    /// * `duration_hours` - 时间范围（小时）
    pub async fn aggregate_data(&self, aggregation_type: AggregationType, duration_hours: u64) -> AppResult<AnalyticsResult> {
        let end_time = Utc::now();
        let start_time = end_time - Duration::hours(duration_hours as i64);

        let mut aggregated_values = Vec::new();

        match aggregation_type {
            AggregationType::Hourly => {
                // 按小时聚合
                for hour in 0..duration_hours {
                    let hour_start = start_time + Duration::hours(hour as i64);
                    let hour_end = hour_start + Duration::hours(1);
                    
                    let avg_temp = self.calculate_average_temperature_in_period(hour_start, hour_end).await?;
                    let avg_fan_speed = self.calculate_average_fan_speed_in_period(hour_start, hour_end).await?;
                    
                    aggregated_values.push(AggregatedValue {
                        timestamp: hour_start,
                        value: avg_temp,
                        count: 1, // 简化处理
                        metadata: Some(serde_json::json!({
                            "avg_temperature": avg_temp,
                            "avg_fan_speed": avg_fan_speed
                        })),
                    });
                }
            },
            AggregationType::Daily => {
                // 按天聚合
                let days = (duration_hours / 24).max(1);
                for day in 0..days {
                    let day_start = start_time + Duration::days(day as i64);
                    let day_end = day_start + Duration::days(1);
                    
                    let avg_temp = self.calculate_average_temperature_in_period(day_start, day_end).await?;
                    let avg_fan_speed = self.calculate_average_fan_speed_in_period(day_start, day_end).await?;
                    
                    aggregated_values.push(AggregatedValue {
                        timestamp: day_start,
                        value: avg_temp,
                        count: 24, // 24小时
                        metadata: Some(serde_json::json!({
                            "avg_temperature": avg_temp,
                            "avg_fan_speed": avg_fan_speed
                        })),
                    });
                }
            },
            AggregationType::Weekly => {
                // 按周聚合
                let weeks = (duration_hours / (24 * 7)).max(1);
                for week in 0..weeks {
                    let week_start = start_time + Duration::weeks(week as i64);
                    let week_end = week_start + Duration::weeks(1);
                    
                    let avg_temp = self.calculate_average_temperature_in_period(week_start, week_end).await?;
                    let avg_fan_speed = self.calculate_average_fan_speed_in_period(week_start, week_end).await?;
                    
                    aggregated_values.push(AggregatedValue {
                        timestamp: week_start,
                        value: avg_temp,
                        count: 168, // 7*24小时
                        metadata: Some(serde_json::json!({
                            "avg_temperature": avg_temp,
                            "avg_fan_speed": avg_fan_speed
                        })),
                    });
                }
            },
        }

        let analysis = DataAggregation {
            aggregation_type,
            period_start: start_time,
            period_end: end_time,
            total_records: aggregated_values.len(),
            aggregated_values,
        };

        let result = AnalyticsResult::new(
            AnalysisType::DataAggregation,
            serde_json::to_value(analysis)?,
        );

        // 缓存结果
        self.cache_result(format!("data_aggregation_{:?}_{}", aggregation_type, duration_hours), result.clone()).await;

        Ok(result)
    }

    /// 生成系统优化建议
    /// 
    /// # 参数
    /// * `duration_hours` - 分析时间范围（小时）
    pub async fn generate_optimization_recommendations(&self, duration_hours: u64) -> AppResult<Vec<OptimizationRecommendation>> {
        let mut recommendations = Vec::new();

        // 分析温度趋势并生成建议
        if let Ok(temp_sensors) = self.thermal_service.get_temperature_sensors().await {
            for sensor_id in temp_sensors {
                if let Ok(trend_result) = self.analyze_temperature_trend(&sensor_id, duration_hours).await {
                    if let Ok(trend_analysis) = serde_json::from_value::<TemperatureTrendAnalysis>(trend_result.data) {
                        recommendations.extend(trend_analysis.recommendations);
                    }
                }
            }
        }

        // 分析风扇效率并生成建议
        if let Ok(fan_list) = self.fan_service.get_fan_list().await {
            for fan_id in fan_list {
                if let Ok(efficiency_result) = self.analyze_fan_efficiency(&fan_id, duration_hours).await {
                    if let Ok(efficiency_analysis) = serde_json::from_value::<FanEfficiencyAnalysis>(efficiency_result.data) {
                        recommendations.extend(efficiency_analysis.recommendations);
                    }
                }
            }
        }

        // 系统级优化建议
        let system_recommendations = self.generate_system_level_recommendations(duration_hours).await?;
        recommendations.extend(system_recommendations);

        Ok(recommendations)
    }

    /// 获取缓存的分析结果
    /// 
    /// # 参数
    /// * `cache_key` - 缓存键
    pub async fn get_cached_result(&self, cache_key: &str) -> Option<AnalyticsResult> {
        let cache = self.analysis_cache.read().await;
        cache.get(cache_key).cloned()
    }

    /// 清理过期的缓存
    pub async fn cleanup_cache(&self) -> AppResult<usize> {
        let mut cache = self.analysis_cache.write().await;
        let cutoff_time = Utc::now() - Duration::hours(1); // 缓存1小时
        
        let original_size = cache.len();
        cache.retain(|_, result| result.timestamp > cutoff_time);
        let removed_count = original_size - cache.len();
        
        Ok(removed_count)
    }

    // 私有辅助方法

    /// 缓存分析结果
    /// 
    /// # 参数
    /// * `cache_key` - 缓存键
    /// * `result` - 分析结果
    async fn cache_result(&self, cache_key: String, result: AnalyticsResult) {
        let mut cache = self.analysis_cache.write().await;
        cache.insert(cache_key, result);
    }

    /// 生成温度建议
    /// 
    /// # 参数
    /// * `trend` - 温度趋势
    /// * `stats` - 温度统计
    async fn generate_temperature_recommendations(
        &self,
        trend: &crate::models::thermal::TemperatureTrend,
        stats: &TemperatureStats,
    ) -> Vec<OptimizationRecommendation> {
        let mut recommendations = Vec::new();

        if stats.avg_temperature > 70.0 {
            recommendations.push(OptimizationRecommendation {
                id: uuid::Uuid::new_v4().to_string(),
                category: "温度控制".to_string(),
                priority: RecommendationPriority::High,
                title: "高温警告".to_string(),
                description: format!("传感器 {} 平均温度过高 ({:.1}°C)", trend.sensor_id, stats.avg_temperature),
                action: "增加风扇转速或检查散热系统".to_string(),
                expected_impact: "降低系统温度5-10°C".to_string(),
                estimated_savings: None,
            });
        }

        if trend.slope > 0.5 {
            recommendations.push(OptimizationRecommendation {
                id: uuid::Uuid::new_v4().to_string(),
                category: "趋势预警".to_string(),
                priority: RecommendationPriority::Medium,
                title: "温度上升趋势".to_string(),
                description: format!("传感器 {} 温度呈上升趋势", trend.sensor_id),
                action: "监控温度变化并准备调整冷却策略".to_string(),
                expected_impact: "预防温度过高".to_string(),
                estimated_savings: None,
            });
        }

        recommendations
    }

    /// 生成风扇建议
    /// 
    /// # 参数
    /// * `stats` - 风扇统计
    /// * `efficiency_score` - 效率分数
    async fn generate_fan_recommendations(&self, stats: &FanStats, efficiency_score: f64) -> Vec<OptimizationRecommendation> {
        let mut recommendations = Vec::new();

        if efficiency_score < 60.0 {
            recommendations.push(OptimizationRecommendation {
                id: uuid::Uuid::new_v4().to_string(),
                category: "风扇优化".to_string(),
                priority: RecommendationPriority::Medium,
                title: "风扇效率低".to_string(),
                description: format!("风扇 {} 效率较低 ({:.1}%)", stats.fan_id, efficiency_score),
                action: "清洁风扇或调整转速曲线".to_string(),
                expected_impact: "提高冷却效率，降低噪音".to_string(),
                estimated_savings: Some("节能10-15%".to_string()),
            });
        }

        if stats.avg_speed_percent > 80.0 {
            recommendations.push(OptimizationRecommendation {
                id: uuid::Uuid::new_v4().to_string(),
                category: "噪音控制".to_string(),
                priority: RecommendationPriority::Low,
                title: "风扇转速过高".to_string(),
                description: format!("风扇 {} 平均转速过高 ({:.1}%)", stats.fan_id, stats.avg_speed_percent),
                action: "优化温度控制策略，降低风扇转速".to_string(),
                expected_impact: "降低噪音水平".to_string(),
                estimated_savings: Some("节能5-10%".to_string()),
            });
        }

        recommendations
    }

    /// 生成系统级建议
    /// 
    /// # 参数
    /// * `duration_hours` - 分析时间范围
    async fn generate_system_level_recommendations(&self, duration_hours: u64) -> AppResult<Vec<OptimizationRecommendation>> {
        let mut recommendations = Vec::new();

        // 检查系统稳定性
        let stability_score = self.calculate_system_stability_score(duration_hours).await?;
        if stability_score < 80.0 {
            recommendations.push(OptimizationRecommendation {
                id: uuid::Uuid::new_v4().to_string(),
                category: "系统稳定性".to_string(),
                priority: RecommendationPriority::High,
                title: "系统稳定性需要改善".to_string(),
                description: format!("系统稳定性评分较低 ({:.1}%)", stability_score),
                action: "检查硬件状态，优化控制参数".to_string(),
                expected_impact: "提高系统可靠性".to_string(),
                estimated_savings: None,
            });
        }

        // 检查能效
        let efficiency_score = self.calculate_energy_efficiency_score(duration_hours).await?;
        if efficiency_score < 70.0 {
            recommendations.push(OptimizationRecommendation {
                id: uuid::Uuid::new_v4().to_string(),
                category: "能效优化".to_string(),
                priority: RecommendationPriority::Medium,
                title: "能效有待提升".to_string(),
                description: format!("系统能效评分较低 ({:.1}%)", efficiency_score),
                action: "优化风扇控制策略，实施智能调节".to_string(),
                expected_impact: "降低能耗，提高效率".to_string(),
                estimated_savings: Some("节能15-25%".to_string()),
            });
        }

        Ok(recommendations)
    }

    /// 计算风扇效率分数
    /// 
    /// # 参数
    /// * `stats` - 风扇统计
    async fn calculate_fan_efficiency_score(&self, stats: &FanStats) -> AppResult<f64> {
        // 简化的效率计算
        let speed_efficiency = if stats.avg_speed_percent > 90.0 {
            50.0 // 转速过高效率低
        } else if stats.avg_speed_percent < 20.0 {
            70.0 // 转速过低可能不够
        } else {
            100.0 - (stats.avg_speed_percent - 50.0).abs() // 50%附近效率最高
        };

        let stability_score = 100.0 - (stats.normal_count as f64 / stats.sample_count as f64) * 100.0;
        
        Ok((speed_efficiency + stability_score) / 2.0)
    }

    /// 估算噪音水平
    /// 
    /// # 参数
    /// * `speed_percent` - 转速百分比
    fn estimate_noise_level(&self, speed_percent: f64) -> NoiseLevel {
        if speed_percent < 30.0 {
            NoiseLevel::Quiet
        } else if speed_percent < 60.0 {
            NoiseLevel::Moderate
        } else if speed_percent < 80.0 {
            NoiseLevel::Loud
        } else {
            NoiseLevel::VeryLoud
        }
    }

    /// 找到最优风扇转速点
    /// 
    /// # 参数
    /// * `fan_id` - 风扇ID
    /// * `duration_hours` - 分析时间范围
    async fn find_optimal_fan_speed(&self, fan_id: &str, duration_hours: u64) -> AppResult<OptimalSpeedPoint> {
        let stats = self.fan_service.get_fan_stats(fan_id, duration_hours).await?;
        
        // 简化的最优点计算
        let optimal_speed = if stats.avg_speed_percent > 70.0 {
            stats.avg_speed_percent * 0.8 // 降低20%
        } else {
            stats.avg_speed_percent
        };

        Ok(OptimalSpeedPoint {
            speed_percent: optimal_speed,
            temperature_range: (20.0, 65.0), // 假设的温度范围
            efficiency_rating: 85.0,
            noise_level: self.estimate_noise_level(optimal_speed),
        })
    }

    /// 估算功耗
    /// 
    /// # 参数
    /// * `speed_percent` - 转速百分比
    fn estimate_power_consumption(&self, speed_percent: f64) -> f64 {
        // 简化的功耗估算（瓦特）
        let base_power = 5.0; // 基础功耗
        let variable_power = (speed_percent / 100.0).powi(3) * 20.0; // 立方关系
        base_power + variable_power
    }

    /// 检测温度异常
    /// 
    /// # 参数
    /// * `sensor_id` - 传感器ID
    /// * `duration_hours` - 分析时间范围
    async fn detect_temperature_anomalies(&self, sensor_id: &str, duration_hours: u64) -> AppResult<Vec<DetectedAnomaly>> {
        let stats = self.thermal_service.get_temperature_stats(sensor_id, duration_hours).await?;
        let mut anomalies = Vec::new();

        // 检测温度峰值
        if stats.max_temperature > 85.0 {
            anomalies.push(DetectedAnomaly {
                id: uuid::Uuid::new_v4().to_string(),
                anomaly_type: AnomalyType::TemperatureSpike,
                severity: AnomalySeverity::High,
                description: format!("传感器 {} 检测到高温峰值: {:.1}°C", sensor_id, stats.max_temperature),
                affected_component: sensor_id.to_string(),
                detection_time: Utc::now(),
                confidence: 0.9,
                recommended_action: "立即检查散热系统".to_string(),
            });
        }

        // 检测温度波动
        if stats.std_deviation > 5.0 {
            anomalies.push(DetectedAnomaly {
                id: uuid::Uuid::new_v4().to_string(),
                anomaly_type: AnomalyType::DataInconsistency,
                severity: AnomalySeverity::Medium,
                description: format!("传感器 {} 温度波动较大: 标准差 {:.1}°C", sensor_id, stats.std_deviation),
                affected_component: sensor_id.to_string(),
                detection_time: Utc::now(),
                confidence: 0.7,
                recommended_action: "检查传感器稳定性".to_string(),
            });
        }

        Ok(anomalies)
    }

    /// 检测风扇异常
    /// 
    /// # 参数
    /// * `fan_id` - 风扇ID
    /// * `duration_hours` - 分析时间范围
    async fn detect_fan_anomalies(&self, fan_id: &str, duration_hours: u64) -> AppResult<Vec<DetectedAnomaly>> {
        let stats = self.fan_service.get_fan_stats(fan_id, duration_hours).await?;
        let mut anomalies = Vec::new();

        // 检测风扇故障
        if stats.error_count > 0 {
            anomalies.push(DetectedAnomaly {
                id: uuid::Uuid::new_v4().to_string(),
                anomaly_type: AnomalyType::FanFailure,
                severity: AnomalySeverity::High,
                description: format!("风扇 {} 检测到 {} 次错误", fan_id, stats.error_count),
                affected_component: fan_id.to_string(),
                detection_time: Utc::now(),
                confidence: 0.95,
                recommended_action: "检查风扇硬件状态".to_string(),
            });
        }

        // 检测转速异常
        if stats.min_speed_percent == 0.0 && stats.max_speed_percent > 0.0 {
            anomalies.push(DetectedAnomaly {
                id: uuid::Uuid::new_v4().to_string(),
                anomaly_type: AnomalyType::FanFailure,
                severity: AnomalySeverity::Medium,
                description: format!("风扇 {} 检测到转速异常停止", fan_id),
                affected_component: fan_id.to_string(),
                detection_time: Utc::now(),
                confidence: 0.8,
                recommended_action: "检查风扇连接和电源".to_string(),
            });
        }

        Ok(anomalies)
    }

    /// 计算系统稳定性分数
    /// 
    /// # 参数
    /// * `duration_hours` - 分析时间范围
    async fn calculate_system_stability_score(&self, duration_hours: u64) -> AppResult<f64> {
        // 简化的稳定性计算
        let mut total_score = 0.0;
        let mut component_count = 0;

        // 温度稳定性
        if let Ok(temp_sensors) = self.thermal_service.get_temperature_sensors().await {
            for sensor_id in temp_sensors {
                if let Ok(stats) = self.thermal_service.get_temperature_stats(&sensor_id, duration_hours).await {
                    let stability = 100.0 - (stats.std_deviation * 10.0).min(100.0);
                    total_score += stability;
                    component_count += 1;
                }
            }
        }

        // 风扇稳定性
        if let Ok(fan_list) = self.fan_service.get_fan_list().await {
            for fan_id in fan_list {
                if let Ok(stats) = self.fan_service.get_fan_stats(&fan_id, duration_hours).await {
                    let error_rate = stats.error_count as f64 / stats.sample_count as f64;
                    let stability = (1.0 - error_rate) * 100.0;
                    total_score += stability;
                    component_count += 1;
                }
            }
        }

        if component_count > 0 {
            Ok(total_score / component_count as f64)
        } else {
            Ok(0.0)
        }
    }

    /// 计算能效分数
    /// 
    /// # 参数
    /// * `duration_hours` - 分析时间范围
    async fn calculate_energy_efficiency_score(&self, _duration_hours: u64) -> AppResult<f64> {
        // 简化的能效计算
        // 实际实现中应该考虑功耗、温度控制效果等因素
        Ok(75.0) // 默认分数
    }

    /// 计算时间段内平均温度
    /// 
    /// # 参数
    /// * `start_time` - 开始时间
    /// * `end_time` - 结束时间
    async fn calculate_average_temperature_in_period(&self, start_time: DateTime<Utc>, end_time: DateTime<Utc>) -> AppResult<f64> {
        // 简化实现，实际应该查询历史数据
        Ok(45.0) // 默认温度
    }

    /// 计算时间段内平均风扇转速
    /// 
    /// # 参数
    /// * `start_time` - 开始时间
    /// * `end_time` - 结束时间
    async fn calculate_average_fan_speed_in_period(&self, start_time: DateTime<Utc>, end_time: DateTime<Utc>) -> AppResult<f64> {
        // 简化实现，实际应该查询历史数据
        Ok(50.0) // 默认转速
    }
}

/// 优化建议
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OptimizationRecommendation {
    /// 建议ID
    pub id: String,
    /// 类别
    pub category: String,
    /// 优先级
    pub priority: RecommendationPriority,
    /// 标题
    pub title: String,
    /// 描述
    pub description: String,
    /// 建议操作
    pub action: String,
    /// 预期影响
    pub expected_impact: String,
    /// 预估节省
    pub estimated_savings: Option<String>,
}

/// 建议优先级
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum RecommendationPriority {
    /// 低
    Low,
    /// 中
    Medium,
    /// 高
    High,
    /// 紧急
    Critical,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_noise_level_estimation() {
        let analytics_service = create_test_analytics_service();

        assert_eq!(analytics_service.estimate_noise_level(25.0), NoiseLevel::Quiet);
        assert_eq!(analytics_service.estimate_noise_level(45.0), NoiseLevel::Moderate);
        assert_eq!(analytics_service.estimate_noise_level(70.0), NoiseLevel::Loud);
        assert_eq!(analytics_service.estimate_noise_level(90.0), NoiseLevel::VeryLoud);
    }

    #[test]
    fn test_power_consumption_estimation() {
        let analytics_service = create_test_analytics_service();

        let power_20 = analytics_service.estimate_power_consumption(20.0);
        let power_50 = analytics_service.estimate_power_consumption(50.0);
        let power_100 = analytics_service.estimate_power_consumption(100.0);

        assert!(power_20 < power_50);
        assert!(power_50 < power_100);
        assert!(power_100 > 20.0); // 100%转速时功耗应该超过20W
    }

    fn create_test_analytics_service() -> AnalyticsService {
        // 创建测试用的分析服务
        // 这里需要模拟的服务实例
        todo!("实现测试用的分析服务创建")
    }
}