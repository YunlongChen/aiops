//! 运行时管理器模型
//! 
//! 定义运行时管理器的数据结构和数据库操作

use super::{RuntimeType, PaginationParams, PaginatedResponse, PaginationInfo};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::{FromRow, SqlitePool, Row, Pool, Sqlite};
use uuid::Uuid;
use utoipa::{ToSchema, IntoParams};



/// 运行时管理器状态
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum ManagerStatus {
    /// 活跃状态
    Active,
    /// 非活跃状态
    Inactive,
    /// 错误状态
    Error,
    /// 维护状态
    Maintenance,
}

impl std::fmt::Display for ManagerStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ManagerStatus::Active => write!(f, "active"),
            ManagerStatus::Inactive => write!(f, "inactive"),
            ManagerStatus::Error => write!(f, "error"),
            ManagerStatus::Maintenance => write!(f, "maintenance"),
        }
    }
}

/// 运行时管理器模型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuntimeManager {
    pub id: String,
    pub name: String,
    pub runtime_type: RuntimeType,
    pub config: Option<String>,
    pub status: String,
    pub tags: Option<Vec<String>>,
    pub last_heartbeat: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 创建运行时管理器请求
#[derive(Debug, Deserialize)]
pub struct CreateRuntimeManagerRequest {
    pub name: String,
    pub runtime_type: RuntimeType,
    pub config: Option<serde_json::Value>,
    pub tags: Option<Vec<String>>,
}

/// 更新运行时管理器请求
#[derive(Debug, Deserialize)]
pub struct UpdateRuntimeManagerRequest {
    pub name: Option<String>,
    pub runtime_type: Option<RuntimeType>,
    pub config: Option<serde_json::Value>,
    pub status: Option<ManagerStatus>,
    pub tags: Option<Vec<String>>,
}

/// 运行时管理器查询参数
#[derive(Debug, Deserialize, ToSchema, IntoParams)]
pub struct RuntimeManagerQuery {
    #[serde(flatten)]
    /// 分页参数
    pub pagination: PaginationParams,
    /// 按名称筛选
    pub name: Option<String>,
    /// 按运行时类型筛选
    pub runtime_type: Option<RuntimeType>,
    /// 按状态筛选
    pub status: Option<String>,
    /// 按标签筛选（逗号分隔的标签列表）
    pub tags: Option<String>,
}

/// 运行时管理器查询结果
#[derive(Debug, Serialize)]
pub struct RuntimeManagerQueryResult {
    pub data: Vec<RuntimeManager>,
    pub pagination: PaginationInfo,
}

/// 运行时管理器配置
#[derive(Debug, Serialize, Deserialize)]
pub struct RuntimeConfig {
    /// Docker配置
    pub docker: Option<DockerConfig>,
    /// Kubernetes配置
    pub kubernetes: Option<KubernetesConfig>,
    /// 本地配置
    pub local: Option<LocalConfig>,
}

/// Docker运行时配置
#[derive(Debug, Serialize, Deserialize)]
pub struct DockerConfig {
    pub host: Option<String>,
    pub tls_verify: Option<bool>,
    pub cert_path: Option<String>,
    pub api_version: Option<String>,
    pub registry: Option<String>,
    pub network: Option<String>,
}

/// Kubernetes运行时配置
#[derive(Debug, Serialize, Deserialize)]
pub struct KubernetesConfig {
    pub kubeconfig_path: Option<String>,
    pub namespace: Option<String>,
    pub context: Option<String>,
    pub cluster: Option<String>,
    pub service_account: Option<String>,
}

/// 本地运行时配置
#[derive(Debug, Serialize, Deserialize)]
pub struct LocalConfig {
    pub python_path: Option<String>,
    pub working_directory: Option<String>,
    pub environment_variables: Option<std::collections::HashMap<String, String>>,
    pub timeout_seconds: Option<u64>,
}

impl RuntimeManager {
    /// 创建新的运行时管理器
    pub async fn create(
        pool: &Pool<Sqlite>,
        req: CreateRuntimeManagerRequest,
    ) -> anyhow::Result<RuntimeManager> {
        let id = Uuid::new_v4().to_string();
        let now = Utc::now();
        let config_str = req.config.map(|c| serde_json::to_string(&c).unwrap_or_default());
        let runtime_type_str = req.runtime_type.to_string();
        let tags_str = req.tags.map(|tags| serde_json::to_string(&tags).unwrap_or_default());

        sqlx::query(
            r#"
            INSERT INTO runtime_managers (id, name, runtime_type, config, status, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            "#,
        )
        .bind(&id)
        .bind(&req.name)
        .bind(&runtime_type_str)
        .bind(&config_str)
        .bind(ManagerStatus::Inactive.to_string())
        .bind(&tags_str)
        .bind(&now)
        .bind(&now)
        .execute(pool)
        .await?;

        Self::find_by_id(pool, &id).await
    }

    /// 根据ID查找运行时管理器
    pub async fn find_by_id(pool: &SqlitePool, id: &str) -> anyhow::Result<RuntimeManager> {
        let row = sqlx::query(
            "SELECT * FROM runtime_managers WHERE id = ?"
        )
        .bind(id)
        .fetch_one(pool)
        .await?;

        let runtime_type_str: String = row.get("runtime_type");
        let runtime_type = match runtime_type_str.as_str() {
            "local" => RuntimeType::Local,
            "docker" => RuntimeType::Docker,
            "kubernetes" => RuntimeType::Kubernetes,
            _ => return Err(anyhow::anyhow!("未知的运行时类型: {}", runtime_type_str)),
        };

        let tags_str: Option<String> = row.get("tags");
        let tags = tags_str.and_then(|s| serde_json::from_str(&s).ok());

        let manager = RuntimeManager {
            id: row.get("id"),
            name: row.get("name"),
            runtime_type,
            config: row.get("config"),
            status: row.get("status"),
            tags,
            last_heartbeat: row.get("last_heartbeat"),
            created_at: row.get("created_at"),
            updated_at: row.get("updated_at"),
        };

        Ok(manager)
    }

    /// 根据ID查找运行时管理器（可选）
    pub async fn find_by_id_optional(pool: &SqlitePool, id: &str) -> anyhow::Result<Option<RuntimeManager>> {
        let row = sqlx::query(
            "SELECT * FROM runtime_managers WHERE id = ?"
        )
        .bind(id)
        .fetch_optional(pool)
        .await?;

        if let Some(row) = row {
            let runtime_type_str: String = row.get("runtime_type");
            let runtime_type = match runtime_type_str.as_str() {
                "local" => RuntimeType::Local,
                "docker" => RuntimeType::Docker,
                "kubernetes" => RuntimeType::Kubernetes,
                _ => return Err(anyhow::anyhow!("未知的运行时类型: {}", runtime_type_str)),
            };

            let tags_str: Option<String> = row.get("tags");
            let tags = tags_str.and_then(|s| serde_json::from_str(&s).ok());

            let manager = RuntimeManager {
                id: row.get("id"),
                name: row.get("name"),
                runtime_type,
                config: row.get("config"),
                status: row.get("status"),
                tags,
                last_heartbeat: row.get("last_heartbeat"),
                created_at: row.get("created_at"),
                updated_at: row.get("updated_at"),
            };
            Ok(Some(manager))
        } else {
            Ok(None)
        }
    }

    /// 根据ID查找运行时管理器
    pub async fn get_by_id(
        pool: &Pool<Sqlite>,
        id: &str,
    ) -> anyhow::Result<Option<Self>> {
        let row = sqlx::query(
            "SELECT * FROM runtime_managers WHERE id = ?"
        )
        .bind(id)
        .fetch_optional(pool)
        .await?;

        if let Some(row) = row {
            let runtime_type_str: String = row.get("runtime_type");
            let runtime_type = match runtime_type_str.as_str() {
                "local" => RuntimeType::Local,
                "docker" => RuntimeType::Docker,
                "kubernetes" => RuntimeType::Kubernetes,
                _ => return Err(anyhow::anyhow!("未知的运行时类型: {}", runtime_type_str)),
            };

            let tags_str: Option<String> = row.get("tags");
            let tags = tags_str.and_then(|s| serde_json::from_str(&s).ok());

            let manager = RuntimeManager {
                id: row.get("id"),
                name: row.get("name"),
                runtime_type,
                config: row.get("config"),
                status: row.get("status"),
                tags,
                last_heartbeat: row.get("last_heartbeat"),
                created_at: row.get("created_at"),
                updated_at: row.get("updated_at"),
            };
            Ok(Some(manager))
        } else {
            Ok(None)
        }
    }

    /// 分页查询运行时管理器
    pub async fn find_all(
        pool: &Pool<Sqlite>,
        query: RuntimeManagerQuery,
    ) -> anyhow::Result<RuntimeManagerQueryResult> {
        query.pagination.validate()?;

        let mut sql = "SELECT * FROM runtime_managers WHERE 1=1".to_string();
        let mut count_sql = "SELECT COUNT(*) FROM runtime_managers WHERE 1=1".to_string();
        let mut params = Vec::new();

        // 添加查询条件
        if let Some(runtime_type) = &query.runtime_type {
            sql.push_str(" AND runtime_type = ?");
            count_sql.push_str(" AND runtime_type = ?");
            params.push(runtime_type.to_string());
        }

        if let Some(status) = &query.status {
            sql.push_str(" AND status = ?");
            count_sql.push_str(" AND status = ?");
            params.push(status.to_string());
        }

        if let Some(name) = &query.name {
            sql.push_str(" AND name LIKE ?");
            count_sql.push_str(" AND name LIKE ?");
            params.push(format!("%{}%", name));
        }

        if let Some(tags) = &query.tags {
            let tag_list: Vec<&str> = tags.split(',').map(|s| s.trim()).collect();
            for tag in tag_list {
                sql.push_str(" AND tags LIKE ?");
                count_sql.push_str(" AND tags LIKE ?");
                params.push(format!("%{}%", tag));
            }
        }

        // 添加排序和分页
        sql.push_str(" ORDER BY created_at DESC LIMIT ? OFFSET ?");

        // 获取总数
        let mut count_query = sqlx::query_scalar::<_, i64>(&count_sql);
        for param in &params {
            count_query = count_query.bind(param);
        }
        let total = count_query.fetch_one(pool).await? as u64;

        // 获取数据
        let mut data_query = sqlx::query(&sql);
        for param in &params {
            data_query = data_query.bind(param);
        }
        data_query = data_query
            .bind(query.pagination.limit as i64)
            .bind(query.pagination.offset() as i64);

        let rows = data_query.fetch_all(pool).await?;
        let mut data = Vec::new();
        
        for row in rows {
            let runtime_type_str: String = row.get("runtime_type");
            let runtime_type = match runtime_type_str.as_str() {
                "local" => RuntimeType::Local,
                "docker" => RuntimeType::Docker,
                "kubernetes" => RuntimeType::Kubernetes,
                _ => continue,
            };
            
            let tags_str: Option<String> = row.get("tags");
            let tags = tags_str.and_then(|s| serde_json::from_str(&s).ok());
            
            let manager = RuntimeManager {
                id: row.get("id"),
                name: row.get("name"),
                runtime_type,
                config: row.get("config"),
                status: row.get("status"),
                tags,
                last_heartbeat: row.get("last_heartbeat"),
                created_at: row.get("created_at"),
                updated_at: row.get("updated_at"),
            };
            data.push(manager);
        }

        let pagination = PaginationInfo::new(
            query.pagination.page,
            query.pagination.limit,
            total,
        );

        Ok(RuntimeManagerQueryResult { data, pagination })
    }

    /// 更新运行时管理器
    pub async fn update(
        pool: &Pool<Sqlite>,
        id: &str,
        req: UpdateRuntimeManagerRequest,
    ) -> anyhow::Result<RuntimeManager> {
        let mut updates = Vec::new();
        let mut params = Vec::new();

        if let Some(name) = &req.name {
            updates.push("name = ?");
            params.push(name.clone());
        }

        if let Some(runtime_type) = &req.runtime_type {
            updates.push("runtime_type = ?");
            params.push(runtime_type.to_string());
        }

        if let Some(config) = &req.config {
            updates.push("config = ?");
            params.push(serde_json::to_string(config).unwrap_or_default());
        }

        if let Some(status) = &req.status {
            updates.push("status = ?");
            params.push(status.to_string());
        }

        if let Some(tags) = &req.tags {
            updates.push("tags = ?");
            params.push(serde_json::to_string(tags).unwrap_or_default());
        }

        if updates.is_empty() {
            return Self::find_by_id(pool, id).await;
        }

        updates.push("updated_at = ?");
        params.push(Utc::now().to_rfc3339());

        let sql = format!(
            "UPDATE runtime_managers SET {} WHERE id = ?",
            updates.join(", ")
        );

        let mut query = sqlx::query(&sql);
        for param in params {
            query = query.bind(param);
        }
        query = query.bind(id);

        query.execute(pool).await?;

        Self::find_by_id(pool, id).await
    }

    /// 更新心跳时间
    pub async fn update_heartbeat(pool: &Pool<Sqlite>, id: &str) -> anyhow::Result<()> {
        let now = Utc::now();
        
        sqlx::query(
            "UPDATE runtime_managers SET last_heartbeat = ?, status = ? WHERE id = ?"
        )
        .bind(&now)
        .bind(ManagerStatus::Active.to_string())
        .bind(id)
        .execute(pool)
        .await?;

        Ok(())
    }

    /// 更新状态
    pub async fn update_status(
        pool: &Pool<Sqlite>,
        id: &str,
        status: ManagerStatus,
    ) -> anyhow::Result<()> {
        let now = Utc::now();
        
        sqlx::query(
            "UPDATE runtime_managers SET status = ?, updated_at = ? WHERE id = ?"
        )
        .bind(status.to_string())
        .bind(now.to_rfc3339())
        .bind(id)
        .execute(pool)
        .await?;

        Ok(())
    }

    /// 删除运行时管理器
    pub async fn delete(pool: &Pool<Sqlite>, id: &str) -> anyhow::Result<()> {
        sqlx::query("DELETE FROM runtime_managers WHERE id = ?")
            .bind(id)
            .execute(pool)
            .await?;

        Ok(())
    }

    /// 获取运行时类型
    pub fn get_runtime_type(&self) -> RuntimeType {
        self.runtime_type.clone()
    }

    /// 获取状态
    pub fn get_status(&self) -> anyhow::Result<ManagerStatus> {
        match self.status.as_str() {
            "active" => Ok(ManagerStatus::Active),
            "inactive" => Ok(ManagerStatus::Inactive),
            "error" => Ok(ManagerStatus::Error),
            "maintenance" => Ok(ManagerStatus::Maintenance),
            _ => anyhow::bail!("未知的管理器状态: {}", self.status),
        }
    }

    /// 获取配置
    pub fn get_config(&self) -> Option<serde_json::Value> {
        self.config
            .as_ref()
            .and_then(|c| serde_json::from_str(c).ok())
    }

    /// 检查是否在线
    pub fn is_online(&self) -> bool {
        if let Some(last_heartbeat) = self.last_heartbeat {
            let now = Utc::now();
            let diff = now - last_heartbeat;
            // 如果超过5分钟没有心跳，认为离线
            diff.num_minutes() < 5 && self.status == ManagerStatus::Active.to_string()
        } else {
            false
        }
    }
}