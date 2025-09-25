-- 服务器热控制系统数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- 温度数据表
CREATE TABLE IF NOT EXISTS temperature_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id VARCHAR(50) NOT NULL,
    sensor_name VARCHAR(100),
    temperature DECIMAL(5,2) NOT NULL,
    unit VARCHAR(10) DEFAULT 'C',
    location VARCHAR(100),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 风扇数据表
CREATE TABLE IF NOT EXISTS fan_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fan_id VARCHAR(50) NOT NULL,
    fan_name VARCHAR(100),
    speed_rpm INTEGER NOT NULL,
    speed_percent DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'normal',
    location VARCHAR(100),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 传感器数据表
CREATE TABLE IF NOT EXISTS sensor_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id VARCHAR(50) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    sensor_name VARCHAR(100),
    value DECIMAL(10,4) NOT NULL,
    unit VARCHAR(20),
    status VARCHAR(20) DEFAULT 'normal',
    location VARCHAR(100),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 控制历史表
CREATE TABLE IF NOT EXISTS control_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_type VARCHAR(50) NOT NULL,
    target_id VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    old_value DECIMAL(10,4),
    new_value DECIMAL(10,4) NOT NULL,
    reason TEXT,
    algorithm VARCHAR(50),
    success BOOLEAN NOT NULL DEFAULT true,
    error_message TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 告警记录表
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    source VARCHAR(100),
    source_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ,
    resolved BOOLEAN DEFAULT false,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 配置表
CREATE TABLE IF NOT EXISTS configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    description TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    created_by VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 监控指标表
CREATE TABLE IF NOT EXISTS monitoring_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    value DECIMAL(15,6) NOT NULL,
    unit VARCHAR(20),
    tags JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 分析结果表
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_type VARCHAR(50) NOT NULL,
    target_id VARCHAR(50),
    target_type VARCHAR(50),
    result JSONB NOT NULL,
    confidence DECIMAL(5,4),
    metadata JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 系统事件表
CREATE TABLE IF NOT EXISTS system_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    event_category VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity VARCHAR(20) DEFAULT 'info',
    source VARCHAR(100),
    user_id VARCHAR(100),
    metadata JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_temperature_data_sensor_timestamp ON temperature_data(sensor_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_temperature_data_timestamp ON temperature_data(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_fan_data_fan_timestamp ON fan_data(fan_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_fan_data_timestamp ON fan_data(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_sensor_data_sensor_timestamp ON sensor_data(sensor_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_data_type_timestamp ON sensor_data(sensor_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_control_history_target_timestamp ON control_history(target_id, target_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_control_history_timestamp ON control_history(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_status_created ON alerts(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_type_severity ON alerts(alert_type, severity);
CREATE INDEX IF NOT EXISTS idx_alerts_source ON alerts(source, source_id);

CREATE INDEX IF NOT EXISTS idx_configurations_key ON configurations(config_key);

CREATE INDEX IF NOT EXISTS idx_monitoring_metrics_name_timestamp ON monitoring_metrics(metric_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_monitoring_metrics_type_timestamp ON monitoring_metrics(metric_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_monitoring_metrics_timestamp ON monitoring_metrics(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_analysis_results_type_timestamp ON analysis_results(analysis_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_results_target ON analysis_results(target_id, target_type);

CREATE INDEX IF NOT EXISTS idx_system_events_type_timestamp ON system_events(event_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_events_category_timestamp ON system_events(event_category, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events(timestamp DESC);

-- 创建触发器函数用于更新updated_at字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建更新触发器
CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_configurations_updated_at BEFORE UPDATE ON configurations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入默认配置
INSERT INTO configurations (config_key, config_value, description, created_by) VALUES
('system.initialized', 'true', '系统初始化标志', 'system'),
('monitoring.enabled', 'true', '监控功能启用状态', 'system'),
('control.auto_enabled', 'true', '自动控制功能启用状态', 'system'),
('alerts.enabled', 'true', '告警功能启用状态', 'system')
ON CONFLICT (config_key) DO NOTHING;

-- 创建数据清理函数
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- 清理30天前的温度数据
    DELETE FROM temperature_data WHERE created_at < NOW() - INTERVAL '30 days';
    
    -- 清理30天前的风扇数据
    DELETE FROM fan_data WHERE created_at < NOW() - INTERVAL '30 days';
    
    -- 清理30天前的传感器数据
    DELETE FROM sensor_data WHERE created_at < NOW() - INTERVAL '30 days';
    
    -- 清理90天前的控制历史
    DELETE FROM control_history WHERE created_at < NOW() - INTERVAL '90 days';
    
    -- 清理90天前的已解决告警
    DELETE FROM alerts WHERE resolved = true AND resolved_at < NOW() - INTERVAL '90 days';
    
    -- 清理7天前的监控指标
    DELETE FROM monitoring_metrics WHERE created_at < NOW() - INTERVAL '7 days';
    
    -- 清理30天前的分析结果
    DELETE FROM analysis_results WHERE created_at < NOW() - INTERVAL '30 days';
    
    -- 清理90天前的系统事件
    DELETE FROM system_events WHERE created_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- 创建数据统计视图
CREATE OR REPLACE VIEW temperature_stats AS
SELECT 
    sensor_id,
    sensor_name,
    COUNT(*) as record_count,
    AVG(temperature) as avg_temperature,
    MIN(temperature) as min_temperature,
    MAX(temperature) as max_temperature,
    STDDEV(temperature) as std_temperature,
    MAX(timestamp) as last_update
FROM temperature_data 
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY sensor_id, sensor_name;

CREATE OR REPLACE VIEW fan_stats AS
SELECT 
    fan_id,
    fan_name,
    COUNT(*) as record_count,
    AVG(speed_rpm) as avg_speed_rpm,
    MIN(speed_rpm) as min_speed_rpm,
    MAX(speed_rpm) as max_speed_rpm,
    AVG(speed_percent) as avg_speed_percent,
    MAX(timestamp) as last_update
FROM fan_data 
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY fan_id, fan_name;

CREATE OR REPLACE VIEW alert_summary AS
SELECT 
    alert_type,
    severity,
    COUNT(*) as total_count,
    COUNT(*) FILTER (WHERE status = 'active') as active_count,
    COUNT(*) FILTER (WHERE acknowledged = true) as acknowledged_count,
    COUNT(*) FILTER (WHERE resolved = true) as resolved_count,
    MAX(created_at) as last_alert
FROM alerts 
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY alert_type, severity;

-- 授权
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO thermal_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO thermal_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO thermal_user;