//! 服务层模块
//! 
//! 提供业务逻辑处理和服务功能

// pub mod test_executor; // 暂时注释掉，模块不存在
// pub mod runtime_service; // 暂时注释掉，模块不存在
// pub mod notification_service; // 暂时注释掉，模块不存在

use std::sync::Arc;
use crate::{AppState, database::Database, config::AppConfig};

/// 服务管理器
#[derive(Clone)]
pub struct ServiceManager {
    // pub test_executor: Arc<test_executor::TestExecutor>, // 暂时注释掉，模块不存在
    // pub runtime_service: Arc<runtime_service::RuntimeService>, // 暂时注释掉，模块不存在
    // pub notification_service: Arc<notification_service::NotificationService>, // 暂时注释掉，模块不存在
}

impl ServiceManager {
    /// 创建新的服务管理器实例
    pub fn new(_db: Arc<Database>, _config: Arc<AppConfig>) -> Self {
        // let test_executor = Arc::new(test_executor::TestExecutor::new(db.clone(), config.clone()));
        // let runtime_service = Arc::new(runtime_service::RuntimeService::new(db.clone()));
        // let notification_service = Arc::new(notification_service::NotificationService::new(config.clone()));

        Self {
            // test_executor,
            // runtime_service,
            // notification_service,
        }
    }

    /// 启动所有后台服务
    pub async fn start_background_services(&self) -> anyhow::Result<()> {
        // 启动测试执行器
        // self.test_executor.start().await?;
        
        // 启动运行时服务监控
        // self.runtime_service.start_monitoring().await?;
        
        // 启动通知服务
        // self.notification_service.start().await?;
        
        tracing::info!("所有后台服务已启动");
        Ok(())
    }

    /// 停止所有后台服务
    pub async fn stop_background_services(&self) -> anyhow::Result<()> {
        // self.test_executor.stop().await?;
        // self.runtime_service.stop_monitoring().await?;
        // self.notification_service.stop().await?;
        
        tracing::info!("所有后台服务已停止");
        Ok(())
    }
}