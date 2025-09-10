//! 数据库模块
//! 
//! 管理SQLite数据库连接、表结构和基础操作

use sqlx::{sqlite::SqlitePool, Row, Sqlite};
use std::path::Path;
use tracing::{info, warn};

/// 数据库连接管理器
#[derive(Debug, Clone)]
pub struct Database {
    pool: SqlitePool,
}

impl Database {
    /// 创建新的数据库连接
    pub async fn new(database_url: &str) -> anyhow::Result<Self> {
        // 确保数据库文件目录存在
        if database_url.starts_with("sqlite:") {
            let db_path = database_url.strip_prefix("sqlite:").unwrap_or(database_url);
            if let Some(parent) = Path::new(db_path).parent() {
                tokio::fs::create_dir_all(parent).await?;
            }
        }

        // 创建连接池
        let pool = SqlitePool::connect(database_url).await?;
        
        let db = Self { pool };
        
        // 初始化数据库表
        db.init_tables().await?;
        
        Ok(db)
    }

    /// 获取数据库连接池
    pub fn pool(&self) -> &SqlitePool {
        &self.pool
    }

    /// 初始化数据库表结构
    async fn init_tables(&self) -> anyhow::Result<()> {
        info!("初始化数据库表结构...");

        // 测试用例表
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS test_cases (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                script_path TEXT NOT NULL,
                config_path TEXT,
                runtime_type TEXT NOT NULL DEFAULT 'local',
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        // 测试运行记录表
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS test_runs (
                id TEXT PRIMARY KEY,
                test_case_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                start_time DATETIME,
                end_time DATETIME,
                duration_ms INTEGER,
                exit_code INTEGER,
                stdout TEXT,
                stderr TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_case_id) REFERENCES test_cases (id)
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        // 运行时管理器表
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS runtime_managers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                runtime_type TEXT NOT NULL,
                config TEXT,
                status TEXT NOT NULL DEFAULT 'inactive',
                last_heartbeat TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            "#,
        )
        .execute(&self.pool)
        .await?;

        // 测试结果表
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS test_results (
                id TEXT PRIMARY KEY,
                test_run_id TEXT NOT NULL,
                result_type TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_run_id) REFERENCES test_runs (id)
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        info!("数据库表结构初始化完成");
        Ok(())
    }

    /// 检查数据库连接状态
    pub async fn health_check(&self) -> anyhow::Result<bool> {
        let result = sqlx::query("SELECT 1 as test")
            .fetch_one(&self.pool)
            .await?;
        
        let test_value: i32 = result.get("test");
        Ok(test_value == 1)
    }

    /// 获取数据库统计信息
    pub async fn get_stats(&self) -> anyhow::Result<DatabaseStats> {
        let test_cases_count = sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM test_cases")
            .fetch_one(&self.pool)
            .await? as u64;

        let test_runs_count = sqlx::query_scalar::<_, i64>("SELECT COUNT(*) FROM test_runs")
            .fetch_one(&self.pool)
            .await? as u64;

        let active_managers_count = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM runtime_managers WHERE status = 'active'"
        )
        .fetch_one(&self.pool)
        .await? as u64;

        Ok(DatabaseStats {
            test_cases_count,
            test_runs_count,
            active_managers_count,
        })
    }
}

/// 数据库统计信息
#[derive(Debug, serde::Serialize)]
pub struct DatabaseStats {
    pub test_cases_count: u64,
    pub test_runs_count: u64,
    pub active_managers_count: u64,
}