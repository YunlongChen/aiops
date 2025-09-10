#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多项目负载测试器

这个脚本扩展了AIOps测试框架，支持多种编程语言项目的负载测试，
包括构建错误、运行时错误、性能测试等场景。

支持的项目类型：
- Java项目 (Maven/Gradle)
- Rust项目 (Cargo)
- Node.js项目 (npm/yarn)
- Python项目 (pip)
- .NET项目 (dotnet)
- Go项目 (go mod)

作者: AIOps测试框架
创建时间: 2025-01-10
"""

import os
import sys
import json
import time
import random
import argparse
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class ProjectLoadTester:
    """多项目负载测试器类"""
    
    def __init__(self):
        """初始化测试器"""
        self.test_results = {}
        self.active_processes = []
        self.metrics = {
            'build_success': 0,
            'build_failure': 0,
            'runtime_success': 0,
            'runtime_failure': 0,
            'performance_tests': 0
        }
        
    def create_mock_java_project(self, project_name: str, introduce_error: bool = False) -> str:
        """创建模拟Java项目"""
        project_dir = Path(f'mock_projects/java/{project_name}')
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建pom.xml
        pom_content = f'''
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.aiops.test</groupId>
    <artifactId>{project_name}</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
            </plugin>
        </plugins>
    </build>
</project>
'''
        
        with open(project_dir / 'pom.xml', 'w', encoding='utf-8') as f:
            f.write(pom_content)
        
        # 创建Java源码
        src_dir = project_dir / 'src/main/java/com/aiops/test'
        src_dir.mkdir(parents=True, exist_ok=True)
        
        # 根据是否引入错误创建不同的代码
        if introduce_error:
            java_content = f'''
package com.aiops.test;

public class {project_name.capitalize()}App {{
    public static void main(String[] args) {{
        System.out.println("Starting {project_name} application...");
        
        // 故意引入编译错误
        UndefinedClass obj = new UndefinedClass();
        obj.nonExistentMethod();
        
        System.out.println("Application completed.");
    }}
    
    public void performHeavyTask() {{
        // 模拟CPU密集型任务
        for (int i = 0; i < 1000000; i++) {{
            Math.sqrt(i * Math.random());
        }}
    }}
}}
'''
        else:
            java_content = f'''
package com.aiops.test;

import java.util.concurrent.TimeUnit;

public class {project_name.capitalize()}App {{
    public static void main(String[] args) {{
        System.out.println("Starting {project_name} application...");
        
        {project_name.capitalize()}App app = new {project_name.capitalize()}App();
        
        // 模拟不同类型的负载
        app.performCpuTask();
        app.performMemoryTask();
        app.performIoTask();
        
        System.out.println("Application completed successfully.");
    }}
    
    public void performCpuTask() {{
        System.out.println("Performing CPU intensive task...");
        for (int i = 0; i < 500000; i++) {{
            Math.sqrt(i * Math.random());
        }}
    }}
    
    public void performMemoryTask() {{
        System.out.println("Performing memory intensive task...");
        java.util.List<String> data = new java.util.ArrayList<>();
        for (int i = 0; i < 100000; i++) {{
            data.add("Data item " + i);
        }}
        data.clear();
    }}
    
    public void performIoTask() {{
        System.out.println("Performing I/O task...");
        try {{
            TimeUnit.MILLISECONDS.sleep(100);
        }} catch (InterruptedException e) {{
            Thread.currentThread().interrupt();
        }}
    }}
}}
'''
        
        with open(src_dir / f'{project_name.capitalize()}App.java', 'w', encoding='utf-8') as f:
            f.write(java_content)
        
        return str(project_dir)
    
    def create_mock_rust_project(self, project_name: str, introduce_error: bool = False) -> str:
        """创建模拟Rust项目"""
        project_dir = Path(f'mock_projects/rust/{project_name}')
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建Cargo.toml
        cargo_content = f'''
[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
rand = "0.8"
tokio = {{ version = "1.0", features = ["full"] }}
'''
        
        with open(project_dir / 'Cargo.toml', 'w', encoding='utf-8') as f:
            f.write(cargo_content)
        
        # 创建src目录
        src_dir = project_dir / 'src'
        src_dir.mkdir(exist_ok=True)
        
        # 根据是否引入错误创建不同的代码
        if introduce_error:
            rust_content = f'''
use std::thread;
use std::time::Duration;

fn main() {{
    println!("Starting {project_name} application...");
    
    // 故意引入编译错误
    let undefined_var = some_undefined_function();
    println!("{{:?}}", undefined_var);
    
    println!("Application completed.");
}}

fn cpu_intensive_task() {{
    for i in 0..1000000 {{
        let _ = (i as f64).sqrt();
    }}
}}
'''
        else:
            rust_content = f'''
use rand::Rng;
use std::thread;
use std::time::Duration;
use tokio::time::sleep;

#[tokio::main]
async fn main() {{
    println!("Starting {project_name} application...");
    
    // 并发执行不同类型的任务
    let cpu_task = tokio::spawn(cpu_intensive_task());
    let memory_task = tokio::spawn(memory_intensive_task());
    let io_task = tokio::spawn(io_intensive_task());
    
    // 等待所有任务完成
    let _ = tokio::join!(cpu_task, memory_task, io_task);
    
    println!("Application completed successfully.");
}}

async fn cpu_intensive_task() {{
    println!("Performing CPU intensive task...");
    for i in 0..500000 {{
        let _ = (i as f64 * rand::thread_rng().gen::<f64>()).sqrt();
    }}
}}

async fn memory_intensive_task() {{
    println!("Performing memory intensive task...");
    let mut data: Vec<String> = Vec::new();
    for i in 0..100000 {{
        data.push(format!("Data item {{}}", i));
    }}
    data.clear();
}}

async fn io_intensive_task() {{
    println!("Performing I/O task...");
    sleep(Duration::from_millis(100)).await;
}}
'''
        
        with open(src_dir / 'main.rs', 'w', encoding='utf-8') as f:
            f.write(rust_content)
        
        return str(project_dir)
    
    def create_mock_nodejs_project(self, project_name: str, introduce_error: bool = False) -> str:
        """创建模拟Node.js项目"""
        project_dir = Path(f'mock_projects/nodejs/{project_name}')
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建package.json
        package_content = {
            "name": project_name,
            "version": "1.0.0",
            "description": f"Mock {project_name} project for load testing",
            "main": "index.js",
            "scripts": {
                "start": "node index.js",
                "test": "echo \"Error: no test specified\" && exit 1"
            },
            "dependencies": {
                "express": "^4.18.0",
                "lodash": "^4.17.21"
            }
        }
        
        with open(project_dir / 'package.json', 'w', encoding='utf-8') as f:
            json.dump(package_content, f, indent=2)
        
        # 根据是否引入错误创建不同的代码
        if introduce_error:
            js_content = f'''
console.log('Starting {project_name} application...');

// 故意引入运行时错误
const undefinedModule = require('non-existent-module');
undefinedModule.someFunction();

console.log('Application completed.');
'''
        else:
            js_content = f'''
const express = require('express');
const _ = require('lodash');

console.log('Starting {project_name} application...');

const app = express();
const port = 3000 + Math.floor(Math.random() * 1000);

// CPU密集型任务
function cpuIntensiveTask() {{
    console.log('Performing CPU intensive task...');
    for (let i = 0; i < 500000; i++) {{
        Math.sqrt(i * Math.random());
    }}
}}

// 内存密集型任务
function memoryIntensiveTask() {{
    console.log('Performing memory intensive task...');
    const data = [];
    for (let i = 0; i < 100000; i++) {{
        data.push(`Data item ${{i}}`);
    }}
    data.length = 0;
}}

// I/O密集型任务
function ioIntensiveTask() {{
    console.log('Performing I/O task...');
    return new Promise(resolve => {{
        setTimeout(resolve, 100);
    }});
}}

async function runTasks() {{
    cpuIntensiveTask();
    memoryIntensiveTask();
    await ioIntensiveTask();
    
    console.log('All tasks completed successfully.');
    process.exit(0);
}}

// 启动任务
runTasks();
'''
        
        with open(project_dir / 'index.js', 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        return str(project_dir)
    
    def run_build_test(self, project_type: str, project_path: str, project_name: str) -> Tuple[bool, str, float]:
        """运行构建测试"""
        start_time = time.time()
        
        try:
            if project_type == 'java':
                # Maven构建
                result = subprocess.run(
                    ['mvn', 'clean', 'compile'],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            elif project_type == 'rust':
                # Cargo构建
                result = subprocess.run(
                    ['cargo', 'build'],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            elif project_type == 'nodejs':
                # npm安装依赖
                result = subprocess.run(
                    ['npm', 'install'],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            else:
                return False, f"Unsupported project type: {project_type}", 0
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            if success:
                self.metrics['build_success'] += 1
            else:
                self.metrics['build_failure'] += 1
            
            return success, result.stderr if not success else "Build successful", duration
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.metrics['build_failure'] += 1
            return False, "Build timeout", duration
        except Exception as e:
            duration = time.time() - start_time
            self.metrics['build_failure'] += 1
            return False, str(e), duration
    
    def run_runtime_test(self, project_type: str, project_path: str, project_name: str) -> Tuple[bool, str, float]:
        """运行运行时测试"""
        start_time = time.time()
        
        try:
            if project_type == 'java':
                # 运行Java应用
                result = subprocess.run(
                    ['mvn', 'exec:java', f'-Dexec.mainClass=com.aiops.test.{project_name.capitalize()}App'],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            elif project_type == 'rust':
                # 运行Rust应用
                result = subprocess.run(
                    ['cargo', 'run'],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            elif project_type == 'nodejs':
                # 运行Node.js应用
                result = subprocess.run(
                    ['node', 'index.js'],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            else:
                return False, f"Unsupported project type: {project_type}", 0
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            if success:
                self.metrics['runtime_success'] += 1
            else:
                self.metrics['runtime_failure'] += 1
            
            return success, result.stderr if not success else "Runtime successful", duration
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.metrics['runtime_failure'] += 1
            return False, "Runtime timeout", duration
        except Exception as e:
            duration = time.time() - start_time
            self.metrics['runtime_failure'] += 1
            return False, str(e), duration
    
    def run_concurrent_load_test(self, project_configs: List[Dict], duration: int = 300):
        """运行并发负载测试"""
        print(f"🚀 开始多项目并发负载测试 (持续时间: {duration}秒)")
        print(f"测试项目数量: {len(project_configs)}")
        
        # 创建所有项目
        projects = []
        for config in project_configs:
            project_type = config['type']
            project_name = config['name']
            introduce_error = config.get('introduce_error', False)
            
            print(f"📁 创建 {project_type} 项目: {project_name}")
            
            if project_type == 'java':
                project_path = self.create_mock_java_project(project_name, introduce_error)
            elif project_type == 'rust':
                project_path = self.create_mock_rust_project(project_name, introduce_error)
            elif project_type == 'nodejs':
                project_path = self.create_mock_nodejs_project(project_name, introduce_error)
            else:
                print(f"❌ 不支持的项目类型: {project_type}")
                continue
            
            projects.append({
                'type': project_type,
                'name': project_name,
                'path': project_path,
                'introduce_error': introduce_error
            })
        
        # 开始负载测试
        start_time = time.time()
        end_time = start_time + duration
        
        test_cycle = 0
        while time.time() < end_time:
            test_cycle += 1
            print(f"\n🔄 测试周期 {test_cycle}")
            
            # 并发测试所有项目
            threads = []
            for project in projects:
                thread = threading.Thread(
                    target=self._test_project_cycle,
                    args=(project, test_cycle)
                )
                threads.append(thread)
                thread.start()
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            
            # 随机等待间隔
            time.sleep(random.uniform(5, 15))
        
        total_duration = time.time() - start_time
        print(f"\n✅ 负载测试完成，总耗时: {total_duration:.2f}秒")
        
        # 生成测试报告
        self._generate_load_test_report(total_duration, test_cycle)
    
    def _test_project_cycle(self, project: Dict, cycle: int):
        """单个项目的测试周期"""
        project_type = project['type']
        project_name = project['name']
        project_path = project['path']
        
        print(f"  🔨 [{project_type}] {project_name} - 构建测试")
        build_success, build_msg, build_duration = self.run_build_test(
            project_type, project_path, project_name
        )
        
        if build_success:
            print(f"  🏃 [{project_type}] {project_name} - 运行时测试")
            runtime_success, runtime_msg, runtime_duration = self.run_runtime_test(
                project_type, project_path, project_name
            )
        else:
            runtime_success = False
            runtime_msg = "Skipped due to build failure"
            runtime_duration = 0
        
        # 记录测试结果
        test_key = f"{project_name}_cycle_{cycle}"
        self.test_results[test_key] = {
            'project_type': project_type,
            'project_name': project_name,
            'cycle': cycle,
            'build_success': build_success,
            'build_duration': build_duration,
            'build_message': build_msg,
            'runtime_success': runtime_success,
            'runtime_duration': runtime_duration,
            'runtime_message': runtime_msg,
            'total_duration': build_duration + runtime_duration
        }
        
        status = "✅" if build_success and runtime_success else "❌"
        print(f"  {status} [{project_type}] {project_name} - 周期完成 ({build_duration + runtime_duration:.2f}s)")
    
    def _generate_load_test_report(self, total_duration: float, total_cycles: int):
        """生成负载测试报告"""
        print("\n" + "="*80)
        print("📊 多项目负载测试报告")
        print("="*80)
        
        print(f"总测试时间: {total_duration:.2f} 秒")
        print(f"测试周期数: {total_cycles}")
        print(f"构建成功: {self.metrics['build_success']}")
        print(f"构建失败: {self.metrics['build_failure']}")
        print(f"运行成功: {self.metrics['runtime_success']}")
        print(f"运行失败: {self.metrics['runtime_failure']}")
        
        total_tests = sum(self.metrics.values())
        if total_tests > 0:
            success_rate = ((self.metrics['build_success'] + self.metrics['runtime_success']) / total_tests) * 100
            print(f"总体成功率: {success_rate:.1f}%")
        
        # 按项目类型统计
        project_stats = {}
        for result in self.test_results.values():
            project_type = result['project_type']
            if project_type not in project_stats:
                project_stats[project_type] = {
                    'build_success': 0,
                    'build_failure': 0,
                    'runtime_success': 0,
                    'runtime_failure': 0,
                    'avg_build_time': 0,
                    'avg_runtime_time': 0,
                    'count': 0
                }
            
            stats = project_stats[project_type]
            stats['count'] += 1
            
            if result['build_success']:
                stats['build_success'] += 1
            else:
                stats['build_failure'] += 1
            
            if result['runtime_success']:
                stats['runtime_success'] += 1
            else:
                stats['runtime_failure'] += 1
            
            stats['avg_build_time'] += result['build_duration']
            stats['avg_runtime_time'] += result['runtime_duration']
        
        print("\n📈 按项目类型统计:")
        for project_type, stats in project_stats.items():
            if stats['count'] > 0:
                avg_build = stats['avg_build_time'] / stats['count']
                avg_runtime = stats['avg_runtime_time'] / stats['count']
                print(f"  {project_type.upper()}:")
                print(f"    构建: {stats['build_success']}成功/{stats['build_failure']}失败 (平均{avg_build:.2f}s)")
                print(f"    运行: {stats['runtime_success']}成功/{stats['runtime_failure']}失败 (平均{avg_runtime:.2f}s)")
        
        # 保存详细报告
        report_data = {
            'test_type': '多项目负载测试',
            'start_time': datetime.now().isoformat(),
            'total_duration': total_duration,
            'total_cycles': total_cycles,
            'metrics': self.metrics,
            'project_statistics': project_stats,
            'detailed_results': self.test_results
        }
        
        # 创建报告目录
        report_dir = Path('load_test_reports')
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'multi_project_load_test_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存到: {report_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='多项目负载测试器')
    parser.add_argument(
        '--duration',
        type=int,
        default=300,
        help='测试持续时间（秒），默认300秒'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='项目配置文件路径（JSON格式）'
    )
    parser.add_argument(
        '--preset',
        choices=['basic', 'comprehensive', 'error-prone'],
        default='basic',
        help='预设配置: basic=基础测试, comprehensive=全面测试, error-prone=错误场景测试'
    )
    
    args = parser.parse_args()
    
    tester = ProjectLoadTester()
    
    # 根据预设或配置文件确定项目配置
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            project_configs = json.load(f)
    else:
        if args.preset == 'basic':
            project_configs = [
                {'type': 'java', 'name': 'basic-java-app', 'introduce_error': False},
                {'type': 'rust', 'name': 'basic-rust-app', 'introduce_error': False},
                {'type': 'nodejs', 'name': 'basic-node-app', 'introduce_error': False}
            ]
        elif args.preset == 'comprehensive':
            project_configs = [
                {'type': 'java', 'name': 'web-service', 'introduce_error': False},
                {'type': 'java', 'name': 'batch-processor', 'introduce_error': False},
                {'type': 'rust', 'name': 'high-performance-api', 'introduce_error': False},
                {'type': 'rust', 'name': 'data-processor', 'introduce_error': False},
                {'type': 'nodejs', 'name': 'express-api', 'introduce_error': False},
                {'type': 'nodejs', 'name': 'websocket-server', 'introduce_error': False}
            ]
        elif args.preset == 'error-prone':
            project_configs = [
                {'type': 'java', 'name': 'buggy-java-app', 'introduce_error': True},
                {'type': 'rust', 'name': 'failing-rust-app', 'introduce_error': True},
                {'type': 'nodejs', 'name': 'broken-node-app', 'introduce_error': True},
                {'type': 'java', 'name': 'stable-java-app', 'introduce_error': False},
                {'type': 'rust', 'name': 'stable-rust-app', 'introduce_error': False}
            ]
    
    # 运行负载测试
    tester.run_concurrent_load_test(project_configs, args.duration)

if __name__ == '__main__':
    main()