//! 测试用例模型
//! 
//! 定义测试用例的数据结构和数据库操作

use super::{RuntimeType, PaginationParams, PaginatedResponse, PaginationInfo};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::{FromRow, SqlitePool};
use uuid::Uuid;

/// 测试用例模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct TestCase {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub script_path: String,
    pub config_path: Option<String>,
    pub runtime_type: String,
    pub tags: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 创建测试用例请求
#[derive(Debug, Deserialize)]
pub struct CreateTestCaseRequest {
    pub name: String,
    pub description: Option<String>,
    pub script_path: String,
    pub config_path: Option<String>,
    pub runtime_type: RuntimeType,
    pub tags: Option<Vec<String>>,
}

/// 更新测试用例请求
#[derive(Debug, Deserialize)]
pub struct UpdateTestCaseRequest {
    pub name: Option<String>,
    pub description: Option<String>,
    pub script_path: Option<String>,
    pub config_path: Option<String>,
    pub runtime_type: Option<RuntimeType>,
    pub tags: Option<Vec<String>>,
}

/// 运行测试用例请求
#[derive(Debug, Deserialize)]
pub struct RunTestCaseRequest {
    pub runtime_type: Option<RuntimeType>,
    pub config_override: Option<String>,
    pub metadata: Option<serde_json::Value>,
}

/// 测试用例查询参数
#[derive(Debug, Deserialize)]
pub struct TestCaseQuery {
    #[serde(flatten)]
    pub pagination: PaginationParams,
    pub name: Option<String>,
    pub runtime_type: Option<RuntimeType>,
    pub tags: Option<String>,
}

impl TestCase {
    /// 获取运行时类型
    pub fn get_runtime_type(&self) -> anyhow::Result<RuntimeType> {
        match self.runtime_type.as_str() {
            "local" => Ok(RuntimeType::Local),
            "docker" => Ok(RuntimeType::Docker),
            "kubernetes" => Ok(RuntimeType::Kubernetes),
            _ => anyhow::bail!("未知的运行时类型: {}", self.runtime_type),
        }
    }

    /// 根据ID获取测试用例
    pub async fn get_by_id(
        pool: &SqlitePool,
        id: &str,
    ) -> anyhow::Result<Option<TestCase>> {
        let test_case = sqlx::query_as::<_, TestCase>(
            "SELECT * FROM test_cases WHERE id = ?"
        )
        .bind(id)
        .fetch_optional(pool)
        .await?;
        
        Ok(test_case)
    }

    /// 获取测试用例列表
    pub async fn list(
        pool: &SqlitePool,
        params: &PaginationParams,
        query: &TestCaseQuery,
    ) -> anyhow::Result<(Vec<TestCase>, PaginationInfo)> {
        let mut sql = "SELECT * FROM test_cases WHERE 1=1".to_string();
        let mut count_sql = "SELECT COUNT(*) FROM test_cases WHERE 1=1".to_string();
        let mut bind_values = Vec::new();

        // 添加查询条件
        if let Some(name) = &query.name {
            sql.push_str(" AND name LIKE ?");
            count_sql.push_str(" AND name LIKE ?");
            bind_values.push(format!("%{}%", name));
        }

        if let Some(runtime_type) = &query.runtime_type {
            sql.push_str(" AND runtime_type = ?");
            count_sql.push_str(" AND runtime_type = ?");
            bind_values.push(runtime_type.to_string());
        }

        // 添加排序和分页
        sql.push_str(" ORDER BY created_at DESC LIMIT ? OFFSET ?");
        
        // 获取总数
        let mut count_query = sqlx::query_scalar::<_, i64>(&count_sql);
        for value in &bind_values {
            count_query = count_query.bind(value);
        }
        let total = count_query.fetch_one(pool).await? as u32;

        // 获取数据
        let mut data_query = sqlx::query_as::<_, TestCase>(&sql);
        for value in &bind_values {
            data_query = data_query.bind(value);
        }
        data_query = data_query.bind(params.limit as i64);
        data_query = data_query.bind(params.offset() as i64);
        
        let test_cases = data_query.fetch_all(pool).await?;

        let pagination_info = PaginationInfo {
            page: params.page,
            limit: params.limit,
            total: total.into(),
            total_pages: (total + params.limit - 1) / params.limit,
            has_next: params.page < (total + params.limit - 1) / params.limit,
            has_prev: params.page > 1,
        };

        Ok((test_cases, pagination_info))
    }

    /// 创建新的测试用例
    pub async fn create(
        pool: &SqlitePool,
        req: CreateTestCaseRequest,
    ) -> anyhow::Result<TestCase> {
        let id = Uuid::new_v4().to_string();
        let now = Utc::now();
        let tags_str = req.tags.map(|tags| tags.join(","));
        let runtime_type_str = req.runtime_type.to_string();

        sqlx::query(
            r#"
            INSERT INTO test_cases (id, name, description, script_path, config_path, runtime_type, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            "#,
        )
        .bind(&id)
        .bind(&req.name)
        .bind(&req.description)
        .bind(&req.script_path)
        .bind(&req.config_path)
        .bind(&runtime_type_str)
        .bind(&tags_str)
        .bind(&now)
        .bind(&now)
        .execute(pool)
        .await?;

        Self::find_by_id(pool, &id).await
    }

    /// 根据ID查找测试用例
    pub async fn find_by_id(pool: &SqlitePool, id: &str) -> anyhow::Result<TestCase> {
        let test_case = sqlx::query_as::<_, TestCase>(
            "SELECT * FROM test_cases WHERE id = ?"
        )
        .bind(id)
        .fetch_one(pool)
        .await?;

        Ok(test_case)
    }

    /// 分页查询测试用例
    pub async fn find_all(
        pool: &SqlitePool,
        query: TestCaseQuery,
    ) -> anyhow::Result<PaginatedResponse<TestCase>> {
        query.pagination.validate()?;

        let mut sql = "SELECT * FROM test_cases WHERE 1=1".to_string();
        let mut count_sql = "SELECT COUNT(*) FROM test_cases WHERE 1=1".to_string();
        let mut params = Vec::new();

        // 添加查询条件
        if let Some(name) = &query.name {
            sql.push_str(" AND name LIKE ?");
            count_sql.push_str(" AND name LIKE ?");
            params.push(format!("%{}%", name));
        }

        if let Some(runtime_type) = &query.runtime_type {
            sql.push_str(" AND runtime_type = ?");
            count_sql.push_str(" AND runtime_type = ?");
            params.push(runtime_type.to_string());
        }

        if let Some(tags) = &query.tags {
            sql.push_str(" AND tags LIKE ?");
            count_sql.push_str(" AND tags LIKE ?");
            params.push(format!("%{}%", tags));
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
        let mut data_query = sqlx::query_as::<_, TestCase>(&sql);
        for param in &params {
            data_query = data_query.bind(param);
        }
        data_query = data_query
            .bind(query.pagination.limit as i64)
            .bind(query.pagination.offset() as i64);

        let data = data_query.fetch_all(pool).await?;

        let pagination = PaginationInfo::new(
            query.pagination.page,
            query.pagination.limit,
            total,
        );

        Ok(PaginatedResponse { data, pagination })
    }

    /// 更新测试用例
    pub async fn update(
        pool: &SqlitePool,
        id: &str,
        req: UpdateTestCaseRequest,
    ) -> anyhow::Result<TestCase> {
        let mut updates = Vec::new();
        let mut params = Vec::new();

        if let Some(name) = &req.name {
            updates.push("name = ?");
            params.push(name.clone());
        }

        if let Some(description) = &req.description {
            updates.push("description = ?");
            params.push(description.clone());
        }

        if let Some(script_path) = &req.script_path {
            updates.push("script_path = ?");
            params.push(script_path.clone());
        }

        if let Some(config_path) = &req.config_path {
            updates.push("config_path = ?");
            params.push(config_path.clone());
        }

        if let Some(runtime_type) = &req.runtime_type {
            updates.push("runtime_type = ?");
            params.push(runtime_type.to_string());
        }

        if let Some(tags) = &req.tags {
            updates.push("tags = ?");
            params.push(tags.join(","));
        }

        if updates.is_empty() {
            return Self::find_by_id(pool, id).await;
        }

        updates.push("updated_at = ?");
        params.push(Utc::now().to_rfc3339());

        let sql = format!(
            "UPDATE test_cases SET {} WHERE id = ?",
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

    /// 删除测试用例
    pub async fn delete(pool: &SqlitePool, id: &str) -> anyhow::Result<()> {
        sqlx::query("DELETE FROM test_cases WHERE id = ?")
            .bind(id)
            .execute(pool)
            .await?;

        Ok(())
    }

    /// 获取测试用例的标签列表
    pub fn get_tags(&self) -> Vec<String> {
        self.tags
            .as_ref()
            .map(|tags| {
                tags.split(',')
                    .map(|tag| tag.trim().to_string())
                    .filter(|tag| !tag.is_empty())
                    .collect()
            })
            .unwrap_or_default()
    }


}