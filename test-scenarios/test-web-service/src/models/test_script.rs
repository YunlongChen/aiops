//! 测试脚本模型
//! 
//! 定义多语言测试脚本的数据结构和执行框架

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::{FromRow, SqlitePool};
use std::collections::HashMap;
use uuid::Uuid;

/// 支持的编程语言枚举
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum ScriptLanguage {
    /// Python脚本
    Python,
    /// JavaScript/Node.js脚本
    Javascript,
    /// Shell脚本 (Bash/PowerShell)
    Shell,
    /// Go语言
    Go,
    /// Rust语言
    Rust,
    /// Java语言
    Java,
    /// 自定义Docker镜像
    Docker,
}

impl std::fmt::Display for ScriptLanguage {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ScriptLanguage::Python => write!(f, "python"),
            ScriptLanguage::Javascript => write!(f, "javascript"),
            ScriptLanguage::Shell => write!(f, "shell"),
            ScriptLanguage::Go => write!(f, "go"),
            ScriptLanguage::Rust => write!(f, "rust"),
            ScriptLanguage::Java => write!(f, "java"),
            ScriptLanguage::Docker => write!(f, "docker"),
        }
    }
}

/// 测试脚本输入参数
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestInput {
    /// 参数名称
    pub name: String,
    /// 参数值
    pub value: String,
    /// 参数类型 (string, number, boolean, json)
    pub param_type: String,
    /// 参数描述
    pub description: Option<String>,
}

/// 测试预期输出
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExpectedOutput {
    /// 输出类型 (exit_code, stdout_contains, stderr_contains, json_path, regex_match)
    pub output_type: String,
    /// 预期值
    pub expected_value: String,
    /// 比较操作符 (equals, contains, greater_than, less_than, regex)
    pub operator: String,
    /// 输出描述
    pub description: Option<String>,
}

/// 多语言测试脚本模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct TestScript {
    pub id: String,
    pub test_case_id: String,
    pub name: String,
    pub description: Option<String>,
    pub language: String,
    pub script_content: String,
    pub inputs: Option<String>, // JSON格式存储TestInput数组
    pub expected_outputs: Option<String>, // JSON格式存储ExpectedOutput数组
    pub timeout_seconds: Option<i32>,
    pub retry_count: Option<i32>,
    pub environment_vars: Option<String>, // JSON格式存储环境变量
    pub dependencies: Option<String>, // JSON格式存储依赖包列表
    pub docker_image: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 创建测试脚本请求
#[derive(Debug, Deserialize)]
pub struct CreateTestScriptRequest {
    pub test_case_id: String,
    pub name: String,
    pub description: Option<String>,
    pub language: ScriptLanguage,
    pub script_content: String,
    pub inputs: Option<Vec<TestInput>>,
    pub expected_outputs: Option<Vec<ExpectedOutput>>,
    pub timeout_seconds: Option<i32>,
    pub retry_count: Option<i32>,
    pub environment_vars: Option<HashMap<String, String>>,
    pub dependencies: Option<Vec<String>>,
    pub docker_image: Option<String>,
}

/// 更新测试脚本请求
#[derive(Debug, Deserialize)]
pub struct UpdateTestScriptRequest {
    pub name: Option<String>,
    pub description: Option<String>,
    pub language: Option<ScriptLanguage>,
    pub script_content: Option<String>,
    pub inputs: Option<Vec<TestInput>>,
    pub expected_outputs: Option<Vec<ExpectedOutput>>,
    pub timeout_seconds: Option<i32>,
    pub retry_count: Option<i32>,
    pub environment_vars: Option<HashMap<String, String>>,
    pub dependencies: Option<Vec<String>>,
    pub docker_image: Option<String>,
}

/// 运行测试脚本请求
#[derive(Debug, Deserialize)]
pub struct RunTestScriptRequest {
    pub inputs: Option<Vec<TestInput>>,
    pub environment_vars: Option<HashMap<String, String>>,
    pub timeout_seconds: Option<i32>,
}

/// 脚本执行结果
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScriptExecutionResult {
    pub exit_code: i32,
    pub stdout: String,
    pub stderr: String,
    pub execution_time_ms: u64,
    pub validation_results: Vec<ValidationResult>,
}

/// 输出验证结果
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationResult {
    pub output_type: String,
    pub expected: String,
    pub actual: String,
    pub passed: bool,
    pub message: String,
}

impl TestScript {
    /// 获取脚本语言
    pub fn get_language(&self) -> anyhow::Result<ScriptLanguage> {
        match self.language.as_str() {
            "python" => Ok(ScriptLanguage::Python),
            "javascript" => Ok(ScriptLanguage::Javascript),
            "shell" => Ok(ScriptLanguage::Shell),
            "go" => Ok(ScriptLanguage::Go),
            "rust" => Ok(ScriptLanguage::Rust),
            "java" => Ok(ScriptLanguage::Java),
            "docker" => Ok(ScriptLanguage::Docker),
            _ => anyhow::bail!("不支持的脚本语言: {}", self.language),
        }
    }

    /// 获取输入参数
    pub fn get_inputs(&self) -> anyhow::Result<Vec<TestInput>> {
        match &self.inputs {
            Some(inputs_json) => {
                let inputs: Vec<TestInput> = serde_json::from_str(inputs_json)?;
                Ok(inputs)
            }
            None => Ok(vec![]),
        }
    }

    /// 获取预期输出
    pub fn get_expected_outputs(&self) -> anyhow::Result<Vec<ExpectedOutput>> {
        match &self.expected_outputs {
            Some(outputs_json) => {
                let outputs: Vec<ExpectedOutput> = serde_json::from_str(outputs_json)?;
                Ok(outputs)
            }
            None => Ok(vec![]),
        }
    }

    /// 获取环境变量
    pub fn get_environment_vars(&self) -> anyhow::Result<HashMap<String, String>> {
        match &self.environment_vars {
            Some(env_json) => {
                let env_vars: HashMap<String, String> = serde_json::from_str(env_json)?;
                Ok(env_vars)
            }
            None => Ok(HashMap::new()),
        }
    }

    /// 获取依赖包列表
    pub fn get_dependencies(&self) -> anyhow::Result<Vec<String>> {
        match &self.dependencies {
            Some(deps_json) => {
                let deps: Vec<String> = serde_json::from_str(deps_json)?;
                Ok(deps)
            }
            None => Ok(vec![]),
        }
    }

    /// 根据ID获取测试脚本
    pub async fn get_by_id(
        pool: &SqlitePool,
        id: &str,
    ) -> anyhow::Result<Option<TestScript>> {
        let script = sqlx::query_as::<_, TestScript>(
            "SELECT * FROM test_scripts WHERE id = ?"
        )
        .bind(id)
        .fetch_optional(pool)
        .await?;
        
        Ok(script)
    }

    /// 根据测试用例ID获取脚本列表
    pub async fn get_by_test_case_id(
        pool: &SqlitePool,
        test_case_id: &str,
    ) -> anyhow::Result<Vec<TestScript>> {
        let scripts = sqlx::query_as::<_, TestScript>(
            "SELECT * FROM test_scripts WHERE test_case_id = ? ORDER BY created_at ASC"
        )
        .bind(test_case_id)
        .fetch_all(pool)
        .await?;
        
        Ok(scripts)
    }

    /// 分页获取测试脚本列表
    pub async fn list(
        pool: &SqlitePool,
        test_case_id: Option<&str>,
        language: Option<&str>,
        page: Option<i32>,
        page_size: Option<i32>,
    ) -> anyhow::Result<Vec<TestScript>> {
        let page = page.unwrap_or(1).max(1);
        let page_size = page_size.unwrap_or(20).min(100).max(1);
        let offset = (page - 1) * page_size;

        let mut query = "SELECT * FROM test_scripts WHERE 1=1".to_string();
        let mut params: Vec<String> = Vec::new();

        if let Some(test_case_id) = test_case_id {
            if !test_case_id.is_empty() {
                query.push_str(" AND test_case_id = ?");
                params.push(test_case_id.to_string());
            }
        }

        if let Some(language) = language {
            if !language.is_empty() {
                query.push_str(" AND language = ?");
                params.push(language.to_string());
            }
        }

        query.push_str(" ORDER BY created_at DESC LIMIT ? OFFSET ?");
        params.push(page_size.to_string());
        params.push(offset.to_string());

        let mut sql_query = sqlx::query_as::<_, TestScript>(&query);
        for param in &params {
            sql_query = sql_query.bind(param);
        }

        let scripts = sql_query.fetch_all(pool).await?;
        Ok(scripts)
    }

    /// 创建测试脚本
    pub async fn create(
        pool: &SqlitePool,
        req: CreateTestScriptRequest,
    ) -> anyhow::Result<TestScript> {
        let id = Uuid::new_v4().to_string();
        let now = Utc::now();
        
        let inputs_json = match req.inputs {
            Some(inputs) => Some(serde_json::to_string(&inputs)?),
            None => None,
        };
        
        let outputs_json = match req.expected_outputs {
            Some(outputs) => Some(serde_json::to_string(&outputs)?),
            None => None,
        };
        
        let env_vars_json = match req.environment_vars {
            Some(env_vars) => Some(serde_json::to_string(&env_vars)?),
            None => None,
        };
        
        let deps_json = match req.dependencies {
            Some(deps) => Some(serde_json::to_string(&deps)?),
            None => None,
        };
        
        sqlx::query(
            r#"
            INSERT INTO test_scripts (
                id, test_case_id, name, description, language, script_content,
                inputs, expected_outputs, timeout_seconds, retry_count,
                environment_vars, dependencies, docker_image, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            "#
        )
        .bind(&id)
        .bind(&req.test_case_id)
        .bind(&req.name)
        .bind(&req.description)
        .bind(req.language.to_string())
        .bind(&req.script_content)
        .bind(&inputs_json)
        .bind(&outputs_json)
        .bind(req.timeout_seconds)
        .bind(req.retry_count)
        .bind(&env_vars_json)
        .bind(&deps_json)
        .bind(&req.docker_image)
        .bind(now)
        .bind(now)
        .execute(pool)
        .await?;
        
        let script = TestScript {
            id,
            test_case_id: req.test_case_id,
            name: req.name,
            description: req.description,
            language: req.language.to_string(),
            script_content: req.script_content,
            inputs: inputs_json,
            expected_outputs: outputs_json,
            timeout_seconds: req.timeout_seconds,
            retry_count: req.retry_count,
            environment_vars: env_vars_json,
            dependencies: deps_json,
            docker_image: req.docker_image,
            created_at: now,
            updated_at: now,
        };
        
        Ok(script)
    }

    /// 更新测试脚本
    pub async fn update(
        pool: &SqlitePool,
        id: &str,
        req: UpdateTestScriptRequest,
    ) -> anyhow::Result<TestScript> {
        let mut script = Self::get_by_id(pool, id)
            .await?
            .ok_or_else(|| anyhow::anyhow!("测试脚本不存在"))?;
        
        let now = Utc::now();
        
        if let Some(name) = req.name {
            script.name = name;
        }
        if let Some(description) = req.description {
            script.description = Some(description);
        }
        if let Some(language) = req.language {
            script.language = language.to_string();
        }
        if let Some(script_content) = req.script_content {
            script.script_content = script_content;
        }
        if let Some(inputs) = req.inputs {
            script.inputs = Some(serde_json::to_string(&inputs)?);
        }
        if let Some(outputs) = req.expected_outputs {
            script.expected_outputs = Some(serde_json::to_string(&outputs)?);
        }
        if let Some(timeout) = req.timeout_seconds {
            script.timeout_seconds = Some(timeout);
        }
        if let Some(retry) = req.retry_count {
            script.retry_count = Some(retry);
        }
        if let Some(env_vars) = req.environment_vars {
            script.environment_vars = Some(serde_json::to_string(&env_vars)?);
        }
        if let Some(deps) = req.dependencies {
            script.dependencies = Some(serde_json::to_string(&deps)?);
        }
        if let Some(docker_image) = req.docker_image {
            script.docker_image = Some(docker_image);
        }
        
        script.updated_at = now;
        
        sqlx::query(
            r#"
            UPDATE test_scripts SET
                name = ?, description = ?, language = ?, script_content = ?,
                inputs = ?, expected_outputs = ?, timeout_seconds = ?, retry_count = ?,
                environment_vars = ?, dependencies = ?, docker_image = ?, updated_at = ?
            WHERE id = ?
            "#
        )
        .bind(&script.name)
        .bind(&script.description)
        .bind(&script.language)
        .bind(&script.script_content)
        .bind(&script.inputs)
        .bind(&script.expected_outputs)
        .bind(script.timeout_seconds)
        .bind(script.retry_count)
        .bind(&script.environment_vars)
        .bind(&script.dependencies)
        .bind(&script.docker_image)
        .bind(script.updated_at)
        .bind(id)
        .execute(pool)
        .await?;
        
        Ok(script)
    }

    /// 删除测试脚本
    pub async fn delete(pool: &SqlitePool, id: &str) -> anyhow::Result<()> {
        sqlx::query("DELETE FROM test_scripts WHERE id = ?")
            .bind(id)
            .execute(pool)
            .await?;
        
        Ok(())
    }
}