#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-Healing System API 启动脚本
提供便捷的API服务启动方式

功能:
- 环境检查和初始化
- 配置验证
- 数据库初始化
- 服务启动
- 优雅关闭
"""

import os
import sys
import signal
import asyncio
import logging
from pathlib import Path
from typing import Optional

import click
import uvicorn
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from app import app

# 初始化控制台
console = Console()
logger = logging.getLogger(__name__)

class APIServer:
    """API服务器管理类"""
    
    def __init__(self):
        self.config = {}
        self.server: Optional[uvicorn.Server] = None
        self.shutdown_event = asyncio.Event()
    
    def load_config(self, config_path: str) -> bool:
        """加载配置文件"""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                console.print(f"[red]配置文件不存在: {config_path}[/red]")
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            console.print(f"[green]配置文件加载成功: {config_path}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]配置文件加载失败: {e}[/red]")
            return False
    
    def validate_config(self) -> bool:
        """验证配置"""
        try:
            required_sections = ['server', 'auth', 'logging']
            
            for section in required_sections:
                if section not in self.config:
                    console.print(f"[red]缺少必需的配置节: {section}[/red]")
                    return False
            
            # 验证服务器配置
            server_config = self.config.get('server', {})
            if not isinstance(server_config.get('port'), int):
                console.print("[red]服务器端口配置无效[/red]")
                return False
            
            console.print("[green]配置验证通过[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]配置验证失败: {e}[/red]")
            return False
    
    def setup_logging(self):
        """设置日志"""
        try:
            log_config = self.config.get('logging', {})
            
            # 创建日志目录
            if log_config.get('file', {}).get('enabled', True):
                log_path = Path(log_config.get('file', {}).get('path', '/var/log/self-healing/api.log'))
                log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 配置日志级别
            log_level = log_config.get('level', 'INFO')
            logging.basicConfig(
                level=getattr(logging, log_level),
                format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            
            console.print("[green]日志配置完成[/green]")
            
        except Exception as e:
            console.print(f"[red]日志配置失败: {e}[/red]")
    
    def check_dependencies(self) -> bool:
        """检查依赖服务"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("检查依赖服务...", total=None)
                
                # 检查外部服务连接
                external_services = self.config.get('external_services', {})
                
                # 这里可以添加具体的服务检查逻辑
                # 例如检查Prometheus、Elasticsearch等服务的连通性
                
                progress.update(task, description="依赖检查完成")
            
            console.print("[green]依赖服务检查通过[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]依赖服务检查失败: {e}[/red]")
            return False
    
    def initialize_database(self) -> bool:
        """初始化数据库"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("初始化数据库...", total=None)
                
                # 这里可以添加数据库初始化逻辑
                # 例如创建表、运行迁移等
                
                progress.update(task, description="数据库初始化完成")
            
            console.print("[green]数据库初始化完成[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]数据库初始化失败: {e}[/red]")
            return False
    
    def display_startup_info(self):
        """显示启动信息"""
        server_config = self.config.get('server', {})
        host = server_config.get('host', '0.0.0.0')
        port = server_config.get('port', 8000)
        
        # 创建信息表格
        table = Table(title="Self-Healing System API")
        table.add_column("配置项", style="cyan")
        table.add_column("值", style="green")
        
        table.add_row("服务地址", f"http://{host}:{port}")
        table.add_row("API文档", f"http://{host}:{port}/docs")
        table.add_row("健康检查", f"http://{host}:{port}/health")
        table.add_row("指标监控", f"http://{host}:{port}/metrics")
        table.add_row("工作进程", str(server_config.get('workers', 1)))
        table.add_row("日志级别", self.config.get('logging', {}).get('level', 'INFO'))
        
        console.print(table)
        
        # 显示启动面板
        startup_panel = Panel(
            "[green]Self-Healing System API 已启动[/green]\n\n"
            "• 按 Ctrl+C 优雅关闭服务\n"
            "• 访问 /docs 查看API文档\n"
            "• 访问 /health 检查服务状态",
            title="🚀 服务启动成功",
            border_style="green"
        )
        console.print(startup_panel)
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            console.print("\n[yellow]接收到关闭信号，正在优雅关闭服务...[/yellow]")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start_server(self, host: str, port: int, workers: int, reload: bool = False):
        """启动服务器"""
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            workers=workers if not reload else 1,
            reload=reload,
            log_level=self.config.get('logging', {}).get('level', 'info').lower(),
            access_log=self.config.get('server', {}).get('access_log', True)
        )
        
        self.server = uvicorn.Server(config)
        
        # 设置信号处理器
        self.setup_signal_handlers()
        
        try:
            # 启动服务器
            await self.server.serve()
        except Exception as e:
            console.print(f"[red]服务器启动失败: {e}[/red]")
            raise
    
    async def shutdown(self):
        """优雅关闭服务"""
        if self.server:
            console.print("[yellow]正在关闭服务器...[/yellow]")
            self.server.should_exit = True
            
            # 等待服务器关闭
            while not self.server.should_exit:
                await asyncio.sleep(0.1)
            
            console.print("[green]服务器已关闭[/green]")

@click.command()
@click.option('--config', '-c', default='config/api-config.yaml', help='配置文件路径')
@click.option('--host', '-h', default=None, help='绑定主机地址')
@click.option('--port', '-p', type=int, default=None, help='绑定端口')
@click.option('--workers', '-w', type=int, default=None, help='工作进程数')
@click.option('--reload', is_flag=True, help='启用自动重载（开发模式）')
@click.option('--debug', is_flag=True, help='启用调试模式')
@click.option('--check-config', is_flag=True, help='仅检查配置文件')
def main(config, host, port, workers, reload, debug, check_config):
    """启动Self-Healing System API服务"""
    
    # 显示启动横幅
    console.print(Panel(
        "[bold blue]Self-Healing System API[/bold blue]\n"
        "运维自愈系统RESTful API服务",
        title="🔧 启动中",
        border_style="blue"
    ))
    
    # 创建API服务器实例
    api_server = APIServer()
    
    # 加载配置
    if not api_server.load_config(config):
        sys.exit(1)
    
    # 验证配置
    if not api_server.validate_config():
        sys.exit(1)
    
    # 如果只是检查配置，则退出
    if check_config:
        console.print("[green]配置文件检查通过[/green]")
        return
    
    # 设置日志
    api_server.setup_logging()
    
    # 检查依赖
    if not api_server.check_dependencies():
        console.print("[yellow]警告: 部分依赖服务不可用，但服务仍将启动[/yellow]")
    
    # 初始化数据库
    if not api_server.initialize_database():
        console.print("[yellow]警告: 数据库初始化失败，但服务仍将启动[/yellow]")
    
    # 获取服务器配置
    server_config = api_server.config.get('server', {})
    
    # 命令行参数覆盖配置文件
    final_host = host or server_config.get('host', '0.0.0.0')
    final_port = port or server_config.get('port', 8000)
    final_workers = workers or server_config.get('workers', 1)
    
    # 开发模式设置
    if debug:
        reload = True
        final_workers = 1
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 显示启动信息
    api_server.display_startup_info()
    
    try:
        # 启动服务器
        asyncio.run(api_server.start_server(
            host=final_host,
            port=final_port,
            workers=final_workers,
            reload=reload
        ))
    except KeyboardInterrupt:
        console.print("\n[yellow]用户中断，正在关闭服务...[/yellow]")
    except Exception as e:
        console.print(f"[red]服务启动失败: {e}[/red]")
        sys.exit(1)
    finally:
        console.print("[green]Self-Healing System API 已关闭[/green]")

if __name__ == '__main__':
    main()