use crate::models::error::{AppError, AppResult};
use std::net::{IpAddr, SocketAddr, ToSocketAddrs};
use std::time::{Duration, Instant};
use tokio::net::{TcpSocket, TcpStream};
use tokio::time::timeout;

/// 网络工具集
///
/// 提供各种网络相关功能
pub struct NetworkUtils;

impl NetworkUtils {
    /// 检查主机是否可达
    ///
    /// # 参数
    /// * `host` - 主机地址
    /// * `port` - 端口号
    /// * `timeout_ms` - 超时时间（毫秒）
    pub async fn check_host_reachable(host: &str, port: u16, timeout_ms: u64) -> bool {
        let addr = format!("{}:{}", host, port);
        let timeout_duration = Duration::from_millis(timeout_ms);

        match timeout(timeout_duration, async { TcpStream::connect(&addr).await }).await {
            Ok(Ok(_)) => true,
            _ => false,
        }
    }

    /// 异步检查主机是否可达
    ///
    /// # 参数
    /// * `host` - 主机地址
    /// * `port` - 端口号
    /// * `timeout_ms` - 超时时间（毫秒）
    pub async fn check_host_reachable_async(host: &str, port: u16, timeout_ms: u64) -> bool {
        let addr = format!("{}:{}", host, port);
        let timeout_duration = Duration::from_millis(timeout_ms);

        let socket = match TcpSocket::new_v4() {
            Ok(socket) => socket,
            Err(_) => return false,
        };

        let addr: SocketAddr = match addr.parse() {
            Ok(addr) => addr,
            Err(_) => return false,
        };

        match timeout(timeout_duration, socket.connect(addr)).await {
            Ok(Ok(_)) => true,
            _ => false,
        }
    }

    /// 测量网络延迟
    ///
    /// # 参数
    /// * `host` - 主机地址
    /// * `port` - 端口号
    /// * `timeout_ms` - 超时时间（毫秒）
    pub async fn measure_latency(host: &str, port: u16, timeout_ms: u64) -> AppResult<Duration> {
        let addr = format!("{}:{}", host, port);
        let timeout_duration = Duration::from_millis(timeout_ms);

        let start = Instant::now();

        match timeout(timeout_duration, async { TcpStream::connect(&addr).await }).await {
            Ok(Ok(_)) => Ok(start.elapsed()),
            Ok(Err(e)) => Err(AppError::network_error(format!("连接失败: {}", e))),
            Err(_) => Err(AppError::network_error("连接超时".to_string())),
        }
    }

    /// 解析主机名到IP地址
    ///
    /// # 参数
    /// * `hostname` - 主机名
    pub async fn resolve_hostname(hostname: &str) -> AppResult<Vec<IpAddr>> {
        let addr = format!("{}:0", hostname);

        tokio::task::spawn_blocking(move || {
            addr.to_socket_addrs()
                .map(|addrs| addrs.map(|addr| addr.ip()).collect())
                .map_err(|e| AppError::network_error(format!("DNS解析失败: {}", e)))
        })
        .await
        .map_err(|e| AppError::internal_server_error(format!("任务执行失败: {}", e)))?
    }

    /// 检查端口是否开放
    ///
    /// # 参数
    /// * `host` - 主机地址
    /// * `port` - 端口号
    /// * `timeout_ms` - 超时时间（毫秒）
    pub async fn is_port_open(host: &str, port: u16, timeout_ms: u64) -> bool {
        Self::check_host_reachable(host, port, timeout_ms).await
    }

    /// 扫描端口范围
    ///
    /// # 参数
    /// * `host` - 主机地址
    /// * `start_port` - 起始端口
    /// * `end_port` - 结束端口
    /// * `timeout_ms` - 每个端口的超时时间（毫秒）
    /// * `max_concurrent` - 最大并发数
    pub async fn scan_ports(
        host: &str,
        start_port: u16,
        end_port: u16,
        timeout_ms: u64,
        max_concurrent: usize,
    ) -> Vec<u16> {
        use futures::stream::{self, StreamExt};

        let host = host.to_string();
        let ports: Vec<u16> = (start_port..=end_port).collect();

        stream::iter(ports)
            .map(|port| {
                let host = host.clone();
                let timeout_ms = timeout_ms; // 捕获timeout_ms到闭包中
                async move {
                    if Self::is_port_open(&host, port, timeout_ms).await {
                        Some(port)
                    } else {
                        None
                    }
                }
            })
            .buffer_unordered(max_concurrent)
            .filter_map(|result| async move { result })
            .collect()
            .await
    }

    /// 获取本地IP地址
    pub fn get_local_ip() -> AppResult<IpAddr> {
        use std::net::UdpSocket;

        // 尝试连接到一个远程地址来获取本地IP
        let socket = UdpSocket::bind("0.0.0.0:0")
            .map_err(|e| AppError::network_error(format!("创建UDP套接字失败: {}", e)))?;

        socket
            .connect("8.8.8.8:80")
            .map_err(|e| AppError::network_error(format!("连接失败: {}", e)))?;

        let local_addr = socket
            .local_addr()
            .map_err(|e| AppError::network_error(format!("获取本地地址失败: {}", e)))?;

        Ok(local_addr.ip())
    }

    /// 检查IP地址是否为私有地址
    ///
    /// # 参数
    /// * `ip` - IP地址
    pub fn is_private_ip(ip: &IpAddr) -> bool {
        match ip {
            IpAddr::V4(ipv4) => {
                let octets = ipv4.octets();
                // 10.0.0.0/8
                octets[0] == 10 ||
                    // 172.16.0.0/12
                    (octets[0] == 172 && octets[1] >= 16 && octets[1] <= 31) ||
                    // 192.168.0.0/16
                    (octets[0] == 192 && octets[1] == 168) ||
                    // 127.0.0.0/8 (loopback)
                    octets[0] == 127
            }
            IpAddr::V6(ipv6) => {
                // IPv6 私有地址和本地地址
                ipv6.is_loopback() ||
                    ipv6.is_unspecified() ||
                    // fc00::/7 (Unique Local Addresses)
                    (ipv6.octets()[0] & 0xfe) == 0xfc ||
                    // fe80::/10 (Link-Local Addresses)
                    (ipv6.octets()[0] == 0xfe && (ipv6.octets()[1] & 0xc0) == 0x80)
            }
        }
    }

    /// 检查IP地址是否为本地回环地址
    ///
    /// # 参数
    /// * `ip` - IP地址
    pub fn is_loopback_ip(ip: &IpAddr) -> bool {
        match ip {
            IpAddr::V4(ipv4) => ipv4.is_loopback(),
            IpAddr::V6(ipv6) => ipv6.is_loopback(),
        }
    }

    /// 验证IP地址格式
    ///
    /// # 参数
    /// * `ip_str` - IP地址字符串
    pub fn validate_ip_format(ip_str: &str) -> AppResult<IpAddr> {
        ip_str
            .parse::<IpAddr>()
            .map_err(|_| AppError::validation_error("ip_address", "无效的IP地址格式"))
    }

    /// 检查网络连接性
    ///
    /// # 参数
    /// * `targets` - 目标地址列表 (host:port)
    /// * `timeout_ms` - 超时时间（毫秒）
    pub async fn check_connectivity(targets: &[String], timeout_ms: u64) -> Vec<(String, bool)> {
        use futures::future::join_all;

        let futures = targets.iter().map(|target| {
            let target = target.clone();
            async move {
                let parts: Vec<&str> = target.split(':').collect();
                if parts.len() != 2 {
                    return (target, false);
                }

                let host = parts[0];
                let port = match parts[1].parse::<u16>() {
                    Ok(port) => port,
                    Err(_) => return (target, false),
                };

                let reachable = Self::check_host_reachable(host, port, timeout_ms).await;
                (target, reachable)
            }
        });

        join_all(futures).await
    }
}

/// 网络监控器
///
/// 提供网络状态监控功能
pub struct NetworkMonitor {
    /// 监控目标
    targets: Vec<String>,
    /// 检查间隔（秒）
    check_interval: u64,
    /// 超时时间（毫秒）
    timeout_ms: u64,
}

impl NetworkMonitor {
    /// 创建新的网络监控器
    ///
    /// # 参数
    /// * `targets` - 监控目标列表
    /// * `check_interval` - 检查间隔（秒）
    /// * `timeout_ms` - 超时时间（毫秒）
    pub fn new(targets: Vec<String>, check_interval: u64, timeout_ms: u64) -> Self {
        Self {
            targets,
            check_interval,
            timeout_ms,
        }
    }

    /// 开始监控
    pub async fn start_monitoring<F>(&self, callback: F) -> AppResult<()>
    where
        F: Fn(Vec<(String, bool)>) + Send + Sync + 'static,
    {
        let mut interval = tokio::time::interval(Duration::from_secs(self.check_interval));

        loop {
            interval.tick().await;

            let results = NetworkUtils::check_connectivity(&self.targets, self.timeout_ms).await;
            callback(results);
        }
    }

    /// 执行单次检查
    pub async fn check_once(&self) -> Vec<(String, bool)> {
        NetworkUtils::check_connectivity(&self.targets, self.timeout_ms).await
    }

    /// 添加监控目标
    ///
    /// # 参数
    /// * `target` - 新的监控目标
    pub fn add_target(&mut self, target: String) {
        if !self.targets.contains(&target) {
            self.targets.push(target);
        }
    }

    /// 移除监控目标
    ///
    /// # 参数
    /// * `target` - 要移除的监控目标
    pub fn remove_target(&mut self, target: &str) {
        self.targets.retain(|t| t != target);
    }

    /// 获取监控目标列表
    pub fn get_targets(&self) -> &[String] {
        &self.targets
    }

    /// 设置检查间隔
    ///
    /// # 参数
    /// * `interval` - 新的检查间隔（秒）
    pub fn set_check_interval(&mut self, interval: u64) {
        self.check_interval = interval;
    }

    /// 设置超时时间
    ///
    /// # 参数
    /// * `timeout_ms` - 新的超时时间（毫秒）
    pub fn set_timeout(&mut self, timeout_ms: u64) {
        self.timeout_ms = timeout_ms;
    }
}

/// HTTP客户端工具
///
/// 提供HTTP请求功能
pub struct HttpClient {
    client: reqwest::Client,
    base_url: Option<String>,
    default_timeout: Duration,
}

impl HttpClient {
    /// 创建新的HTTP客户端
    ///
    /// # 参数
    /// * `base_url` - 基础URL
    /// * `timeout_ms` - 默认超时时间（毫秒）
    pub fn new(base_url: Option<String>, timeout_ms: u64) -> AppResult<Self> {
        let client = reqwest::Client::builder()
            .timeout(Duration::from_millis(timeout_ms))
            .build()
            .map_err(|e| AppError::network_error(format!("创建HTTP客户端失败: {}", e)))?;

        Ok(Self {
            client,
            base_url,
            default_timeout: Duration::from_millis(timeout_ms),
        })
    }

    /// 构建完整URL
    ///
    /// # 参数
    /// * `path` - 路径
    fn build_url(&self, path: &str) -> String {
        match &self.base_url {
            Some(base) => {
                if path.starts_with('/') {
                    format!("{}{}", base.trim_end_matches('/'), path)
                } else {
                    format!("{}/{}", base.trim_end_matches('/'), path)
                }
            }
            None => path.to_string(),
        }
    }

    /// 发送GET请求
    ///
    /// # 参数
    /// * `path` - 请求路径
    /// * `headers` - 请求头
    pub async fn get(
        &self,
        path: &str,
        headers: Option<&[(&str, &str)]>,
    ) -> AppResult<reqwest::Response> {
        let url = self.build_url(path);
        let mut request = self.client.get(&url);

        if let Some(headers) = headers {
            for (key, value) in headers {
                request = request.header(*key, *value);
            }
        }

        request
            .send()
            .await
            .map_err(|e| AppError::network_error(format!("GET请求失败: {}", e)))
    }

    /// 发送POST请求
    ///
    /// # 参数
    /// * `path` - 请求路径
    /// * `body` - 请求体
    /// * `headers` - 请求头
    pub async fn post(
        &self,
        path: &str,
        body: Option<String>,
        headers: Option<&[(&str, &str)]>,
    ) -> AppResult<reqwest::Response> {
        let url = self.build_url(path);
        let mut request = self.client.post(&url);

        if let Some(body) = body {
            request = request.body(body);
        }

        if let Some(headers) = headers {
            for (key, value) in headers {
                request = request.header(*key, *value);
            }
        }

        request
            .send()
            .await
            .map_err(|e| AppError::network_error(format!("POST请求失败: {}", e)))
    }

    /// 发送PUT请求
    ///
    /// # 参数
    /// * `path` - 请求路径
    /// * `body` - 请求体
    /// * `headers` - 请求头
    pub async fn put(
        &self,
        path: &str,
        body: Option<String>,
        headers: Option<&[(&str, &str)]>,
    ) -> AppResult<reqwest::Response> {
        let url = self.build_url(path);
        let mut request = self.client.put(&url);

        if let Some(body) = body {
            request = request.body(body);
        }

        if let Some(headers) = headers {
            for (key, value) in headers {
                request = request.header(*key, *value);
            }
        }

        request
            .send()
            .await
            .map_err(|e| AppError::network_error(format!("PUT请求失败: {}", e)))
    }

    /// 发送DELETE请求
    ///
    /// # 参数
    /// * `path` - 请求路径
    /// * `headers` - 请求头
    pub async fn delete(
        &self,
        path: &str,
        headers: Option<&[(&str, &str)]>,
    ) -> AppResult<reqwest::Response> {
        let url = self.build_url(path);
        let mut request = self.client.delete(&url);

        if let Some(headers) = headers {
            for (key, value) in headers {
                request = request.header(*key, *value);
            }
        }

        request
            .send()
            .await
            .map_err(|e| AppError::network_error(format!("DELETE请求失败: {}", e)))
    }

    /// 检查URL是否可访问
    ///
    /// # 参数
    /// * `url` - 要检查的URL
    pub async fn check_url_accessible(&self, url: &str) -> bool {
        match self.client.head(url).send().await {
            Ok(response) => response.status().is_success(),
            Err(_) => false,
        }
    }

    /// 下载文件
    ///
    /// # 参数
    /// * `url` - 文件URL
    /// * `file_path` - 保存路径
    pub async fn download_file(&self, url: &str, file_path: &str) -> AppResult<()> {
        let response = self
            .client
            .get(url)
            .send()
            .await
            .map_err(|e| AppError::network_error(format!("下载请求失败: {}", e)))?;

        if !response.status().is_success() {
            return Err(AppError::network_error(format!(
                "下载失败，状态码: {}",
                response.status()
            )));
        }

        let content = response
            .bytes()
            .await
            .map_err(|e| AppError::network_error(format!("读取响应内容失败: {}", e)))?;

        tokio::fs::write(file_path, content)
            .await
            .map_err(|e| AppError::file_system_error(format!("写入文件失败: {}", e)))?;

        Ok(())
    }
}

/// 检查网络连接性
///
/// # 参数
/// * `host` - 主机地址
/// * `port` - 端口号
///
/// # 返回
/// * `AppResult<bool>` - 连接性检查结果
pub async fn check_connectivity(host: &str, port: u16) -> AppResult<bool> {
    let result = NetworkUtils::check_host_reachable(host, port, 5000).await;
    Ok(result)
}

/// 发送通知
///
/// # 参数
/// * `message` - 通知消息
/// * `recipient` - 接收者
///
/// # 返回
/// * `AppResult<()>` - 发送结果
pub async fn send_notification(message: &str, recipient: &str) -> AppResult<()> {
    // 这里可以实现具体的通知发送逻辑，比如邮件、短信、Webhook等
    tracing::info!("发送通知给 {}: {}", recipient, message);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::net::Ipv4Addr;

    #[tokio::test]
    async fn test_check_host_reachable() {
        // 测试本地回环地址
        let reachable = NetworkUtils::check_host_reachable("127.0.0.1", 80, 1000).await;
        // 注意：这个测试可能失败，因为端口80可能没有开放
        println!("127.0.0.1:80 reachable: {}", reachable);
    }

    #[tokio::test]
    async fn test_resolve_hostname() {
        match NetworkUtils::resolve_hostname("localhost").await {
            Ok(ips) => {
                assert!(!ips.is_empty());
                println!("Resolved IPs for localhost: {:?}", ips);
            }
            Err(e) => {
                println!("DNS resolution failed: {}", e);
            }
        }
    }

    #[test]
    fn test_is_private_ip() {
        let private_ipv4 = IpAddr::V4(Ipv4Addr::new(192, 168, 1, 1));
        assert!(NetworkUtils::is_private_ip(&private_ipv4));

        let public_ipv4 = IpAddr::V4(Ipv4Addr::new(8, 8, 8, 8));
        assert!(!NetworkUtils::is_private_ip(&public_ipv4));

        let loopback = IpAddr::V4(Ipv4Addr::new(127, 0, 0, 1));
        assert!(NetworkUtils::is_private_ip(&loopback));
    }

    #[test]
    fn test_validate_ip_format() {
        assert!(NetworkUtils::validate_ip_format("192.168.1.1").is_ok());
        assert!(NetworkUtils::validate_ip_format("::1").is_ok());
        assert!(NetworkUtils::validate_ip_format("invalid-ip").is_err());
    }

    #[tokio::test]
    async fn test_network_monitor() {
        let targets = vec!["127.0.0.1:22".to_string(), "127.0.0.1:80".to_string()];

        let monitor = NetworkMonitor::new(targets, 5, 1000);
        let results = monitor.check_once().await;

        println!("Network monitor results: {:?}", results);
        assert_eq!(results.len(), 2);
    }

    #[tokio::test]
    async fn test_http_client() {
        let client = HttpClient::new(None, 5000).unwrap();

        // 测试一个公共API（如果网络可用）
        match client.get("https://httpbin.org/get", None).await {
            Ok(response) => {
                println!("HTTP GET status: {}", response.status());
                assert!(response.status().is_success());
            }
            Err(e) => {
                println!("HTTP GET failed: {}", e);
                // 网络测试可能失败，这是正常的
            }
        }
    }

    #[tokio::test]
    async fn test_port_scanning() {
        // 扫描本地常见端口
        let open_ports = NetworkUtils::scan_ports("127.0.0.1", 20, 25, 100, 5).await;
        println!("Open ports on localhost (20-25): {:?}", open_ports);
    }
}