use crate::models::{
    error::{AppError, AppResult},
    alert::*,
    api::{ApiResponse, PaginationParams, TimeRangeParams},
};
use crate::services::AlertService;
use actix_web::{
    web::{Path, Query, Data, ServiceConfig},
    HttpResponse, Result as ActixResult,
    get, post, put, delete,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tracing::{info, warn, error};

/// 告警控制器
/// 
/// 提供系统告警、通知和事件管理的HTTP API接口
#[derive(Clone)]
pub struct AlertController {
    alert_service: Arc<AlertService>,
}

impl AlertController {
    /// 创建新的告警控制器
    /// 
    /// # 参数
    /// * `alert_service` - 告警服务
    pub fn new(alert_service: Arc<AlertService>) -> Self {
        Self { alert_service }
    }

    /// 配置路由
    pub fn configure(cfg: &mut ServiceConfig) {
        cfg.service(
            actix_web::web::scope("/alerts")
                .route("", actix_web::web::get().to(Self::get_active_alerts))
                .route("", actix_web::web::post().to(Self::create_alert))
                .route("/{alert_id}", actix_web::web::get().to(Self::get_alert))
                .route("/{alert_id}/acknowledge", actix_web::web::post().to(Self::acknowledge_alert))
                .route("/{alert_id}/resolve", actix_web::web::post().to(Self::resolve_alert))
                .route("/history", actix_web::web::get().to(Self::get_alert_history))
                .route("/statistics", actix_web::web::get().to(Self::get_alert_statistics))
                .route("/rules", actix_web::web::get().to(Self::get_alert_rules))
                .route("/rules", actix_web::web::post().to(Self::add_alert_rule))
                .route("/rules/{rule_id}", actix_web::web::get().to(Self::get_alert_rule))
                .route("/rules/{rule_id}", actix_web::web::put().to(Self::update_alert_rule))
                .route("/rules/{rule_id}", actix_web::web::delete().to(Self::remove_alert_rule))
                .route("/channels", actix_web::web::get().to(Self::get_notification_channels))
        );
    }

    /// 获取活跃告警
    /// 
    /// GET /api/v1/alerts
    async fn get_active_alerts(
        service: Data<AlertService>,
        Query(params): Query<AlertQueryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取活跃告警");

        match service.get_active_alerts(
            params.severity,
            params.alert_type.as_deref(),
            params.limit,
        ).await {
            Ok(alerts) => Ok(HttpResponse::Ok().json(ApiResponse::success(alerts))),
            Err(e) => {
                error!("获取活跃告警失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 创建告警
    /// 
    /// POST /api/v1/alerts
    async fn create_alert(
        service: Data<AlertService>,
        actix_web::web::Json(request): actix_web::web::Json<CreateAlertRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("创建告警: {}", request.title);

        match service.create_alert(
            request.alert_type,
            request.severity,
            request.title,
            request.message,
            request.source.as_deref(),
            request.metadata,
        ).await {
            Ok(alert) => Ok(HttpResponse::Ok().json(ApiResponse::success(alert))),
            Err(e) => {
                error!("创建告警失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 获取指定告警
    /// 
    /// GET /api/v1/alerts/:alert_id
    async fn get_alert(
        service: Data<AlertService>,
        path: Path<String>,
    ) -> ActixResult<HttpResponse> {
        let alert_id = path.into_inner();
        info!("获取告警: {}", alert_id);

        match service.get_alert(&alert_id).await {
            Ok(alert) => Ok(HttpResponse::Ok().json(ApiResponse::success(alert))),
            Err(e) => {
                error!("获取告警失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 确认告警
    /// 
    /// POST /api/v1/alerts/:alert_id/acknowledge
    async fn acknowledge_alert(
        service: Data<AlertService>,
        path: Path<String>,
        actix_web::web::Json(request): actix_web::web::Json<AcknowledgeAlertRequest>,
    ) -> ActixResult<HttpResponse> {
        let alert_id = path.into_inner();
        info!("确认告警: {}", alert_id);

        match service.acknowledge_alert(
            &alert_id,
            request.acknowledged_by.as_deref(),
            request.note.as_deref(),
        ).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("确认告警失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 解决告警
    /// 
    /// POST /api/v1/alerts/:alert_id/resolve
    async fn resolve_alert(
        service: Data<AlertService>,
        path: Path<String>,
        actix_web::web::Json(request): actix_web::web::Json<ResolveAlertRequest>,
    ) -> ActixResult<HttpResponse> {
        let alert_id = path.into_inner();
        info!("解决告警: {}", alert_id);

        match service.resolve_alert(
            &alert_id,
            request.resolved_by.as_deref(),
            request.resolution_note.as_deref(),
        ).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("解决告警失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 获取告警历史
    /// 
    /// GET /api/v1/alerts/history
    async fn get_alert_history(
        service: Data<AlertService>,
        Query(params): Query<AlertHistoryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取告警历史");

        match service.get_alert_history(
            params.start_time,
            params.end_time,
            params.severity,
            params.alert_type.as_deref(),
            params.limit,
        ).await {
            Ok(history) => Ok(HttpResponse::Ok().json(ApiResponse::success(history))),
            Err(e) => {
                error!("获取告警历史失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 获取告警统计
    /// 
    /// GET /api/v1/alerts/statistics
    async fn get_alert_statistics(
        service: Data<AlertService>,
        Query(params): Query<AlertStatisticsParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取告警统计");

        match service.get_alert_statistics(
            params.time_window_hours.unwrap_or(24),
        ).await {
            Ok(statistics) => Ok(HttpResponse::Ok().json(ApiResponse::success(statistics))),
            Err(e) => {
                error!("获取告警统计失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 获取告警规则
    /// 
    /// GET /api/v1/alerts/rules
    async fn get_alert_rules(
        service: Data<AlertService>,
    ) -> ActixResult<HttpResponse> {
        info!("获取告警规则");

        match service.get_alert_rules().await {
            Ok(rules) => Ok(HttpResponse::Ok().json(ApiResponse::success(rules))),
            Err(e) => {
                error!("获取告警规则失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 添加告警规则
    /// 
    /// POST /api/v1/alerts/rules
    async fn add_alert_rule(
        service: Data<AlertService>,
        actix_web::web::Json(rule): actix_web::web::Json<AlertRule>,
    ) -> ActixResult<HttpResponse> {
        info!("添加告警规则: {}", rule.name);

        match service.add_alert_rule(rule).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("添加告警规则失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 获取指定告警规则
    /// 
    /// GET /api/v1/alerts/rules/:rule_id
    async fn get_alert_rule(
        service: Data<AlertService>,
        path: Path<String>,
    ) -> ActixResult<HttpResponse> {
        let rule_id = path.into_inner();
        info!("获取告警规则: {}", rule_id);

        match service.get_alert_rule(&rule_id).await {
            Ok(rule) => Ok(HttpResponse::Ok().json(ApiResponse::success(rule))),
            Err(e) => {
                error!("获取告警规则失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 更新告警规则
    /// 
    /// PUT /api/v1/alerts/rules/:rule_id
    async fn update_alert_rule(
        service: Data<AlertService>,
        path: Path<String>,
        actix_web::web::Json(rule): actix_web::web::Json<AlertRule>,
    ) -> ActixResult<HttpResponse> {
        let rule_id = path.into_inner();
        info!("更新告警规则: {}", rule_id);

        match service.update_alert_rule(&rule_id, rule).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("更新告警规则失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 删除告警规则
    /// 
    /// DELETE /api/v1/alerts/rules/:rule_id
    async fn remove_alert_rule(
        service: Data<AlertService>,
        path: Path<String>,
    ) -> ActixResult<HttpResponse> {
        let rule_id = path.into_inner();
        info!("删除告警规则: {}", rule_id);

        match service.remove_alert_rule(&rule_id).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("移除告警规则失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 获取通知渠道
    /// 
    /// GET /api/v1/alerts/channels
    async fn get_notification_channels(
        service: Data<AlertService>,
    ) -> ActixResult<HttpResponse> {
        info!("获取通知渠道");

        match service.get_notification_channels().await {
            Ok(channels) => Ok(HttpResponse::Ok().json(ApiResponse::success(channels))),
            Err(e) => {
                error!("获取通知渠道失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 添加通知渠道
    /// 
    /// POST /api/v1/alerts/channels
    async fn add_notification_channel(
        service: Data<Arc<AlertService>>,
        channel: actix_web::web::Json<NotificationChannel>,
    ) -> ActixResult<HttpResponse> {
        info!("添加通知渠道: {}", channel.name);

        service.add_notification_channel(channel.into_inner()).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 获取指定通知渠道
    /// 
    /// GET /api/v1/alerts/channels/:channel_id
    async fn get_notification_channel(
        service: Data<Arc<AlertService>>,
        path: Path<String>,
    ) -> ActixResult<HttpResponse> {
        let channel_id = path.into_inner();
        info!("获取通知渠道: {}", channel_id);

        let channel = service.get_notification_channel(&channel_id).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(channel)))
    }

    /// 更新通知渠道
    /// 
    /// PUT /api/v1/alerts/channels/:channel_id
    async fn update_notification_channel(
        service: Data<Arc<AlertService>>,
        path: Path<String>,
        channel: actix_web::web::Json<NotificationChannel>,
    ) -> ActixResult<HttpResponse> {
        let channel_id = path.into_inner();
        info!("更新通知渠道: {}", channel_id);

        service.update_notification_channel(&channel_id, channel.into_inner()).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 移除通知渠道
    /// 
    /// DELETE /api/v1/alerts/channels/:channel_id
    async fn remove_notification_channel(
        service: Data<Arc<AlertService>>,
        path: Path<String>,
    ) -> ActixResult<HttpResponse> {
        let channel_id = path.into_inner();
        info!("移除通知渠道: {}", channel_id);

        service.remove_notification_channel(&channel_id).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 测试通知渠道
    /// 
    /// POST /api/v1/alerts/channels/:channel_id/test
    async fn test_notification_channel(
        service: Data<Arc<AlertService>>,
        path: Path<String>,
        request: actix_web::web::Json<TestNotificationRequest>,
    ) -> ActixResult<HttpResponse> {
        let channel_id = path.into_inner();
        info!("测试通知渠道: {}", channel_id);

        let result = service.test_notification_channel(
            &channel_id,
            request.test_message.as_deref(),
        ).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 批量确认告警
    /// 
    /// POST /api/v1/alerts/bulk/acknowledge
    async fn bulk_acknowledge_alerts(
        service: Data<Arc<AlertService>>,
        request: actix_web::web::Json<BulkAcknowledgeRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("批量确认告警: {} 个", request.alert_ids.len());

        let result = service.bulk_acknowledge_alerts(
            request.alert_ids.clone(),
            request.acknowledged_by.as_deref(),
            request.note.as_deref(),
        ).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 批量解决告警
    /// 
    /// POST /api/v1/alerts/bulk/resolve
    async fn bulk_resolve_alerts(
        service: Data<Arc<AlertService>>,
        request: actix_web::web::Json<BulkResolveRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("批量解决告警: {} 个", request.alert_ids.len());

        let result = service.bulk_resolve_alerts(
            request.alert_ids.clone(),
            request.resolved_by.as_deref(),
            request.resolution_note.as_deref(),
        ).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 导出告警
    /// 
    /// GET /api/v1/alerts/export
    async fn export_alerts(
        service: Data<Arc<AlertService>>,
        params: Query<ExportAlertsParams>,
    ) -> ActixResult<HttpResponse> {
        info!("导出告警");

        let export_data = service.export_alerts(
            params.start_time,
            params.end_time,
            params.format.unwrap_or(ExportFormat::Json),
            params.include_resolved.unwrap_or(false),
        ).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(export_data)))
    }

    /// 导入告警
    /// 
    /// POST /api/v1/alerts/import
    async fn import_alerts(
        service: Data<Arc<AlertService>>,
        request: actix_web::web::Json<ImportAlertsRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("导入告警");

        let result = service.import_alerts(
            request.data.clone(),
            request.format,
            request.merge_strategy.unwrap_or(MergeStrategy::Skip),
        ).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 获取告警模板
    /// 
    /// GET /api/v1/alerts/templates
    async fn get_alert_templates(
        service: Data<Arc<AlertService>>,
    ) -> ActixResult<HttpResponse> {
        info!("获取告警模板");

        let templates = service.get_alert_templates().await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(templates)))
    }

    /// 创建告警模板
    /// 
    /// POST /api/v1/alerts/templates
    async fn create_alert_template(
        service: Data<Arc<AlertService>>,
        template: actix_web::web::Json<CreateAlertTemplateRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("创建告警模板: {}", template.name);

        let created_template = service.create_alert_template(
            template.name.clone(),
            template.description.clone(),
            template.alert_type,
            template.severity,
            template.title_template.clone(),
            template.message_template.clone(),
            template.metadata_template.clone(),
        ).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(created_template)))
    }

    /// 获取指定告警模板
    /// 
    /// GET /api/v1/alerts/templates/:template_id
    async fn get_alert_template(
        service: Data<Arc<AlertService>>,
        path: Path<String>,
    ) -> ActixResult<HttpResponse> {
        let template_id = path.into_inner();
        info!("获取告警模板: {}", template_id);

        let template = service.get_alert_template(&template_id).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(template)))
    }

    /// 更新告警模板
    /// 
    /// PUT /api/v1/alerts/templates/:template_id
    async fn update_alert_template(
        service: Data<Arc<AlertService>>,
        path: Path<String>,
        request: actix_web::web::Json<UpdateAlertTemplateRequest>,
    ) -> ActixResult<HttpResponse> {
        let template_id = path.into_inner();
        info!("更新告警模板: {}", template_id);

        service.update_alert_template(
            &template_id,
            request.name.clone(),
            request.description.clone(),
            request.alert_type.clone(),
            request.severity,
            request.title_template.clone(),
            request.message_template.clone(),
            request.metadata_template.clone(),
        ).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 删除告警模板
    /// 
    /// DELETE /api/v1/alerts/templates/:template_id
    async fn delete_alert_template(
        service: Data<Arc<AlertService>>,
        path: Path<String>,
    ) -> ActixResult<HttpResponse> {
        let template_id = path.into_inner();
        info!("删除告警模板: {}", template_id);

        service.delete_alert_template(&template_id).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }
}

// 请求和响应结构体

/// 告警类型枚举
/// 
/// 定义不同类型的告警
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum AlertType {
    /// 系统告警
    System,
    /// 传感器告警
    Sensor,
    /// 温度告警
    Temperature,
    /// 风扇告警
    Fan,
    /// 网络告警                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
    Network,
    /// 硬件告警
    Hardware,
}

/// 告警过滤器
/// 
/// 用于过滤告警记录
#[derive(Debug, Clone, Deserialize)]
pub struct AlertFilter {
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 严重程度
    pub severity: Option<AlertSeverity>,
    /// 告警类型
    pub alert_type: Option<AlertType>,
    /// 告警状态
    pub status: Option<AlertStatus>,
    /// 告警源
    pub source: Option<String>,
}

/// 告警查询参数
#[derive(Debug, Deserialize)]
pub struct AlertQueryParams {
    /// 严重程度过滤
    pub severity: Option<AlertSeverity>,
    /// 告警类型过滤
    pub alert_type: Option<Vec<String>>,
    /// 返回记录数限制
    pub limit: Option<usize>,
}

/// 创建告警请求
#[derive(Debug, Deserialize)]
pub struct CreateAlertRequest {
    /// 告警类型
    pub alert_type: String,
    /// 严重程度
    pub severity: AlertSeverity,
    /// 标题
    pub title: String,
    /// 消息
    pub message: String,
    /// 来源
    pub source: Option<String>,
    /// 元数据
    pub metadata: Option<serde_json::Value>,
}

/// 确认告警请求
#[derive(Debug, Deserialize)]
pub struct AcknowledgeAlertRequest {
    /// 确认人
    pub acknowledged_by: Option<String>,
    /// 备注
    pub note: Option<String>,
}

/// 解决告警请求
#[derive(Debug, Deserialize)]
pub struct ResolveAlertRequest {
    /// 解决人
    pub resolved_by: Option<String>,
    /// 解决备注
    pub resolution_note: Option<String>,
}

/// 告警历史参数
#[derive(Debug, Deserialize)]
pub struct AlertHistoryParams {
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 严重程度过滤
    pub severity: Option<AlertSeverity>,
    /// 告警类型过滤
    pub alert_type: Option<Vec<String>>,
    /// 返回记录数限制
    pub limit: Option<usize>,
}

/// 告警统计参数
#[derive(Debug, Deserialize)]
pub struct AlertStatisticsParams {
    /// 时间窗口（小时）
    pub time_window_hours: Option<u32>,
}

/// 测试通知请求
#[derive(Debug, Deserialize)]
pub struct TestNotificationRequest {
    /// 测试消息
    pub test_message: Option<String>,
}

/// 测试通知结果
#[derive(Debug, Serialize)]
pub struct TestNotificationResult {
    /// 是否成功
    pub success: bool,
    /// 响应时间（毫秒）
    pub response_time_ms: u64,
    /// 错误消息
    pub error_message: Option<String>,
    /// 测试时间
    pub tested_at: chrono::DateTime<chrono::Utc>,
}

/// 批量确认请求
#[derive(Debug, Deserialize)]
pub struct BulkAcknowledgeRequest {
    /// 告警ID列表
    pub alert_ids: Vec<String>,
    /// 确认人
    pub acknowledged_by: Option<String>,
    /// 备注
    pub note: Option<String>,
}

/// 批量解决请求
#[derive(Debug, Deserialize)]
pub struct BulkResolveRequest {
    /// 告警ID列表
    pub alert_ids: Vec<String>,
    /// 解决人
    pub resolved_by: Option<String>,
    /// 解决备注
    pub resolution_note: Option<String>,
}

/// 批量操作结果
#[derive(Debug, Serialize)]
pub struct BulkOperationResult {
    /// 成功处理的告警数
    pub successful_count: usize,
    /// 失败处理的告警数
    pub failed_count: usize,
    /// 失败的告警ID和错误信息
    pub failures: Vec<BulkOperationFailure>,
    /// 操作时间
    pub processed_at: chrono::DateTime<chrono::Utc>,
}

/// 批量操作失败项
#[derive(Debug, Serialize)]
pub struct BulkOperationFailure {
    /// 告警ID
    pub alert_id: String,
    /// 错误消息
    pub error_message: String,
}

/// 导出告警参数
#[derive(Debug, Deserialize)]
pub struct ExportAlertsParams {
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 导出格式
    pub format: Option<ExportFormat>,
    /// 是否包含已解决的告警
    pub include_resolved: Option<bool>,
}

/// 导出格式
#[derive(Debug, Clone, Deserialize)]
pub enum ExportFormat {
    /// JSON格式
    Json,
    /// CSV格式
    Csv,
    /// Excel格式
    Excel,
}

/// 告警导出数据
#[derive(Debug, Serialize)]
pub struct AlertExportData {
    /// 导出格式
    pub format: ExportFormat,
    /// 导出的告警数量
    pub alert_count: usize,
    /// 导出数据（base64编码）
    pub data: String,
    /// 文件名
    pub filename: String,
    /// 导出时间
    pub exported_at: chrono::DateTime<chrono::Utc>,
}

/// 导入告警请求
#[derive(Debug, Deserialize)]
pub struct ImportAlertsRequest {
    /// 导入数据（base64编码）
    pub data: String,
    /// 数据格式
    pub format: ExportFormat,
    /// 合并策略
    pub merge_strategy: Option<MergeStrategy>,
}

/// 合并策略
#[derive(Debug, Clone, Deserialize)]
pub enum MergeStrategy {
    /// 跳过重复项
    Skip,
    /// 覆盖重复项
    Overwrite,
    /// 合并重复项
    Merge,
}

/// 导入结果
#[derive(Debug, Serialize)]
pub struct ImportResult {
    /// 导入的告警数量
    pub imported_count: usize,
    /// 跳过的告警数量
    pub skipped_count: usize,
    /// 失败的告警数量
    pub failed_count: usize,
    /// 失败详情
    pub failures: Vec<ImportFailure>,
    /// 导入时间
    pub imported_at: chrono::DateTime<chrono::Utc>,
}

/// 导入失败项
#[derive(Debug, Serialize)]
pub struct ImportFailure {
    /// 行号或记录索引
    pub record_index: usize,
    /// 错误消息
    pub error_message: String,
    /// 原始数据
    pub raw_data: Option<serde_json::Value>,
}

/// 创建告警模板请求
#[derive(Debug, Deserialize)]
pub struct CreateAlertTemplateRequest {
    /// 模板名称
    pub name: String,
    /// 描述
    pub description: Option<String>,
    /// 告警类型
    pub alert_type: String,
    /// 严重程度
    pub severity: AlertSeverity,
    /// 标题模板
    pub title_template: String,
    /// 消息模板
    pub message_template: String,
    /// 元数据模板
    pub metadata_template: Option<serde_json::Value>,
}

/// 更新告警模板请求
#[derive(Debug, Deserialize)]
pub struct UpdateAlertTemplateRequest {
    /// 模板名称
    pub name: Option<String>,
    /// 描述
    pub description: Option<String>,
    /// 告警类型
    pub alert_type: Option<String>,
    /// 严重程度
    pub severity: Option<AlertSeverity>,
    /// 标题模板
    pub title_template: Option<String>,
    /// 消息模板
    pub message_template: Option<String>,
    /// 元数据模板
    pub metadata_template: Option<serde_json::Value>,
}

/// 告警模板
#[derive(Debug, Serialize, Deserialize)]
pub struct AlertTemplate {
    /// 模板ID
    pub id: String,
    /// 名称
    pub name: String,
    /// 描述
    pub description: Option<String>,
    /// 告警类型
    pub alert_type: String,
    /// 严重程度
    pub severity: AlertSeverity,
    /// 标题模板
    pub title_template: String,
    /// 消息模板
    pub message_template: String,
    /// 元数据模板
    pub metadata_template: Option<serde_json::Value>,
    /// 创建时间
    pub created_at: chrono::DateTime<chrono::Utc>,
    /// 更新时间
    pub updated_at: chrono::DateTime<chrono::Utc>,
    /// 使用次数
    pub usage_count: u64,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::services::AlertService;
    use actix_web::{test, App};

    #[actix_web::test]
    async fn test_alert_controller_routes() {
        let alert_service = Arc::new(AlertService::new().await.unwrap());
        let controller = AlertController::new(alert_service.clone());
        
        let app = test::init_service(
            App::new()
                .app_data(Data::new(alert_service))
                .configure(controller.configure)
        ).await;
        
        // 测试获取活跃告警
        let req = test::TestRequest::get()
            .uri("/alerts")
            .to_request();
        let resp = test::call_service(&app, req).await;
        assert!(resp.status().is_success());
        
        // 测试获取告警统计
        let req = test::TestRequest::get()
            .uri("/alerts/statistics")
            .to_request();
        let resp = test::call_service(&app, req).await;
        assert!(resp.status().is_success());
    }

    #[test]
    fn test_create_alert_request_deserialization() {
        let json = r#"{
            "alert_type": "temperature",
            "severity": "Critical",
            "title": "High Temperature",
            "message": "Temperature exceeded threshold"
        }"#;
        let request: CreateAlertRequest = serde_json::from_str(json).unwrap();
        
        assert_eq!(request.alert_type, "temperature");
        assert_eq!(request.title, "High Temperature");
    }

    #[test]
    fn test_export_format_deserialization() {
        let json = r#""Json""#;
        let format: ExportFormat = serde_json::from_str(json).unwrap();
        
        matches!(format, ExportFormat::Json);
    }
}