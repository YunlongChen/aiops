<#
.SYNOPSIS
    AIOps测试框架PowerShell封装脚本
    
.DESCRIPTION
    为不熟悉Python的用户提供简化的测试执行接口
    支持所有主要的测试场景，无需直接使用Python命令
    
.PARAMETER TestType
    测试类型：web, database, system, anomaly, alert, dashboard, stress, multi_project, error_injection
    
.PARAMETER Duration
    测试持续时间（秒），默认300秒
    
.PARAMETER OutputPath
    测试结果输出路径，默认为当前目录
    
.PARAMETER ConfigFile
    自定义配置文件路径
    
.PARAMETER Scenario
    多项目测试场景名称（用于multi_project测试）
    
.PARAMETER ShowHelp
    显示详细帮助信息
    
.EXAMPLE
    .\Run-AIOpsTest.ps1 -TestType web -Duration 600
    运行Web监控测试600秒
    
.EXAMPLE
    .\Run-AIOpsTest.ps1 -TestType multi_project -Scenario "comprehensive_load_test"
    运行综合负载测试场景
    
.EXAMPLE
    .\Run-AIOpsTest.ps1 -ShowHelp
    显示详细帮助信息
    
.NOTES
    作者: AIOps Team
    版本: 1.0.0
    创建日期: 2025-01-10
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("web", "database", "system", "anomaly", "alert", "dashboard", "stress", "multi_project", "error_injection", "quick_demo", "simple_demo")]
    [string]$TestType = "web",
    
    [Parameter(Mandatory=$false)]
    [int]$Duration = 300,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".",
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigFile = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Scenario = "basic_load_test",
    
    [Parameter(Mandatory=$false)]
    [switch]$ShowHelp,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun
)

# 函数：显示帮助信息
function Show-Help {
    Write-Host "=== AIOps测试框架使用指南 ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "支持的测试类型：" -ForegroundColor Yellow
    Write-Host "  web           - Web应用监控测试" -ForegroundColor White
    Write-Host "  database      - 数据库性能监控测试" -ForegroundColor White
    Write-Host "  system        - 系统资源监控测试" -ForegroundColor White
    Write-Host "  anomaly       - 异常检测测试" -ForegroundColor White
    Write-Host "  alert         - 告警系统测试" -ForegroundColor White
    Write-Host "  dashboard     - 仪表板数据生成测试" -ForegroundColor White
    Write-Host "  stress        - 压力测试" -ForegroundColor White
    Write-Host "  multi_project - 多项目负载测试" -ForegroundColor White
    Write-Host "  error_injection - 错误注入测试" -ForegroundColor White
    Write-Host "  quick_demo    - 快速演示" -ForegroundColor White
    Write-Host "  simple_demo   - 简单演示" -ForegroundColor White
    Write-Host ""
    Write-Host "多项目测试场景：" -ForegroundColor Yellow
    Write-Host "  basic_load_test        - 基础负载测试" -ForegroundColor White
    Write-Host "  comprehensive_load_test - 综合负载测试" -ForegroundColor White
    Write-Host "  error_injection_test   - 错误注入测试" -ForegroundColor White
    Write-Host "  high_load_stress_test  - 高负载压力测试" -ForegroundColor White
    Write-Host ""
    Write-Host "使用示例：" -ForegroundColor Yellow
    Write-Host "  .\Run-AIOpsTest.ps1 -TestType web -Duration 600" -ForegroundColor Cyan
    Write-Host "  .\Run-AIOpsTest.ps1 -TestType database -Duration 1200 -Verbose" -ForegroundColor Cyan
    Write-Host "  .\Run-AIOpsTest.ps1 -TestType multi_project -Scenario comprehensive_load_test" -ForegroundColor Cyan
    Write-Host "  .\Run-AIOpsTest.ps1 -TestType quick_demo" -ForegroundColor Cyan
    Write-Host ""
}

# 函数：检查Python环境
function Test-PythonEnvironment {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python环境检查通过: $pythonVersion" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "❌ 未找到Python环境" -ForegroundColor Red
        Write-Host "请安装Python 3.7+并确保python命令可用" -ForegroundColor Yellow
        return $false
    }
    return $false
}

# 函数：检查依赖文件
function Test-Dependencies {
    $requiredFiles = @(
        "requirements.txt",
        "test_config.json",
        "project_configs.json"
    )
    
    $missingFiles = @()
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Host "❌ 缺少必要文件:" -ForegroundColor Red
        foreach ($file in $missingFiles) {
            Write-Host "  - $file" -ForegroundColor Yellow
        }
        return $false
    }
    
    Write-Host "✅ 依赖文件检查通过" -ForegroundColor Green
    return $true
}

# 函数：安装Python依赖
function Install-PythonDependencies {
    Write-Host "正在检查Python依赖..." -ForegroundColor Yellow
    
    try {
        python -m pip install -r requirements.txt --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python依赖安装完成" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Python依赖安装失败" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ 无法安装Python依赖: $_" -ForegroundColor Red
        return $false
    }
}

# 函数：构建Python命令
function Build-PythonCommand {
    param(
        [string]$TestType,
        [int]$Duration,
        [string]$OutputPath,
        [string]$ConfigFile,
        [string]$Scenario
    )
    
    $command = ""
    $outputFile = ""
    
    switch ($TestType) {
        "web" {
            $command = "python web_app_simulator.py --duration $Duration"
            $outputFile = "web_test_results.json"
        }
        "database" {
            $command = "python database_simulator.py --duration $Duration --export db_metrics.json --report db_report.json"
            $outputFile = "db_report.json"
        }
        "system" {
            $command = "python system_monitor.py --duration $Duration --export sys_metrics.json --report sys_report.json"
            $outputFile = "sys_report.json"
        }
        "anomaly" {
            $command = "python anomaly_simulator.py"
            $outputFile = "anomaly_results.json"
        }
        "alert" {
            $command = "python alert_simulator.py"
            $outputFile = "alert_results.json"
        }
        "dashboard" {
            $command = "python data_pusher.py --duration $Duration"
            $outputFile = "dashboard_data.json"
        }
        "stress" {
            $command = "python stress_tester.py --duration $Duration"
            $outputFile = "stress_test_results.json"
        }
        "multi_project" {
            $command = "python integrated_test_runner.py --test-type multi_project --scenario $Scenario"
            $outputFile = "multi_project_results.json"
        }
        "error_injection" {
            $command = "python error_injector.py --scenario $Scenario"
            $outputFile = "error_injection_results.json"
        }
        "quick_demo" {
            $command = "python quick_demo.py"
            $outputFile = "quick_demo_results.json"
        }
        "simple_demo" {
            $command = "python simple_demo.py"
            $outputFile = "simple_demo_results.json"
        }
        default {
            throw "不支持的测试类型: $TestType"
        }
    }
    
    # 添加自定义配置文件参数
    if ($ConfigFile -and (Test-Path $ConfigFile)) {
        $command += " --config $ConfigFile"
    }
    
    return @{
        Command = $command
        OutputFile = $outputFile
    }
}

# 函数：执行测试
function Invoke-AIOpsTest {
    param(
        [string]$Command,
        [string]$OutputFile,
        [string]$OutputPath,
        [bool]$VerboseOutput,
        [bool]$DryRunMode
    )
    
    Write-Host "=== 开始执行AIOps测试 ===" -ForegroundColor Green
    Write-Host "测试命令: $Command" -ForegroundColor Cyan
    
    if ($DryRunMode) {
        Write-Host "[试运行模式] 将执行以下命令:" -ForegroundColor Yellow
        Write-Host $Command -ForegroundColor White
        return $true
    }
    
    $startTime = Get-Date
    
    try {
        if ($VerboseOutput) {
            # 详细输出模式
            Invoke-Expression $Command
        } else {
            # 静默模式，只显示关键信息
            $output = Invoke-Expression $Command 2>&1
            
            # 过滤并显示重要信息
            $output | ForEach-Object {
                $line = $_.ToString()
                if ($line -match "(✅|❌|警告|错误|完成|开始|===)" -or $line -match "\d+%") {
                    Write-Host $line
                }
            }
        }
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        Write-Host "✅ 测试执行完成，耗时: $([math]::Round($duration, 2))秒" -ForegroundColor Green
        
        # 检查输出文件
        if ($OutputFile -and (Test-Path $OutputFile)) {
            $outputFullPath = Join-Path $OutputPath $OutputFile
            if ($OutputPath -ne ".") {
                Move-Item $OutputFile $outputFullPath -Force
            }
            Write-Host "📄 测试结果已保存到: $outputFullPath" -ForegroundColor Blue
        }
        
        return $true
        
    } catch {
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        Write-Host "❌ 测试执行失败，耗时: $([math]::Round($duration, 2))秒" -ForegroundColor Red
        Write-Host "错误信息: $_" -ForegroundColor Red
        return $false
    }
}

# 函数：显示测试结果摘要
function Show-TestSummary {
    param(
        [string]$TestType,
        [int]$Duration,
        [string]$OutputPath,
        [bool]$Success
    )
    
    Write-Host ""
    Write-Host "=== 测试执行摘要 ===" -ForegroundColor Green
    Write-Host "测试类型: $TestType" -ForegroundColor White
    Write-Host "持续时间: $Duration 秒" -ForegroundColor White
    Write-Host "输出路径: $OutputPath" -ForegroundColor White
    Write-Host "执行状态: $(if ($Success) { '✅ 成功' } else { '❌ 失败' })" -ForegroundColor $(if ($Success) { 'Green' } else { 'Red' })
    
    if ($Success) {
        Write-Host ""
        Write-Host "📊 查看测试结果:" -ForegroundColor Yellow
        Write-Host "  - 检查输出目录中的结果文件" -ForegroundColor White
        Write-Host "  - 查看Grafana仪表板 (如果已配置)" -ForegroundColor White
        Write-Host "  - 检查Prometheus指标 (如果已配置)" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "🔧 故障排除建议:" -ForegroundColor Yellow
        Write-Host "  - 检查Python环境和依赖" -ForegroundColor White
        Write-Host "  - 验证配置文件格式" -ForegroundColor White
        Write-Host "  - 查看详细错误日志" -ForegroundColor White
        Write-Host "  - 使用 -Verbose 参数获取更多信息" -ForegroundColor White
    }
}

# 主执行逻辑
function Main {
    # 显示帮助信息
    if ($ShowHelp) {
        Show-Help
        return
    }
    
    Write-Host "🚀 AIOps测试框架 PowerShell 启动器" -ForegroundColor Magenta
    Write-Host "版本: 1.0.0" -ForegroundColor Gray
    Write-Host ""
    
    # 环境检查
    if (-not (Test-PythonEnvironment)) {
        return
    }
    
    if (-not (Test-Dependencies)) {
        return
    }
    
    # 安装依赖
    if (-not (Install-PythonDependencies)) {
        return
    }
    
    # 创建输出目录
    if ($OutputPath -ne "." -and -not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
        Write-Host "📁 创建输出目录: $OutputPath" -ForegroundColor Blue
    }
    
    try {
        # 构建命令
        $commandInfo = Build-PythonCommand -TestType $TestType -Duration $Duration -OutputPath $OutputPath -ConfigFile $ConfigFile -Scenario $Scenario
        
        # 执行测试
        $success = Invoke-AIOpsTest -Command $commandInfo.Command -OutputFile $commandInfo.OutputFile -OutputPath $OutputPath -VerboseOutput $Verbose -DryRunMode $DryRun
        
        # 显示摘要
        Show-TestSummary -TestType $TestType -Duration $Duration -OutputPath $OutputPath -Success $success
        
    } catch {
        Write-Host "❌ 执行过程中发生错误: $_" -ForegroundColor Red
        Show-TestSummary -TestType $TestType -Duration $Duration -OutputPath $OutputPath -Success $false
    }
}

# 执行主函数
Main