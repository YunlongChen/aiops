use crate::models::AlertStatus;
use crate::{models, AppState};
use actix_web::{web, HttpResponse, Result};
use chrono::Utc;
use serde_json::json;
use uuid;

/// 获取告警列表
pub async fn list_alerts(
    _query: web::Query<models::PaginationParams>,
    _data: web::Data<AppState>,
) -> Result<HttpResponse> {
    // TODO: 从数据库获取真实的告警数据
    let alerts = vec![
        models::Alert {
            id: uuid::Uuid::new_v4(),
            alert_type: "temperature".to_string(),
            severity: "warning".to_string(),
            title: "High Temperature Alert".to_string(),
            message: "CPU temperature exceeded 80°C".to_string(),
            source: "CPU_TEMP_1".to_string(),
            source_id: "sensor_001".to_string(),
            status: AlertStatus::Ignored,
            acknowledged: false,
            acknowledged_by: None,
            acknowledged_at: None,
            resolved_at: None,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        },
    ];

    let response = models::PaginatedResponse {
        data: alerts,
        total: 1,
        page: 1,
        limit: 10,
        total_pages: 1,
    };

    Ok(HttpResponse::Ok().json(models::ApiResponse::success(
        response,
        "Alerts retrieved successfully"
    )))
}

/// 确认告警
pub async fn acknowledge_alert(
    path: web::Path<uuid::Uuid>,
    ack_data: web::Json<serde_json::Value>,
    _data: web::Data<AppState>,
) -> Result<HttpResponse> {
    let alert_id = path.into_inner();
    let acknowledged_by = ack_data.get("acknowledged_by")
        .and_then(|v| v.as_str())
        .unwrap_or("system");
    
    // TODO: 在数据库中更新告警状态
    tracing::info!("Acknowledging alert {} by {}", alert_id, acknowledged_by);

    Ok(HttpResponse::Ok().json(models::ApiResponse::success(
        json!({
            "alert_id": alert_id,
            "acknowledged_by": acknowledged_by,
            "acknowledged_at": Utc::now().to_rfc3339()
        }),
        "Alert acknowledged successfully"
    )))
}