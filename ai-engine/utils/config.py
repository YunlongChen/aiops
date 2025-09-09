#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理工具模块

本模块提供配置管理功能，包括：
- 多格式配置文件支持（JSON、YAML、TOML、INI）
- 环境变量覆盖
- 配置验证和类型转换
- 配置热重载
- 配置加密和解密
- 配置模板和继承
- 配置缓存

Author: AIOps Team
Version: 1.0.0
Date: 2024-01-15
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Type, Callable
from pathlib import Path
from dataclasses import dataclass, field, fields
from abc import ABC, abstractmethod
import time
from copy import deepcopy
import hashlib
from threading import Lock
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 可选依赖
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False

try:
    from configparser import ConfigParser
    INI_AVAILABLE = True
except ImportError:
    INI_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    from pydantic import BaseModel, ValidationError, validator
    from pydantic.fields import Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """配置错误"""
    pass

class ConfigValidationError(ConfigError):
    """配置验证错误"""
    pass

class ConfigNotFoundError(ConfigError):
    """配置文件未找到错误"""
    pass

@dataclass
class ConfigMetadata:
    """配置元数据"""
    source: str  # 配置来源（文件路径、环境变量等）
    format: str  # 配置格式（json、yaml、toml、ini）
    last_modified: datetime = field(default_factory=datetime.now)
    checksum: str = ""
    encrypted: bool = False
    
    def update_checksum(self, content: str):
        """更新校验和"""
        self.checksum = hashlib.md5(content.encode()).hexdigest()
        self.last_modified = datetime.now()

class ConfigLoader(ABC):
    """配置加载器基类"""
    
    @abstractmethod
    def load(self, source: str) -> Dict[str, Any]:
        """加载配置"""
        pass
    
    @abstractmethod
    def save(self, data: Dict[str, Any], target: str):
        """保存配置"""
        pass
    
    @abstractmethod
    def supports_format(self, format_name: str) -> bool:
        """是否支持指定格式"""
        pass

class JSONConfigLoader(ConfigLoader):
    """JSON配置加载器"""
    
    def load(self, source: str) -> Dict[str, Any]:
        """加载JSON配置"""
        try:
            if os.path.isfile(source):
                with open(source, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 尝试解析为JSON字符串
                return json.loads(source)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ConfigError(f"JSON配置加载失败: {e}")
    
    def save(self, data: Dict[str, Any], target: str):
        """保存JSON配置"""
        try:
            with open(target, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigError(f"JSON配置保存失败: {e}")
    
    def supports_format(self, format_name: str) -> bool:
        """是否支持JSON格式"""
        return format_name.lower() in ['json']

class YAMLConfigLoader(ConfigLoader):
    """YAML配置加载器"""
    
    def __init__(self):
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML库未安装，请运行: pip install PyYAML")
    
    def load(self, source: str) -> Dict[str, Any]:
        """加载YAML配置"""
        try:
            if os.path.isfile(source):
                with open(source, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                # 尝试解析为YAML字符串
                return yaml.safe_load(source) or {}
        except (yaml.YAMLError, FileNotFoundError) as e:
            raise ConfigError(f"YAML配置加载失败: {e}")
    
    def save(self, data: Dict[str, Any], target: str):
        """保存YAML配置"""
        try:
            with open(target, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise ConfigError(f"YAML配置保存失败: {e}")
    
    def supports_format(self, format_name: str) -> bool:
        """是否支持YAML格式"""
        return format_name.lower() in ['yaml', 'yml']

class TOMLConfigLoader(ConfigLoader):
    """TOML配置加载器"""
    
    def __init__(self):
        if not TOML_AVAILABLE:
            raise ImportError("toml库未安装，请运行: pip install toml")
    
    def load(self, source: str) -> Dict[str, Any]:
        """加载TOML配置"""
        try:
            if os.path.isfile(source):
                with open(source, 'r', encoding='utf-8') as f:
                    return toml.load(f)
            else:
                # 尝试解析为TOML字符串
                return toml.loads(source)
        except (toml.TomlDecodeError, FileNotFoundError) as e:
            raise ConfigError(f"TOML配置加载失败: {e}")
    
    def save(self, data: Dict[str, Any], target: str):
        """保存TOML配置"""
        try:
            with open(target, 'w', encoding='utf-8') as f:
                toml.dump(data, f)
        except Exception as e:
            raise ConfigError(f"TOML配置保存失败: {e}")
    
    def supports_format(self, format_name: str) -> bool:
        """是否支持TOML格式"""
        return format_name.lower() in ['toml']

class INIConfigLoader(ConfigLoader):
    """INI配置加载器"""
    
    def __init__(self):
        if not INI_AVAILABLE:
            raise ImportError("configparser库不可用")
    
    def load(self, source: str) -> Dict[str, Any]:
        """加载INI配置"""
        try:
            parser = ConfigParser()
            
            if os.path.isfile(source):
                parser.read(source, encoding='utf-8')
            else:
                # 尝试解析为INI字符串
                parser.read_string(source)
            
            # 转换为嵌套字典
            result = {}
            for section_name in parser.sections():
                result[section_name] = dict(parser[section_name])
            
            return result
            
        except Exception as e:
            raise ConfigError(f"INI配置加载失败: {e}")
    
    def save(self, data: Dict[str, Any], target: str):
        """保存INI配置"""
        try:
            parser = ConfigParser()
            
            # 转换嵌套字典为INI格式
            for section_name, section_data in data.items():
                if isinstance(section_data, dict):
                    parser.add_section(section_name)
                    for key, value in section_data.items():
                        parser.set(section_name, key, str(value))
            
            with open(target, 'w', encoding='utf-8') as f:
                parser.write(f)
                
        except Exception as e:
            raise ConfigError(f"INI配置保存失败: {e}")
    
    def supports_format(self, format_name: str) -> bool:
        """是否支持INI格式"""
        return format_name.lower() in ['ini', 'cfg']

class ConfigEncryption:
    """配置加密工具"""
    
    def __init__(self, key: Optional[bytes] = None):
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography库未安装，请运行: pip install cryptography")
        
        if key is None:
            key = Fernet.generate_key()
        
        self.fernet = Fernet(key)
        self.key = key
    
    def encrypt(self, data: str) -> bytes:
        """加密数据"""
        return self.fernet.encrypt(data.encode())
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """解密数据"""
        return self.fernet.decrypt(encrypted_data).decode()
    
    def encrypt_config(self, config_data: Dict[str, Any]) -> bytes:
        """加密配置数据"""
        json_str = json.dumps(config_data, ensure_ascii=False)
        return self.encrypt(json_str)
    
    def decrypt_config(self, encrypted_data: bytes) -> Dict[str, Any]:
        """解密配置数据"""
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str)
    
    @staticmethod
    def generate_key() -> bytes:
        """生成新的加密密钥"""
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography库未安装，请运行: pip install cryptography")
        return Fernet.generate_key()

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.validators: Dict[str, Callable] = {}
        self.type_converters: Dict[str, Callable] = {
            'int': int,
            'float': float,
            'bool': self._convert_bool,
            'str': str,
            'list': self._convert_list,
            'dict': dict
        }
    
    def _convert_bool(self, value: Any) -> bool:
        """转换布尔值"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def _convert_list(self, value: Any) -> List[Any]:
        """转换列表"""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            # 尝试解析逗号分隔的字符串
            return [item.strip() for item in value.split(',') if item.strip()]
        return [value]
    
    def add_validator(self, path: str, validator: Callable[[Any], bool]):
        """添加验证器"""
        self.validators[path] = validator
    
    def validate(self, config: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """验证配置"""
        validated_config = deepcopy(config)
        
        if schema:
            validated_config = self._validate_with_schema(validated_config, schema)
        
        # 应用自定义验证器
        for path, validator in self.validators.items():
            value = self._get_nested_value(validated_config, path)
            if value is not None and not validator(value):
                raise ConfigValidationError(f"配置项 '{path}' 验证失败")
        
        return validated_config
    
    def _validate_with_schema(self, config: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """使用模式验证配置"""
        validated = {}
        
        for key, schema_item in schema.items():
            if key in config:
                value = config[key]
                
                # 类型转换
                if 'type' in schema_item:
                    expected_type = schema_item['type']
                    if expected_type in self.type_converters:
                        try:
                            value = self.type_converters[expected_type](value)
                        except (ValueError, TypeError) as e:
                            raise ConfigValidationError(f"配置项 '{key}' 类型转换失败: {e}")
                
                # 值验证
                if 'choices' in schema_item:
                    if value not in schema_item['choices']:
                        raise ConfigValidationError(f"配置项 '{key}' 值必须在 {schema_item['choices']} 中")
                
                if 'min' in schema_item and value < schema_item['min']:
                    raise ConfigValidationError(f"配置项 '{key}' 值不能小于 {schema_item['min']}")
                
                if 'max' in schema_item and value > schema_item['max']:
                    raise ConfigValidationError(f"配置项 '{key}' 值不能大于 {schema_item['max']}")
                
                if 'pattern' in schema_item:
                    import re
                    if not re.match(schema_item['pattern'], str(value)):
                        raise ConfigValidationError(f"配置项 '{key}' 值不匹配模式 {schema_item['pattern']}")
                
                validated[key] = value
                
            elif schema_item.get('required', False):
                if 'default' in schema_item:
                    validated[key] = schema_item['default']
                else:
                    raise ConfigValidationError(f"必需的配置项 '{key}' 缺失")
        
        return validated
    
    def _get_nested_value(self, config: Dict[str, Any], path: str) -> Any:
        """获取嵌套配置值"""
        keys = path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value

class ConfigWatcher(FileSystemEventHandler):
    """配置文件监控器"""
    
    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        self.last_reload = {}
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # 防止重复触发
        now = time.time()
        if file_path in self.last_reload and now - self.last_reload[file_path] < 1.0:
            return
        
        self.last_reload[file_path] = now
        
        # 检查是否是被监控的配置文件
        for config_name, metadata in self.config_manager._metadata.items():
            if metadata.source == file_path:
                try:
                    logger.info(f"检测到配置文件变化，重新加载: {file_path}")
                    self.config_manager.reload_config(config_name)
                except Exception as e:
                    logger.error(f"重新加载配置失败: {e}")
                break

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.configs: Dict[str, Dict[str, Any]] = {}
        self._metadata: Dict[str, ConfigMetadata] = {}
        self._loaders: List[ConfigLoader] = []
        self._validator = ConfigValidator()
        self._encryption: Optional[ConfigEncryption] = None
        self._cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, float] = {}
        self._lock = Lock()
        self._observer: Optional[Observer] = None
        self._watcher: Optional[ConfigWatcher] = None
        self._watch_enabled = False
        
        # 注册默认加载器
        self._register_default_loaders()
    
    def _register_default_loaders(self):
        """注册默认配置加载器"""
        self._loaders.append(JSONConfigLoader())
        
        if YAML_AVAILABLE:
            self._loaders.append(YAMLConfigLoader())
        
        if TOML_AVAILABLE:
            self._loaders.append(TOMLConfigLoader())
        
        if INI_AVAILABLE:
            self._loaders.append(INIConfigLoader())
    
    def add_loader(self, loader: ConfigLoader):
        """添加配置加载器"""
        self._loaders.append(loader)
    
    def set_encryption(self, key: Optional[bytes] = None):
        """设置配置加密"""
        self._encryption = ConfigEncryption(key)
    
    def enable_file_watching(self):
        """启用文件监控"""
        if self._watch_enabled:
            return
        
        self._watcher = ConfigWatcher(self)
        self._observer = Observer()
        self._watch_enabled = True
        
        # 监控已加载的配置文件
        watched_dirs = set()
        for metadata in self._metadata.values():
            if os.path.isfile(metadata.source):
                dir_path = os.path.dirname(metadata.source)
                if dir_path not in watched_dirs:
                    self._observer.schedule(self._watcher, dir_path, recursive=False)
                    watched_dirs.add(dir_path)
        
        self._observer.start()
        logger.info("配置文件监控已启用")
    
    def disable_file_watching(self):
        """禁用文件监控"""
        if not self._watch_enabled:
            return
        
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
        
        self._watcher = None
        self._watch_enabled = False
        logger.info("配置文件监控已禁用")
    
    def _get_loader(self, format_name: str) -> ConfigLoader:
        """获取配置加载器"""
        for loader in self._loaders:
            if loader.supports_format(format_name):
                return loader
        
        raise ConfigError(f"不支持的配置格式: {format_name}")
    
    def _detect_format(self, file_path: str) -> str:
        """检测配置文件格式"""
        ext = Path(file_path).suffix.lower()
        
        format_map = {
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.cfg': 'ini'
        }
        
        return format_map.get(ext, 'json')
    
    def load_config(self, name: str, source: str, format_name: Optional[str] = None, 
                   encrypted: bool = False, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """加载配置"""
        with self._lock:
            try:
                # 检测格式
                if format_name is None:
                    if os.path.isfile(source):
                        format_name = self._detect_format(source)
                    else:
                        format_name = 'json'  # 默认JSON格式
                
                # 获取加载器
                loader = self._get_loader(format_name)
                
                # 加载配置数据
                if encrypted and self._encryption:
                    # 加载加密配置
                    with open(source, 'rb') as f:
                        encrypted_data = f.read()
                    config_data = self._encryption.decrypt_config(encrypted_data)
                else:
                    # 加载普通配置
                    config_data = loader.load(source)
                
                # 环境变量覆盖
                config_data = self._apply_env_overrides(config_data, name)
                
                # 配置验证
                if schema or self._validator.validators:
                    config_data = self._validator.validate(config_data, schema)
                
                # 存储配置
                self.configs[name] = config_data
                
                # 创建元数据
                metadata = ConfigMetadata(
                    source=source,
                    format=format_name,
                    encrypted=encrypted
                )
                
                if os.path.isfile(source):
                    with open(source, 'r', encoding='utf-8') as f:
                        content = f.read()
                    metadata.update_checksum(content)
                
                self._metadata[name] = metadata
                
                # 添加文件监控
                if self._watch_enabled and os.path.isfile(source):
                    dir_path = os.path.dirname(source)
                    if self._observer:
                        self._observer.schedule(self._watcher, dir_path, recursive=False)
                
                logger.info(f"配置 '{name}' 加载成功: {source}")
                return config_data
                
            except Exception as e:
                logger.error(f"配置 '{name}' 加载失败: {e}")
                raise ConfigError(f"配置加载失败: {e}")
    
    def _apply_env_overrides(self, config: Dict[str, Any], config_name: str) -> Dict[str, Any]:
        """应用环境变量覆盖"""
        result = deepcopy(config)
        prefix = f"{config_name.upper()}_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # 移除前缀并转换为小写
                config_key = key[len(prefix):].lower()
                
                # 支持嵌套键（用双下划线分隔）
                if '__' in config_key:
                    keys = config_key.split('__')
                    self._set_nested_value(result, keys, value)
                else:
                    result[config_key] = value
        
        return result
    
    def _set_nested_value(self, config: Dict[str, Any], keys: List[str], value: str):
        """设置嵌套配置值"""
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def save_config(self, name: str, target: Optional[str] = None, encrypted: bool = False):
        """保存配置"""
        if name not in self.configs:
            raise ConfigError(f"配置 '{name}' 不存在")
        
        config_data = self.configs[name]
        metadata = self._metadata.get(name)
        
        if target is None:
            if metadata:
                target = metadata.source
            else:
                raise ConfigError(f"配置 '{name}' 没有指定保存目标")
        
        try:
            if encrypted and self._encryption:
                # 保存加密配置
                encrypted_data = self._encryption.encrypt_config(config_data)
                with open(target, 'wb') as f:
                    f.write(encrypted_data)
            else:
                # 保存普通配置
                format_name = metadata.format if metadata else self._detect_format(target)
                loader = self._get_loader(format_name)
                loader.save(config_data, target)
            
            logger.info(f"配置 '{name}' 保存成功: {target}")
            
        except Exception as e:
            logger.error(f"配置 '{name}' 保存失败: {e}")
            raise ConfigError(f"配置保存失败: {e}")
    
    def reload_config(self, name: str):
        """重新加载配置"""
        if name not in self._metadata:
            raise ConfigError(f"配置 '{name}' 不存在")
        
        metadata = self._metadata[name]
        
        # 检查文件是否变化
        if os.path.isfile(metadata.source):
            with open(metadata.source, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_checksum = hashlib.md5(content.encode()).hexdigest()
            if new_checksum == metadata.checksum:
                logger.debug(f"配置文件 '{name}' 未变化，跳过重新加载")
                return
        
        # 重新加载
        self.load_config(
            name=name,
            source=metadata.source,
            format_name=metadata.format,
            encrypted=metadata.encrypted
        )
        
        # 清除缓存
        self._clear_cache(name)
        
        logger.info(f"配置 '{name}' 重新加载完成")
    
    def get_config(self, name: str, use_cache: bool = True, cache_ttl: int = 300) -> Dict[str, Any]:
        """获取配置"""
        if use_cache:
            cache_key = f"config_{name}"
            
            # 检查缓存
            if cache_key in self._cache:
                if cache_key in self._cache_ttl and time.time() < self._cache_ttl[cache_key]:
                    return self._cache[cache_key]
            
            # 更新缓存
            if name in self.configs:
                config_data = deepcopy(self.configs[name])
                self._cache[cache_key] = config_data
                self._cache_ttl[cache_key] = time.time() + cache_ttl
                return config_data
        
        if name not in self.configs:
            raise ConfigError(f"配置 '{name}' 不存在")
        
        return deepcopy(self.configs[name])
    
    def get_value(self, config_name: str, key_path: str, default: Any = None, use_cache: bool = True) -> Any:
        """获取配置值"""
        config = self.get_config(config_name, use_cache)
        
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set_value(self, config_name: str, key_path: str, value: Any):
        """设置配置值"""
        if config_name not in self.configs:
            raise ConfigError(f"配置 '{config_name}' 不存在")
        
        keys = key_path.split('.')
        config = self.configs[config_name]
        current = config
        
        # 导航到目标位置
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 设置值
        current[keys[-1]] = value
        
        # 清除缓存
        self._clear_cache(config_name)
        
        logger.debug(f"配置值已更新: {config_name}.{key_path} = {value}")
    
    def merge_configs(self, target_name: str, *source_names: str):
        """合并配置"""
        if target_name not in self.configs:
            self.configs[target_name] = {}
        
        target_config = self.configs[target_name]
        
        for source_name in source_names:
            if source_name not in self.configs:
                logger.warning(f"源配置 '{source_name}' 不存在，跳过合并")
                continue
            
            source_config = self.configs[source_name]
            self._deep_merge(target_config, source_config)
        
        # 清除缓存
        self._clear_cache(target_name)
        
        logger.info(f"配置合并完成: {target_name} <- {', '.join(source_names)}")
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """深度合并字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = deepcopy(value)
    
    def create_config_template(self, name: str, template: Dict[str, Any]):
        """创建配置模板"""
        self.configs[name] = deepcopy(template)
        
        # 创建模板元数据
        metadata = ConfigMetadata(
            source=f"template:{name}",
            format="json"
        )
        self._metadata[name] = metadata
        
        logger.info(f"配置模板 '{name}' 创建成功")
    
    def list_configs(self) -> List[str]:
        """列出所有配置名称"""
        return list(self.configs.keys())
    
    def get_config_info(self, name: str) -> Optional[ConfigMetadata]:
        """获取配置信息"""
        return self._metadata.get(name)
    
    def remove_config(self, name: str):
        """移除配置"""
        if name in self.configs:
            del self.configs[name]
        
        if name in self._metadata:
            del self._metadata[name]
        
        self._clear_cache(name)
        
        logger.info(f"配置 '{name}' 已移除")
    
    def _clear_cache(self, config_name: str = None):
        """清除缓存"""
        if config_name:
            cache_key = f"config_{config_name}"
            if cache_key in self._cache:
                del self._cache[cache_key]
            if cache_key in self._cache_ttl:
                del self._cache_ttl[cache_key]
        else:
            self._cache.clear()
            self._cache_ttl.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'total_configs': len(self.configs),
            'cached_items': len(self._cache),
            'watch_enabled': self._watch_enabled,
            'encryption_enabled': self._encryption is not None,
            'supported_formats': [loader.__class__.__name__ for loader in self._loaders],
            'configs': {
                name: {
                    'source': metadata.source,
                    'format': metadata.format,
                    'last_modified': metadata.last_modified.isoformat(),
                    'encrypted': metadata.encrypted
                }
                for name, metadata in self._metadata.items()
            }
        }
    
    def cleanup(self):
        """清理资源"""
        self.disable_file_watching()
        self._clear_cache()
        self.configs.clear()
        self._metadata.clear()
        logger.info("配置管理器已清理")

# 全局配置管理器实例
_config_manager = ConfigManager()

# 便捷函数
def get_config_manager() -> ConfigManager:
    """获取配置管理器"""
    return _config_manager

def load_config(name: str, source: str, format_name: Optional[str] = None, 
               encrypted: bool = False, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """加载配置"""
    return _config_manager.load_config(name, source, format_name, encrypted, schema)

def get_config(name: str, use_cache: bool = True) -> Dict[str, Any]:
    """获取配置"""
    return _config_manager.get_config(name, use_cache)

def get_value(config_name: str, key_path: str, default: Any = None) -> Any:
    """获取配置值"""
    return _config_manager.get_value(config_name, key_path, default)

def set_value(config_name: str, key_path: str, value: Any):
    """设置配置值"""
    _config_manager.set_value(config_name, key_path, value)

def enable_file_watching():
    """启用文件监控"""
    _config_manager.enable_file_watching()

def set_encryption_key(key: Optional[bytes] = None):
    """设置加密密钥"""
    _config_manager.set_encryption(key)

# 配置装饰器
def config_required(config_name: str, key_path: Optional[str] = None):
    """配置必需装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                if key_path:
                    value = get_value(config_name, key_path)
                    if value is None:
                        raise ConfigError(f"必需的配置项 '{config_name}.{key_path}' 缺失")
                else:
                    get_config(config_name)
                
                return func(*args, **kwargs)
            except ConfigError as e:
                logger.error(f"配置检查失败: {e}")
                raise
        
        return wrapper
    return decorator

# 示例配置模式
DEFAULT_AI_ENGINE_SCHEMA = {
    'database': {
        'type': 'str',
        'required': True,
        'choices': ['sqlite', 'postgresql', 'mysql', 'mongodb'],
        'default': 'sqlite'
    },
    'redis': {
        'type': 'dict',
        'required': False,
        'default': {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        }
    },
    'logging': {
        'type': 'dict',
        'required': False,
        'default': {
            'level': 'INFO',
            'format': 'structured'
        }
    },
    'ai_models': {
        'type': 'dict',
        'required': False,
        'default': {
            'anomaly_detection': {
                'algorithm': 'isolation_forest',
                'threshold': 0.1
            },
            'prediction': {
                'algorithm': 'lstm',
                'window_size': 100
            }
        }
    }
}