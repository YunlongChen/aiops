#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI引擎主应用模块

本模块实现了AIOps平台的AI引擎核心功能，包括：
- 异常检测算法
- 预测分析
- 自动化决策
- 模型管理
- API接口服务

Author: AIOps Team
Version: 1.0.0
Date: 2024-01-15
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from core.anomaly_detector import AnomalyDetector
from core.predictor import Predictor
from core.model_manager import ModelManager
from core.decision_engine import DecisionEngine
from utils.logger import setup_logger
from utils.config import Config
from utils.metrics import MetricsCollector

# 配置日志
logger = setup_logger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title="AIOps AI Engine",
    description="智能运维AI引擎服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
config = Config()
anomaly_detector = None
predictor = None
model_manager = None
decision_engine = None
metrics_collector = None

# 数据模型定义
class MetricData(BaseModel):
    """指标数据模型"""
    timestamp: datetime = Field(..., description="时间戳")
    metric_name: str = Field(..., description="指标名称")
    value: float = Field(..., description="指标值")
    labels: Dict[str, str] = Field(default_factory=dict, description="标签")
    source: str = Field(..., description="数据源")

class AnomalyRequest(BaseModel):
    """异常检测请求模型"""
    metrics: List[MetricData] = Field(..., description="指标数据列表")
    algorithm: str = Field(default="isolation_forest", description="检测算法")
    threshold: float = Field(default=0.1, description="异常阈值")
    window_size: int = Field(default=100, description="时间窗口大小")

class PredictionRequest(BaseModel):
    """预测请求模型"""
    metrics: List[MetricData] = Field(..., description="历史指标数据")
    horizon: int = Field(default=60, description="预测时长（分钟）")
    model_type: str = Field(default="lstm", description="预测模型类型")

class DecisionRequest(BaseModel):
    """决策请求模型"""
    anomalies: List[Dict[str, Any]] = Field(..., description="异常信息")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")
    severity: str = Field(default="medium", description="严重程度")

@app.on_event("startup")
async def startup_event():
    """应用启动事件处理"""
    global anomaly_detector, predictor, model_manager, decision_engine, metrics_collector
    
    logger.info("正在启动AI引擎服务...")
    
    try:
        # 初始化组件
        model_manager = ModelManager(config)
        await model_manager.initialize()
        
        anomaly_detector = AnomalyDetector(config, model_manager)
        await anomaly_detector.initialize()
        
        predictor = Predictor(config, model_manager)
        await predictor.initialize()
        
        decision_engine = DecisionEngine(config)
        await decision_engine.initialize()
        
        metrics_collector = MetricsCollector(config)
        await metrics_collector.initialize()
        
        logger.info("AI引擎服务启动成功")
        
    except Exception as e:
        logger.error(f"AI引擎服务启动失败: {e}")
        sys.exit(1)

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件处理"""
    logger.info("正在关闭AI引擎服务...")
    
    # 清理资源
    if metrics_collector:
        await metrics_collector.cleanup()
    if decision_engine:
        await decision_engine.cleanup()
    if predictor:
        await predictor.cleanup()
    if anomaly_detector:
        await anomaly_detector.cleanup()
    if model_manager:
        await model_manager.cleanup()
    
    logger.info("AI引擎服务已关闭")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {
            "anomaly_detector": anomaly_detector.is_ready() if anomaly_detector else False,
            "predictor": predictor.is_ready() if predictor else False,
            "model_manager": model_manager.is_ready() if model_manager else False,
            "decision_engine": decision_engine.is_ready() if decision_engine else False
        }
    }

@app.get("/metrics")
async def get_metrics():
    """获取系统指标"""
    if not metrics_collector:
        raise HTTPException(status_code=503, detail="指标收集器未初始化")
    
    try:
        metrics = await metrics_collector.get_metrics()
        return {"metrics": metrics, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"获取指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect/anomaly")
async def detect_anomaly(request: AnomalyRequest, background_tasks: BackgroundTasks):
    """异常检测接口"""
    if not anomaly_detector:
        raise HTTPException(status_code=503, detail="异常检测器未初始化")
    
    try:
        # 执行异常检测
        result = await anomaly_detector.detect(
            metrics=request.metrics,
            algorithm=request.algorithm,
            threshold=request.threshold,
            window_size=request.window_size
        )
        
        # 后台任务：记录检测结果
        background_tasks.add_task(
            metrics_collector.record_detection,
            result
        )
        
        return {
            "anomalies": result.get("anomalies", []),
            "confidence": result.get("confidence", 0.0),
            "algorithm": request.algorithm,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"异常检测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def predict_metrics(request: PredictionRequest, background_tasks: BackgroundTasks):
    """指标预测接口"""
    if not predictor:
        raise HTTPException(status_code=503, detail="预测器未初始化")
    
    try:
        # 执行预测
        result = await predictor.predict(
            metrics=request.metrics,
            horizon=request.horizon,
            model_type=request.model_type
        )
        
        # 后台任务：记录预测结果
        background_tasks.add_task(
            metrics_collector.record_prediction,
            result
        )
        
        return {
            "predictions": result.get("predictions", []),
            "confidence": result.get("confidence", 0.0),
            "model_type": request.model_type,
            "horizon": request.horizon,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"预测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decide")
async def make_decision(request: DecisionRequest, background_tasks: BackgroundTasks):
    """自动决策接口"""
    if not decision_engine:
        raise HTTPException(status_code=503, detail="决策引擎未初始化")
    
    try:
        # 执行决策
        result = await decision_engine.decide(
            anomalies=request.anomalies,
            context=request.context,
            severity=request.severity
        )
        
        # 后台任务：记录决策结果
        background_tasks.add_task(
            metrics_collector.record_decision,
            result
        )
        
        return {
            "actions": result.get("actions", []),
            "confidence": result.get("confidence", 0.0),
            "reasoning": result.get("reasoning", ""),
            "severity": request.severity,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"决策失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """获取模型列表"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="模型管理器未初始化")
    
    try:
        models = await model_manager.list_models()
        return {"models": models, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/{model_name}/train")
async def train_model(model_name: str, background_tasks: BackgroundTasks):
    """训练模型接口"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="模型管理器未初始化")
    
    try:
        # 后台任务：训练模型
        background_tasks.add_task(
            model_manager.train_model,
            model_name
        )
        
        return {
            "message": f"模型 {model_name} 训练已开始",
            "model_name": model_name,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"启动模型训练失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

def main():
    """主函数"""
    # 从环境变量获取配置
    host = os.getenv("AI_ENGINE_HOST", "0.0.0.0")
    port = int(os.getenv("AI_ENGINE_PORT", "8080"))
    workers = int(os.getenv("AI_ENGINE_WORKERS", "1"))
    log_level = os.getenv("AI_ENGINE_LOG_LEVEL", "info")
    
    logger.info(f"启动AI引擎服务 - Host: {host}, Port: {port}, Workers: {workers}")
    
    # 启动服务
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        workers=workers,
        log_level=log_level,
        reload=False
    )

if __name__ == "__main__":
    main()