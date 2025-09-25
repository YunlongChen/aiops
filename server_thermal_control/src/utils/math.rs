use crate::models::error::{AppError, AppResult};
use std::collections::VecDeque;

/// 计算平均值
///
/// # 参数
/// * `values` - 数值序列
pub fn calculate_average(values: &[f64]) -> AppResult<f64> {
    if values.is_empty() {
        return Err(AppError::validation_error("values", "数值序列不能为空"));
    }

    let sum: f64 = values.iter().sum();
    Ok(sum / values.len() as f64)
}

/// 计算趋势
///
/// # 参数
/// * `values` - 数值序列
pub fn calculate_trend(values: &[f64]) -> AppResult<f64> {
    if values.len() < 2 {
        return Err(AppError::validation_error("values", "至少需要2个数据点"));
    }

    let x_values: Vec<f64> = (0..values.len()).map(|i| i as f64).collect();
    let (slope, _, _) = MathUtils::linear_regression(&x_values, values)?;
    Ok(slope)
}

/// 数学计算工具集
///
/// 提供温度控制系统所需的各种数学计算功能
#[derive(Clone)]
pub struct MathUtils;

impl MathUtils {
    /// 计算移动平均值
    ///
    /// # 参数
    /// * `values` - 数值序列
    /// * `window_size` - 窗口大小
    pub fn moving_average(values: &[f64], window_size: usize) -> AppResult<Vec<f64>> {
        if window_size == 0 {
            return Err(AppError::validation_error("window_size", "窗口大小不能为0"));
        }

        if values.len() < window_size {
            return Err(AppError::validation_error(
                "values",
                "数据点数量少于窗口大小",
            ));
        }

        let mut result = Vec::new();

        for i in window_size - 1..values.len() {
            let sum: f64 = values[i - window_size + 1..=i].iter().sum();
            result.push(sum / window_size as f64);
        }

        Ok(result)
    }

    /// 计算指数移动平均值
    ///
    /// # 参数
    /// * `values` - 数值序列
    /// * `alpha` - 平滑因子 (0 < alpha <= 1)
    pub fn exponential_moving_average(values: &[f64], alpha: f64) -> AppResult<Vec<f64>> {
        if alpha <= 0.0 || alpha > 1.0 {
            return Err(AppError::validation_error(
                "alpha",
                "平滑因子必须在(0,1]范围内",
            ));
        }

        if values.is_empty() {
            return Ok(Vec::new());
        }

        let mut result = Vec::with_capacity(values.len());
        result.push(values[0]);

        for i in 1..values.len() {
            let ema = alpha * values[i] + (1.0 - alpha) * result[i - 1];
            result.push(ema);
        }

        Ok(result)
    }

    /// 计算线性回归
    ///
    /// # 参数
    /// * `x_values` - X轴数值
    /// * `y_values` - Y轴数值
    ///
    /// # 返回
    /// (斜率, 截距, 相关系数)
    pub fn linear_regression(x_values: &[f64], y_values: &[f64]) -> AppResult<(f64, f64, f64)> {
        if x_values.len() != y_values.len() {
            return Err(AppError::validation_error("values", "X和Y数组长度不匹配"));
        }

        if x_values.len() < 2 {
            return Err(AppError::validation_error("values", "至少需要2个数据点"));
        }

        let n = x_values.len() as f64;
        let sum_x: f64 = x_values.iter().sum();
        let sum_y: f64 = y_values.iter().sum();
        let sum_xy: f64 = x_values
            .iter()
            .zip(y_values.iter())
            .map(|(x, y)| x * y)
            .sum();
        let sum_x2: f64 = x_values.iter().map(|x| x * x).sum();
        let sum_y2: f64 = y_values.iter().map(|y| y * y).sum();

        let mean_x = sum_x / n;
        let mean_y = sum_y / n;

        // 计算斜率和截距
        let denominator = sum_x2 - sum_x * sum_x / n;
        if denominator.abs() < f64::EPSILON {
            return Err(AppError::validation_error(
                "values",
                "X值方差为0，无法计算回归",
            ));
        }

        let slope = (sum_xy - sum_x * sum_y / n) / denominator;
        let intercept = mean_y - slope * mean_x;

        // 计算相关系数
        let numerator = n * sum_xy - sum_x * sum_y;
        let denominator_r = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)).sqrt();

        let correlation = if denominator_r.abs() < f64::EPSILON {
            0.0
        } else {
            numerator / denominator_r
        };

        Ok((slope, intercept, correlation))
    }

    /// 计算标准差
    ///
    /// # 参数
    /// * `values` - 数值序列
    pub fn standard_deviation(values: &[f64]) -> AppResult<f64> {
        if values.is_empty() {
            return Err(AppError::validation_error("values", "数组不能为空"));
        }

        let mean = values.iter().sum::<f64>() / values.len() as f64;
        let variance = values.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / values.len() as f64;

        Ok(variance.sqrt())
    }

    /// 计算百分位数
    ///
    /// # 参数
    /// * `values` - 数值序列
    /// * `percentile` - 百分位数 (0-100)
    pub fn percentile(values: &[f64], percentile: f64) -> AppResult<f64> {
        if values.is_empty() {
            return Err(AppError::validation_error("values", "数组不能为空"));
        }

        if percentile < 0.0 || percentile > 100.0 {
            return Err(AppError::validation_error(
                "percentile",
                "百分位数必须在0-100范围内",
            ));
        }

        let mut sorted_values = values.to_vec();
        sorted_values.sort_by(|a, b| a.partial_cmp(b).unwrap());

        let index = (percentile / 100.0) * (sorted_values.len() - 1) as f64;
        let lower_index = index.floor() as usize;
        let upper_index = index.ceil() as usize;

        if lower_index == upper_index {
            Ok(sorted_values[lower_index])
        } else {
            let weight = index - lower_index as f64;
            Ok(sorted_values[lower_index] * (1.0 - weight) + sorted_values[upper_index] * weight)
        }
    }

    /// 检测异常值（使用IQR方法）
    ///
    /// # 参数
    /// * `values` - 数值序列
    /// * `multiplier` - IQR倍数（默认1.5）
    pub fn detect_outliers(values: &[f64], multiplier: f64) -> AppResult<Vec<usize>> {
        if values.len() < 4 {
            return Ok(Vec::new()); // 数据点太少，无法检测异常值
        }

        let q1 = Self::percentile(values, 25.0)?;
        let q3 = Self::percentile(values, 75.0)?;
        let iqr = q3 - q1;

        let lower_bound = q1 - multiplier * iqr;
        let upper_bound = q3 + multiplier * iqr;

        let outliers: Vec<usize> = values
            .iter()
            .enumerate()
            .filter_map(|(i, &value)| {
                if value < lower_bound || value > upper_bound {
                    Some(i)
                } else {
                    None
                }
            })
            .collect();

        Ok(outliers)
    }

    /// 平滑数据（使用Savitzky-Golay滤波器的简化版本）
    ///
    /// # 参数
    /// * `values` - 数值序列
    /// * `window_size` - 窗口大小（必须为奇数）
    pub fn smooth_data(values: &[f64], window_size: usize) -> AppResult<Vec<f64>> {
        if window_size % 2 == 0 {
            return Err(AppError::validation_error(
                "window_size",
                "窗口大小必须为奇数",
            ));
        }

        if values.len() < window_size {
            return Ok(values.to_vec());
        }

        let half_window = window_size / 2;
        let mut smoothed = Vec::with_capacity(values.len());

        // 处理边界
        for i in 0..half_window {
            smoothed.push(values[i]);
        }

        // 处理中间部分
        for i in half_window..values.len() - half_window {
            let sum: f64 = values[i - half_window..=i + half_window].iter().sum();
            smoothed.push(sum / window_size as f64);
        }

        // 处理边界
        for i in values.len() - half_window..values.len() {
            smoothed.push(values[i]);
        }

        Ok(smoothed)
    }

    /// 计算趋势（使用最小二乘法）
    ///
    /// # 参数
    /// * `values` - 数值序列
    ///
    /// # 返回
    /// 趋势斜率（正值表示上升趋势，负值表示下降趋势）
    pub fn calculate_trend(values: &[f64]) -> AppResult<f64> {
        if values.len() < 2 {
            return Ok(0.0);
        }

        let x_values: Vec<f64> = (0..values.len()).map(|i| i as f64).collect();
        let (slope, _, _) = Self::linear_regression(&x_values, values)?;

        Ok(slope)
    }

    /// 预测下一个值（使用线性外推）
    ///
    /// # 参数
    /// * `values` - 历史数值序列
    /// * `steps` - 预测步数
    pub fn predict_next_values(values: &[f64], steps: usize) -> AppResult<Vec<f64>> {
        if values.len() < 2 {
            return Err(AppError::validation_error(
                "values",
                "至少需要2个历史数据点",
            ));
        }

        let x_values: Vec<f64> = (0..values.len()).map(|i| i as f64).collect();
        let (slope, intercept, _) = Self::linear_regression(&x_values, values)?;

        let mut predictions = Vec::with_capacity(steps);
        let start_x = values.len() as f64;

        for i in 0..steps {
            let x = start_x + i as f64;
            let prediction = slope * x + intercept;
            predictions.push(prediction);
        }

        Ok(predictions)
    }

    /// 计算平均值
    ///
    /// # 参数
    /// * `values` - 数值序列
    pub fn calculate_average(values: &[f64]) -> AppResult<f64> {
        if values.is_empty() {
            return Err(AppError::validation_error("values", "数组不能为空"));
        }

        let sum: f64 = values.iter().sum();
        Ok(sum / values.len() as f64)
    }

    /// 计算标准差（别名函数，用于兼容性）
    ///
    /// # 参数
    /// * `values` - 数值序列
    pub fn calculate_standard_deviation(values: &[f64]) -> AppResult<f64> {
        Self::standard_deviation(values)
    }
}

/// PID控制器
///
/// 实现比例-积分-微分控制算法
#[derive(Debug, Clone)]
pub struct PidController {
    /// 比例增益
    pub kp: f64,
    /// 积分增益
    pub ki: f64,
    /// 微分增益
    pub kd: f64,
    /// 积分项累积值
    integral: f64,
    /// 上一次的误差值
    previous_error: Option<f64>,
    /// 输出限制
    output_limits: Option<(f64, f64)>,
    /// 积分限制（防止积分饱和）
    integral_limits: Option<(f64, f64)>,
}

impl PidController {
    /// 创建新的PID控制器
    ///
    /// # 参数
    /// * `kp` - 比例增益
    /// * `ki` - 积分增益
    /// * `kd` - 微分增益
    pub fn new(kp: f64, ki: f64, kd: f64) -> Self {
        Self {
            kp,
            ki,
            kd,
            integral: 0.0,
            previous_error: None,
            output_limits: None,
            integral_limits: None,
        }
    }

    /// 设置输出限制
    ///
    /// # 参数
    /// * `min` - 最小输出值
    /// * `max` - 最大输出值
    pub fn set_output_limits(&mut self, min: f64, max: f64) {
        self.output_limits = Some((min, max));
    }

    /// 设置积分限制
    ///
    /// # 参数
    /// * `min` - 最小积分值
    /// * `max` - 最大积分值
    pub fn set_integral_limits(&mut self, min: f64, max: f64) {
        self.integral_limits = Some((min, max));
    }

    /// 计算控制输出
    ///
    /// # 参数
    /// * `setpoint` - 设定值
    /// * `process_value` - 当前过程值
    /// * `dt` - 时间间隔
    pub fn compute(&mut self, setpoint: f64, process_value: f64, dt: f64) -> f64 {
        let error = setpoint - process_value;

        // 比例项
        let proportional = self.kp * error;

        // 积分项
        self.integral += error * dt;

        // 应用积分限制
        if let Some((min, max)) = self.integral_limits {
            self.integral = self.integral.clamp(min, max);
        }

        let integral = self.ki * self.integral;

        // 微分项
        let derivative = if let Some(prev_error) = self.previous_error {
            self.kd * (error - prev_error) / dt
        } else {
            0.0
        };

        self.previous_error = Some(error);

        // 计算总输出
        let mut output = proportional + integral + derivative;

        // 应用输出限制
        if let Some((min, max)) = self.output_limits {
            output = output.clamp(min, max);
        }

        output
    }

    /// 重置控制器状态
    pub fn reset(&mut self) {
        self.integral = 0.0;
        self.previous_error = None;
    }

    /// 获取当前积分值
    pub fn get_integral(&self) -> f64 {
        self.integral
    }

    /// 获取上一次误差值
    pub fn get_previous_error(&self) -> Option<f64> {
        self.previous_error
    }
}

/// 滑动窗口统计
///
/// 维护一个固定大小的滑动窗口，并提供实时统计功能
#[derive(Debug, Clone)]
pub struct SlidingWindowStats {
    /// 数据窗口
    window: VecDeque<f64>,
    /// 窗口大小
    window_size: usize,
    /// 当前总和
    sum: f64,
}

impl SlidingWindowStats {
    /// 创建新的滑动窗口统计
    ///
    /// # 参数
    /// * `window_size` - 窗口大小
    pub fn new(window_size: usize) -> AppResult<Self> {
        if window_size == 0 {
            return Err(AppError::validation_error("window_size", "窗口大小不能为0"));
        }

        Ok(Self {
            window: VecDeque::with_capacity(window_size),
            window_size,
            sum: 0.0,
        })
    }

    /// 添加新数据点
    ///
    /// # 参数
    /// * `value` - 新数据值
    pub fn add(&mut self, value: f64) {
        if self.window.len() == self.window_size {
            if let Some(old_value) = self.window.pop_front() {
                self.sum -= old_value;
            }
        }

        self.window.push_back(value);
        self.sum += value;
    }

    /// 获取当前平均值
    pub fn mean(&self) -> f64 {
        if self.window.is_empty() {
            0.0
        } else {
            self.sum / self.window.len() as f64
        }
    }

    /// 获取当前最小值
    pub fn min(&self) -> Option<f64> {
        self.window
            .iter()
            .min_by(|a, b| a.partial_cmp(b).unwrap())
            .copied()
    }

    /// 获取当前最大值
    pub fn max(&self) -> Option<f64> {
        self.window
            .iter()
            .max_by(|a, b| a.partial_cmp(b).unwrap())
            .copied()
    }

    /// 获取当前标准差
    pub fn std_dev(&self) -> f64 {
        if self.window.len() < 2 {
            return 0.0;
        }

        let mean = self.mean();
        let variance =
            self.window.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / self.window.len() as f64;

        variance.sqrt()
    }

    /// 获取窗口中的数据点数量
    pub fn len(&self) -> usize {
        self.window.len()
    }

    /// 检查窗口是否为空
    pub fn is_empty(&self) -> bool {
        self.window.is_empty()
    }

    /// 检查窗口是否已满
    pub fn is_full(&self) -> bool {
        self.window.len() == self.window_size
    }

    /// 清空窗口
    pub fn clear(&mut self) {
        self.window.clear();
        self.sum = 0.0;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_moving_average() {
        let values = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let result = MathUtils::moving_average(&values, 3).unwrap();
        assert_eq!(result, vec![2.0, 3.0, 4.0]);
    }

    #[test]
    fn test_linear_regression() {
        let x = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let y = vec![2.0, 4.0, 6.0, 8.0, 10.0];
        let (slope, intercept, correlation) = MathUtils::linear_regression(&x, &y).unwrap();

        assert!((slope - 2.0).abs() < 1e-10);
        assert!((intercept - 0.0).abs() < 1e-10);
        assert!((correlation - 1.0).abs() < 1e-10);
    }

    #[test]
    fn test_pid_controller() {
        let mut pid = PidController::new(1.0, 0.1, 0.01);
        pid.set_output_limits(-100.0, 100.0);

        let output = pid.compute(50.0, 40.0, 1.0);
        assert!(output > 0.0); // 应该有正输出来减少误差
    }

    #[test]
    fn test_sliding_window_stats() {
        let mut stats = SlidingWindowStats::new(3).unwrap();

        stats.add(1.0);
        stats.add(2.0);
        stats.add(3.0);

        assert_eq!(stats.mean(), 2.0);
        assert_eq!(stats.min(), Some(1.0));
        assert_eq!(stats.max(), Some(3.0));

        stats.add(4.0); // 应该移除1.0
        assert_eq!(stats.mean(), 3.0);
        assert_eq!(stats.min(), Some(2.0));
    }

    #[test]
    fn test_detect_outliers() {
        let values = vec![1.0, 2.0, 3.0, 4.0, 5.0, 100.0]; // 100.0是异常值
        let outliers = MathUtils::detect_outliers(&values, 1.5).unwrap();
        assert_eq!(outliers, vec![5]);
    }

    #[test]
    fn test_calculate_trend() {
        let increasing = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let trend = MathUtils::calculate_trend(&increasing).unwrap();
        assert!(trend > 0.0);

        let decreasing = vec![5.0, 4.0, 3.0, 2.0, 1.0];
        let trend = MathUtils::calculate_trend(&decreasing).unwrap();
        assert!(trend < 0.0);
    }
}
