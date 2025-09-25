use crate::models::error::{AppError, AppResult};
use chrono::{DateTime, Duration, Local, TimeZone, Utc};
use std::collections::HashMap;
use std::time::Instant;

/// 时间工具集
///
/// 提供时间处理、格式化和计算功能
#[derive(Clone)]
pub struct TimeUtils;

/// 格式化时间戳
///
/// # 参数
/// * `timestamp` - Unix时间戳（秒）
/// * `format` - 可选的格式字符串
pub fn format_timestamp(timestamp: i64, format: Option<&str>) -> AppResult<String> {
    let datetime = TimeUtils::from_unix_timestamp(timestamp)?;
    let format_str = format.unwrap_or("%Y-%m-%d %H:%M:%S");
    Ok(datetime.format(format_str).to_string())
}

/// 解析持续时间字符串
///
/// # 参数
/// * `duration_str` - 持续时间字符串（如："1h", "30m", "5s"）
pub fn parse_duration(duration_str: &str) -> AppResult<Duration> {
    let duration_str = duration_str.trim().to_lowercase();

    if duration_str.is_empty() {
        return Err(AppError::validation_error(
            "duration",
            "持续时间字符串不能为空",
        ));
    }

    // 解析数字和单位
    let (number_part, unit_part) = if let Some(pos) = duration_str.find(|c: char| c.is_alphabetic())
    {
        (&duration_str[..pos], &duration_str[pos..])
    } else {
        return Err(AppError::validation_error("duration", "无效的持续时间格式"));
    };

    let number: i64 = number_part
        .parse()
        .map_err(|_| AppError::validation_error("duration", "无效的数字格式"))?;

    match unit_part {
        "s" | "sec" | "second" | "seconds" => Ok(Duration::seconds(number)),
        "m" | "min" | "minute" | "minutes" => Ok(Duration::minutes(number)),
        "h" | "hour" | "hours" => Ok(Duration::hours(number)),
        "d" | "day" | "days" => Ok(Duration::days(number)),
        "w" | "week" | "weeks" => Ok(Duration::weeks(number)),
        _ => Err(AppError::validation_error(
            "duration",
            &format!("不支持的时间单位: {}", unit_part),
        )),
    }
}

impl TimeUtils {
    /// 获取当前UTC时间
    pub fn now_utc() -> DateTime<Utc> {
        Utc::now()
    }

    /// 获取当前本地时间
    pub fn now_local() -> DateTime<Local> {
        Local::now()
    }

    /// 获取Unix时间戳（秒）
    pub fn unix_timestamp() -> i64 {
        Utc::now().timestamp()
    }

    /// 获取Unix时间戳（毫秒）
    pub fn unix_timestamp_millis() -> i64 {
        Utc::now().timestamp_millis()
    }

    /// 从Unix时间戳创建DateTime
    ///
    /// # 参数
    /// * `timestamp` - Unix时间戳（秒）
    pub fn from_unix_timestamp(timestamp: i64) -> AppResult<DateTime<Utc>> {
        Utc.timestamp_opt(timestamp, 0)
            .single()
            .ok_or_else(|| AppError::validation_error("duration", "无效的Unix时间戳"))
    }

    /// 从Unix时间戳（毫秒）创建DateTime
    ///
    /// # 参数
    /// * `timestamp_millis` - Unix时间戳（毫秒）
    pub fn from_unix_timestamp_millis(timestamp_millis: i64) -> AppResult<DateTime<Utc>> {
        Utc.timestamp_millis_opt(timestamp_millis)
            .single()
            .ok_or_else(|| AppError::validation_error("duration", "无效的Unix时间戳（毫秒）"))
    }

    /// 解析ISO 8601格式的时间字符串
    ///
    /// # 参数
    /// * `time_str` - 时间字符串
    pub fn parse_iso8601(time_str: &str) -> AppResult<DateTime<Utc>> {
        DateTime::parse_from_rfc3339(time_str)
            .map(|dt| dt.with_timezone(&Utc))
            .map_err(|e| {
                AppError::validation_error("duration", format!("解析ISO 8601时间失败: {}", e))
            })
    }

    /// 格式化时间为ISO 8601字符串
    ///
    /// # 参数
    /// * `datetime` - 要格式化的时间
    pub fn format_iso8601(datetime: &DateTime<Utc>) -> String {
        datetime.to_rfc3339()
    }

    /// 格式化时间为人类可读的字符串
    ///
    /// # 参数
    /// * `datetime` - 要格式化的时间
    /// * `format` - 格式字符串
    pub fn format_human_readable(datetime: &DateTime<Utc>, format: &str) -> String {
        datetime.format(format).to_string()
    }

    /// 计算两个时间之间的持续时间
    ///
    /// # 参数
    /// * `start` - 开始时间
    /// * `end` - 结束时间
    pub fn duration_between(start: &DateTime<Utc>, end: &DateTime<Utc>) -> Duration {
        *end - *start
    }

    /// 检查时间是否在指定范围内
    ///
    /// # 参数
    /// * `time` - 要检查的时间
    /// * `start` - 范围开始时间
    /// * `end` - 范围结束时间
    pub fn is_time_in_range(
        time: &DateTime<Utc>,
        start: &DateTime<Utc>,
        end: &DateTime<Utc>,
    ) -> bool {
        time >= start && time <= end
    }

    /// 格式化时间戳为字符串
    ///
    /// # 参数
    /// * `timestamp` - Unix时间戳（秒）
    /// * `format` - 格式字符串，默认为 "%Y-%m-%d %H:%M:%S"
    pub fn format_timestamp(timestamp: i64, format: Option<&str>) -> AppResult<String> {
        let datetime = Self::from_unix_timestamp(timestamp)?;
        let format_str = format.unwrap_or("%Y-%m-%d %H:%M:%S");
        Ok(datetime.format(format_str).to_string())
    }

    /// 解析持续时间字符串
    ///
    /// # 参数
    /// * `duration_str` - 持续时间字符串，支持格式如 "1h30m", "90s", "2d", "1w"
    pub fn parse_duration(duration_str: &str) -> AppResult<Duration> {
        let duration_str = duration_str.trim().to_lowercase();

        if duration_str.is_empty() {
            return Err(AppError::validation_error(
                "duration",
                "持续时间字符串不能为空",
            ));
        }

        // 支持的单位：s(秒), m(分), h(小时), d(天), w(周)
        let mut total_seconds = 0i64;
        let mut current_number = String::new();

        for ch in duration_str.chars() {
            if ch.is_ascii_digit() {
                current_number.push(ch);
            } else {
                if current_number.is_empty() {
                    return Err(AppError::validation_error("duration", "无效的持续时间格式"));
                }

                let number: i64 = current_number
                    .parse()
                    .map_err(|_| AppError::validation_error("duration", "无效的数字"))?;

                let multiplier = match ch {
                    's' => 1,      // 秒
                    'm' => 60,     // 分钟
                    'h' => 3600,   // 小时
                    'd' => 86400,  // 天
                    'w' => 604800, // 周
                    _ => {
                        return Err(AppError::validation_error(
                            "duration",
                            format!("不支持的时间单位: {}", ch),
                        ))
                    }
                };

                total_seconds += number * multiplier;
                current_number.clear();
            }
        }

        // 处理最后一个数字（如果没有单位，默认为秒）
        if !current_number.is_empty() {
            let number: i64 = current_number
                .parse()
                .map_err(|_| AppError::validation_error("duration", "无效的数字"))?;
            total_seconds += number; // 默认为秒
        }

        Duration::try_seconds(total_seconds)
            .ok_or_else(|| AppError::validation_error("duration", "持续时间超出范围"))
    }

    /// 获取时间的开始（当天00:00:00）
    ///
    /// # 参数
    /// * `datetime` - 输入时间
    pub fn start_of_day(datetime: &DateTime<Utc>) -> DateTime<Utc> {
        datetime
            .date_naive()
            .and_hms_opt(0, 0, 0)
            .map(|naive| Utc.from_utc_datetime(&naive))
            .unwrap_or(*datetime)
    }

    /// 获取时间的结束（当天23:59:59）
    ///
    /// # 参数
    /// * `datetime` - 输入时间
    pub fn end_of_day(datetime: &DateTime<Utc>) -> DateTime<Utc> {
        datetime
            .date_naive()
            .and_hms_opt(23, 59, 59)
            .map(|naive| Utc.from_utc_datetime(&naive))
            .unwrap_or(*datetime)
    }

    /// 获取指定天数前的时间
    ///
    /// # 参数
    /// * `days` - 天数
    pub fn days_ago(days: i64) -> DateTime<Utc> {
        Utc::now() - Duration::days(days)
    }

    /// 获取指定小时前的时间
    ///
    /// # 参数
    /// * `hours` - 小时数
    pub fn hours_ago(hours: i64) -> DateTime<Utc> {
        Utc::now() - Duration::hours(hours)
    }

    /// 获取指定分钟前的时间
    ///
    /// # 参数
    /// * `minutes` - 分钟数
    pub fn minutes_ago(minutes: i64) -> DateTime<Utc> {
        Utc::now() - Duration::minutes(minutes)
    }

    /// 将持续时间转换为人类可读的字符串
    ///
    /// # 参数
    /// * `duration` - 持续时间
    pub fn duration_to_human_readable(duration: &Duration) -> String {
        let total_seconds = duration.num_seconds();

        if total_seconds < 60 {
            format!("{}秒", total_seconds)
        } else if total_seconds < 3600 {
            let minutes = total_seconds / 60;
            let seconds = total_seconds % 60;
            if seconds == 0 {
                format!("{}分钟", minutes)
            } else {
                format!("{}分钟{}秒", minutes, seconds)
            }
        } else if total_seconds < 86400 {
            let hours = total_seconds / 3600;
            let minutes = (total_seconds % 3600) / 60;
            if minutes == 0 {
                format!("{}小时", hours)
            } else {
                format!("{}小时{}分钟", hours, minutes)
            }
        } else {
            let days = total_seconds / 86400;
            let hours = (total_seconds % 86400) / 3600;
            if hours == 0 {
                format!("{}天", days)
            } else {
                format!("{}天{}小时", days, hours)
            }
        }
    }

    /// 生成时间序列
    ///
    /// # 参数
    /// * `start` - 开始时间
    /// * `end` - 结束时间
    /// * `interval` - 时间间隔
    pub fn generate_time_series(
        start: &DateTime<Utc>,
        end: &DateTime<Utc>,
        interval: Duration,
    ) -> AppResult<Vec<DateTime<Utc>>> {
        if interval <= Duration::zero() {
            return Err(AppError::validation_error("interval", "时间间隔必须大于0"));
        }

        if start >= end {
            return Err(AppError::validation_error(
                "time_range",
                "开始时间必须早于结束时间",
            ));
        }

        let mut series = Vec::new();
        let mut current = *start;

        while current <= *end {
            series.push(current);
            current = current + interval;
        }

        Ok(series)
    }

    /// 安全的持续时间计算，返回Result
    pub fn try_duration_seconds_of_from_now(
        start_time: Option<DateTime<Utc>>,
        end_time: Option<DateTime<Utc>>,
        now: DateTime<Utc>,
    ) -> Result<usize, &'static str> {
        match (start_time, end_time) {
            (Some(start), Some(end)) => {
                let duration = end.signed_duration_since(start);
                if duration.num_seconds() < 0 {
                    return Err("结束时间不能早于开始时间");
                }
                Ok(duration.num_seconds() as usize)
            }
            // todo 时间待完善
            (None, Some(end)) => Err("开始时间为空"),
            (Some(_), None) => Err("结束时间为空"),
            (None, None) => Err("开始时间和结束时间都为空"),
        }
    }

    /// 获取绝对值时间段（不关心时间顺序）
    pub fn absolute_duration_seconds(
        start_time: Option<DateTime<Utc>>,
        end_time: Option<DateTime<Utc>>,
    ) -> Option<usize> {
        match (start_time, end_time) {
            (Some(start), Some(end)) => {
                let duration = (end - start).abs();
                Some(duration.num_seconds() as usize)
            }
            _ => None,
        }
    }
}

/// 时间窗口
///
/// 表示一个时间范围
#[derive(Debug, Clone, PartialEq)]
pub struct TimeWindow {
    /// 开始时间
    pub start: DateTime<Utc>,
    /// 结束时间
    pub end: DateTime<Utc>,
}

impl TimeWindow {
    /// 创建新的时间窗口
    ///
    /// # 参数
    /// * `start` - 开始时间
    /// * `end` - 结束时间
    pub fn new(start: DateTime<Utc>, end: DateTime<Utc>) -> AppResult<Self> {
        if start >= end {
            return Err(AppError::validation_error(
                "time_window",
                "开始时间必须早于结束时间",
            ));
        }

        Ok(Self { start, end })
    }

    /// 创建从现在开始的时间窗口
    ///
    /// # 参数
    /// * `duration` - 窗口持续时间
    pub fn from_now(duration: Duration) -> AppResult<Self> {
        let start = Utc::now();
        let end = start + duration;
        Self::new(start, end)
    }

    /// 创建到现在结束的时间窗口
    ///
    /// # 参数
    /// * `duration` - 窗口持续时间
    pub fn until_now(duration: Duration) -> AppResult<Self> {
        let end = Utc::now();
        let start = end - duration;
        Self::new(start, end)
    }

    /// 获取窗口持续时间
    pub fn duration(&self) -> Duration {
        self.end - self.start
    }

    /// 检查时间是否在窗口内
    ///
    /// # 参数
    /// * `time` - 要检查的时间
    pub fn contains(&self, time: &DateTime<Utc>) -> bool {
        time >= &self.start && time <= &self.end
    }

    /// 检查两个时间窗口是否重叠
    ///
    /// # 参数
    /// * `other` - 另一个时间窗口
    pub fn overlaps(&self, other: &TimeWindow) -> bool {
        self.start < other.end && self.end > other.start
    }

    /// 获取两个时间窗口的交集
    ///
    /// # 参数
    /// * `other` - 另一个时间窗口
    pub fn intersection(&self, other: &TimeWindow) -> Option<TimeWindow> {
        if !self.overlaps(other) {
            return None;
        }

        let start = self.start.max(other.start);
        let end = self.end.min(other.end);

        TimeWindow::new(start, end).ok()
    }

    /// 将时间窗口分割为多个子窗口
    ///
    /// # 参数
    /// * `interval` - 子窗口间隔
    pub fn split(&self, interval: Duration) -> AppResult<Vec<TimeWindow>> {
        if interval <= Duration::zero() {
            return Err(AppError::validation_error("interval", "间隔必须大于0"));
        }

        let mut windows = Vec::new();
        let mut current_start = self.start;

        while current_start < self.end {
            let current_end = (current_start + interval).min(self.end);
            windows.push(TimeWindow::new(current_start, current_end)?);
            current_start = current_end;
        }

        Ok(windows)
    }
}

/// 性能计时器
///
/// 用于测量代码执行时间
#[derive(Debug)]
pub struct PerformanceTimer {
    /// 开始时间
    start_time: Instant,
    /// 检查点记录
    checkpoints: HashMap<String, Instant>,
}

impl PerformanceTimer {
    /// 创建并启动计时器
    pub fn start() -> Self {
        Self {
            start_time: Instant::now(),
            checkpoints: HashMap::new(),
        }
    }

    /// 记录检查点
    ///
    /// # 参数
    /// * `name` - 检查点名称
    pub fn checkpoint(&mut self, name: impl Into<String>) {
        self.checkpoints.insert(name.into(), Instant::now());
    }

    /// 获取从开始到现在的耗时
    pub fn elapsed(&self) -> std::time::Duration {
        self.start_time.elapsed()
    }

    /// 获取从检查点到现在的耗时
    ///
    /// # 参数
    /// * `checkpoint_name` - 检查点名称
    pub fn elapsed_since_checkpoint(&self, checkpoint_name: &str) -> Option<std::time::Duration> {
        self.checkpoints
            .get(checkpoint_name)
            .map(|checkpoint| checkpoint.elapsed())
    }

    /// 获取两个检查点之间的耗时
    ///
    /// # 参数
    /// * `start_checkpoint` - 开始检查点
    /// * `end_checkpoint` - 结束检查点
    pub fn duration_between_checkpoints(
        &self,
        start_checkpoint: &str,
        end_checkpoint: &str,
    ) -> Option<std::time::Duration> {
        let start = self.checkpoints.get(start_checkpoint)?;
        let end = self.checkpoints.get(end_checkpoint)?;

        if end >= start {
            Some(end.duration_since(*start))
        } else {
            None
        }
    }

    /// 重置计时器
    pub fn reset(&mut self) {
        self.start_time = Instant::now();
        self.checkpoints.clear();
    }

    /// 获取所有检查点的耗时报告
    pub fn get_report(&self) -> HashMap<String, std::time::Duration> {
        self.checkpoints
            .iter()
            .map(|(name, instant)| (name.clone(), instant.duration_since(self.start_time)))
            .collect()
    }
}

/// 时间格式化器
///
/// 提供各种时间格式化功能
pub struct TimeFormatter;

impl TimeFormatter {
    /// 格式化为标准日期时间格式
    ///
    /// # 参数
    /// * `datetime` - 要格式化的时间
    pub fn standard(datetime: &DateTime<Utc>) -> String {
        datetime.format("%Y-%m-%d %H:%M:%S UTC").to_string()
    }

    /// 格式化为简短格式
    ///
    /// # 参数
    /// * `datetime` - 要格式化的时间
    pub fn short(datetime: &DateTime<Utc>) -> String {
        datetime.format("%m/%d %H:%M").to_string()
    }

    /// 格式化为文件名安全格式
    ///
    /// # 参数
    /// * `datetime` - 要格式化的时间
    pub fn filename_safe(datetime: &DateTime<Utc>) -> String {
        datetime.format("%Y%m%d_%H%M%S").to_string()
    }

    /// 格式化为相对时间（如"2小时前"）
    ///
    /// # 参数
    /// * `datetime` - 要格式化的时间
    pub fn relative(datetime: &DateTime<Utc>) -> String {
        let now = Utc::now();
        let duration = now - *datetime;

        if duration < Duration::zero() {
            return "未来".to_string();
        }

        let seconds = duration.num_seconds();

        if seconds < 60 {
            format!("{}秒前", seconds)
        } else if seconds < 3600 {
            format!("{}分钟前", seconds / 60)
        } else if seconds < 86400 {
            format!("{}小时前", seconds / 3600)
        } else if seconds < 2592000 {
            format!("{}天前", seconds / 86400)
        } else if seconds < 31536000 {
            format!("{}个月前", seconds / 2592000)
        } else {
            format!("{}年前", seconds / 31536000)
        }
    }

    /// 格式化持续时间为精确格式
    ///
    /// # 参数
    /// * `duration` - 持续时间
    pub fn duration_precise(duration: &std::time::Duration) -> String {
        let total_millis = duration.as_millis();

        if total_millis < 1000 {
            format!("{}ms", total_millis)
        } else if total_millis < 60000 {
            format!("{:.2}s", total_millis as f64 / 1000.0)
        } else if total_millis < 3600000 {
            let minutes = total_millis / 60000;
            let seconds = (total_millis % 60000) as f64 / 1000.0;
            format!("{}m {:.1}s", minutes, seconds)
        } else {
            let hours = total_millis / 3600000;
            let minutes = (total_millis % 3600000) / 60000;
            format!("{}h {}m", hours, minutes)
        }
    }
}

/// 时区转换器
///
/// 提供时区转换功能
pub struct TimezoneConverter;

impl TimezoneConverter {
    /// 转换为本地时区
    ///
    /// # 参数
    /// * `utc_time` - UTC时间
    pub fn to_local(utc_time: &DateTime<Utc>) -> DateTime<Local> {
        utc_time.with_timezone(&Local)
    }

    /// 从本地时区转换为UTC
    ///
    /// # 参数
    /// * `local_time` - 本地时间
    pub fn to_utc(local_time: &DateTime<Local>) -> DateTime<Utc> {
        local_time.with_timezone(&Utc)
    }

    /// 获取时区偏移量（小时）
    pub fn get_local_offset_hours() -> i32 {
        let local_now = Local::now();
        let utc_now = Utc::now();
        let offset = local_now.offset().local_minus_utc();
        offset / 3600
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_time_utils() {
        let now = TimeUtils::now_utc();
        let timestamp = TimeUtils::unix_timestamp();
        let from_timestamp = TimeUtils::from_unix_timestamp(timestamp).unwrap();

        // 允许1秒的误差
        assert!((now.timestamp() - from_timestamp.timestamp()).abs() <= 1);
    }

    #[test]
    fn test_time_window() {
        let start = Utc::now();
        let end = start + Duration::hours(1);
        let window = TimeWindow::new(start, end).unwrap();

        assert_eq!(window.duration(), Duration::hours(1));

        let middle_time = start + Duration::minutes(30);
        assert!(window.contains(&middle_time));

        let outside_time = start - Duration::minutes(10);
        assert!(!window.contains(&outside_time));
    }

    #[test]
    fn test_time_window_split() {
        let start = Utc::now();
        let end = start + Duration::hours(2);
        let window = TimeWindow::new(start, end).unwrap();

        let sub_windows = window.split(Duration::minutes(30)).unwrap();
        assert_eq!(sub_windows.len(), 4);

        for sub_window in &sub_windows {
            assert_eq!(sub_window.duration(), Duration::minutes(30));
        }
    }

    #[test]
    fn test_performance_timer() {
        let mut timer = PerformanceTimer::start();

        std::thread::sleep(std::time::Duration::from_millis(10));
        timer.checkpoint("checkpoint1");

        std::thread::sleep(std::time::Duration::from_millis(10));
        timer.checkpoint("checkpoint2");

        let elapsed = timer.elapsed();
        assert!(elapsed >= std::time::Duration::from_millis(20));

        let since_checkpoint = timer.elapsed_since_checkpoint("checkpoint1").unwrap();
        assert!(since_checkpoint >= std::time::Duration::from_millis(10));
    }

    #[test]
    fn test_time_formatter() {
        let time = Utc::now();

        let standard = TimeFormatter::standard(&time);
        assert!(standard.contains("UTC"));

        let filename_safe = TimeFormatter::filename_safe(&time);
        assert!(!filename_safe.contains(" "));
        assert!(!filename_safe.contains(":"));
    }

    #[test]
    fn test_duration_to_human_readable() {
        let duration = Duration::seconds(65);
        let readable = TimeUtils::duration_to_human_readable(&duration);
        assert_eq!(readable, "1分钟5秒");

        let duration = Duration::hours(2);
        let readable = TimeUtils::duration_to_human_readable(&duration);
        assert_eq!(readable, "2小时");
    }
}
