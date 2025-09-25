# API 文档

服务器热控制系统 RESTful API 完整文档。

## 基础信息

- **Base URL**: `http://localhost:8081` (默认端口)
- **API Version**: v1
- **Content-Type**: `application/json`
- **Authentication**: 暂未实现（计划中）

## 响应格式

所有API响应都遵循统一的格式：

### 成功响应
```json
{
  "success": true,
  "message": "操作成功描述",
  "data": {
    // 具体数据内容
  }
}
```

### 错误响应
```json
{
  "success": false,
  "error": "错误类型",
  "message": "错误详细描述",
  "code": 400
}
```

## API 端点

### 1. 基础信息端点

#### 1.1 获取服务信息
```http
GET /
```

**响应示例**:
```json
{
  "name": "Server Thermal Control System",
  "status": "running",
  "version": "0.1.0"
}
```

#### 1.2 获取版本信息
```http
GET /version
```

**响应示例**:
```json
{
  "version": "0.1.0",
  "build_date": "2025-09-25",
  "git_commit": "abc123"
}
```

#### 1.3 获取API信息
```http
GET /api
```

**响应示例**:
```json
{
  "api_version": "v1",
  "endpoints": [
    "/api/v1/health",
    "/api/v1/temperature",
    "/api/v1/fans"
  ]
}
```

### 2. 健康检查端点

#### 2.1 服务健康检查
```http
GET /api/v1/health
```

**响应示例**:
```json
{
  "service": "thermal-control-server",
  "status": "ok",
  "timestamp": "2025-09-25T10:31:29.863339800+00:00"
}
```

#### 2.2 系统信息
```http
GET /api/v1/system/info
```

**响应示例**:
```json
{
  "success": true,
  "message": "System information retrieved successfully",
  "data": {
    "service_name": "Thermal Control Server",
    "cpu_cores": 28,
    "uptime": "running...",
    "timestamp": "2025-09-25T10:31:41.877996400+00:00"
  }
}
```

#### 2.3 系统健康详情
```http
GET /api/v1/system/health
```

**响应示例**:
```json
{
  "success": true,
  "message": "System health check completed",
  "data": {
    "overall_status": "healthy",
    "components": {
      "database": "connected",
      "redis": "connected",
      "sensors": "active",
      "fans": "operational"
    },
    "timestamp": "2025-09-25T10:32:00.000000000+00:00"
  }
}
```

### 3. 温度监控端点

#### 3.1 获取所有温度数据
```http
GET /api/v1/temperature
```

**查询参数**:
- `limit` (可选): 返回记录数量限制，默认100
- `offset` (可选): 偏移量，默认0
- `sensor_id` (可选): 过滤特定传感器

**响应示例**:
```json
{
  "success": true,
  "message": "Temperature data retrieved successfully",
  "data": {
    "data": [
      {
        "id": "9d9ebc8f-a496-41c1-91ea-98fc276de7d2",
        "sensor_id": "CPU_TEMP_1",
        "temperature": 65.5,
        "unit": "°C",
        "location": "CPU Socket 1",
        "status": "normal",
        "timestamp": "2025-09-25T10:30:00.000000000+00:00"
      },
      {
        "id": "7f8e9c2a-b123-4567-8901-234567890abc",
        "sensor_id": "GPU_TEMP_1",
        "temperature": 72.3,
        "unit": "°C",
        "location": "Graphics Card",
        "status": "normal",
        "timestamp": "2025-09-25T10:30:00.000000000+00:00"
      }
    ],
    "total": 2,
    "limit": 100,
    "offset": 0
  }
}
```

#### 3.2 获取指定传感器温度
```http
GET /api/v1/temperature/{sensor_id}
```

**路径参数**:
- `sensor_id`: 传感器ID

**响应示例**:
```json
{
  "success": true,
  "message": "Temperature data for sensor CPU_TEMP_1 retrieved successfully",
  "data": {
    "id": "9d9ebc8f-a496-41c1-91ea-98fc276de7d2",
    "sensor_id": "CPU_TEMP_1",
    "temperature": 65.5,
    "unit": "°C",
    "location": "CPU Socket 1",
    "status": "normal",
    "timestamp": "2025-09-25T10:30:00.000000000+00:00",
    "history": [
      {
        "temperature": 64.2,
        "timestamp": "2025-09-25T10:29:00.000000000+00:00"
      },
      {
        "temperature": 63.8,
        "timestamp": "2025-09-25T10:28:00.000000000+00:00"
      }
    ]
  }
}
```

#### 3.3 温度统计信息
```http
GET /api/v1/stats/temperature
```

**查询参数**:
- `period` (可选): 统计周期 (hour, day, week, month)，默认hour
- `sensor_id` (可选): 特定传感器统计

**响应示例**:
```json
{
  "success": true,
  "message": "Temperature statistics retrieved successfully",
  "data": {
    "period": "hour",
    "statistics": {
      "average_temp": 67.2,
      "max_temp": 75.8,
      "min_temp": 58.4,
      "sensor_count": 8,
      "readings_count": 1440
    },
    "sensors": [
      {
        "sensor_id": "CPU_TEMP_1",
        "average": 65.5,
        "max": 72.1,
        "min": 58.9
      },
      {
        "sensor_id": "GPU_TEMP_1",
        "average": 69.8,
        "max": 75.8,
        "min": 62.3
      }
    ],
    "timestamp": "2025-09-25T10:32:00.000000000+00:00"
  }
}
```

### 4. 风扇控制端点

#### 4.1 获取所有风扇数据
```http
GET /api/v1/fans
```

**响应示例**:
```json
{
  "success": true,
  "message": "Fan data retrieved successfully",
  "data": {
    "data": [
      {
        "id": "44ac74e6-57c4-4993-9d55-4c521f808274",
        "fan_id": "CPU_FAN_1",
        "speed_rpm": 1800,
        "speed_percent": 75,
        "status": "normal",
        "location": "CPU Cooler",
        "control_mode": "auto",
        "target_temp": 65.0,
        "timestamp": "2025-09-25T10:32:00.000000000+00:00"
      },
      {
        "id": "55bd85f7-68d5-5aa4-a066-5d632f919385",
        "fan_id": "CASE_FAN_1",
        "speed_rpm": 1200,
        "speed_percent": 50,
        "status": "normal",
        "location": "Front Intake",
        "control_mode": "manual",
        "target_temp": null,
        "timestamp": "2025-09-25T10:32:00.000000000+00:00"
      }
    ],
    "total": 2
  }
}
```

#### 4.2 获取指定风扇数据
```http
GET /api/v1/fans/{fan_id}
```

**路径参数**:
- `fan_id`: 风扇ID

**响应示例**:
```json
{
  "success": true,
  "message": "Fan data for CPU_FAN_1 retrieved successfully",
  "data": {
    "id": "44ac74e6-57c4-4993-9d55-4c521f808274",
    "fan_id": "CPU_FAN_1",
    "speed_rpm": 1800,
    "speed_percent": 75,
    "status": "normal",
    "location": "CPU Cooler",
    "control_mode": "auto",
    "target_temp": 65.0,
    "timestamp": "2025-09-25T10:32:00.000000000+00:00",
    "history": [
      {
        "speed_rpm": 1750,
        "speed_percent": 73,
        "timestamp": "2025-09-25T10:31:00.000000000+00:00"
      }
    ]
  }
}
```

#### 4.3 设置风扇转速
```http
POST /api/v1/fans/{fan_id}/speed
```

**路径参数**:
- `fan_id`: 风扇ID

**请求体**:
```json
{
  "speed_percent": 80,
  "control_mode": "manual"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Fan speed updated successfully",
  "data": {
    "fan_id": "CPU_FAN_1",
    "old_speed_percent": 75,
    "new_speed_percent": 80,
    "control_mode": "manual",
    "timestamp": "2025-09-25T10:33:00.000000000+00:00"
  }
}
```

#### 4.4 设置风扇控制模式
```http
POST /api/v1/fans/{fan_id}/mode
```

**路径参数**:
- `fan_id`: 风扇ID

**请求体**:
```json
{
  "control_mode": "auto",
  "target_temp": 65.0
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Fan control mode updated successfully",
  "data": {
    "fan_id": "CPU_FAN_1",
    "control_mode": "auto",
    "target_temp": 65.0,
    "timestamp": "2025-09-25T10:34:00.000000000+00:00"
  }
}
```

#### 4.5 风扇统计信息
```http
GET /api/v1/stats/fan
```

**响应示例**:
```json
{
  "success": true,
  "message": "Fan statistics retrieved successfully",
  "data": {
    "total_fans": 4,
    "active_fans": 4,
    "average_speed_rpm": 1650,
    "average_speed_percent": 69,
    "control_modes": {
      "auto": 3,
      "manual": 1
    },
    "status_distribution": {
      "normal": 4,
      "warning": 0,
      "error": 0
    },
    "timestamp": "2025-09-25T10:35:00.000000000+00:00"
  }
}
```

### 5. 告警管理端点

#### 5.1 获取告警列表
```http
GET /api/v1/alerts
```

**查询参数**:
- `status` (可选): 告警状态 (active, acknowledged, resolved)
- `severity` (可选): 告警级别 (low, medium, high, critical)
- `limit` (可选): 返回记录数量限制，默认50
- `offset` (可选): 偏移量，默认0

**响应示例**:
```json
{
  "success": true,
  "message": "Alerts retrieved successfully",
  "data": {
    "alerts": [
      {
        "id": "alert-001",
        "type": "temperature_high",
        "severity": "high",
        "status": "active",
        "message": "CPU temperature exceeded threshold",
        "details": {
          "sensor_id": "CPU_TEMP_1",
          "current_temp": 85.2,
          "threshold": 80.0,
          "location": "CPU Socket 1"
        },
        "created_at": "2025-09-25T10:30:00.000000000+00:00",
        "updated_at": "2025-09-25T10:30:00.000000000+00:00"
      }
    ],
    "total": 1,
    "active_count": 1,
    "acknowledged_count": 0,
    "resolved_count": 0
  }
}
```

#### 5.2 确认告警
```http
POST /api/v1/alerts/{alert_id}/acknowledge
```

**路径参数**:
- `alert_id`: 告警ID

**请求体**:
```json
{
  "acknowledged_by": "admin",
  "note": "正在处理中"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Alert acknowledged successfully",
  "data": {
    "alert_id": "alert-001",
    "status": "acknowledged",
    "acknowledged_by": "admin",
    "acknowledged_at": "2025-09-25T10:35:00.000000000+00:00",
    "note": "正在处理中"
  }
}
```

#### 5.3 解决告警
```http
POST /api/v1/alerts/{alert_id}/resolve
```

**路径参数**:
- `alert_id`: 告警ID

**请求体**:
```json
{
  "resolved_by": "admin",
  "resolution_note": "温度已恢复正常"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Alert resolved successfully",
  "data": {
    "alert_id": "alert-001",
    "status": "resolved",
    "resolved_by": "admin",
    "resolved_at": "2025-09-25T10:40:00.000000000+00:00",
    "resolution_note": "温度已恢复正常"
  }
}
```

### 6. 配置管理端点

#### 6.1 获取系统配置
```http
GET /api/v1/config
```

**响应示例**:
```json
{
  "success": true,
  "message": "Configuration retrieved successfully",
  "data": {
    "monitoring": {
      "enabled": true,
      "interval": 30,
      "alert_threshold_temp": 80.0
    },
    "control": {
      "enabled": true,
      "mode": "auto",
      "temp_target": 65.0
    },
    "alert": {
      "enabled": true,
      "email_enabled": false,
      "webhook_enabled": false
    }
  }
}
```

#### 6.2 更新系统配置
```http
PUT /api/v1/config
```

**请求体**:
```json
{
  "monitoring": {
    "interval": 60,
    "alert_threshold_temp": 85.0
  },
  "control": {
    "temp_target": 70.0
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "data": {
    "updated_fields": [
      "monitoring.interval",
      "monitoring.alert_threshold_temp",
      "control.temp_target"
    ],
    "timestamp": "2025-09-25T10:45:00.000000000+00:00"
  }
}
```

## 错误代码

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未授权访问 |
| 403 | Forbidden | 禁止访问 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 请求数据验证失败 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务不可用 |

## 使用示例

### cURL 示例

```bash
# 获取服务健康状态
curl -X GET http://localhost:8081/api/v1/health

# 获取温度数据
curl -X GET http://localhost:8081/api/v1/temperature

# 设置风扇转速
curl -X POST http://localhost:8081/api/v1/fans/CPU_FAN_1/speed \
  -H "Content-Type: application/json" \
  -d '{"speed_percent": 80, "control_mode": "manual"}'

# 确认告警
curl -X POST http://localhost:8081/api/v1/alerts/alert-001/acknowledge \
  -H "Content-Type: application/json" \
  -d '{"acknowledged_by": "admin", "note": "正在处理中"}'
```

### JavaScript 示例

```javascript
// 获取温度数据
async function getTemperatureData() {
  try {
    const response = await fetch('http://localhost:8081/api/v1/temperature');
    const data = await response.json();
    console.log('Temperature data:', data);
  } catch (error) {
    console.error('Error fetching temperature data:', error);
  }
}

// 设置风扇转速
async function setFanSpeed(fanId, speedPercent) {
  try {
    const response = await fetch(`http://localhost:8081/api/v1/fans/${fanId}/speed`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        speed_percent: speedPercent,
        control_mode: 'manual'
      })
    });
    const data = await response.json();
    console.log('Fan speed updated:', data);
  } catch (error) {
    console.error('Error setting fan speed:', error);
  }
}
```

### Python 示例

```python
import requests
import json

# 基础URL
BASE_URL = "http://localhost:8081"

def get_system_info():
    """获取系统信息"""
    response = requests.get(f"{BASE_URL}/api/v1/system/info")
    return response.json()

def get_temperature_data():
    """获取温度数据"""
    response = requests.get(f"{BASE_URL}/api/v1/temperature")
    return response.json()

def set_fan_speed(fan_id, speed_percent):
    """设置风扇转速"""
    data = {
        "speed_percent": speed_percent,
        "control_mode": "manual"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/fans/{fan_id}/speed",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 获取系统信息
    system_info = get_system_info()
    print("System Info:", system_info)
    
    # 获取温度数据
    temp_data = get_temperature_data()
    print("Temperature Data:", temp_data)
    
    # 设置风扇转速
    result = set_fan_speed("CPU_FAN_1", 80)
    print("Fan Speed Result:", result)
```

## 版本历史

### v1.0 (当前版本)
- 基础温度监控API
- 风扇控制API
- 告警管理API
- 系统健康检查API
- 配置管理API

## 支持

如有问题或建议，请通过以下方式联系：

- GitHub Issues: [项目Issues页面]
- 邮箱: [support@example.com]
- 文档: [在线文档地址]