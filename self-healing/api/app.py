#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运维操作API服务
提供RESTful接口用于管理自愈系统

主要功能:
- 系统健康检查API
- 自愈规则管理API
- 告警处理API
- Ansible Playbook执行API
- 系统监控API
- 配置管理API
"""

import os
import sys
import json
import logging
import asyncio
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import yaml
import aiofiles
import aiohttp
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client.core import CollectorRegistry

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from trigger_system import TriggerSystem, Alert, AlertSeverity, AlertStatus
from self_healing_executor import SelfHealingExecutor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/self-healing/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Prometheus指标
registry = CollectorRegistry()
api_requests_total = Counter(
    'api_requests_total', 
    'Total API requests', 
    ['method', 'endpoint', 'status'],
    registry=registry
)
api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint'],
    registry=registry
)
active_alerts = Gauge(
    'active_alerts_total',
    'Number of active alerts',
    ['severity'],
    registry=registry
)
playbook_executions = Counter(
    'playbook_executions_total',
    'Total playbook executions',
    ['playbook', 'status'],
    registry=registry
)

# FastAPI应用实例
app = FastAPI(
    title="Self-Healing System API",
    description="运维自愈系统RESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全认证
security = HTTPBearer()

# 全局变量
trigger_system: Optional[TriggerSystem] = None
self_healing_executor: Optional[SelfHealingExecutor] = None
config: Dict[str, Any] = {}

# Pydantic模型
class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(..., description="检查时间")
    version: str = Field(..., description="API版本")
    components: Dict[str, str] = Field(..., description="组件状态")
    uptime: float = Field(..., description="运行时间（秒）")

class AlertModel(BaseModel):
    """告警模型"""
    id: str = Field(..., description="告警ID")
    name: str = Field(..., description="告警名称")
    severity: str = Field(..., description="严重程度")
    status: str = Field(..., description="告警状态")
    message: str = Field(..., description="告警消息")
    labels: Dict[str, str] = Field(default_factory=dict, description="标签")
    annotations: Dict[str, str] = Field(default_factory=dict, description="注释")
    timestamp: datetime = Field(..., description="告警时间")
    resolved_at: Optional[datetime] = Field(None, description="解决时间")

class RuleModel(BaseModel):
    """规则模型"""
    id: str = Field(..., description="规则ID")
    name: str = Field(..., description="规则名称")
    description: str = Field(..., description="规则描述")
    pattern: str = Field(..., description="匹配模式")
    severity_threshold: str = Field(..., description="严重程度阈值")
    actions: List[Dict[str, Any]] = Field(..., description="执行动作")
    cooldown_minutes: int = Field(default=5, description="冷却时间（分钟）")
    max_executions: int = Field(default=3, description="最大执行次数")
    enabled: bool = Field(default=True, description="是否启用")

class PlaybookExecutionRequest(BaseModel):
    """Playbook执行请求模型"""
    playbook_path: str = Field(..., description="Playbook路径")
    inventory: str = Field(default="localhost,", description="主机清单")
    extra_vars: Dict[str, Any] = Field(default_factory=dict, description="额外变量")
    tags: List[str] = Field(default_factory=list, description="标签")
    skip_tags: List[str] = Field(default_factory=list, description="跳过的标签")
    check_mode: bool = Field(default=False, description="检查模式")
    timeout: int = Field(default=300, description="超时时间（秒）")

class PlaybookExecutionResponse(BaseModel):
    """Playbook执行响应模型"""
    execution_id: str = Field(..., description="执行ID")
    status: str = Field(..., description="执行状态")
    started_at: datetime = Field(..., description="开始时间")
    finished_at: Optional[datetime] = Field(None, description="结束时间")
    duration: Optional[float] = Field(None, description="执行时长（秒）")
    return_code: Optional[int] = Field(None, description="返回码")
    stdout: str = Field(default="", description="标准输出")
    stderr: str = Field(default="", description="错误输出")
    summary: Dict[str, Any] = Field(default_factory=dict, description="执行摘要")

class SystemMetrics(BaseModel):
    """系统指标模型"""
    timestamp: datetime = Field(..., description="指标时间")
    cpu_usage: float = Field(..., description="CPU使用率")
    memory_usage: float = Field(..., description="内存使用率")
    disk_usage: float = Field(..., description="磁盘使用率")
    network_io: Dict[str, float] = Field(..., description="网络IO")
    active_alerts_count: int = Field(..., description="活跃告警数量")
    services_status: Dict[str, str] = Field(..., description="服务状态")

# 启动时间
start_time = datetime.now()

# 依赖注入
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户（简单的token验证）"""
    token = credentials.credentials
    # 这里应该实现真正的token验证逻辑
    if not token or token != config.get('api_token', 'default-token'):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return {"username": "admin", "token": token}

# 中间件
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """指标收集中间件"""
    start_time = datetime.now()
    
    response = await call_next(request)
    
    # 记录指标
    duration = (datetime.now() - start_time).total_seconds()
    method = request.method
    endpoint = request.url.path
    status = str(response.status_code)
    
    api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    return response

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global trigger_system, self_healing_executor, config
    
    logger.info("启动Self-Healing API服务...")
    
    try:
        # 加载配置
        config_path = Path(__file__).parent.parent / "config" / "api-config.yaml"
        if config_path.exists():
            async with aiofiles.open(config_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                config = yaml.safe_load(content)
        else:
            logger.warning(f"配置文件不存在: {config_path}")
            config = {}
        
        # 初始化触发器系统
        trigger_config_path = Path(__file__).parent.parent / "config" / "trigger-system.yaml"
        if trigger_config_path.exists():
            trigger_system = TriggerSystem(str(trigger_config_path))
            # 在后台启动触发器系统，避免阻塞API服务
            asyncio.create_task(trigger_system.start())
            logger.info("触发器系统已启动")
        
        # 初始化自愈执行器
        executor_config_path = Path(__file__).parent.parent / "config" / "self-healing.yaml"
        if executor_config_path.exists():
            self_healing_executor = SelfHealingExecutor(str(executor_config_path))
            logger.info("自愈执行器已初始化")
        
        logger.info("Self-Healing API服务启动完成")
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("关闭Self-Healing API服务...")
    
    if trigger_system:
        trigger_system.stop()
    
    logger.info("Self-Healing API服务已关闭")

# API路由
@app.get("/", response_model=Dict[str, str])
async def root():
    """根路径"""
    return {
        "message": "Self-Healing System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """健康检查接口"""
    uptime = (datetime.now() - start_time).total_seconds()
    
    components = {
        "api": "healthy",
        "trigger_system": "healthy" if trigger_system else "unavailable",
        "self_healing_executor": "healthy" if self_healing_executor else "unavailable"
    }
    
    # 检查各组件状态
    overall_status = "healthy"
    for component, status in components.items():
        if status != "healthy":
            overall_status = "degraded"
            break
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.now(),
        version="1.0.0",
        components=components,
        uptime=uptime
    )

@app.get("/metrics")
async def metrics():
    """Prometheus指标接口"""
    # 更新活跃告警指标
    if trigger_system:
        alerts = await trigger_system.alert_store.get_active_alerts()
        severity_counts = {}
        for alert in alerts:
            severity = alert.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        for severity in ['critical', 'warning', 'info']:
            active_alerts.labels(severity=severity).set(severity_counts.get(severity, 0))
    
    return generate_latest(registry)

# 告警管理API
@app.get("/api/v1/alerts", response_model=List[AlertModel])
async def get_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    user: dict = Depends(get_current_user)
):
    """获取告警列表"""
    if not trigger_system:
        raise HTTPException(status_code=503, detail="Trigger system not available")
    
    alerts = trigger_system.alert_store.get_active_alerts()
    
    # 过滤条件
    if severity:
        alerts = [a for a in alerts if a.severity.value == severity]
    if status:
        alerts = [a for a in alerts if a.status.value == status]
    
    # 限制数量
    alerts = alerts[:limit]
    
    # 转换为响应模型
    result = []
    for alert in alerts:
        result.append(AlertModel(
            id=alert.id,
            name=alert.name,
            severity=alert.severity.value,
            status=alert.status.value,
            message=alert.message,
            labels=alert.labels,
            annotations=alert.annotations,
            timestamp=alert.timestamp,
            resolved_at=alert.resolved_at
        ))
    
    return result

@app.get("/api/v1/alerts/{alert_id}", response_model=AlertModel)
async def get_alert(
    alert_id: str,
    user: dict = Depends(get_current_user)
):
    """获取特定告警详情"""
    if not trigger_system:
        raise HTTPException(status_code=503, detail="Trigger system not available")
    
    alert = trigger_system.alert_store.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertModel(
        id=alert.id,
        name=alert.name,
        severity=alert.severity.value,
        status=alert.status.value,
        message=alert.message,
        labels=alert.labels,
        annotations=alert.annotations,
        timestamp=alert.timestamp,
        resolved_at=alert.resolved_at
    )

@app.post("/api/v1/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    user: dict = Depends(get_current_user)
):
    """手动解决告警"""
    if not trigger_system:
        raise HTTPException(status_code=503, detail="Trigger system not available")
    
    alert = trigger_system.alert_store.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # 更新告警状态
    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.now()
    trigger_system.alert_store.update_alert(alert)
    
    logger.info(f"告警 {alert_id} 已被用户 {user['username']} 手动解决")
    
    return {"message": "Alert resolved successfully", "alert_id": alert_id}

# 规则管理API
@app.get("/api/v1/rules", response_model=List[RuleModel])
async def get_rules(user: dict = Depends(get_current_user)):
    """获取规则列表"""
    if not trigger_system:
        raise HTTPException(status_code=503, detail="Trigger system not available")
    
    rules = trigger_system.rules
    result = []
    
    for rule in rules:
        result.append(RuleModel(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            pattern=rule.pattern,
            severity_threshold=rule.severity_threshold.value,
            actions=[action.__dict__ for action in rule.actions],
            cooldown_minutes=rule.cooldown_minutes,
            max_executions=rule.max_executions,
            enabled=rule.enabled
        ))
    
    return result

@app.get("/api/v1/rules/{rule_id}", response_model=RuleModel)
async def get_rule(
    rule_id: str,
    user: dict = Depends(get_current_user)
):
    """获取特定规则详情"""
    if not trigger_system:
        raise HTTPException(status_code=503, detail="Trigger system not available")
    
    rule = next((r for r in trigger_system.rules if r.id == rule_id), None)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return RuleModel(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        pattern=rule.pattern,
        severity_threshold=rule.severity_threshold.value,
        actions=[action.__dict__ for action in rule.actions],
        cooldown_minutes=rule.cooldown_minutes,
        max_executions=rule.max_executions,
        enabled=rule.enabled
    )

@app.put("/api/v1/rules/{rule_id}/enable")
async def enable_rule(
    rule_id: str,
    user: dict = Depends(get_current_user)
):
    """启用规则"""
    if not trigger_system:
        raise HTTPException(status_code=503, detail="Trigger system not available")
    
    rule = next((r for r in trigger_system.rules if r.id == rule_id), None)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule.enabled = True
    logger.info(f"规则 {rule_id} 已被用户 {user['username']} 启用")
    
    return {"message": "Rule enabled successfully", "rule_id": rule_id}

@app.put("/api/v1/rules/{rule_id}/disable")
async def disable_rule(
    rule_id: str,
    user: dict = Depends(get_current_user)
):
    """禁用规则"""
    if not trigger_system:
        raise HTTPException(status_code=503, detail="Trigger system not available")
    
    rule = next((r for r in trigger_system.rules if r.id == rule_id), None)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule.enabled = False
    logger.info(f"规则 {rule_id} 已被用户 {user['username']} 禁用")
    
    return {"message": "Rule disabled successfully", "rule_id": rule_id}

# Playbook执行API
@app.post("/api/v1/playbooks/execute", response_model=PlaybookExecutionResponse)
async def execute_playbook(
    request: PlaybookExecutionRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """执行Ansible Playbook"""
    if not self_healing_executor:
        raise HTTPException(status_code=503, detail="Self-healing executor not available")
    
    # 验证Playbook路径
    playbook_path = Path(request.playbook_path)
    if not playbook_path.exists():
        raise HTTPException(status_code=404, detail="Playbook not found")
    
    # 生成执行ID
    execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(request.playbook_path)) % 10000}"
    
    # 创建执行响应
    execution = PlaybookExecutionResponse(
        execution_id=execution_id,
        status="running",
        started_at=datetime.now()
    )
    
    # 后台执行Playbook
    background_tasks.add_task(
        _execute_playbook_background,
        execution_id,
        request,
        user['username']
    )
    
    logger.info(f"用户 {user['username']} 启动Playbook执行: {request.playbook_path}")
    
    return execution

@app.get("/api/v1/playbooks/executions/{execution_id}", response_model=PlaybookExecutionResponse)
async def get_playbook_execution(
    execution_id: str,
    user: dict = Depends(get_current_user)
):
    """获取Playbook执行状态"""
    # 从文件系统读取执行结果
    result_file = Path(f"/tmp/playbook_executions/{execution_id}.json")
    if not result_file.exists():
        raise HTTPException(status_code=404, detail="Execution not found")
    
    async with aiofiles.open(result_file, 'r') as f:
        content = await f.read()
        result = json.loads(content)
    
    return PlaybookExecutionResponse(**result)

@app.get("/api/v1/playbooks")
async def list_playbooks(user: dict = Depends(get_current_user)):
    """列出可用的Playbook"""
    playbooks_dir = Path(__file__).parent.parent / "playbooks"
    playbooks = []
    
    if playbooks_dir.exists():
        for playbook_file in playbooks_dir.rglob("*.yml"):
            relative_path = playbook_file.relative_to(playbooks_dir)
            playbooks.append({
                "name": playbook_file.stem,
                "path": str(playbook_file),
                "relative_path": str(relative_path),
                "category": relative_path.parts[0] if len(relative_path.parts) > 1 else "general",
                "size": playbook_file.stat().st_size,
                "modified": datetime.fromtimestamp(playbook_file.stat().st_mtime).isoformat()
            })
    
    return {"playbooks": playbooks}

# 系统监控API
@app.get("/api/v1/system/metrics", response_model=SystemMetrics)
async def get_system_metrics(user: dict = Depends(get_current_user)):
    """获取系统指标"""
    try:
        # 获取系统指标（这里使用模拟数据，实际应该从监控系统获取）
        import psutil
        
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        # 获取活跃告警数量
        active_alerts_count = 0
        if trigger_system:
            active_alerts_count = len(trigger_system.alert_store.get_active_alerts())
        
        # 获取服务状态（模拟）
        services_status = {
            "elasticsearch": "running",
            "prometheus": "running",
            "grafana": "running",
            "alertmanager": "running"
        }
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_io={
                "bytes_sent": float(network.bytes_sent),
                "bytes_recv": float(network.bytes_recv)
            },
            active_alerts_count=active_alerts_count,
            services_status=services_status
        )
    
    except ImportError:
        # 如果psutil不可用，返回模拟数据
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=25.5,
            memory_usage=68.2,
            disk_usage=45.8,
            network_io={"bytes_sent": 1024000.0, "bytes_recv": 2048000.0},
            active_alerts_count=3,
            services_status={"api": "running"}
        )

@app.get("/api/v1/system/status")
async def get_system_status(user: dict = Depends(get_current_user)):
    """获取系统状态概览"""
    uptime = (datetime.now() - start_time).total_seconds()
    
    status = {
        "system": {
            "uptime_seconds": uptime,
            "start_time": start_time.isoformat(),
            "current_time": datetime.now().isoformat()
        },
        "components": {
            "trigger_system": {
                "status": "running" if trigger_system else "stopped",
                "active_rules": len(trigger_system.rules) if trigger_system else 0,
                "active_alerts": len(trigger_system.alert_store.get_active_alerts()) if trigger_system else 0
            },
            "self_healing_executor": {
                "status": "available" if self_healing_executor else "unavailable"
            }
        },
        "statistics": {
            "total_api_requests": sum([s._value._value for s in api_requests_total.collect()[0].samples]),
            "total_playbook_executions": sum([s._value._value for s in playbook_executions.collect()[0].samples])
        }
    }
    
    return status

# 配置管理API
@app.get("/api/v1/config")
async def get_config(user: dict = Depends(get_current_user)):
    """获取系统配置"""
    # 返回非敏感配置信息
    safe_config = {k: v for k, v in config.items() if not k.endswith('_password') and not k.endswith('_token')}
    return safe_config

@app.post("/api/v1/config/reload")
async def reload_config(user: dict = Depends(get_current_user)):
    """重新加载配置"""
    global config
    
    try:
        config_path = Path(__file__).parent.parent / "config" / "api-config.yaml"
        if config_path.exists():
            async with aiofiles.open(config_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                config = yaml.safe_load(content)
        
        logger.info(f"配置已被用户 {user['username']} 重新加载")
        return {"message": "Configuration reloaded successfully"}
    
    except Exception as e:
        logger.error(f"配置重新加载失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reload configuration: {str(e)}")

# 后台任务函数
async def _execute_playbook_background(execution_id: str, request: PlaybookExecutionRequest, username: str):
    """后台执行Playbook"""
    result_file = Path(f"/tmp/playbook_executions/{execution_id}.json")
    result_file.parent.mkdir(parents=True, exist_ok=True)
    
    started_at = datetime.now()
    
    try:
        # 构建ansible-playbook命令
        cmd = [
            "ansible-playbook",
            request.playbook_path,
            "-i", request.inventory
        ]
        
        # 添加额外变量
        if request.extra_vars:
            cmd.extend(["-e", json.dumps(request.extra_vars)])
        
        # 添加标签
        if request.tags:
            cmd.extend(["--tags", ",".join(request.tags)])
        
        if request.skip_tags:
            cmd.extend(["--skip-tags", ",".join(request.skip_tags)])
        
        # 检查模式
        if request.check_mode:
            cmd.append("--check")
        
        # 执行命令
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=request.timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise Exception("Playbook execution timed out")
        
        finished_at = datetime.now()
        duration = (finished_at - started_at).total_seconds()
        
        # 保存执行结果
        result = PlaybookExecutionResponse(
            execution_id=execution_id,
            status="completed" if process.returncode == 0 else "failed",
            started_at=started_at,
            finished_at=finished_at,
            duration=duration,
            return_code=process.returncode,
            stdout=stdout.decode('utf-8'),
            stderr=stderr.decode('utf-8'),
            summary={
                "playbook": request.playbook_path,
                "inventory": request.inventory,
                "executed_by": username
            }
        )
        
        # 更新Prometheus指标
        playbook_name = Path(request.playbook_path).stem
        status = "success" if process.returncode == 0 else "failed"
        playbook_executions.labels(playbook=playbook_name, status=status).inc()
        
        logger.info(f"Playbook执行完成: {execution_id}, 状态: {result.status}")
        
    except Exception as e:
        finished_at = datetime.now()
        duration = (finished_at - started_at).total_seconds()
        
        result = PlaybookExecutionResponse(
            execution_id=execution_id,
            status="error",
            started_at=started_at,
            finished_at=finished_at,
            duration=duration,
            return_code=-1,
            stdout="",
            stderr=str(e),
            summary={
                "playbook": request.playbook_path,
                "error": str(e),
                "executed_by": username
            }
        )
        
        logger.error(f"Playbook执行失败: {execution_id}, 错误: {e}")
    
    # 保存结果到文件
    async with aiofiles.open(result_file, 'w') as f:
        await f.write(result.json())

if __name__ == "__main__":
    # 开发模式运行
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )