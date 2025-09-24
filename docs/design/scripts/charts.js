/**
 * AIOps Platform - 图表脚本文件
 * 使用Chart.js实现各种数据可视化图表
 */

class ChartManager {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#4F46E5',
            secondary: '#10B981',
            warning: '#F59E0B',
            danger: '#EF4444',
            info: '#3B82F6',
            success: '#10B981',
            gray: '#6B7280'
        };
        this.init();
    }

    /**
     * 初始化图表管理器
     */
    init() {
        // 等待DOM加载完成后初始化图表
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeCharts();
            });
        } else {
            this.initializeCharts();
        }
    }

    /**
     * 初始化所有图表
     */
    initializeCharts() {
        this.createPerformanceChart();
        console.log('Charts initialized');
    }

    /**
     * 创建性能趋势图表
     */
    createPerformanceChart() {
        const ctx = document.getElementById('performance-chart');
        if (!ctx) return;

        // 生成模拟数据
        const timeLabels = this.generateTimeLabels(24); // 24小时数据
        const cpuData = this.generateRandomData(24, 30, 80);
        const memoryData = this.generateRandomData(24, 40, 90);
        const networkData = this.generateRandomData(24, 20, 70);

        this.charts.performance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timeLabels,
                datasets: [
                    {
                        label: 'CPU使用率 (%)',
                        data: cpuData,
                        borderColor: this.colors.primary,
                        backgroundColor: this.hexToRgba(this.colors.primary, 0.1),
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 6
                    },
                    {
                        label: '内存使用率 (%)',
                        data: memoryData,
                        borderColor: this.colors.secondary,
                        backgroundColor: this.hexToRgba(this.colors.secondary, 0.1),
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 6
                    },
                    {
                        label: '网络使用率 (%)',
                        data: networkData,
                        borderColor: this.colors.info,
                        backgroundColor: this.hexToRgba(this.colors.info, 0.1),
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#4F46E5',
                        borderWidth: 1,
                        cornerRadius: 6,
                        displayColors: true,
                        callbacks: {
                            title: function(context) {
                                return '时间: ' + context[0].label;
                            },
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxTicksLimit: 8,
                            font: {
                                size: 11
                            },
                            color: '#6B7280'
                        }
                    },
                    y: {
                        display: true,
                        min: 0,
                        max: 100,
                        grid: {
                            color: '#E5E7EB',
                            drawBorder: false
                        },
                        ticks: {
                            stepSize: 20,
                            font: {
                                size: 11
                            },
                            color: '#6B7280',
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                elements: {
                    line: {
                        borderJoinStyle: 'round'
                    }
                }
            }
        });
    }

    /**
     * 创建资源分布饼图
     * @param {string} canvasId - 画布ID
     * @param {Object} data - 数据对象
     */
    createResourcePieChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const chartData = {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    this.colors.primary,
                    this.colors.secondary,
                    this.colors.warning,
                    this.colors.info,
                    this.colors.danger
                ],
                borderWidth: 0,
                hoverBorderWidth: 2,
                hoverBorderColor: '#fff'
            }]
        };

        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        cornerRadius: 6,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return context.label + ': ' + percentage + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * 创建实时监控图表
     * @param {string} canvasId - 画布ID
     * @param {string} label - 数据标签
     * @param {string} color - 图表颜色
     */
    createRealtimeChart(canvasId, label, color = this.colors.primary) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const initialData = Array(20).fill(0);
        const timeLabels = Array.from({length: 20}, (_, i) => '');

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timeLabels,
                datasets: [{
                    label: label,
                    data: initialData,
                    borderColor: color,
                    backgroundColor: this.hexToRgba(color, 0.1),
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 0
                },
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        display: true,
                        min: 0,
                        max: 100,
                        grid: {
                            color: '#E5E7EB'
                        },
                        ticks: {
                            stepSize: 25,
                            font: {
                                size: 10
                            },
                            color: '#6B7280'
                        }
                    }
                }
            }
        });

        // 启动实时数据更新
        this.startRealtimeUpdate(canvasId);
    }

    /**
     * 创建柱状图
     * @param {string} canvasId - 画布ID
     * @param {Array} labels - 标签数组
     * @param {Array} data - 数据数组
     * @param {string} label - 数据集标签
     */
    createBarChart(canvasId, labels, data, label) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    backgroundColor: this.hexToRgba(this.colors.primary, 0.8),
                    borderColor: this.colors.primary,
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        cornerRadius: 6
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 11
                            },
                            color: '#6B7280'
                        }
                    },
                    y: {
                        grid: {
                            color: '#E5E7EB'
                        },
                        ticks: {
                            font: {
                                size: 11
                            },
                            color: '#6B7280'
                        }
                    }
                }
            }
        });
    }

    /**
     * 创建热力图
     * @param {string} canvasId - 画布ID
     * @param {Array} data - 热力图数据
     */
    createHeatmapChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        // 使用散点图模拟热力图效果
        this.charts[canvasId] = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: '系统负载',
                    data: data,
                    backgroundColor: function(context) {
                        const value = context.parsed.y;
                        if (value > 80) return '#EF4444';
                        if (value > 60) return '#F59E0B';
                        if (value > 40) return '#10B981';
                        return '#3B82F6';
                    },
                    pointRadius: 8,
                    pointHoverRadius: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function() {
                                return '系统负载';
                            },
                            label: function(context) {
                                return `负载: ${context.parsed.y}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: '时间'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: '负载 (%)'
                        }
                    }
                }
            }
        });
    }

    /**
     * 更新图表数据
     * @param {string} chartId - 图表ID
     * @param {Object} newData - 新数据
     */
    updateChart(chartId, newData) {
        const chart = this.charts[chartId];
        if (!chart) return;

        chart.data = newData;
        chart.update('none');
    }

    /**
     * 更新性能图表时间范围
     * @param {string} timeRange - 时间范围
     */
    updatePerformanceChartTimeRange(timeRange) {
        const chart = this.charts.performance;
        if (!chart) return;

        let dataPoints;
        switch (timeRange) {
            case '1h':
                dataPoints = 12; // 5分钟间隔
                break;
            case '6h':
                dataPoints = 24; // 15分钟间隔
                break;
            case '24h':
                dataPoints = 24; // 1小时间隔
                break;
            case '7d':
                dataPoints = 28; // 6小时间隔
                break;
            default:
                dataPoints = 24;
        }

        const timeLabels = this.generateTimeLabels(dataPoints, timeRange);
        const cpuData = this.generateRandomData(dataPoints, 30, 80);
        const memoryData = this.generateRandomData(dataPoints, 40, 90);
        const networkData = this.generateRandomData(dataPoints, 20, 70);

        chart.data.labels = timeLabels;
        chart.data.datasets[0].data = cpuData;
        chart.data.datasets[1].data = memoryData;
        chart.data.datasets[2].data = networkData;
        
        chart.update();
    }

    /**
     * 开始实时数据更新
     * @param {string} chartId - 图表ID
     */
    startRealtimeUpdate(chartId) {
        const chart = this.charts[chartId];
        if (!chart) return;

        setInterval(() => {
            const data = chart.data.datasets[0].data;
            data.shift(); // 移除第一个数据点
            data.push(Math.random() * 100); // 添加新的随机数据点
            chart.update('none');
        }, 1000);
    }

    /**
     * 生成时间标签
     * @param {number} count - 数据点数量
     * @param {string} range - 时间范围
     * @returns {Array} 时间标签数组
     */
    generateTimeLabels(count, range = '24h') {
        const labels = [];
        const now = new Date();
        
        let interval;
        switch (range) {
            case '1h':
                interval = 5 * 60 * 1000; // 5分钟
                break;
            case '6h':
                interval = 15 * 60 * 1000; // 15分钟
                break;
            case '24h':
                interval = 60 * 60 * 1000; // 1小时
                break;
            case '7d':
                interval = 6 * 60 * 60 * 1000; // 6小时
                break;
            default:
                interval = 60 * 60 * 1000; // 1小时
        }

        for (let i = count - 1; i >= 0; i--) {
            const time = new Date(now.getTime() - i * interval);
            if (range === '7d') {
                labels.push(time.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }));
            } else {
                labels.push(time.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }));
            }
        }

        return labels;
    }

    /**
     * 生成随机数据
     * @param {number} count - 数据点数量
     * @param {number} min - 最小值
     * @param {number} max - 最大值
     * @returns {Array} 随机数据数组
     */
    generateRandomData(count, min, max) {
        const data = [];
        let lastValue = (min + max) / 2;

        for (let i = 0; i < count; i++) {
            // 生成相对平滑的随机数据
            const change = (Math.random() - 0.5) * 10;
            lastValue = Math.max(min, Math.min(max, lastValue + change));
            data.push(Math.round(lastValue * 10) / 10);
        }

        return data;
    }

    /**
     * 将十六进制颜色转换为RGBA
     * @param {string} hex - 十六进制颜色
     * @param {number} alpha - 透明度
     * @returns {string} RGBA颜色字符串
     */
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    /**
     * 销毁所有图表
     */
    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }

    /**
     * 销毁特定图表
     * @param {string} chartId - 图表ID
     */
    destroyChart(chartId) {
        const chart = this.charts[chartId];
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
            delete this.charts[chartId];
        }
    }

    /**
     * 获取图表实例
     * @param {string} chartId - 图表ID
     * @returns {Object} 图表实例
     */
    getChart(chartId) {
        return this.charts[chartId];
    }

    /**
     * 重置图表大小
     */
    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    }
}

// 创建全局图表管理器实例
let chartManager;

// 初始化图表管理器
document.addEventListener('DOMContentLoaded', () => {
    chartManager = new ChartManager();
});

// 窗口大小改变时重置图表大小
window.addEventListener('resize', () => {
    if (chartManager) {
        chartManager.resizeCharts();
    }
});

// 导出全局函数供其他脚本使用
window.updatePerformanceChart = function() {
    if (chartManager && chartManager.charts.performance) {
        // 生成新的随机数据
        const chart = chartManager.charts.performance;
        chart.data.datasets.forEach(dataset => {
            dataset.data = chartManager.generateRandomData(dataset.data.length, 20, 90);
        });
        chart.update();
    }
};

window.updateChartTimeRange = function(timeRange) {
    if (chartManager) {
        chartManager.updatePerformanceChartTimeRange(timeRange);
    }
};

// 导出图表管理器类
window.ChartManager = ChartManager;