use crate::models::{
    config::{IpmiConfig, ServerTarget},
    error::{AppError, AppResult},
    fan::{FanControlCommand, FanOperationStatus, FanStatus},
    sensor::{SensorReading, SensorStatus, SensorType},
    thermal::{TemperatureReading, TemperatureStatus},
    AlertThresholds, TemperatureThreshold,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::process::{Command, Stdio};
use std::time::Duration;
use tokio::time::timeout;
use tracing::{debug, error, info, warn};
use uuid::Uuid;

/// IPMI客户端
///
/// 提供与IPMI工具交互的功能
#[derive(Debug, Clone)]
pub struct IpmiClient {
    /// IPMI配置
    config: IpmiConfig,
    /// 当前连接的服务器
    current_server: Option<ServerTarget>,
}

/// IPMI命令类型
///
/// 定义支持的IPMI命令类型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum IpmiCommand {
    /// 获取传感器数据
    GetSensorData,
    /// 获取风扇状态
    GetFanStatus,
    /// 设置风扇转速
    SetFanSpeed { fan_id: String, speed_percent: u8 },
    /// 获取温度数据
    GetTemperature,
    /// 获取系统事件日志
    GetSystemEventLog,
    /// 获取电源状态
    GetPowerStatus,
    /// 设置电源状态
    SetPowerStatus { action: PowerAction },
    /// 获取系统信息
    GetSystemInfo,
    /// 重置BMC
    ResetBmc,
    /// 自定义命令
    Custom { command: String, args: Vec<String> },
}

/// 电源操作类型
///
/// 定义电源相关的操作
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PowerAction {
    /// 开机
    PowerOn,
    /// 关机
    PowerOff,
    /// 重启
    Reset,
    /// 软关机
    SoftShutdown,
}

/// IPMI命令结果
///
/// IPMI命令执行的结果
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IpmiResult {
    /// 命令是否成功
    pub success: bool,
    /// 返回的数据
    pub data: serde_json::Value,
    /// 错误消息（如果有）
    pub error_message: Option<String>,
    /// 执行时间
    pub execution_time: Duration,
    /// 原始输出
    pub raw_output: String,
}

/// 传感器数据解析结果
///
/// 解析IPMI传感器数据的结果
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SensorData {
    /// 传感器ID
    pub sensor_id: String,
    /// 传感器名称
    pub sensor_name: String,
    /// 传感器类型
    pub sensor_type: SensorType,
    /// 当前值
    pub current_value: f32,
    /// 单位
    pub unit: String,
    /// 状态
    pub status: SensorStatus,
    /// 阈值信息
    pub thresholds: Option<SensorThresholds>,
}

/// 传感器阈值信息
///
/// 传感器的各种阈值设置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SensorThresholds {
    /// 下临界阈值
    pub lower_critical: Option<f32>,
    /// 下非临界阈值
    pub lower_non_critical: Option<f32>,
    /// 上非临界阈值
    pub upper_non_critical: Option<f32>,
    /// 上临界阈值
    pub upper_critical: Option<f32>,
}

impl IpmiClient {
    /// 创建新的IPMI客户端
    ///
    /// # 参数
    /// * `config` - IPMI配置
    pub fn new(config: IpmiConfig) -> Self {
        Self {
            config,
            current_server: None,
        }
    }

    /// 连接到指定服务器
    ///
    /// # 参数
    /// * `server_id` - 服务器ID
    pub fn connect(&mut self, server_id: &str) -> AppResult<()> {
        let server = self
            .config
            .servers
            .iter()
            .find(|s| s.id == server_id)
            .ok_or_else(|| AppError::not_found_error("server", server_id))?;

        if !server.enabled {
            return Err(AppError::ipmi_error(format!("服务器 {} 未启用", server_id)));
        }

        // 测试连接
        self.test_connection(server)?;

        self.current_server = Some(server.clone());
        info!("已连接到服务器: {}", server.name);

        Ok(())
    }

    /// 测试与服务器的连接
    ///
    /// # 参数
    /// * `server` - 服务器配置
    fn test_connection(&self, server: &ServerTarget) -> AppResult<()> {
        let mut cmd = Command::new(&self.config.ipmitool_path);
        cmd.args(&[
            "-I",
            &server.interface,
            "-H",
            &server.host,
            "-p",
            &server.port.to_string(),
            "-U",
            &server.username,
            "-P",
            &server.password,
            "chassis",
            "status",
        ]);

        debug!("测试IPMI连接: {:?}", cmd);

        let output = cmd
            .output()
            .map_err(|e| AppError::ipmi_error(format!("执行IPMI命令失败: {}", e)))?;

        if !output.status.success() {
            let error_msg = String::from_utf8_lossy(&output.stderr);
            return Err(AppError::ipmi_error(format!(
                "IPMI连接测试失败: {}",
                error_msg
            )));
        }

        Ok(())
    }

    /// 执行IPMI命令
    ///
    /// # 参数
    /// * `command` - IPMI命令
    pub async fn execute_command(&self, command: IpmiCommand) -> AppResult<IpmiResult> {
        let server = self
            .current_server
            .as_ref()
            .ok_or_else(|| AppError::ipmi_error("未连接到任何服务器"))?;

        let start_time = std::time::Instant::now();

        let (cmd_args, parser) = self.build_command_args(&command)?;

        let mut cmd = Command::new(&self.config.ipmitool_path);
        cmd.args(&[
            "-I",
            &server.interface,
            "-H",
            &server.host,
            "-p",
            &server.port.to_string(),
            "-U",
            &server.username,
            "-P",
            &server.password,
        ]);
        cmd.args(&cmd_args);
        cmd.stdout(Stdio::piped());
        cmd.stderr(Stdio::piped());

        debug!("执行IPMI命令: {:?}", cmd);

        // 使用超时执行命令
        let output = timeout(
            Duration::from_secs(self.config.default_timeout),
            tokio::task::spawn_blocking(move || cmd.output()),
        )
        .await
        .map_err(|_| AppError::TimeoutError {
            operation: "IPMI命令执行".to_string(),
        })?
        .map_err(|e| AppError::ipmi_error(format!("执行IPMI命令失败: {}", e)))?
        .map_err(|e| AppError::ipmi_error(format!("IPMI命令执行错误: {}", e)))?;

        let execution_time = start_time.elapsed();
        let raw_output = String::from_utf8_lossy(&output.stdout).to_string();

        if !output.status.success() {
            let error_msg = String::from_utf8_lossy(&output.stderr);
            return Ok(IpmiResult {
                success: false,
                data: serde_json::Value::Null,
                error_message: Some(error_msg.to_string()),
                execution_time,
                raw_output,
            });
        }

        // 解析输出
        let parsed_data = parser(&raw_output)?;

        Ok(IpmiResult {
            success: true,
            data: parsed_data,
            error_message: None,
            execution_time,
            raw_output,
        })
    }

    /// 构建命令参数和解析器
    ///
    /// # 参数
    /// * `command` - IPMI命令
    fn build_command_args(
        &self,
        command: &IpmiCommand,
    ) -> AppResult<(Vec<String>, fn(&str) -> AppResult<serde_json::Value>)> {
        match command {
            IpmiCommand::GetSensorData => Ok((
                vec!["sdr".to_string(), "list".to_string(), "full".to_string()],
                Self::parse_sensor_data,
            )),
            IpmiCommand::GetFanStatus => Ok((
                vec!["sdr".to_string(), "type".to_string(), "Fan".to_string()],
                Self::parse_fan_data,
            )),
            IpmiCommand::SetFanSpeed {
                fan_id,
                speed_percent,
            } => {
                let args = vec![
                    "raw".to_string(),
                    "0x30".to_string(),
                    "0x30".to_string(),
                    "0x02".to_string(),
                    "0xff".to_string(),
                    format!("0x{:02x}", speed_percent),
                ];
                Ok((args, Self::parse_raw_response))
            }
            IpmiCommand::GetTemperature => Ok((
                vec![
                    "sdr".to_string(),
                    "type".to_string(),
                    "Temperature".to_string(),
                ],
                Self::parse_temperature_data,
            )),
            IpmiCommand::GetSystemEventLog => Ok((
                vec!["sel".to_string(), "list".to_string()],
                Self::parse_event_log,
            )),
            IpmiCommand::GetPowerStatus => Ok((
                vec![
                    "chassis".to_string(),
                    "power".to_string(),
                    "status".to_string(),
                ],
                Self::parse_power_status,
            )),
            IpmiCommand::SetPowerStatus { action } => {
                let action_str = match action {
                    PowerAction::PowerOn => "on",
                    PowerAction::PowerOff => "off",
                    PowerAction::Reset => "reset",
                    PowerAction::SoftShutdown => "soft",
                };
                Ok((
                    vec![
                        "chassis".to_string(),
                        "power".to_string(),
                        action_str.to_string(),
                    ],
                    Self::parse_power_action,
                ))
            }
            IpmiCommand::GetSystemInfo => Ok((
                vec!["fru".to_string(), "print".to_string()],
                Self::parse_system_info,
            )),
            IpmiCommand::ResetBmc => Ok((
                vec!["bmc".to_string(), "reset".to_string(), "cold".to_string()],
                Self::parse_raw_response,
            )),
            IpmiCommand::Custom { command, args } => {
                let mut cmd_args = vec![command.clone()];
                cmd_args.extend(args.clone());
                Ok((cmd_args, Self::parse_raw_response))
            }
        }
    }

    /// 解析传感器数据
    ///
    /// # 参数
    /// * `output` - IPMI命令输出
    fn parse_sensor_data(output: &str) -> AppResult<serde_json::Value> {
        let mut sensors = Vec::new();

        for line in output.lines() {
            if line.trim().is_empty() {
                continue;
            }

            let parts: Vec<&str> = line.split('|').collect();
            if parts.len() >= 3 {
                let sensor_name = parts[0].trim();
                let value_str = parts[1].trim();
                let status_str = parts[2].trim();

                // 解析传感器值
                let (value, unit) = Self::parse_sensor_value(value_str);

                let sensor = SensorData {
                    sensor_id: sensor_name.replace(" ", "_").to_lowercase(),
                    sensor_name: sensor_name.to_string(),
                    sensor_type: Self::determine_sensor_type(sensor_name),
                    current_value: value,
                    unit,
                    status: Self::parse_sensor_status(status_str),
                    thresholds: None, // 需要额外的命令获取阈值信息
                };

                sensors.push(sensor);
            }
        }

        Ok(serde_json::to_value(sensors)?)
    }

    /// 解析风扇数据
    ///
    /// # 参数
    /// * `output` - IPMI命令输出
    fn parse_fan_data(output: &str) -> AppResult<serde_json::Value> {
        let mut fans = Vec::new();

        for line in output.lines() {
            if line.trim().is_empty() || !line.to_lowercase().contains("fan") {
                continue;
            }

            let parts: Vec<&str> = line.split('|').collect();
            if parts.len() >= 3 {
                let fan_name = parts[0].trim();
                let value_str = parts[1].trim();
                let status_str = parts[2].trim();

                let (rpm, _) = Self::parse_sensor_value(value_str);

                let fan_status = FanStatus::new(
                    fan_name.replace(" ", "_").to_lowercase(),
                    fan_name.to_string(),
                    rpm,
                    Self::rpm_to_percentage(rpm),
                    "".into(),
                );

                fans.push(fan_status);
            }
        }

        Ok(serde_json::to_value(fans)?)
    }

    /// 解析温度数据
    ///
    /// # 参数
    /// * `output` - IPMI命令输出
    fn parse_temperature_data(output: &str) -> AppResult<serde_json::Value> {
        let mut temperatures = Vec::new();

        for line in output.lines() {
            if line.trim().is_empty() || !line.to_lowercase().contains("temp") {
                continue;
            }

            let parts: Vec<&str> = line.split('|').collect();
            if parts.len() >= 3 {
                let sensor_name = parts[0].trim();
                let value_str = parts[1].trim();
                let status_str = parts[2].trim();

                let (temperature, _) = Self::parse_sensor_value(value_str);

                let temp_reading = TemperatureReading::new(
                    Uuid::new_v4().to_string(),
                    sensor_name.replace(" ", "_").to_lowercase(),
                    temperature as f64,
                    ".".into(),
                    &TemperatureThreshold::default(),
                );

                temperatures.push(temp_reading);
            }
        }

        Ok(serde_json::to_value(temperatures)?)
    }

    /// 解析事件日志
    ///
    /// # 参数
    /// * `output` - IPMI命令输出
    fn parse_event_log(output: &str) -> AppResult<serde_json::Value> {
        let mut events = Vec::new();

        for line in output.lines() {
            if line.trim().is_empty() {
                continue;
            }

            // 简单的事件日志解析
            let event = serde_json::json!({
                "raw_line": line,
                "timestamp": Utc::now(),
            });

            events.push(event);
        }

        Ok(serde_json::to_value(events)?)
    }

    /// 解析电源状态
    ///
    /// # 参数
    /// * `output` - IPMI命令输出
    fn parse_power_status(output: &str) -> AppResult<serde_json::Value> {
        let is_on = output.to_lowercase().contains("power is on");

        Ok(serde_json::json!({
            "power_on": is_on,
            "raw_status": output.trim(),
        }))
    }

    /// 解析电源操作结果
    ///
    /// # 参数
    /// * `output` - IPMI命令输出
    fn parse_power_action(output: &str) -> AppResult<serde_json::Value> {
        Ok(serde_json::json!({
            "result": output.trim(),
            "timestamp": Utc::now(),
        }))
    }

    /// 解析系统信息
    ///
    /// # 参数
    /// * `output` - IPMI命令输出
    fn parse_system_info(output: &str) -> AppResult<serde_json::Value> {
        let mut info = HashMap::new();

        for line in output.lines() {
            if let Some(colon_pos) = line.find(':') {
                let key = line[..colon_pos].trim();
                let value = line[colon_pos + 1..].trim();
                info.insert(key.to_string(), value.to_string());
            }
        }

        Ok(serde_json::to_value(info)?)
    }

    /// 解析原始响应
    ///
    /// # 参数
    /// * `output` - IPMI命令输出
    fn parse_raw_response(output: &str) -> AppResult<serde_json::Value> {
        Ok(serde_json::json!({
            "raw_output": output.trim(),
            "timestamp": Utc::now(),
        }))
    }

    /// 解析传感器值
    ///
    /// # 参数
    /// * `value_str` - 值字符串
    fn parse_sensor_value(value_str: &str) -> (f32, String) {
        if value_str == "na" || value_str == "disabled" {
            return (0.0, "".to_string());
        }

        // 尝试解析数值和单位
        let parts: Vec<&str> = value_str.split_whitespace().collect();
        if parts.len() >= 2 {
            if let Ok(value) = parts[0].parse::<f32>() {
                return (value, parts[1].to_string());
            }
        } else if parts.len() == 1 {
            if let Ok(value) = parts[0].parse::<f32>() {
                return (value, "".to_string());
            }
        }

        (0.0, "".to_string())
    }

    /// 确定传感器类型
    ///
    /// # 参数
    /// * `sensor_name` - 传感器名称
    fn determine_sensor_type(sensor_name: &str) -> SensorType {
        let name_lower = sensor_name.to_lowercase();

        if name_lower.contains("temp") {
            SensorType::Temperature
        } else if name_lower.contains("fan") {
            SensorType::Fan
        } else if name_lower.contains("volt") {
            SensorType::Voltage
        } else if name_lower.contains("current") {
            SensorType::Current
        } else if name_lower.contains("power") {
            SensorType::Power
        } else {
            SensorType::Other(sensor_name.to_string())
        }
    }

    /// 解析传感器状态
    ///
    /// # 参数
    /// * `status_str` - 状态字符串
    fn parse_sensor_status(status_str: &str) -> SensorStatus {
        match status_str.to_lowercase().as_str() {
            "ok" => SensorStatus::Ok,
            "nc" | "nr" => SensorStatus::NotAvailable,
            "unc" => SensorStatus::Warning,
            "ucr" | "lnr" | "lcr" => SensorStatus::Critical,
            _ => SensorStatus::NotAvailable,
        }
    }

    /// 将RPM转换为百分比
    ///
    /// # 参数
    /// * `rpm` - 转速（RPM）
    fn rpm_to_percentage(rpm: f32) -> f32 {
        // 假设最大转速为6000 RPM
        const MAX_RPM: f32 = 6000.0;
        (rpm / MAX_RPM * 100.0).min(100.0).max(0.0)
    }

    /// 获取所有传感器数据
    ///
    /// 获取服务器的所有传感器数据
    pub async fn get_all_sensors(&self) -> AppResult<Vec<SensorReading>> {
        let result = self.execute_command(IpmiCommand::GetSensorData).await?;

        if !result.success {
            return Err(AppError::ipmi_error(
                result
                    .error_message
                    .unwrap_or_else(|| "获取传感器数据失败".to_string()),
            ));
        }

        let sensor_data: Vec<SensorData> = serde_json::from_value(result.data.clone())?;
        let mut readings = Vec::new();

        for sensor in sensor_data {
            // todo 这里的内容不完全对
            let reading = SensorReading::new(
                sensor.sensor_id,
                sensor.current_value as f64,
                &AlertThresholds::default(),
                None,
            );
            readings.push(reading);
        }

        Ok(readings)
    }

    /// 获取温度数据
    ///
    /// 获取服务器的温度传感器数据
    pub async fn get_temperatures(&self) -> AppResult<Vec<TemperatureReading>> {
        let result = self.execute_command(IpmiCommand::GetTemperature).await?;

        if !result.success {
            return Err(AppError::ipmi_error(
                result
                    .error_message
                    .unwrap_or_else(|| "获取温度数据失败".to_string()),
            ));
        }

        let temperatures: Vec<TemperatureReading> = serde_json::from_value(result.data)?;
        Ok(temperatures)
    }

    /// 获取风扇状态
    ///
    /// 获取服务器的风扇状态数据
    pub async fn get_fan_status(&self) -> AppResult<Vec<FanStatus>> {
        let result = self.execute_command(IpmiCommand::GetFanStatus).await?;

        if !result.success {
            return Err(AppError::ipmi_error(
                result
                    .error_message
                    .unwrap_or_else(|| "获取风扇状态失败".to_string()),
            ));
        }

        let fans: Vec<FanStatus> = serde_json::from_value(result.data)?;
        Ok(fans)
    }

    /// 设置风扇转速
    ///
    /// # 参数
    /// * `fan_id` - 风扇ID
    /// * `speed_percent` - 转速百分比
    pub async fn set_fan_speed(&self, fan_id: &str, speed_percent: u8) -> AppResult<()> {
        if speed_percent > 100 {
            return Err(AppError::validation_error(
                "speed_percent",
                "转速百分比不能超过100",
            ));
        }

        let command = IpmiCommand::SetFanSpeed {
            fan_id: fan_id.to_string(),
            speed_percent,
        };

        let result = self.execute_command(command).await?;

        if !result.success {
            return Err(AppError::ipmi_error(
                result
                    .error_message
                    .unwrap_or_else(|| "设置风扇转速失败".to_string()),
            ));
        }

        info!("成功设置风扇 {} 转速为 {}%", fan_id, speed_percent);
        Ok(())
    }

    /// 断开连接
    ///
    /// 断开与当前服务器的连接
    pub fn disconnect(&mut self) {
        if let Some(server) = &self.current_server {
            info!("断开与服务器 {} 的连接", server.name);
        }
        self.current_server = None;
    }

    /// 获取当前连接的服务器
    ///
    /// 返回当前连接的服务器信息
    pub fn current_server(&self) -> Option<&ServerTarget> {
        self.current_server.as_ref()
    }

    /// 检查连接状态
    ///
    /// 检查是否已连接到服务器
    pub fn is_connected(&self) -> bool {
        self.current_server.is_some()
    }
}
