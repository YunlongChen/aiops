//! 测试运行记录模型
//! 
//! 定义测试运行的数据结构和数据库操作

use super::{TestStatus, PaginationParams, PaginatedResponse, PaginationInfo};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::{FromRow, SqlitePool};
use uuid::Uuid;
use utoipa::{ToSchema, IntoParams};

/// 测试运行记录模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct TestRun {
    /// 测试运行ID
    pub id: String,
    /// 测试用例ID
    pub test_case_id: String,
    /// 运行状态
    pub status: String,
    /// 开始时间
    pub start_time: Option<DateTime<Utc>>,
    /// 结束时间
    pub end_time: Option<DateTime<Utc>>,
    /// 运行时长（毫秒）
    pub duration_ms: Option<i64>,
    /// 退出码
    pub exit_code: Option<i32>,
    /// 标准输出
    pub stdout: Option<String>,
    /// 标准错误
    pub stderr: Option<String>,
    /// 元数据（JSON字符串）
    pub metadata: Option<String>,
    /// 创建时间
    pub created_at: DateTime<Utc>,
}

/// 创建测试运行请求
#[derive(Debug, Deserialize, ToSchema)]
pub struct CreateTestRunRequest {
    /// 测试用例ID
    pub test_case_id: String,
    /// 元数据
    pub metadata: Option<serde_json::Value>,
}

/// 更新测试运行状态请求
#[derive(Debug, Deserialize, ToSchema)]
pub struct UpdateTestRunRequest {
    /// 运行状态
    pub status: Option<TestStatus>,
    /// 退出码
    pub exit_code: Option<i32>,
    /// 标准输出
    pub stdout: Option<String>,
    /// 标准错误
    pub stderr: Option<String>,
    /// 元数据
    pub metadata: Option<serde_json::Value>,
}

/// 测试运行查询参数
#[derive(Debug, Deserialize, ToSchema, IntoParams)]
pub struct TestRunQuery {
    #[serde(flatten)]
    /// 分页参数
    pub pagination: PaginationParams,
    /// 按测试用例ID筛选
    pub test_case_id: Option<String>,
    /// 按状态筛选
    pub status: Option<TestStatus>,
    /// 按运行时管理器ID筛选
    pub runtime_manager_id: Option<String>,
    /// 开始日期筛选
    pub start_date: Option<DateTime<Utc>>,
    /// 结束日期筛选
    pub end_date: Option<DateTime<Utc>>,
}

/// 测试运行统计信息
#[derive(Debug, Serialize, ToSchema)]
pub struct TestRunStats {
    /// 总运行次数
    pub total_runs: u64,
    /// 成功运行次数
    pub success_runs: u64,
    /// 失败运行次数
    pub failed_runs: u64,
    /// 正在运行次数
    pub running_runs: u64,
    /// 等待运行次数
    pub pending_runs: u64,
    /// 成功率
    pub success_rate: f64,
    /// 平均运行时长（毫秒）
    pub average_duration_ms: Option<f64>,
}

impl TestRun {
    /// 获取测试运行列表
    pub async fn list(
        pool: &SqlitePool,
        params: &PaginationParams,
        query: &TestRunQuery,
    ) -> anyhow::Result<(Vec<TestRun>, PaginationInfo)> {
        let mut sql = "SELECT * FROM test_runs WHERE 1=1".to_string();
        let mut count_sql = "SELECT COUNT(*) FROM test_runs WHERE 1=1".to_string();
        
        // 添加查询条件
        if let Some(ref status) = query.status {
            sql.push_str(&format!(" AND status = '{}'", status));
            count_sql.push_str(&format!(" AND status = '{}'", status));
        }
        
        if let Some(ref test_case_id) = query.test_case_id {
            sql.push_str(&format!(" AND test_case_id = '{}'", test_case_id));
            count_sql.push_str(&format!(" AND test_case_id = '{}'", test_case_id));
        }
        
        // 添加分页
        let page = params.page;
        let limit = params.limit;
        let offset = params.offset();
        
        sql.push_str(&format!(" ORDER BY created_at DESC LIMIT {} OFFSET {}", limit, offset));
        
        // 执行查询
        let test_runs = sqlx::query_as::<_, TestRun>(&sql)
            .fetch_all(pool)
            .await?;
            
        // 获取总数
        let total: i64 = sqlx::query_scalar(&count_sql)
            .fetch_one(pool)
            .await?;
            
        let pagination = PaginationInfo::new(
            page,
            limit,
            total as u64,
        );
        
        Ok((test_runs, pagination))
    }

    /// 创建新的测试运行
    pub async fn create(
        pool: &SqlitePool,
        req: CreateTestRunRequest,
    ) -> anyhow::Result<TestRun> {
        let id = Uuid::new_v4().to_string();
        let now = Utc::now();
        let metadata_str = req.metadata.map(|m| serde_json::to_string(&m).unwrap_or_default());

        sqlx::query(
            r#"
            INSERT INTO test_runs (id, test_case_id, status, metadata, created_at)
            VALUES (?, ?, ?, ?, ?)
            "#,
        )
        .bind(&id)
        .bind(&req.test_case_id)
        .bind(TestStatus::Pending.to_string())
        .bind(&metadata_str)
        .bind(&now)
        .execute(pool)
        .await?;

        Self::find_by_id(pool, &id).await
    }

    /// 根据ID查找测试运行记录
    pub async fn find_by_id(pool: &SqlitePool, id: &str) -> anyhow::Result<TestRun> {
        let test_run = sqlx::query_as::<_, TestRun>(
            "SELECT * FROM test_runs WHERE id = ?"
        )
        .bind(id)
        .fetch_one(pool)
        .await?;

        Ok(test_run)
    }

    /// 分页查询测试运行记录
    pub async fn find_all(
        pool: &SqlitePool,
        query: TestRunQuery,
    ) -> anyhow::Result<PaginatedResponse<TestRun>> {
        query.pagination.validate()?;

        let mut sql = "SELECT * FROM test_runs WHERE 1=1".to_string();
        let mut count_sql = "SELECT COUNT(*) FROM test_runs WHERE 1=1".to_string();
        let mut params = Vec::new();

        // 添加查询条件
        if let Some(test_case_id) = &query.test_case_id {
            sql.push_str(" AND test_case_id = ?");
            count_sql.push_str(" AND test_case_id = ?");
            params.push(test_case_id.clone());
        }

        if let Some(status) = &query.status {
            sql.push_str(" AND status = ?");
            count_sql.push_str(" AND status = ?");
            params.push(status.to_string());
        }

        if let Some(start_date) = &query.start_date {
            sql.push_str(" AND created_at >= ?");
            count_sql.push_str(" AND created_at >= ?");
            params.push(start_date.to_rfc3339());
        }

        if let Some(end_date) = &query.end_date {
            sql.push_str(" AND created_at <= ?");
            count_sql.push_str(" AND created_at <= ?");
            params.push(end_date.to_rfc3339());
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
        let mut data_query = sqlx::query_as::<_, TestRun>(&sql);
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

    /// 开始测试运行
    pub async fn start(pool: &SqlitePool, id: &str) -> anyhow::Result<TestRun> {
        let now = Utc::now();
        
        sqlx::query(
            "UPDATE test_runs SET status = ?, start_time = ? WHERE id = ?"
        )
        .bind(TestStatus::Running.to_string())
        .bind(&now)
        .bind(id)
        .execute(pool)
        .await?;

        Self::find_by_id(pool, id).await
    }

    /// 完成测试运行
    pub async fn finish(
        pool: &SqlitePool,
        id: &str,
        status: TestStatus,
        exit_code: Option<i32>,
        stdout: Option<String>,
        stderr: Option<String>,
    ) -> anyhow::Result<TestRun> {
        let now = Utc::now();
        
        // 获取开始时间以计算持续时间
        let current_run = Self::find_by_id(pool, id).await?;
        let duration_ms = if let Some(start_time) = current_run.start_time {
            Some((now - start_time).num_milliseconds())
        } else {
            None
        };

        sqlx::query(
            r#"
            UPDATE test_runs 
            SET status = ?, end_time = ?, duration_ms = ?, exit_code = ?, stdout = ?, stderr = ?
            WHERE id = ?
            "#
        )
        .bind(status.to_string())
        .bind(&now)
        .bind(duration_ms)
        .bind(exit_code)
        .bind(&stdout)
        .bind(&stderr)
        .bind(id)
        .execute(pool)
        .await?;

        Self::find_by_id(pool, id).await
    }

    /// 更新测试运行记录
    pub async fn update(
        pool: &SqlitePool,
        id: &str,
        req: UpdateTestRunRequest,
    ) -> anyhow::Result<TestRun> {
        let mut updates = Vec::new();
        let mut params = Vec::new();

        if let Some(status) = &req.status {
            updates.push("status = ?");
            params.push(status.to_string());
        }

        if let Some(exit_code) = &req.exit_code {
            updates.push("exit_code = ?");
            params.push(exit_code.to_string());
        }

        if let Some(stdout) = &req.stdout {
            updates.push("stdout = ?");
            params.push(stdout.clone());
        }

        if let Some(stderr) = &req.stderr {
            updates.push("stderr = ?");
            params.push(stderr.clone());
        }

        if let Some(metadata) = &req.metadata {
            updates.push("metadata = ?");
            params.push(serde_json::to_string(metadata).unwrap_or_default());
        }

        if updates.is_empty() {
            return Self::find_by_id(pool, id).await;
        }

        let sql = format!(
            "UPDATE test_runs SET {} WHERE id = ?",
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

    /// 获取测试运行统计信息
    pub async fn get_stats(pool: &SqlitePool) -> anyhow::Result<TestRunStats> {
        let total_runs = sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM test_runs")
            .fetch_one(pool)
            .await? as u64;

        let success_runs = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM test_runs WHERE status = 'success'"
        )
        .fetch_one(pool)
        .await? as u64;

        let failed_runs = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM test_runs WHERE status = 'failed'"
        )
        .fetch_one(pool)
        .await? as u64;

        let running_runs = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM test_runs WHERE status = 'running'"
        )
        .fetch_one(pool)
        .await? as u64;

        let pending_runs = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM test_runs WHERE status = 'pending'"
        )
        .fetch_one(pool)
        .await? as u64;

        let success_rate = if total_runs > 0 {
            (success_runs as f64) / (total_runs as f64) * 100.0
        } else {
            0.0
        };

        let average_duration_ms = sqlx::query_scalar::<_, Option<f64>>(
            "SELECT AVG(duration_ms) FROM test_runs WHERE duration_ms IS NOT NULL"
        )
        .fetch_one(pool)
        .await?;

        Ok(TestRunStats {
            total_runs,
            success_runs,
            failed_runs,
            running_runs,
            pending_runs,
            success_rate,
            average_duration_ms,
        })
    }

    /// 获取测试状态
    pub fn get_status(&self) -> anyhow::Result<TestStatus> {
        match self.status.as_str() {
            "pending" => Ok(TestStatus::Pending),
            "running" => Ok(TestStatus::Running),
            "success" => Ok(TestStatus::Success),
            "failed" => Ok(TestStatus::Failed),
            "cancelled" => Ok(TestStatus::Cancelled),
            "timeout" => Ok(TestStatus::Timeout),
            _ => anyhow::bail!("未知的测试状态: {}", self.status),
        }
    }

    /// 获取测试运行状态枚举
    pub fn get_test_status(&self) -> anyhow::Result<TestStatus> {
        match self.status.as_str() {
            "pending" => Ok(TestStatus::Pending),
            "running" => Ok(TestStatus::Running),
            "success" | "completed" => Ok(TestStatus::Success),
            "failed" => Ok(TestStatus::Failed),
            "cancelled" => Ok(TestStatus::Cancelled),
            "timeout" => Ok(TestStatus::Timeout),
            _ => anyhow::bail!("未知的测试状态: {}", self.status),
        }
    }

    /// 获取元数据
    pub fn get_metadata(&self) -> Option<serde_json::Value> {
        self.metadata
            .as_ref()
            .and_then(|m| serde_json::from_str(m).ok())
    }

    /// 更新测试运行结果
    pub async fn update_result(
        pool: &sqlx::Pool<sqlx::Sqlite>,
        id: &uuid::Uuid,
        status: TestStatus,
        start_time: Option<chrono::DateTime<chrono::Utc>>,
        end_time: Option<chrono::DateTime<chrono::Utc>>,
        duration_ms: Option<i64>,
        exit_code: Option<i32>,
        stdout: Option<String>,
        stderr: Option<String>,
    ) -> anyhow::Result<TestRun> {
        sqlx::query(
            r#"
            UPDATE test_runs 
            SET status = ?, start_time = ?, end_time = ?, duration_ms = ?, 
                exit_code = ?, stdout = ?, stderr = ?
            WHERE id = ?
            "#,
        )
        .bind(status.to_string())
        .bind(start_time)
        .bind(end_time)
        .bind(duration_ms)
        .bind(exit_code)
        .bind(stdout)
        .bind(stderr)
        .bind(id.to_string())
        .execute(pool)
        .await?;

        Self::find_by_id(pool, &id.to_string()).await
    }

    /// 更新测试状态
    pub async fn update_status(
        pool: &sqlx::Pool<sqlx::Sqlite>,
        id: &uuid::Uuid,
        status: TestStatus,
    ) -> anyhow::Result<TestRun> {
        sqlx::query(
            "UPDATE test_runs SET status = ? WHERE id = ?"
        )
        .bind(status.to_string())
        .bind(id.to_string())
        .execute(pool)
        .await?;

        Self::find_by_id(pool, &id.to_string()).await
    }

    /// 根据ID获取测试运行记录（支持UUID参数）
    pub async fn get_by_id(
        pool: &sqlx::Pool<sqlx::Sqlite>,
        id: &uuid::Uuid,
    ) -> anyhow::Result<Option<TestRun>> {
        let test_run = sqlx::query_as::<_, TestRun>(
            "SELECT * FROM test_runs WHERE id = ?"
        )
        .bind(id.to_string())
        .fetch_optional(pool)
        .await?;

        Ok(test_run)
    }
}