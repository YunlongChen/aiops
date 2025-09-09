#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块

本模块提供统一的日志配置和管理功能，包括：
- 多级别日志记录
- 文件和控制台输出
- 日志轮转和压缩
- 结构化日志格式
- 性能监控日志

Author: AIOps Team
Version: 1.0.0
Date: 2024-01-15
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
import traceback
from functools import wraps
import time

# 日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

class StructuredFormatter(logging.Formatter):
    """结构化日志格式器"""
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录
        
        Args:
            record: 日志记录
            
        Returns:
            格式化后的日志字符串
        """
        # 基础日志信息
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加进程和线程信息
        if hasattr(record, 'process'):
            log_data['process_id'] = record.process
        if hasattr(record, 'thread'):
            log_data['thread_id'] = record.thread
        
        # 添加异常信息
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # 添加额外字段
        if self.include_extra:
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                              'pathname', 'filename', 'module', 'lineno', 
                              'funcName', 'created', 'msecs', 'relativeCreated', 
                              'thread', 'threadName', 'processName', 'process',
                              'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                    try:
                        # 确保值可以JSON序列化
                        json.dumps(value)
                        extra_fields[key] = value
                    except (TypeError, ValueError):
                        extra_fields[key] = str(value)
            
            if extra_fields:
                log_data['extra'] = extra_fields
        
        return json.dumps(log_data, ensure_ascii=False)

class ColoredFormatter(logging.Formatter):
    """彩色日志格式器（用于控制台输出）"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录
        
        Args:
            record: 日志记录
            
        Returns:
            格式化后的日志字符串
        """
        # 基础格式
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()
        location = f"{record.filename}:{record.lineno}"
        
        # 应用颜色
        if self.use_colors:
            color = self.COLORS.get(level, '')
            reset = self.COLORS['RESET']
            level = f"{color}{level}{reset}"
            logger_name = f"\033[34m{logger_name}{reset}"  # 蓝色
            location = f"\033[90m{location}{reset}"  # 灰色
        
        # 组装日志行
        log_line = f"{timestamp} [{level:8}] {logger_name} - {message} ({location})"
        
        # 添加异常信息
        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)
        
        return log_line

class PerformanceLogger:
    """性能日志记录器"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """
        开始计时
        
        Args:
            operation: 操作名称
        """
        self.start_times[operation] = time.time()
        self.logger.debug(f"开始操作: {operation}")
    
    def end_timer(self, operation: str, **extra_data):
        """
        结束计时并记录
        
        Args:
            operation: 操作名称
            **extra_data: 额外数据
        """
        if operation not in self.start_times:
            self.logger.warning(f"操作{operation}未找到开始时间")
            return
        
        duration = time.time() - self.start_times[operation]
        del self.start_times[operation]
        
        self.logger.info(
            f"操作完成: {operation}",
            extra={
                'operation': operation,
                'duration_seconds': duration,
                'performance_metric': True,
                **extra_data
            }
        )
    
    def log_metric(self, metric_name: str, value: float, unit: str = None, **extra_data):
        """
        记录性能指标
        
        Args:
            metric_name: 指标名称
            value: 指标值
            unit: 单位
            **extra_data: 额外数据
        """
        self.logger.info(
            f"性能指标: {metric_name} = {value}{unit or ''}",
            extra={
                'metric_name': metric_name,
                'metric_value': value,
                'metric_unit': unit,
                'performance_metric': True,
                **extra_data
            }
        )

def performance_monitor(operation_name: str = None):
    """
    性能监控装饰器
    
    Args:
        operation_name: 操作名称，如果为None则使用函数名
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            perf_logger = PerformanceLogger(logger)
            
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            perf_logger.start_timer(op_name)
            
            try:
                result = func(*args, **kwargs)
                perf_logger.end_timer(op_name, status='success')
                return result
            except Exception as e:
                perf_logger.end_timer(op_name, status='error', error=str(e))
                raise
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            perf_logger = PerformanceLogger(logger)
            
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            perf_logger.start_timer(op_name)
            
            try:
                result = await func(*args, **kwargs)
                perf_logger.end_timer(op_name, status='success')
                return result
            except Exception as e:
                perf_logger.end_timer(op_name, status='error', error=str(e))
                raise
        
        # 根据函数类型返回相应的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator

class LoggerManager:
    """日志管理器"""
    
    def __init__(self):
        self.loggers = {}
        self.handlers = {}
        self.default_config = {
            'level': 'INFO',
            'format': 'colored',  # 'colored', 'structured', 'simple'
            'file_output': True,
            'console_output': True,
            'log_dir': './logs',
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5,
            'encoding': 'utf-8'
        }
    
    def setup_logger(self, name: str, config: Dict[str, Any] = None) -> logging.Logger:
        """
        设置日志记录器
        
        Args:
            name: 日志记录器名称
            config: 配置字典
            
        Returns:
            配置好的日志记录器
        """
        if name in self.loggers:
            return self.loggers[name]
        
        # 合并配置
        final_config = self.default_config.copy()
        if config:
            final_config.update(config)
        
        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(LOG_LEVELS.get(final_config['level'].upper(), logging.INFO))
        
        # 清除现有处理器
        logger.handlers.clear()
        
        # 添加控制台处理器
        if final_config['console_output']:
            console_handler = self._create_console_handler(final_config)
            logger.addHandler(console_handler)
        
        # 添加文件处理器
        if final_config['file_output']:
            file_handler = self._create_file_handler(name, final_config)
            logger.addHandler(file_handler)
        
        # 防止日志传播到根日志记录器
        logger.propagate = False
        
        self.loggers[name] = logger
        return logger
    
    def _create_console_handler(self, config: Dict[str, Any]) -> logging.Handler:
        """
        创建控制台处理器
        
        Args:
            config: 配置字典
            
        Returns:
            控制台处理器
        """
        handler = logging.StreamHandler(sys.stdout)
        
        if config['format'] == 'structured':
            formatter = StructuredFormatter()
        elif config['format'] == 'colored':
            formatter = ColoredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s - %(message)s (%(filename)s:%(lineno)d)'
            )
        
        handler.setFormatter(formatter)
        return handler
    
    def _create_file_handler(self, logger_name: str, config: Dict[str, Any]) -> logging.Handler:
        """
        创建文件处理器
        
        Args:
            logger_name: 日志记录器名称
            config: 配置字典
            
        Returns:
            文件处理器
        """
        # 创建日志目录
        log_dir = Path(config['log_dir'])
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 日志文件路径
        log_file = log_dir / f"{logger_name.replace('.', '_')}.log"
        
        # 创建轮转文件处理器
        handler = logging.handlers.RotatingFileHandler(
            filename=str(log_file),
            maxBytes=config['max_file_size'],
            backupCount=config['backup_count'],
            encoding=config['encoding']
        )
        
        # 设置格式器
        if config['format'] == 'structured':
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s - %(message)s (%(filename)s:%(lineno)d)'
            )
        
        handler.setFormatter(formatter)
        return handler
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            日志记录器
        """
        if name not in self.loggers:
            return self.setup_logger(name)
        return self.loggers[name]
    
    def update_log_level(self, name: str, level: str):
        """
        更新日志级别
        
        Args:
            name: 日志记录器名称
            level: 新的日志级别
        """
        if name in self.loggers:
            logger = self.loggers[name]
            logger.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))
    
    def add_handler(self, name: str, handler: logging.Handler):
        """
        添加处理器
        
        Args:
            name: 日志记录器名称
            handler: 处理器
        """
        if name in self.loggers:
            self.loggers[name].addHandler(handler)
    
    def remove_handler(self, name: str, handler: logging.Handler):
        """
        移除处理器
        
        Args:
            name: 日志记录器名称
            handler: 处理器
        """
        if name in self.loggers:
            self.loggers[name].removeHandler(handler)
    
    def shutdown(self):
        """
        关闭所有日志记录器
        """
        for logger in self.loggers.values():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        
        self.loggers.clear()
        self.handlers.clear()

# 全局日志管理器实例
_logger_manager = LoggerManager()

def setup_logger(name: str, config: Dict[str, Any] = None) -> logging.Logger:
    """
    设置日志记录器（便捷函数）
    
    Args:
        name: 日志记录器名称
        config: 配置字典
        
    Returns:
        配置好的日志记录器
    """
    return _logger_manager.setup_logger(name, config)

def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器（便捷函数）
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器
    """
    return _logger_manager.get_logger(name)

def configure_logging(config: Dict[str, Any]):
    """
    配置全局日志设置
    
    Args:
        config: 全局配置字典
    """
    _logger_manager.default_config.update(config)

def shutdown_logging():
    """
    关闭所有日志记录器
    """
    _logger_manager.shutdown()

# 创建性能日志记录器的便捷函数
def get_performance_logger(name: str) -> PerformanceLogger:
    """
    获取性能日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        性能日志记录器
    """
    logger = get_logger(name)
    return PerformanceLogger(logger)

# 示例配置
DEFAULT_CONFIG = {
    'level': 'INFO',
    'format': 'colored',
    'file_output': True,
    'console_output': True,
    'log_dir': './logs',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'encoding': 'utf-8'
}

PRODUCTION_CONFIG = {
    'level': 'WARNING',
    'format': 'structured',
    'file_output': True,
    'console_output': False,
    'log_dir': '/var/log/aiops',
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'backup_count': 10,
    'encoding': 'utf-8'
}

DEVELOPMENT_CONFIG = {
    'level': 'DEBUG',
    'format': 'colored',
    'file_output': True,
    'console_output': True,
    'log_dir': './logs',
    'max_file_size': 5 * 1024 * 1024,  # 5MB
    'backup_count': 3,
    'encoding': 'utf-8'
}