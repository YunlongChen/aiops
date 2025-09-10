//! 多语言脚本执行引擎
//! 
//! 支持多种编程语言的测试脚本执行和结果验证

use crate::models::test_script::{
    TestScript, ScriptLanguage, TestInput, ExpectedOutput, 
    ScriptExecutionResult, ValidationResult
};
use std::collections::HashMap;
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};
use std::fs;
use std::path::Path;
use tempfile::TempDir;
use tokio::time::timeout;
use regex::Regex;
use serde_json::Value;

/// 脚本执行器
pub struct ScriptExecutor {
    /// 工作目录
    work_dir: TempDir,
    /// 默认超时时间（秒）
    default_timeout: u64,
}

impl ScriptExecutor {
    /// 创建新的脚本执行器
    pub fn new() -> anyhow::Result<Self> {
        let work_dir = TempDir::new()?;
        Ok(Self {
            work_dir,
            default_timeout: 300, // 5分钟默认超时
        })
    }

    /// 执行测试脚本
    pub async fn execute_script(
        &self,
        script: &TestScript,
    ) -> anyhow::Result<ScriptExecutionResult> {
        let language = script.get_language()?;
        let inputs = script.get_inputs()?;
        let expected_outputs = script.get_expected_outputs()?;
        let env_vars = script.get_environment_vars()?;
        let timeout_duration = Duration::from_secs(
            script.timeout_seconds.unwrap_or(self.default_timeout as i32) as u64
        );

        // 准备执行环境
        let script_file = self.prepare_script_file(&script, &language)?;
        let mut env_vars_with_inputs = env_vars.clone();
        
        // 将输入参数作为环境变量传递
        for input in &inputs {
            env_vars_with_inputs.insert(format!("TEST_INPUT_{}", input.name.to_uppercase()), input.value.clone());
        }

        // 执行脚本
        let start_time = Instant::now();
        let execution_result = timeout(
            timeout_duration,
            self.run_script(&script_file, &language, &env_vars_with_inputs, script)
        ).await;

        let execution_time = start_time.elapsed();

        let (exit_code, stdout, stderr) = match execution_result {
            Ok(Ok((code, out, err))) => (code, out, err),
            Ok(Err(e)) => (1, String::new(), format!("执行错误: {}", e)),
            Err(_) => (124, String::new(), "脚本执行超时".to_string()),
        };

        // 验证输出
        let validation_results = self.validate_outputs(
            &expected_outputs,
            exit_code,
            &stdout,
            &stderr
        )?;

        Ok(ScriptExecutionResult {
            exit_code,
            stdout,
            stderr,
            execution_time_ms: execution_time.as_millis() as u64,
            validation_results,
        })
    }

    /// 准备脚本文件
    fn prepare_script_file(
        &self,
        script: &TestScript,
        language: &ScriptLanguage,
    ) -> anyhow::Result<std::path::PathBuf> {
        let file_extension = match language {
            ScriptLanguage::Python => "py",
            ScriptLanguage::Javascript => "js",
            ScriptLanguage::Shell => if cfg!(windows) { "ps1" } else { "sh" },
            ScriptLanguage::Go => "go",
            ScriptLanguage::Rust => "rs",
            ScriptLanguage::Java => "java",
            ScriptLanguage::Docker => "dockerfile",
        };

        let script_path = self.work_dir.path().join(format!("test_script.{}", file_extension));
        
        // 根据语言添加必要的导入和设置
        let enhanced_script = self.enhance_script_content(&script.script_content, language)?;
        
        fs::write(&script_path, enhanced_script)?;
        
        // 为shell脚本设置执行权限
        #[cfg(unix)]
        if matches!(language, ScriptLanguage::Shell) {
            use std::os::unix::fs::PermissionsExt;
            let mut perms = fs::metadata(&script_path)?.permissions();
            perms.set_mode(0o755);
            fs::set_permissions(&script_path, perms)?;
        }

        Ok(script_path)
    }

    /// 增强脚本内容，添加必要的导入和工具函数
    fn enhance_script_content(
        &self,
        content: &str,
        language: &ScriptLanguage,
    ) -> anyhow::Result<String> {
        let enhanced = match language {
            ScriptLanguage::Python => {
                format!(
                    r#"#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import subprocess
from datetime import datetime

# 获取测试输入参数的辅助函数
def get_test_input(name, default=None):
    return os.environ.get(f'TEST_INPUT_{{name.upper()}}', default)

# 输出测试结果的辅助函数
def output_test_result(key, value):
    print(f'TEST_OUTPUT_{{key.upper()}}: {{value}}')

# 用户脚本内容
{}
"#,
                    content
                )
            }
            ScriptLanguage::Javascript => {
                format!(
                    r#"#!/usr/bin/env node
// 获取测试输入参数的辅助函数
function getTestInput(name, defaultValue = null) {{
    return process.env[`TEST_INPUT_${{name.toUpperCase()}}`] || defaultValue;
}}

// 输出测试结果的辅助函数
function outputTestResult(key, value) {{
    console.log(`TEST_OUTPUT_${{key.toUpperCase()}}: ${{value}}`);
}}

// 用户脚本内容
{}
"#,
                    content
                )
            }
            ScriptLanguage::Shell => {
                if cfg!(windows) {
                    format!(
                        r#"# PowerShell脚本
# 获取测试输入参数的辅助函数
function Get-TestInput {{
    param([string]$Name, [string]$Default = $null)
    $envVar = "TEST_INPUT_" + $Name.ToUpper()
    $value = [Environment]::GetEnvironmentVariable($envVar)
    if ($value) {{ return $value }} else {{ return $Default }}
}}

# 输出测试结果的辅助函数
function Output-TestResult {{
    param([string]$Key, [string]$Value)
    Write-Output "TEST_OUTPUT_$($Key.ToUpper()): $Value"
}}

# 用户脚本内容
{}
"#,
                        content
                    )
                } else {
                    format!(
                        r#"#!/bin/bash
set -e

# 获取测试输入参数的辅助函数
get_test_input() {{
    local name=$(echo "$1" | tr '[:lower:]' '[:upper:]')
    local default="$2"
    local var_name="TEST_INPUT_$name"
    echo "${{!var_name:-$default}}"
}}

# 输出测试结果的辅助函数
output_test_result() {{
    local key=$(echo "$1" | tr '[:lower:]' '[:upper:]')
    local value="$2"
    echo "TEST_OUTPUT_$key: $value"
}}

# 用户脚本内容
{}
"#,
                        content
                    )
                }
            }
            ScriptLanguage::Go => {
                format!(
                    r#"package main

import (
    "fmt"
    "os"
    "strings"
    "time"
)

// 获取测试输入参数的辅助函数
func getTestInput(name, defaultValue string) string {{
    envVar := "TEST_INPUT_" + strings.ToUpper(name)
    if value := os.Getenv(envVar); value != "" {{
        return value
    }}
    return defaultValue
}}

// 输出测试结果的辅助函数
func outputTestResult(key, value string) {{
    fmt.Printf("TEST_OUTPUT_%s: %s\n", strings.ToUpper(key), value)
}}

// 用户脚本内容
func main() {{
{}
}}
"#,
                    content
                )
            }
            ScriptLanguage::Rust => {
                format!(
                    r#"use std::env;
use std::time::{{Duration, Instant}};

// 获取测试输入参数的辅助函数
fn get_test_input(name: &str, default: Option<&str>) -> String {{
    let env_var = format!("TEST_INPUT_{{}}", name.to_uppercase());
    env::var(&env_var).unwrap_or_else(|_| default.unwrap_or("").to_string())
}}

// 输出测试结果的辅助函数
fn output_test_result(key: &str, value: &str) {{
    println!("TEST_OUTPUT_{{}}: {{}}", key.to_uppercase(), value);
}}

// 用户脚本内容
fn main() {{
{}
}}
"#,
                    content
                )
            }
            ScriptLanguage::Java => {
                format!(
                    r#"import java.util.*;
import java.time.*;

public class TestScript {{
    // 获取测试输入参数的辅助函数
    public static String getTestInput(String name, String defaultValue) {{
        String envVar = "TEST_INPUT_" + name.toUpperCase();
        return System.getenv().getOrDefault(envVar, defaultValue);
    }}
    
    // 输出测试结果的辅助函数
    public static void outputTestResult(String key, String value) {{
        System.out.println("TEST_OUTPUT_" + key.toUpperCase() + ": " + value);
    }}
    
    // 用户脚本内容
    public static void main(String[] args) {{
{}
    }}
}}
"#,
                    content
                )
            }
            ScriptLanguage::Docker => content.to_string(),
        };

        Ok(enhanced)
    }

    /// 运行脚本
    async fn run_script(
        &self,
        script_path: &Path,
        language: &ScriptLanguage,
        env_vars: &HashMap<String, String>,
        script: &TestScript,
    ) -> anyhow::Result<(i32, String, String)> {
        let mut cmd = match language {
            ScriptLanguage::Python => {
                let mut c = Command::new("python3");
                c.arg(script_path);
                c
            }
            ScriptLanguage::Javascript => {
                let mut c = Command::new("node");
                c.arg(script_path);
                c
            }
            ScriptLanguage::Shell => {
                if cfg!(windows) {
                    let mut c = Command::new("powershell");
                    c.args(["-ExecutionPolicy", "Bypass", "-File"]);
                    c.arg(script_path);
                    c
                } else {
                    let mut c = Command::new("bash");
                    c.arg(script_path);
                    c
                }
            }
            ScriptLanguage::Go => {
                let mut c = Command::new("go");
                c.args(["run"]);
                c.arg(script_path);
                c
            }
            ScriptLanguage::Rust => {
                // 先编译再运行
                let exe_path = script_path.with_extension("exe");
                let compile_result = Command::new("rustc")
                    .arg(script_path)
                    .arg("-o")
                    .arg(&exe_path)
                    .output()?;
                
                if !compile_result.status.success() {
                    anyhow::bail!("Rust编译失败: {}", String::from_utf8_lossy(&compile_result.stderr));
                }
                
                let mut c = Command::new(&exe_path);
                c
            }
            ScriptLanguage::Java => {
                // 先编译再运行
                let compile_result = Command::new("javac")
                    .arg(script_path)
                    .current_dir(script_path.parent().unwrap())
                    .output()?;
                
                if !compile_result.status.success() {
                    anyhow::bail!("Java编译失败: {}", String::from_utf8_lossy(&compile_result.stderr));
                }
                
                let mut c = Command::new("java");
                c.arg("TestScript");
                c.current_dir(script_path.parent().unwrap());
                c
            }
            ScriptLanguage::Docker => {
                if let Some(docker_image) = &script.docker_image {
                    let mut c = Command::new("docker");
                    c.args(["run", "--rm", "-i"]);
                    
                    // 添加环境变量
                    for (key, value) in env_vars {
                        c.args(["-e", &format!("{}={}", key, value)]);
                    }
                    
                    c.arg(docker_image);
                    c.arg("sh");
                    c.arg("-c");
                    c.arg(&script.script_content);
                    c
                } else {
                    anyhow::bail!("Docker脚本需要指定docker_image");
                }
            }
        };

        // 设置环境变量
        for (key, value) in env_vars {
            cmd.env(key, value);
        }

        // 设置工作目录
        cmd.current_dir(self.work_dir.path());
        cmd.stdout(Stdio::piped());
        cmd.stderr(Stdio::piped());

        let output = cmd.output()?;
        let exit_code = output.status.code().unwrap_or(-1);
        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();

        Ok((exit_code, stdout, stderr))
    }

    /// 验证输出结果
    fn validate_outputs(
        &self,
        expected_outputs: &[ExpectedOutput],
        exit_code: i32,
        stdout: &str,
        stderr: &str,
    ) -> anyhow::Result<Vec<ValidationResult>> {
        let mut results = Vec::new();

        for expected in expected_outputs {
            let validation_result = match expected.output_type.as_str() {
                "exit_code" => self.validate_exit_code(expected, exit_code)?,
                "stdout_contains" => self.validate_stdout_contains(expected, stdout)?,
                "stderr_contains" => self.validate_stderr_contains(expected, stderr)?,
                "stdout_regex" => self.validate_stdout_regex(expected, stdout)?,
                "stderr_regex" => self.validate_stderr_regex(expected, stderr)?,
                "json_path" => self.validate_json_path(expected, stdout)?,
                _ => ValidationResult {
                    output_type: expected.output_type.clone(),
                    expected: expected.expected_value.clone(),
                    actual: "未知验证类型".to_string(),
                    passed: false,
                    message: format!("不支持的验证类型: {}", expected.output_type),
                },
            };
            
            results.push(validation_result);
        }

        Ok(results)
    }

    /// 验证退出码
    fn validate_exit_code(
        &self,
        expected: &ExpectedOutput,
        actual_exit_code: i32,
    ) -> anyhow::Result<ValidationResult> {
        let expected_code: i32 = expected.expected_value.parse()?;
        let passed = match expected.operator.as_str() {
            "equals" | "=" | "==" => actual_exit_code == expected_code,
            "not_equals" | "!=" => actual_exit_code != expected_code,
            "greater_than" | ">" => actual_exit_code > expected_code,
            "less_than" | "<" => actual_exit_code < expected_code,
            "greater_equal" | ">=" => actual_exit_code >= expected_code,
            "less_equal" | "<=" => actual_exit_code <= expected_code,
            _ => false,
        };

        Ok(ValidationResult {
            output_type: expected.output_type.clone(),
            expected: expected.expected_value.clone(),
            actual: actual_exit_code.to_string(),
            passed,
            message: if passed {
                "退出码验证通过".to_string()
            } else {
                format!("退出码验证失败: 期望 {} {} {}, 实际 {}", 
                    expected_code, expected.operator, expected.expected_value, actual_exit_code)
            },
        })
    }

    /// 验证标准输出包含内容
    fn validate_stdout_contains(
        &self,
        expected: &ExpectedOutput,
        stdout: &str,
    ) -> anyhow::Result<ValidationResult> {
        let passed = match expected.operator.as_str() {
            "contains" => stdout.contains(&expected.expected_value),
            "not_contains" => !stdout.contains(&expected.expected_value),
            "equals" => stdout.trim() == expected.expected_value,
            "not_equals" => stdout.trim() != expected.expected_value,
            _ => false,
        };

        Ok(ValidationResult {
            output_type: expected.output_type.clone(),
            expected: expected.expected_value.clone(),
            actual: stdout.to_string(),
            passed,
            message: if passed {
                "标准输出验证通过".to_string()
            } else {
                format!("标准输出验证失败: {} {} '{}'", 
                    expected.operator, expected.expected_value, stdout.trim())
            },
        })
    }

    /// 验证标准错误包含内容
    fn validate_stderr_contains(
        &self,
        expected: &ExpectedOutput,
        stderr: &str,
    ) -> anyhow::Result<ValidationResult> {
        let passed = match expected.operator.as_str() {
            "contains" => stderr.contains(&expected.expected_value),
            "not_contains" => !stderr.contains(&expected.expected_value),
            "equals" => stderr.trim() == expected.expected_value,
            "not_equals" => stderr.trim() != expected.expected_value,
            _ => false,
        };

        Ok(ValidationResult {
            output_type: expected.output_type.clone(),
            expected: expected.expected_value.clone(),
            actual: stderr.to_string(),
            passed,
            message: if passed {
                "标准错误验证通过".to_string()
            } else {
                format!("标准错误验证失败: {} {} '{}'", 
                    expected.operator, expected.expected_value, stderr.trim())
            },
        })
    }

    /// 验证标准输出正则匹配
    fn validate_stdout_regex(
        &self,
        expected: &ExpectedOutput,
        stdout: &str,
    ) -> anyhow::Result<ValidationResult> {
        let regex = Regex::new(&expected.expected_value)?;
        let passed = match expected.operator.as_str() {
            "matches" | "regex" => regex.is_match(stdout),
            "not_matches" | "not_regex" => !regex.is_match(stdout),
            _ => false,
        };

        Ok(ValidationResult {
            output_type: expected.output_type.clone(),
            expected: expected.expected_value.clone(),
            actual: stdout.to_string(),
            passed,
            message: if passed {
                "正则表达式验证通过".to_string()
            } else {
                format!("正则表达式验证失败: 模式 '{}' {} 匹配 '{}'", 
                    expected.expected_value, 
                    if expected.operator == "matches" { "未能" } else { "意外" },
                    stdout.trim())
            },
        })
    }

    /// 验证标准错误正则匹配
    fn validate_stderr_regex(
        &self,
        expected: &ExpectedOutput,
        stderr: &str,
    ) -> anyhow::Result<ValidationResult> {
        let regex = Regex::new(&expected.expected_value)?;
        let passed = match expected.operator.as_str() {
            "matches" | "regex" => regex.is_match(stderr),
            "not_matches" | "not_regex" => !regex.is_match(stderr),
            _ => false,
        };

        Ok(ValidationResult {
            output_type: expected.output_type.clone(),
            expected: expected.expected_value.clone(),
            actual: stderr.to_string(),
            passed,
            message: if passed {
                "正则表达式验证通过".to_string()
            } else {
                format!("正则表达式验证失败: 模式 '{}' {} 匹配 '{}'", 
                    expected.expected_value, 
                    if expected.operator == "matches" { "未能" } else { "意外" },
                    stderr.trim())
            },
        })
    }

    /// 验证JSON路径
    fn validate_json_path(
        &self,
        expected: &ExpectedOutput,
        stdout: &str,
    ) -> anyhow::Result<ValidationResult> {
        // 尝试解析JSON
        let json_value: Value = match serde_json::from_str(stdout) {
            Ok(v) => v,
            Err(e) => {
                return Ok(ValidationResult {
                    output_type: expected.output_type.clone(),
                    expected: expected.expected_value.clone(),
                    actual: stdout.to_string(),
                    passed: false,
                    message: format!("JSON解析失败: {}", e),
                });
            }
        };

        // 简单的JSON路径解析（支持点号分隔的路径）
        let path_parts: Vec<&str> = expected.expected_value.split('.').collect();
        let mut current_value = &json_value;
        
        for part in &path_parts {
            if part.is_empty() {
                continue;
            }
            
            current_value = match current_value {
                Value::Object(obj) => {
                    match obj.get(*part) {
                        Some(v) => v,
                        None => {
                            return Ok(ValidationResult {
                                output_type: expected.output_type.clone(),
                                expected: expected.expected_value.clone(),
                                actual: "路径不存在".to_string(),
                                passed: false,
                                message: format!("JSON路径 '{}' 不存在", expected.expected_value),
                            });
                        }
                    }
                }
                Value::Array(arr) => {
                    if let Ok(index) = part.parse::<usize>() {
                        match arr.get(index) {
                            Some(v) => v,
                            None => {
                                return Ok(ValidationResult {
                                    output_type: expected.output_type.clone(),
                                    expected: expected.expected_value.clone(),
                                    actual: "数组索引越界".to_string(),
                                    passed: false,
                                    message: format!("数组索引 {} 越界", index),
                                });
                            }
                        }
                    } else {
                        return Ok(ValidationResult {
                            output_type: expected.output_type.clone(),
                            expected: expected.expected_value.clone(),
                            actual: "无效数组索引".to_string(),
                            passed: false,
                            message: format!("无效的数组索引: {}", part),
                        });
                    }
                }
                _ => {
                    return Ok(ValidationResult {
                        output_type: expected.output_type.clone(),
                        expected: expected.expected_value.clone(),
                        actual: "路径类型错误".to_string(),
                        passed: false,
                        message: format!("JSON路径 '{}' 类型错误", expected.expected_value),
                    });
                }
            };
        }

        let actual_value = current_value.to_string();
        let passed = true; // JSON路径存在即为通过

        Ok(ValidationResult {
            output_type: expected.output_type.clone(),
            expected: expected.expected_value.clone(),
            actual: actual_value,
            passed,
            message: if passed {
                "JSON路径验证通过".to_string()
            } else {
                "JSON路径验证失败".to_string()
            },
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::test_script::*;

    #[tokio::test]
    async fn test_python_script_execution() {
        let executor = ScriptExecutor::new().unwrap();
        
        let script = TestScript {
            id: "test-1".to_string(),
            test_case_id: "case-1".to_string(),
            name: "Python测试".to_string(),
            description: None,
            language: "python".to_string(),
            script_content: "print('Hello, World!')".to_string(),
            inputs: None,
            expected_outputs: Some(serde_json::to_string(&vec![
                ExpectedOutput {
                    output_type: "exit_code".to_string(),
                    expected_value: "0".to_string(),
                    operator: "equals".to_string(),
                    description: None,
                },
                ExpectedOutput {
                    output_type: "stdout_contains".to_string(),
                    expected_value: "Hello, World!".to_string(),
                    operator: "contains".to_string(),
                    description: None,
                }
            ]).unwrap()),
            timeout_seconds: Some(30),
            retry_count: Some(1),
            environment_vars: None,
            dependencies: None,
            docker_image: None,
            created_at: chrono::Utc::now(),
            updated_at: chrono::Utc::now(),
        };

        let result = executor.execute_script(&script).await.unwrap();
        
        assert_eq!(result.exit_code, 0);
        assert!(result.stdout.contains("Hello, World!"));
        assert_eq!(result.validation_results.len(), 2);
        assert!(result.validation_results.iter().all(|r| r.passed));
    }
}