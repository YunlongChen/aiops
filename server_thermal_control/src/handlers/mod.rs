use crate::models::FanStats;
use crate::{models, AppState};
use actix_web::{web, HttpResponse, Result};
use chrono::Utc;
use serde_json::json;

// pub mod alert;
pub mod fan;
pub mod temperature;

/// 健康检查处理器
pub async fn health_check() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(json!({
        "status": "ok",
        "timestamp": Utc::now().to_rfc3339(),
        "service": "thermal-control-server"
    })))
}

/// 系统信息处理器
pub async fn system_info(data: web::Data<AppState>) -> Result<HttpResponse> {
    let cpu_count = num_cpus::get();

    // 尝试获取IPMI系统信息
    let ipmi_info = match data.ipmi_service.get_system_info().await {
        Ok(info) => Some(info),
        Err(e) => {
            tracing::warn!("Failed to get IPMI system info: {}", e);
            None
        }
    };

    let mut system_info = json!({
        "service_name": "Thermal Control Server",
        "version": "1.0.0",
        "cpu_cores": cpu_count,
        "uptime": "running",
        "timestamp": Utc::now().to_rfc3339()
    });

    // 如果有IPMI信息，添加到响应中
    if let Some(info) = ipmi_info {
        system_info["ipmi_info"] = json!({
            "manufacturer": info.manufacturer,
            "product_name": info.product_name,
            "firmware_version": info.firmware_version,
            "ipmi_version": info.ipmi_version
        });
    }

    Ok(HttpResponse::Ok().json(models::ApiResponse::success(
        system_info,
        "System information retrieved successfully",
    )))
}

/// 系统健康状态处理器
pub async fn system_health(data: web::Data<AppState>) -> Result<HttpResponse> {
    let mut overall_status = "healthy";
    let mut issues = Vec::new();

    // 检查IPMI连接状态
    let ipmi_status = if let Ok(_) = data.ipmi_service.test_connection().await {
        "connected"
    } else if let Err(e) = data.ipmi_service.test_connection().await {
        tracing::warn!("IPMI connection test failed: {}", e);
        issues.push(format!("IPMI connection issue: {}", e));
        overall_status = "warning";
        "disconnected"
    } else {
        unreachable!()
    };

    // 检查温度传感器状态
    let temperature_status = match data.ipmi_service.get_temperature_sensors().await {
        Ok(sensors) => {
            let mut temp_issues = Vec::new();
            for sensor in sensors {
                if sensor.value > 80.0 {
                    temp_issues.push(format!(
                        "High temperature on {}: {:.1}°C",
                        sensor.name, sensor.value
                    ));
                    overall_status = "critical";
                } else if sensor.value > 70.0 {
                    temp_issues.push(format!(
                        "Elevated temperature on {}: {:.1}°C",
                        sensor.name, sensor.value
                    ));
                    if overall_status == "healthy" {
                        overall_status = "warning";
                    }
                }
            }
            issues.extend(temp_issues);
            if issues.is_empty() {
                "normal"
            } else {
                "elevated"
            }
        }
        Err(_) => {
            issues.push("Unable to read temperature sensors".to_string());
            if overall_status == "healthy" {
                overall_status = "warning";
            }
            "unknown"
        }
    };

    // 检查风扇状态
    let fan_status = match data.ipmi_service.get_fan_sensors().await {
        Ok(fans) => {
            let mut fan_issues = Vec::new();
            for fan in fans {
                if fan.rpm == 0 {
                    fan_issues.push(format!("Fan {} not running", fan.name));
                    overall_status = "critical";
                } else if fan.rpm < 500 {
                    fan_issues.push(format!("Fan {} running slow: {} RPM", fan.name, fan.rpm));
                    if overall_status == "healthy" {
                        overall_status = "warning";
                    }
                }
            }
            issues.extend(fan_issues);
            if fan_issues.is_empty() {
                "operational"
            } else {
                "issues"
            }
        }
        Err(_) => {
            issues.push("Unable to read fan status".to_string());
            if overall_status == "healthy" {
                overall_status = "warning";
            }
            "unknown"
        }
    };

    let system_health = json!({
        "overall_status": overall_status,
        "components": {
            "ipmi": ipmi_status,
            "temperature_sensors": temperature_status,
            "fans": fan_status,
            "database": "not_configured",
            "redis": "not_configured"
        },
        "issues": issues,
        "timestamp": Utc::now().to_rfc3339()
    });

    Ok(HttpResponse::Ok().json(models::ApiResponse::success(
        system_health,
        "System health check completed",
    )))
}

/// 温度统计处理器
pub async fn temperature_stats(_data: web::Data<AppState>) -> Result<HttpResponse> {
    // TODO: 从数据库获取真实的温度统计数据
    let temp_stats = models::TemperatureStats {
        avg_temperature: 65.2,
        min_temperature: 45.0,
        max_temperature: 85.0,
        sensor_count: 8,
        timestamp: Utc::now(),
    };

    Ok(HttpResponse::Ok().json(models::ApiResponse::success(
        temp_stats,
        "Temperature statistics retrieved successfully",
    )))
}

/// 风扇统计处理器
pub async fn fan_stats(_data: web::Data<AppState>) -> Result<HttpResponse> {
    // TODO: 从数据库获取真实的风扇统计数据
    // avg_speed_rpm: 1850.0,
    //         avg_speed_percent: 75.0,
    //         active_fans: 4,
    //         total_fans: 4,
    //         timestamp: Utc::now(),
    let fan_stats = FanStats {
        fan_id: "".to_string(),
        average_rpm: 1850.0,
        min_rpm: 0,
        max_rpm: 0,
        runtime_hours: 0.0,
        speed_changes: 0,
        time_range_hours: 0,
    };

    Ok(HttpResponse::Ok().json(models::ApiResponse::success(
        fan_stats,
        "Fan statistics retrieved successfully",
    )))
}
