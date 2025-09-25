/// API控制器模块
/// 
/// 提供HTTP API接口，处理客户端请求并调用相应的服务

pub mod thermal_controller;
pub mod fan_controller;
// pub mod sensor_controller;
// pub mod analytics_controller;
// pub mod monitoring_controller;
// pub mod control_controller;
// pub mod alert_controller;
// pub mod config_controller;
// pub mod health_controller;

// 重新导出常用类型
pub use thermal_controller::ThermalController;
pub use fan_controller::FanController;
// pub use sensor_controller::SensorController;
// pub use analytics_controller::AnalyticsController;
// pub use monitoring_controller::MonitoringController;
// pub use control_controller::ControlController;
// pub use alert_controller::AlertController;
// pub use config_controller::ConfigController;
// pub use health_controller::HealthController;