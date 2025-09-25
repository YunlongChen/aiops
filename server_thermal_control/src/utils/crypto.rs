use crate::models::error::{AppError, AppResult};
use base64::{engine::general_purpose, Engine as _};
use rand::{thread_rng, Rng};
use sha2::{Digest, Sha256};
use std::time::{SystemTime, UNIX_EPOCH};

/// 加密工具集
///
/// 提供各种加密和安全相关功能
pub struct CryptoUtils;

impl CryptoUtils {
    /// 生成随机字符串
    ///
    /// # 参数
    /// * `length` - 字符串长度
    /// * `charset` - 字符集，None表示使用默认字符集
    pub fn generate_random_string(length: usize, charset: Option<&str>) -> String {
        let default_charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        let chars: Vec<char> = charset.unwrap_or(default_charset).chars().collect();

        let mut rng = thread_rng();
        (0..length)
            .map(|_| chars[rng.gen_range(0..chars.len())])
            .collect()
    }

    /// 生成随机数字字符串
    ///
    /// # 参数
    /// * `length` - 字符串长度
    pub fn generate_random_numeric_string(length: usize) -> String {
        Self::generate_random_string(length, Some("0123456789"))
    }

    /// 生成随机字母字符串
    ///
    /// # 参数
    /// * `length` - 字符串长度
    /// * `uppercase` - 是否包含大写字母
    /// * `lowercase` - 是否包含小写字母
    pub fn generate_random_alpha_string(length: usize, uppercase: bool, lowercase: bool) -> String {
        let mut charset = String::new();
        if uppercase {
            charset.push_str("ABCDEFGHIJKLMNOPQRSTUVWXYZ");
        }
        if lowercase {
            charset.push_str("abcdefghijklmnopqrstuvwxyz");
        }

        if charset.is_empty() {
            charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz".to_string();
        }

        Self::generate_random_string(length, Some(&charset))
    }

    /// 生成随机字节数组
    ///
    /// # 参数
    /// * `length` - 字节数组长度
    pub fn generate_random_bytes(length: usize) -> Vec<u8> {
        let mut rng = thread_rng();
        (0..length).map(|_| rng.gen()).collect()
    }

    /// 计算SHA256哈希
    ///
    /// # 参数
    /// * `data` - 要哈希的数据
    pub fn sha256_hash(data: &[u8]) -> String {
        let mut hasher = Sha256::new();
        hasher.update(data);
        format!("{:x}", hasher.finalize())
    }

    /// 计算字符串的SHA256哈希
    ///
    /// # 参数
    /// * `text` - 要哈希的字符串
    pub fn sha256_hash_string(text: &str) -> String {
        Self::sha256_hash(text.as_bytes())
    }

    /// Base64编码
    ///
    /// # 参数
    /// * `data` - 要编码的数据
    pub fn base64_encode(data: &[u8]) -> String {
        general_purpose::STANDARD.encode(data)
    }

    /// Base64解码
    ///
    /// # 参数
    /// * `encoded` - 要解码的Base64字符串
    pub fn base64_decode(encoded: &str) -> AppResult<Vec<u8>> {
        general_purpose::STANDARD
            .decode(encoded)
            .map_err(|e| AppError::serialization_error(format!("Base64解码失败: {}", e)))
    }

    /// URL安全的Base64编码
    ///
    /// # 参数
    /// * `data` - 要编码的数据
    pub fn base64_url_encode(data: &[u8]) -> String {
        general_purpose::URL_SAFE_NO_PAD.encode(data)
    }

    /// URL安全的Base64解码
    ///
    /// # 参数
    /// * `encoded` - 要解码的Base64字符串
    pub fn base64_url_decode(encoded: &str) -> AppResult<Vec<u8>> {
        general_purpose::URL_SAFE_NO_PAD
            .decode(encoded)
            .map_err(|e| AppError::serialization_error(format!("Base64 URL解码失败: {}", e)))
    }

    /// 生成UUID v4
    pub fn generate_uuid() -> String {
        uuid::Uuid::new_v4().to_string()
    }

    /// 生成简短的UUID（去掉连字符）
    pub fn generate_short_uuid() -> String {
        uuid::Uuid::new_v4().simple().to_string()
    }

    /// 生成时间戳
    pub fn generate_timestamp() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs()
    }

    /// 生成毫秒时间戳
    pub fn generate_timestamp_millis() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64
    }

    /// 生成纳秒时间戳
    pub fn generate_timestamp_nanos() -> u128 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_nanos()
    }

    /// 验证哈希值
    ///
    /// # 参数
    /// * `data` - 原始数据
    /// * `hash` - 要验证的哈希值
    pub fn verify_sha256_hash(data: &[u8], hash: &str) -> bool {
        Self::sha256_hash(data) == hash
    }

    /// 验证字符串哈希值
    ///
    /// # 参数
    /// * `text` - 原始字符串
    /// * `hash` - 要验证的哈希值
    pub fn verify_sha256_hash_string(text: &str, hash: &str) -> bool {
        Self::sha256_hash_string(text) == hash
    }
}

/// 密码工具
///
/// 提供密码相关的安全功能
pub struct PasswordUtils;

impl PasswordUtils {
    /// 生成安全密码
    ///
    /// # 参数
    /// * `length` - 密码长度
    /// * `include_symbols` - 是否包含特殊符号
    pub fn generate_secure_password(length: usize, include_symbols: bool) -> String {
        let mut charset =
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789".to_string();
        if include_symbols {
            charset.push_str("!@#$%^&*()_+-=[]{}|;:,.<>?");
        }

        CryptoUtils::generate_random_string(length, Some(&charset))
    }

    /// 检查密码强度
    ///
    /// # 参数
    /// * `password` - 要检查的密码
    ///
    /// # 返回
    /// 密码强度分数（0-100）
    pub fn check_password_strength(password: &str) -> u8 {
        let mut score = 0u8;

        // 长度检查
        if password.len() >= 8 {
            score += 20;
        }
        if password.len() >= 12 {
            score += 10;
        }
        if password.len() >= 16 {
            score += 10;
        }

        // 字符类型检查
        if password.chars().any(|c| c.is_lowercase()) {
            score += 10;
        }
        if password.chars().any(|c| c.is_uppercase()) {
            score += 10;
        }
        if password.chars().any(|c| c.is_numeric()) {
            score += 10;
        }
        if password.chars().any(|c| !c.is_alphanumeric()) {
            score += 15;
        }

        // 复杂性检查
        let unique_chars = password
            .chars()
            .collect::<std::collections::HashSet<_>>()
            .len();
        if unique_chars >= password.len() / 2 {
            score += 15;
        }

        score.min(100)
    }

    /// 验证密码强度是否足够
    ///
    /// # 参数
    /// * `password` - 要验证的密码
    /// * `min_score` - 最低分数要求
    pub fn validate_password_strength(password: &str, min_score: u8) -> AppResult<()> {
        let score = Self::check_password_strength(password);
        if score >= min_score {
            Ok(())
        } else {
            Err(AppError::validation_error(
                "password",
                &format!("密码强度不足，当前分数: {}, 要求: {}", score, min_score),
            ))
        }
    }
}

/// API密钥工具
///
/// 提供API密钥生成和验证功能
pub struct ApiKeyUtils;

impl ApiKeyUtils {
    /// 生成API密钥
    ///
    /// # 参数
    /// * `prefix` - 密钥前缀
    /// * `length` - 密钥长度（不包括前缀）
    pub fn generate_api_key(prefix: Option<&str>, length: usize) -> String {
        let key = CryptoUtils::generate_random_string(length, None);
        match prefix {
            Some(p) => format!("{}_{}", p, key),
            None => key,
        }
    }

    /// 生成带校验和的API密钥
    ///
    /// # 参数
    /// * `prefix` - 密钥前缀
    /// * `length` - 密钥长度（不包括前缀和校验和）
    pub fn generate_api_key_with_checksum(prefix: Option<&str>, length: usize) -> String {
        let key = CryptoUtils::generate_random_string(length, None);
        let checksum = &CryptoUtils::sha256_hash_string(&key)[..8];

        match prefix {
            Some(p) => format!("{}_{}_{}", p, key, checksum),
            None => format!("{}_{}", key, checksum),
        }
    }

    /// 验证带校验和的API密钥
    ///
    /// # 参数
    /// * `api_key` - 要验证的API密钥
    pub fn verify_api_key_checksum(api_key: &str) -> bool {
        let parts: Vec<&str> = api_key.split('_').collect();

        if parts.len() < 2 {
            return false;
        }

        let (key, checksum) = if parts.len() == 2 {
            (parts[0], parts[1])
        } else if parts.len() == 3 {
            (parts[1], parts[2])
        } else {
            return false;
        };

        let expected_checksum = &CryptoUtils::sha256_hash_string(key)[..8];
        checksum == expected_checksum
    }

    /// 掩码API密钥（用于日志记录）
    ///
    /// # 参数
    /// * `api_key` - 要掩码的API密钥
    /// * `visible_chars` - 可见字符数量
    pub fn mask_api_key(api_key: &str, visible_chars: usize) -> String {
        if api_key.len() <= visible_chars * 2 {
            return "*".repeat(api_key.len());
        }

        let start = &api_key[..visible_chars];
        let end = &api_key[api_key.len() - visible_chars..];
        let middle = "*".repeat(api_key.len() - visible_chars * 2);

        format!("{}{}{}", start, middle, end)
    }
}

/// 令牌工具
///
/// 提供访问令牌生成和验证功能
pub struct TokenUtils;

impl TokenUtils {
    /// 生成访问令牌
    ///
    /// # 参数
    /// * `user_id` - 用户ID
    /// * `expires_in` - 过期时间（秒）
    pub fn generate_access_token(user_id: &str, expires_in: u64) -> String {
        let timestamp = CryptoUtils::generate_timestamp();
        let expires_at = timestamp + expires_in;
        let payload = format!("{}:{}:{}", user_id, timestamp, expires_at);
        let signature = CryptoUtils::sha256_hash_string(&payload);

        CryptoUtils::base64_url_encode(format!("{}:{}", payload, signature).as_bytes())
    }

    /// 验证访问令牌
    ///
    /// # 参数
    /// * `token` - 要验证的令牌
    pub fn verify_access_token(token: &str) -> AppResult<(String, u64, u64)> {
        let decoded = CryptoUtils::base64_url_decode(token)?;
        let token_str = String::from_utf8(decoded)
            .map_err(|e| AppError::serialization_error(format!("令牌格式错误: {}", e)))?;

        let parts: Vec<&str> = token_str.split(':').collect();
        if parts.len() != 4 {
            return Err(AppError::validation_error("token", "令牌格式无效"));
        }

        let user_id = parts[0];
        let timestamp: u64 = parts[1]
            .parse()
            .map_err(|_| AppError::validation_error("token", "时间戳格式无效"))?;
        let expires_at: u64 = parts[2]
            .parse()
            .map_err(|_| AppError::validation_error("token", "过期时间格式无效"))?;
        let signature = parts[3];

        // 验证签名
        let payload = format!("{}:{}:{}", user_id, timestamp, expires_at);
        let expected_signature = CryptoUtils::sha256_hash_string(&payload);

        if signature != expected_signature {
            return Err(AppError::validation_error("token", "令牌签名无效"));
        }

        // 检查过期时间
        let current_timestamp = CryptoUtils::generate_timestamp();
        if current_timestamp > expires_at {
            return Err(AppError::validation_error("token", "令牌已过期"));
        }

        Ok((user_id.to_string(), timestamp, expires_at))
    }

    /// 生成刷新令牌
    ///
    /// # 参数
    /// * `user_id` - 用户ID
    pub fn generate_refresh_token(user_id: &str) -> String {
        let timestamp = CryptoUtils::generate_timestamp();
        let random_part = CryptoUtils::generate_random_string(32, None);
        let payload = format!("{}:{}:{}", user_id, timestamp, random_part);

        CryptoUtils::base64_url_encode(payload.as_bytes())
    }

    /// 解析刷新令牌
    ///
    /// # 参数
    /// * `token` - 要解析的刷新令牌
    pub fn parse_refresh_token(token: &str) -> AppResult<(String, u64)> {
        let decoded = CryptoUtils::base64_url_decode(token)?;
        let token_str = String::from_utf8(decoded)
            .map_err(|e| AppError::serialization_error(format!("令牌格式错误: {}", e)))?;

        let parts: Vec<&str> = token_str.split(':').collect();
        if parts.len() != 3 {
            return Err(AppError::validation_error("token", "刷新令牌格式无效"));
        }

        let user_id = parts[0];
        let timestamp: u64 = parts[1]
            .parse()
            .map_err(|_| AppError::validation_error("token", "时间戳格式无效"))?;

        Ok((user_id.to_string(), timestamp))
    }
}

/// 安全工具
///
/// 提供各种安全相关功能
pub struct SecurityUtils;

impl SecurityUtils {
    /// 生成随机盐值
    ///
    /// # 参数
    /// * `length` - 盐值长度
    pub fn generate_salt(length: usize) -> String {
        CryptoUtils::base64_encode(&CryptoUtils::generate_random_bytes(length))
    }

    /// 计算带盐哈希
    ///
    /// # 参数
    /// * `data` - 要哈希的数据
    /// * `salt` - 盐值
    pub fn hash_with_salt(data: &str, salt: &str) -> String {
        CryptoUtils::sha256_hash_string(&format!("{}{}", data, salt))
    }

    /// 验证带盐哈希
    ///
    /// # 参数
    /// * `data` - 原始数据
    /// * `salt` - 盐值
    /// * `hash` - 要验证的哈希值
    pub fn verify_hash_with_salt(data: &str, salt: &str, hash: &str) -> bool {
        Self::hash_with_salt(data, salt) == hash
    }

    /// 生成CSRF令牌
    pub fn generate_csrf_token() -> String {
        CryptoUtils::generate_random_string(32, None)
    }

    /// 生成会话ID
    pub fn generate_session_id() -> String {
        CryptoUtils::generate_random_string(64, None)
    }

    /// 生成随机nonce
    ///
    /// # 参数
    /// * `length` - nonce长度
    pub fn generate_nonce(length: usize) -> String {
        CryptoUtils::generate_random_string(length, None)
    }

    /// 计算HMAC-SHA256
    ///
    /// # 参数
    /// * `key` - 密钥
    /// * `data` - 要签名的数据
    pub fn hmac_sha256(key: &[u8], data: &[u8]) -> Vec<u8> {
        use hmac::{Hmac, Mac};
        type HmacSha256 = Hmac<Sha256>;

        let mut mac = HmacSha256::new_from_slice(key).expect("HMAC can take key of any size");
        mac.update(data);
        mac.finalize().into_bytes().to_vec()
    }

    /// 验证HMAC-SHA256
    ///
    /// # 参数
    /// * `key` - 密钥
    /// * `data` - 原始数据
    /// * `signature` - 要验证的签名
    pub fn verify_hmac_sha256(key: &[u8], data: &[u8], signature: &[u8]) -> bool {
        let expected = Self::hmac_sha256(key, data);
        expected == signature
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate_random_string() {
        let random_str = CryptoUtils::generate_random_string(10, None);
        assert_eq!(random_str.len(), 10);

        let numeric_str = CryptoUtils::generate_random_numeric_string(5);
        assert_eq!(numeric_str.len(), 5);
        assert!(numeric_str.chars().all(|c| c.is_numeric()));
    }

    #[test]
    fn test_sha256_hash() {
        let hash = CryptoUtils::sha256_hash_string("hello world");
        assert_eq!(hash.len(), 64); // SHA256 produces 64 hex characters

        let same_hash = CryptoUtils::sha256_hash_string("hello world");
        assert_eq!(hash, same_hash);

        let different_hash = CryptoUtils::sha256_hash_string("hello world!");
        assert_ne!(hash, different_hash);
    }

    #[test]
    fn test_base64_encoding() {
        let data = b"hello world";
        let encoded = CryptoUtils::base64_encode(data);
        let decoded = CryptoUtils::base64_decode(&encoded).unwrap();
        assert_eq!(data, decoded.as_slice());
    }

    #[test]
    fn test_uuid_generation() {
        let uuid = CryptoUtils::generate_uuid();
        assert_eq!(uuid.len(), 36); // Standard UUID format

        let short_uuid = CryptoUtils::generate_short_uuid();
        assert_eq!(short_uuid.len(), 32); // UUID without hyphens
    }

    #[test]
    fn test_password_strength() {
        assert!(PasswordUtils::check_password_strength("password") < 50);
        assert!(PasswordUtils::check_password_strength("Password123!") > 70);

        let strong_password = PasswordUtils::generate_secure_password(16, true);
        assert_eq!(strong_password.len(), 16);
        assert!(PasswordUtils::check_password_strength(&strong_password) > 60);
    }

    #[test]
    fn test_api_key_generation() {
        let api_key = ApiKeyUtils::generate_api_key(Some("test"), 32);
        assert!(api_key.starts_with("test_"));
        assert_eq!(api_key.len(), 37); // "test_" + 32 characters

        let api_key_with_checksum = ApiKeyUtils::generate_api_key_with_checksum(Some("test"), 32);
        assert!(ApiKeyUtils::verify_api_key_checksum(&api_key_with_checksum));
    }

    #[test]
    fn test_access_token() {
        let token = TokenUtils::generate_access_token("user123", 3600);
        let (user_id, _timestamp, _expires_at) = TokenUtils::verify_access_token(&token).unwrap();
        assert_eq!(user_id, "user123");
    }

    #[test]
    fn test_refresh_token() {
        let token = TokenUtils::generate_refresh_token("user123");
        let (user_id, _timestamp) = TokenUtils::parse_refresh_token(&token).unwrap();
        assert_eq!(user_id, "user123");
    }

    #[test]
    fn test_security_utils() {
        let salt = SecurityUtils::generate_salt(16);
        let hash = SecurityUtils::hash_with_salt("password", &salt);
        assert!(SecurityUtils::verify_hash_with_salt(
            "password", &salt, &hash
        ));
        assert!(!SecurityUtils::verify_hash_with_salt(
            "wrong_password",
            &salt,
            &hash
        ));

        let csrf_token = SecurityUtils::generate_csrf_token();
        assert_eq!(csrf_token.len(), 32);

        let session_id = SecurityUtils::generate_session_id();
        assert_eq!(session_id.len(), 64);
    }

    #[test]
    fn test_hmac() {
        let key = b"secret_key";
        let data = b"hello world";
        let signature = SecurityUtils::hmac_sha256(key, data);

        assert!(SecurityUtils::verify_hmac_sha256(key, data, &signature));
        assert!(!SecurityUtils::verify_hmac_sha256(
            key,
            b"different data",
            &signature
        ));
    }
}

/// 密码哈希函数
///
/// # 参数
/// * `password` - 原始密码
///
/// # 返回
/// * `AppResult<String>` - 哈希后的密码
pub fn hash_password(password: &str) -> AppResult<String> {
    use argon2::{
        password_hash::{rand_core::OsRng, SaltString},
        Argon2, PasswordHasher,
    };

    let salt = SaltString::generate(&mut OsRng);
    let argon2 = Argon2::default();

    match argon2.hash_password(password.as_bytes(), &salt) {
        Ok(hash) => Ok(hash.to_string()),
        Err(e) => Err(AppError::internal_server_error(&format!(
            "密码哈希失败: {}",
            e
        ))),
    }
}

/// 验证密码函数
///
/// # 参数
/// * `password` - 原始密码
/// * `hash` - 哈希值
///
/// # 返回
/// * `AppResult<bool>` - 验证结果
pub fn verify_password(password: &str, hash: &str) -> AppResult<bool> {
    use argon2::{Argon2, PasswordHash, PasswordVerifier};

    let parsed_hash = match PasswordHash::new(hash) {
        Ok(hash) => hash,
        Err(e) => {
            return Err(AppError::validation_error(
                "hash",
                &format!("无效的哈希格式: {}", e),
            ))
        }
    };

    let argon2 = Argon2::default();
    Ok(argon2
        .verify_password(password.as_bytes(), &parsed_hash)
        .is_ok())
}
