use crate::models::error::{AppError, AppResult};
use regex::Regex;
use std::collections::HashMap;
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr};
use std::str::FromStr;

/// 验证器特征
///
/// 定义验证器的通用接口
pub trait Validator<T> {
    /// 验证值
    ///
    /// # 参数
    /// * `value` - 要验证的值
    ///
    /// # 返回
    /// 验证结果，成功返回Ok(())，失败返回错误信息
    fn validate(&self, value: &T) -> AppResult<()>;
}

/// 字符串验证器
///
/// 提供各种字符串验证功能
#[derive(Debug, Clone)]
pub struct StringValidator {
    /// 最小长度
    min_length: Option<usize>,
    /// 最大长度
    max_length: Option<usize>,
    /// 正则表达式模式
    pattern: Option<Regex>,
    /// 是否允许空字符串
    allow_empty: bool,
    /// 是否只允许ASCII字符
    ascii_only: bool,
}

impl StringValidator {
    /// 创建新的字符串验证器
    pub fn new() -> Self {
        Self {
            min_length: None,
            max_length: None,
            pattern: None,
            allow_empty: true,
            ascii_only: false,
        }
    }

    /// 设置最小长度
    ///
    /// # 参数
    /// * `min` - 最小长度
    pub fn min_length(mut self, min: usize) -> Self {
        self.min_length = Some(min);
        self
    }

    /// 设置最大长度
    ///
    /// # 参数
    /// * `max` - 最大长度
    pub fn max_length(mut self, max: usize) -> Self {
        self.max_length = Some(max);
        self
    }

    /// 设置正则表达式模式
    ///
    /// # 参数
    /// * `pattern` - 正则表达式字符串
    pub fn pattern(mut self, pattern: &str) -> AppResult<Self> {
        self.pattern = Some(Regex::new(pattern).map_err(|e| {
            AppError::validation_error("pattern", &format!("无效的正则表达式: {}", e))
        })?);
        Ok(self)
    }

    /// 设置是否允许空字符串
    ///
    /// # 参数
    /// * `allow` - 是否允许
    pub fn allow_empty(mut self, allow: bool) -> Self {
        self.allow_empty = allow;
        self
    }

    /// 设置是否只允许ASCII字符
    ///
    /// # 参数
    /// * `ascii_only` - 是否只允许ASCII
    pub fn ascii_only(mut self, ascii_only: bool) -> Self {
        self.ascii_only = ascii_only;
        self
    }
}

impl Validator<String> for StringValidator {
    fn validate(&self, value: &String) -> AppResult<()> {
        // 检查空字符串
        if value.is_empty() && !self.allow_empty {
            return Err(AppError::validation_error("string", "不能为空"));
        }

        // 检查长度
        if let Some(min) = self.min_length {
            if value.len() < min {
                return Err(AppError::validation_error(
                    "string",
                    &format!("长度不能少于{}个字符", min),
                ));
            }
        }

        if let Some(max) = self.max_length {
            if value.len() > max {
                return Err(AppError::validation_error(
                    "string",
                    &format!("长度不能超过{}个字符", max),
                ));
            }
        }

        // 检查ASCII
        if self.ascii_only && !value.is_ascii() {
            return Err(AppError::validation_error("string", "只能包含ASCII字符"));
        }

        // 检查正则表达式
        if let Some(ref pattern) = self.pattern {
            if !pattern.is_match(value) {
                return Err(AppError::validation_error("string", "格式不正确"));
            }
        }

        Ok(())
    }
}

/// 数值验证器
///
/// 提供数值范围验证功能
#[derive(Debug, Clone)]
pub struct NumberValidator<T> {
    /// 最小值
    min_value: Option<T>,
    /// 最大值
    max_value: Option<T>,
}

impl<T> NumberValidator<T>
where
    T: PartialOrd + Copy,
{
    /// 创建新的数值验证器
    pub fn new() -> Self {
        Self {
            min_value: None,
            max_value: None,
        }
    }

    /// 设置最小值
    ///
    /// # 参数
    /// * `min` - 最小值
    pub fn min_value(mut self, min: T) -> Self {
        self.min_value = Some(min);
        self
    }

    /// 设置最大值
    ///
    /// # 参数
    /// * `max` - 最大值
    pub fn max_value(mut self, max: T) -> Self {
        self.max_value = Some(max);
        self
    }

    /// 设置值范围
    ///
    /// # 参数
    /// * `min` - 最小值
    /// * `max` - 最大值
    pub fn range(mut self, min: T, max: T) -> Self {
        self.min_value = Some(min);
        self.max_value = Some(max);
        self
    }
}

impl<T> Validator<T> for NumberValidator<T>
where
    T: PartialOrd + Copy + std::fmt::Display,
{
    fn validate(&self, value: &T) -> AppResult<()> {
        if let Some(min) = self.min_value {
            if *value < min {
                return Err(AppError::validation_error(
                    "number",
                    &format!("值不能小于{}", min),
                ));
            }
        }

        if let Some(max) = self.max_value {
            if *value > max {
                return Err(AppError::validation_error(
                    "number",
                    &format!("值不能大于{}", max),
                ));
            }
        }

        Ok(())
    }
}

/// 验证工具集
///
/// 提供常用的验证功能
pub struct ValidationUtils;

/// 验证温度值
///
/// # 参数
/// * `temperature` - 温度值（摄氏度）
pub fn validate_temperature(temperature: f64) -> AppResult<()> {
    if temperature < -273.15 {
        return Err(AppError::validation_error(
            "temperature",
            "温度不能低于绝对零度",
        ));
    }
    if temperature > 200.0 {
        return Err(AppError::validation_error("temperature", "温度过高"));
    }
    Ok(())
}

/// 验证风扇转速
///
/// # 参数
/// * `rpm` - 风扇转速（RPM）
pub fn validate_fan_speed(rpm: u32) -> AppResult<()> {
    if rpm > 10000 {
        return Err(AppError::validation_error("fan_speed", "风扇转速过高"));
    }
    Ok(())
}

impl ValidationUtils {
    /// 验证电子邮件地址
    ///
    /// # 参数
    /// * `email` - 电子邮件地址
    pub fn validate_email(email: &str) -> AppResult<()> {
        let email_regex = Regex::new(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
            .map_err(|e| AppError::internal_server_error(format!("正则表达式错误: {}", e)))?;

        if email_regex.is_match(email) {
            Ok(())
        } else {
            Err(AppError::validation_error("email", "无效的电子邮件地址"))
        }
    }

    /// 验证IP地址
    ///
    /// # 参数
    /// * `ip` - IP地址字符串
    pub fn validate_ip_address(ip: &str) -> AppResult<IpAddr> {
        ip.parse::<IpAddr>()
            .map_err(|_| AppError::validation_error("ip_address", "无效的IP地址"))
    }

    /// 验证IPv4地址
    ///
    /// # 参数
    /// * `ip` - IPv4地址字符串
    pub fn validate_ipv4_address(ip: &str) -> AppResult<Ipv4Addr> {
        ip.parse::<Ipv4Addr>()
            .map_err(|_| AppError::validation_error("ipv4_address", "无效的IPv4地址"))
    }

    /// 验证IPv6地址
    ///
    /// # 参数
    /// * `ip` - IPv6地址字符串
    pub fn validate_ipv6_address(ip: &str) -> AppResult<Ipv6Addr> {
        ip.parse::<Ipv6Addr>()
            .map_err(|_| AppError::validation_error("ipv6_address", "无效的IPv6地址"))
    }

    /// 验证端口号
    ///
    /// # 参数
    /// * `port` - 端口号
    pub fn validate_port(port: u16) -> AppResult<()> {
        if port == 0 {
            Err(AppError::validation_error("port", "端口号不能为0"))
        } else {
            Ok(())
        }
    }

    /// 验证URL
    ///
    /// # 参数
    /// * `url` - URL字符串
    pub fn validate_url(url: &str) -> AppResult<()> {
        let url_regex = Regex::new(r"^https?://[^\s/$.?#].[^\s]*$")
            .map_err(|e| AppError::internal_server_error(format!("正则表达式错误: {}", e)))?;

        if url_regex.is_match(url) {
            Ok(())
        } else {
            Err(AppError::validation_error("url", "无效的URL"))
        }
    }

    /// 验证UUID
    ///
    /// # 参数
    /// * `uuid` - UUID字符串
    pub fn validate_uuid(uuid: &str) -> AppResult<uuid::Uuid> {
        uuid::Uuid::from_str(uuid).map_err(|_| AppError::validation_error("uuid", "无效的UUID"))
    }

    /// 验证温度值
    ///
    /// # 参数
    /// * `temperature` - 温度值（摄氏度）
    pub fn validate_temperature(temperature: f64) -> AppResult<()> {
        if temperature < -273.15 {
            Err(AppError::validation_error(
                "temperature",
                "温度不能低于绝对零度",
            ))
        } else if temperature > 200.0 {
            Err(AppError::validation_error(
                "temperature",
                "温度值过高，可能不正确",
            ))
        } else {
            Ok(())
        }
    }

    /// 验证风扇转速
    ///
    /// # 参数
    /// * `rpm` - 转速（RPM）
    pub fn validate_fan_speed(rpm: u32) -> AppResult<()> {
        if rpm > 10000 {
            Err(AppError::validation_error("fan_speed", "风扇转速过高"))
        } else {
            Ok(())
        }
    }

    /// 验证百分比值
    ///
    /// # 参数
    /// * `percentage` - 百分比值（0-100）
    pub fn validate_percentage(percentage: f64) -> AppResult<()> {
        if percentage < 0.0 || percentage > 100.0 {
            Err(AppError::validation_error(
                "percentage",
                "百分比值必须在0-100之间",
            ))
        } else {
            Ok(())
        }
    }

    /// 验证时间间隔（秒）
    ///
    /// # 参数
    /// * `interval` - 时间间隔
    pub fn validate_time_interval(interval: u64) -> AppResult<()> {
        if interval == 0 {
            Err(AppError::validation_error(
                "time_interval",
                "时间间隔不能为0",
            ))
        } else if interval > 86400 {
            Err(AppError::validation_error(
                "time_interval",
                "时间间隔不能超过24小时",
            ))
        } else {
            Ok(())
        }
    }

    /// 验证文件路径
    ///
    /// # 参数
    /// * `path` - 文件路径
    pub fn validate_file_path(path: &str) -> AppResult<()> {
        if path.is_empty() {
            return Err(AppError::validation_error("file_path", "文件路径不能为空"));
        }

        // 检查危险字符
        let dangerous_chars = ['<', '>', ':', '"', '|', '?', '*'];
        if path.chars().any(|c| dangerous_chars.contains(&c)) {
            return Err(AppError::validation_error(
                "file_path",
                "文件路径包含非法字符",
            ));
        }

        // 检查路径遍历攻击
        if path.contains("..") {
            return Err(AppError::validation_error(
                "file_path",
                "文件路径不能包含'..'",
            ));
        }

        Ok(())
    }

    /// 验证主机名
    ///
    /// # 参数
    /// * `hostname` - 主机名
    pub fn validate_hostname(hostname: &str) -> AppResult<()> {
        if hostname.is_empty() {
            return Err(AppError::validation_error("hostname", "主机名不能为空"));
        }

        if hostname.len() > 253 {
            return Err(AppError::validation_error(
                "hostname",
                "主机名长度不能超过253个字符",
            ));
        }

        let hostname_regex = Regex::new(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$")
            .map_err(|e| AppError::internal_server_error(format!("正则表达式错误: {}", e)))?;

        if hostname_regex.is_match(hostname) {
            Ok(())
        } else {
            Err(AppError::validation_error("hostname", "无效的主机名"))
        }
    }
}

/// 复合验证器
///
/// 可以组合多个验证器
pub struct CompositeValidator<T> {
    validators: Vec<Box<dyn Validator<T>>>,
}

impl<T> CompositeValidator<T> {
    /// 创建新的复合验证器
    pub fn new() -> Self {
        Self {
            validators: Vec::new(),
        }
    }

    /// 添加验证器
    ///
    /// # 参数
    /// * `validator` - 要添加的验证器
    pub fn add_validator(mut self, validator: Box<dyn Validator<T>>) -> Self {
        self.validators.push(validator);
        self
    }
}

impl<T> Validator<T> for CompositeValidator<T> {
    fn validate(&self, value: &T) -> AppResult<()> {
        for validator in &self.validators {
            validator.validate(value)?;
        }
        Ok(())
    }
}

/// 验证结果收集器
///
/// 收集所有验证错误，而不是在第一个错误时停止
pub struct ValidationResultCollector {
    errors: HashMap<String, Vec<String>>,
}

impl ValidationResultCollector {
    /// 创建新的验证结果收集器
    pub fn new() -> Self {
        Self {
            errors: HashMap::new(),
        }
    }

    /// 添加验证结果
    ///
    /// # 参数
    /// * `field` - 字段名
    /// * `result` - 验证结果
    pub fn add_result(&mut self, field: &str, result: AppResult<()>) {
        if let Err(error) = result {
            self.errors
                .entry(field.to_string())
                .or_insert_with(Vec::new)
                .push(error.to_string());
        }
    }

    /// 检查是否有错误
    pub fn has_errors(&self) -> bool {
        !self.errors.is_empty()
    }

    /// 获取所有错误
    pub fn get_errors(&self) -> &HashMap<String, Vec<String>> {
        &self.errors
    }

    /// 转换为验证错误
    pub fn into_validation_error(self) -> AppResult<()> {
        if self.has_errors() {
            let error_message = self
                .errors
                .iter()
                .map(|(field, errors)| format!("{}: {}", field, errors.join(", ")))
                .collect::<Vec<_>>()
                .join("; ");

            Err(AppError::validation_error("validation", &error_message))
        } else {
            Ok(())
        }
    }
}

/// 条件验证器
///
/// 根据条件决定是否执行验证
pub struct ConditionalValidator<T, F>
where
    F: Fn(&T) -> bool,
{
    condition: F,
    validator: Box<dyn Validator<T>>,
}

impl<T, F> ConditionalValidator<T, F>
where
    F: Fn(&T) -> bool,
{
    /// 创建新的条件验证器
    ///
    /// # 参数
    /// * `condition` - 条件函数
    /// * `validator` - 验证器
    pub fn new(condition: F, validator: Box<dyn Validator<T>>) -> Self {
        Self {
            condition,
            validator,
        }
    }
}

impl<T, F> Validator<T> for ConditionalValidator<T, F>
where
    F: Fn(&T) -> bool,
{
    fn validate(&self, value: &T) -> AppResult<()> {
        if (self.condition)(value) {
            self.validator.validate(value)
        } else {
            Ok(())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_string_validator() {
        let validator = StringValidator::new()
            .min_length(3)
            .max_length(10)
            .allow_empty(false);

        assert!(validator.validate(&"hello".to_string()).is_ok());
        assert!(validator.validate(&"hi".to_string()).is_err()); // 太短
        assert!(validator.validate(&"hello world".to_string()).is_err()); // 太长
        assert!(validator.validate(&"".to_string()).is_err()); // 空字符串
    }

    #[test]
    fn test_number_validator() {
        let validator = NumberValidator::new().min_value(0).max_value(100);

        assert!(validator.validate(&50).is_ok());
        assert!(validator.validate(&-1).is_err()); // 太小
        assert!(validator.validate(&101).is_err()); // 太大
    }

    #[test]
    fn test_email_validation() {
        assert!(ValidationUtils::validate_email("test@example.com").is_ok());
        assert!(ValidationUtils::validate_email("invalid-email").is_err());
        assert!(ValidationUtils::validate_email("test@").is_err());
    }

    #[test]
    fn test_ip_validation() {
        assert!(ValidationUtils::validate_ip_address("192.168.1.1").is_ok());
        assert!(ValidationUtils::validate_ip_address("::1").is_ok());
        assert!(ValidationUtils::validate_ip_address("invalid-ip").is_err());
    }

    #[test]
    fn test_temperature_validation() {
        assert!(ValidationUtils::validate_temperature(25.0).is_ok());
        assert!(ValidationUtils::validate_temperature(-300.0).is_err()); // 低于绝对零度
        assert!(ValidationUtils::validate_temperature(250.0).is_err()); // 过高
    }

    #[test]
    fn test_validation_result_collector() {
        let mut collector = ValidationResultCollector::new();

        collector.add_result("field1", Ok(()));
        collector.add_result("field2", Err(AppError::validation_error("field2", "错误")));

        assert!(collector.has_errors());
        assert_eq!(collector.get_errors().len(), 1);
        assert!(collector.into_validation_error().is_err());
    }

    #[test]
    fn test_composite_validator() {
        let validator = CompositeValidator::new()
            .add_validator(Box::new(NumberValidator::new().min_value(0)))
            .add_validator(Box::new(NumberValidator::new().max_value(100)));

        assert!(validator.validate(&50).is_ok());
        assert!(validator.validate(&-1).is_err());
        assert!(validator.validate(&101).is_err());
    }
}
