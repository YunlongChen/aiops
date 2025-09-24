/**
 * 监控中心JavaScript功能
 * 包含子标签页切换、图表初始化和数据刷新功能
 */

// 监控中心子标签页切换功能
function initMonitoringSubtabs() {
    const subtabs = document.querySelectorAll('.monitoring-subtab');
    const contents = document.querySelectorAll('.subtab-content');
    
    subtabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // 移除所有活动状态
            subtabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            // 添加当前标签的活动状态
            tab.classList.add('active');
            const targetId = tab.getAttribute('data-target');
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

// 应用性能图表初始化
function initAppPerformanceChart() {
    const canvas = document.getElementById('app-performance-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // 模拟数据
    const data = {
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
        datasets: [
            {
                label: '响应时间 (ms)',
                data: [120, 135, 180, 125, 145, 130],
                borderColor: '#4a90e2',
                backgroundColor: 'rgba(74, 144, 226, 0.1)',
                tension: 0.4
            },
            {
                label: '吞吐量 (req/min)',
                data: [1200, 1100, 800, 1300, 1150, 1250],
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4,
                yAxisID: 'y1'
            }
        ]
    };
    
    // 绘制简单的折线图
    drawLineChart(ctx, data, canvas.width, canvas.height);
}

// 数据库查询性能图表
function initDbQueryChart() {
    const canvas = document.getElementById('db-query-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // 模拟数据
    const data = {
        labels: ['MySQL', 'Redis', 'MongoDB'],
        datasets: [{
            data: [1234, 567, 890],
            backgroundColor: ['#28a745', '#ffc107', '#17a2b8']
        }]
    };
    
    drawBarChart(ctx, data, canvas.width, canvas.height);
}

// 数据库连接池图表
function initDbConnectionChart() {
    const canvas = document.getElementById('db-connection-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // 模拟数据
    const data = {
        labels: ['已使用', '空闲'],
        datasets: [{
            data: [45, 155],
            backgroundColor: ['#4a90e2', '#e9ecef']
        }]
    };
    
    drawDoughnutChart(ctx, data, canvas.width, canvas.height);
}

// 网络流量图表
function initNetworkTrafficChart() {
    const canvas = document.getElementById('network-traffic-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // 模拟数据
    const data = {
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
        datasets: [
            {
                label: '上行流量 (Mbps)',
                data: [45, 52, 68, 45, 58, 62],
                borderColor: '#4a90e2',
                backgroundColor: 'rgba(74, 144, 226, 0.1)',
                tension: 0.4
            },
            {
                label: '下行流量 (Mbps)',
                data: [32, 38, 45, 32, 41, 44],
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4
            }
        ]
    };
    
    drawLineChart(ctx, data, canvas.width, canvas.height);
}

// 简单的折线图绘制函数
function drawLineChart(ctx, data, width, height) {
    ctx.clearRect(0, 0, width, height);
    
    const padding = 40;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;
    
    // 绘制坐标轴
    ctx.strokeStyle = '#e9ecef';
    ctx.lineWidth = 1;
    
    // X轴
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Y轴
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.stroke();
    
    // 绘制数据线
    data.datasets.forEach((dataset, index) => {
        ctx.strokeStyle = dataset.borderColor;
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        dataset.data.forEach((value, i) => {
            const x = padding + (i / (dataset.data.length - 1)) * chartWidth;
            const y = height - padding - (value / Math.max(...dataset.data)) * chartHeight;
            
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
    });
}

// 简单的柱状图绘制函数
function drawBarChart(ctx, data, width, height) {
    ctx.clearRect(0, 0, width, height);
    
    const padding = 40;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;
    const barWidth = chartWidth / data.labels.length * 0.6;
    const maxValue = Math.max(...data.datasets[0].data);
    
    data.datasets[0].data.forEach((value, index) => {
        const x = padding + (index + 0.5) * (chartWidth / data.labels.length) - barWidth / 2;
        const barHeight = (value / maxValue) * chartHeight;
        const y = height - padding - barHeight;
        
        ctx.fillStyle = data.datasets[0].backgroundColor[index];
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // 绘制数值标签
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(value, x + barWidth / 2, y - 5);
    });
}

// 简单的环形图绘制函数
function drawDoughnutChart(ctx, data, width, height) {
    ctx.clearRect(0, 0, width, height);
    
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 20;
    const innerRadius = radius * 0.6;
    
    const total = data.datasets[0].data.reduce((sum, value) => sum + value, 0);
    let currentAngle = -Math.PI / 2;
    
    data.datasets[0].data.forEach((value, index) => {
        const sliceAngle = (value / total) * 2 * Math.PI;
        
        // 绘制扇形
        ctx.fillStyle = data.datasets[0].backgroundColor[index];
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
        ctx.arc(centerX, centerY, innerRadius, currentAngle + sliceAngle, currentAngle, true);
        ctx.closePath();
        ctx.fill();
        
        currentAngle += sliceAngle;
    });
}

// 刷新监控数据
function refreshMonitoringData() {
    // 模拟数据刷新
    console.log('刷新监控数据...');
    
    // 重新初始化图表
    setTimeout(() => {
        initAppPerformanceChart();
        initDbQueryChart();
        initDbConnectionChart();
        initNetworkTrafficChart();
    }, 500);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initMonitoringSubtabs();
    initAppPerformanceChart();
    initDbQueryChart();
    initDbConnectionChart();
    initNetworkTrafficChart();
    
    // 设置定时刷新
    setInterval(refreshMonitoringData, 30000); // 30秒刷新一次
});