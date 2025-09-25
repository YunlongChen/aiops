use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::process::Command;
use tracing::error;
use uuid::Uuid;

/// IPMI配置结构
#[derive(Debug, Clone)]
pub struct IpmiConfig {
    pub host: String,
    pub username: String,
    pub password: String,
    pub interface: String, // lanplus, lan, etc.
}

/// 温度传感器数据结构
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct TemperatureSensor {
    pub id: String,
    pub sensor_id: String,
    pub temperature: f64,
    pub unit: String,
    pub location: String,
    pub status: String,
    pub timestamp: DateTime<Utc>,
}

/// 风扇数据结构
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct FanSensor {
    pub id: String,
    pub fan_id: String,
    pub speed_rpm: u32,
    pub speed_percent: u8,
    pub status: String,
    pub location: String,
    pub control_mode: String,
    pub target_temp: Option<f64>,
    pub timestamp: DateTime<Utc>,
}

/// 系统信息结构
#[derive(Debug, Serialize, Deserialize)]
pub struct SystemInfo {
    pub manufacturer: String,
    pub device_id: String,
    pub firmware_version: String,
    pub ipmi_version: String,
    pub product_name: String,
    pub power_consumption: Option<f64>,
    pub voltage: Option<f64>,
    pub current: Option<f64>,
}

/// IPMI服务结构
pub struct IpmiService {
    config: IpmiConfig,
}

impl IpmiService {
    /// 创建新的IPMI服务实例
    pub fn new(config: IpmiConfig) -> Self {
        Self { config }
    }

    /// 执行IPMI命令
    fn execute_ipmi_command(&self, args: &[&str]) -> Result<String, Box<dyn std::error::Error>> {
        let mut cmd = Command::new("ipmitool");
        cmd.args(&["-I", &self.config.interface])
            .args(&["-H", &self.config.host])
            .args(&["-U", &self.config.username])
            .args(&["-P", &self.config.password])
            .args(args);

        let output = cmd.output()?;

        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).to_string())
        } else {
            let error = String::from_utf8_lossy(&output.stderr);
            Err(format!("IPMI command failed: {}", error).into())
        }
    }

    /// 获取系统基本信息
    pub fn get_system_info(&self) -> Result<SystemInfo, Box<dyn std::error::Error>> {
        let output = self.execute_ipmi_command(&["mc", "info"])?;

        let mut manufacturer = "Unknown".to_string();
        let mut device_id = "Unknown".to_string();
        let mut firmware_version = "Unknown".to_string();
        let mut ipmi_version = "Unknown".to_string();
        let mut product_name = "Unknown".to_string();

        for line in output.lines() {
            if line.contains("Manufacturer Name") {
                manufacturer = line
                    .split(':')
                    .nth(1)
                    .unwrap_or("Unknown")
                    .trim()
                    .to_string();
            } else if line.contains("Device ID") {
                device_id = line
                    .split(':')
                    .nth(1)
                    .unwrap_or("Unknown")
                    .trim()
                    .to_string();
            } else if line.contains("Firmware Revision") {
                firmware_version = line
                    .split(':')
                    .nth(1)
                    .unwrap_or("Unknown")
                    .trim()
                    .to_string();
            } else if line.contains("IPMI Version") {
                ipmi_version = line
                    .split(':')
                    .nth(1)
                    .unwrap_or("Unknown")
                    .trim()
                    .to_string();
            } else if line.contains("Product Name") {
                product_name = line
                    .split(':')
                    .nth(1)
                    .unwrap_or("Unknown")
                    .trim()
                    .to_string();
            }
        }

        // 获取电源信息
        let (power_consumption, voltage, current) =
            self.get_power_info().unwrap_or((None, None, None));

        Ok(SystemInfo {
            manufacturer,
            device_id,
            firmware_version,
            ipmi_version,
            product_name,
            power_consumption,
            voltage,
            current,
        })
    }

    /// 获取电源信息
    fn get_power_info(
        &self,
    ) -> Result<(Option<f64>, Option<f64>, Option<f64>), Box<dyn std::error::Error>> {
        let output = self.execute_ipmi_command(&["sdr", "list", "full"])?;

        let mut power_consumption = None;
        let mut voltage = None;
        let mut current = None;

        for line in output.lines() {
            if line.contains("Pwr Consumption") {
                if let Some(value_str) = line.split('|').nth(1) {
                    if let Ok(value) = value_str.trim().replace(" Watts", "").parse::<f64>() {
                        power_consumption = Some(value);
                    }
                }
            } else if line.contains("Voltage") && voltage.is_none() {
                if let Some(value_str) = line.split('|').nth(1) {
                    if let Ok(value) = value_str.trim().replace(" Volts", "").parse::<f64>() {
                        voltage = Some(value);
                    }
                }
            } else if line.contains("Current") && current.is_none() {
                if let Some(value_str) = line.split('|').nth(1) {
                    if let Ok(value) = value_str.trim().replace(" Amps", "").parse::<f64>() {
                        current = Some(value);
                    }
                }
            }
        }

        Ok((power_consumption, voltage, current))
    }

    /// 获取所有温度传感器数据
    pub fn get_temperature_sensors(
        &self,
    ) -> Result<Vec<TemperatureSensor>, Box<dyn std::error::Error>> {
        let output = self.execute_ipmi_command(&["sdr", "list", "full"])?;
        let mut sensors = Vec::new();
        let timestamp = Utc::now();

        for line in output.lines() {
            if line.contains("Temp") && line.contains("degrees C") {
                if let Some(parts) = self.parse_sensor_line(line) {
                    let (name, value_str, status) = parts;

                    if let Ok(temperature) =
                        value_str.replace(" degrees C", "").trim().parse::<f64>()
                    {
                        let sensor_id = name.trim().replace(" ", "_").to_uppercase();
                        let location = match sensor_id.as_str() {
                            "INLET_TEMP" => "Server Inlet",
                            "EXHAUST_TEMP" => "Server Exhaust",
                            _ => "Internal Sensor",
                        };

                        sensors.push(TemperatureSensor {
                            id: Uuid::new_v4().to_string(),
                            sensor_id,
                            temperature,
                            unit: "°C".to_string(),
                            location: location.to_string(),
                            status: status.to_lowercase(),
                            timestamp,
                        });
                    }
                }
            }
        }

        Ok(sensors)
    }

    /// 获取所有风扇数据
    pub fn get_fan_sensors(&self) -> Result<Vec<FanSensor>, Box<dyn std::error::Error>> {
        let output = self.execute_ipmi_command(&["sdr", "list", "full"])?;
        let mut fans = Vec::new();
        let timestamp = Utc::now();

        for line in output.lines() {
            if line.contains("Fan") && line.contains("RPM") {
                if let Some(parts) = self.parse_sensor_line(line) {
                    let (name, value_str, status) = parts;

                    if let Ok(speed_rpm) = value_str.replace(" RPM", "").trim().parse::<u32>() {
                        let fan_id = name.trim().replace(" ", "_").to_uppercase();

                        // 计算转速百分比 (假设最大转速为15000 RPM)
                        let speed_percent = ((speed_rpm as f64 / 15000.0) * 100.0).min(100.0) as u8;

                        let location = match fan_id.as_str() {
                            "FAN1" | "FAN2" => "Front Intake",
                            "FAN3" | "FAN4" => "CPU Cooling",
                            "FAN5" | "FAN6" => "Rear Exhaust",
                            _ => "Unknown Location",
                        };

                        fans.push(FanSensor {
                            id: Uuid::new_v4().to_string(),
                            fan_id,
                            speed_rpm,
                            speed_percent,
                            status: status.to_lowercase(),
                            location: location.to_string(),
                            control_mode: "auto".to_string(),
                            target_temp: None,
                            timestamp,
                        });
                    }
                }
            }
        }

        Ok(fans)
    }

    /// 解析传感器数据行
    fn parse_sensor_line(&self, line: &str) -> Option<(String, String, String)> {
        let parts: Vec<&str> = line.split('|').collect();
        if parts.len() >= 3 {
            let name = parts[0].trim().to_string();
            let value = parts[1].trim().to_string();
            let status = parts[2].trim().to_string();
            Some((name, value, status))
        } else {
            None
        }
    }

    /// 测试IPMI连接
    pub fn test_connection(&self) -> Result<bool, Box<dyn std::error::Error>> {
        match self.execute_ipmi_command(&["mc", "info"]) {
            Ok(_) => Ok(true),
            Err(e) => {
                error!("IPMI connection test failed: {}", e);
                Ok(false)
            }
        }
    }

    /// 获取特定温度传感器数据
    pub fn get_temperature_by_sensor(
        &self,
        sensor_id: &str,
    ) -> Result<Option<TemperatureSensor>, Box<dyn std::error::Error>> {
        let sensors = self.get_temperature_sensors()?;
        Ok(sensors.into_iter().find(|s| s.sensor_id == sensor_id))
    }

    /// 获取特定风扇数据
    pub fn get_fan_by_id(
        &self,
        fan_id: &str,
    ) -> Result<Option<FanSensor>, Box<dyn std::error::Error>> {
        let fans = self.get_fan_sensors()?;
        Ok(fans.into_iter().find(|f| f.fan_id == fan_id))
    }
}

/// 创建默认的IPMI配置
impl Default for IpmiConfig {
    fn default() -> Self {
        Self {
            host: "192.168.3.48".to_string(),
            username: "root".to_string(),
            password: "4745701816long".to_string(),
            interface: "lanplus".to_string(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ipmi_config_creation() {
        let config = IpmiConfig::default();
        assert_eq!(config.host, "192.168.3.48");
        assert_eq!(config.username, "root");
        assert_eq!(config.interface, "lanplus");
    }

    #[test]
    fn test_ipmi_service_creation() {
        let config = IpmiConfig::default();
        let service = IpmiService::new(config);
        // 基本的服务创建测试
        assert!(true); // 如果能创建服务就通过
    }
}
