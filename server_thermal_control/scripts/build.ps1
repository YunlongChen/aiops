# 服务器热控制系统构建脚本
# PowerShell脚本用于构建、测试和部署应用程序

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("build", "test", "run", "docker", "clean", "all")]
    [string]$Action = "build",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("debug", "release")]
    [string]$Profile = "debug",
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose,
    
    [Parameter(Mandatory=$false)]
    [switch]$Watch
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ $Message" "Cyan"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" "Yellow"
}

# 检查依赖
function Test-Dependencies {
    Write-Info "检查构建依赖..."
    
    # 检查Rust
    if (-not (Get-Command "cargo" -ErrorAction SilentlyContinue)) {
        Write-Error "未找到Rust/Cargo，请先安装Rust工具链"
        exit 1
    }
    
    # 检查Docker（如果需要）
    if ($Action -eq "docker" -and -not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
        Write-Error "未找到Docker，请先安装Docker"
        exit 1
    }
    
    Write-Success "依赖检查完成"
}

# 清理构建产物
function Invoke-Clean {
    Write-Info "清理构建产物..."
    
    if (Test-Path "target") {
        Remove-Item -Recurse -Force "target"
        Write-Success "已清理target目录"
    }
    
    if (Test-Path "Cargo.lock") {
        Remove-Item -Force "Cargo.lock"
        Write-Success "已清理Cargo.lock"
    }
    
    # 清理日志文件
    if (Test-Path "logs") {
        Get-ChildItem "logs" -Filter "*.log" | Remove-Item -Force
        Write-Success "已清理日志文件"
    }
    
    Write-Success "清理完成"
}

# 构建应用程序
function Invoke-Build {
    Write-Info "开始构建应用程序 (Profile: $Profile)..."
    
    $buildArgs = @("build")
    
    if ($Profile -eq "release") {
        $buildArgs += "--release"
    }
    
    if ($Verbose) {
        $buildArgs += "--verbose"
    }
    
    try {
        & cargo @buildArgs
        Write-Success "构建完成"
    }
    catch {
        Write-Error "构建失败: $_"
        exit 1
    }
}

# 运行测试
function Invoke-Test {
    Write-Info "运行测试..."
    
    $testArgs = @("test")
    
    if ($Verbose) {
        $testArgs += "--verbose"
    }
    
    try {
        & cargo @testArgs
        Write-Success "测试通过"
    }
    catch {
        Write-Error "测试失败: $_"
        exit 1
    }
}

# 运行应用程序
function Invoke-Run {
    Write-Info "启动应用程序..."
    
    # 确保配置文件存在
    if (-not (Test-Path "config/app.toml")) {
        Write-Warning "配置文件不存在，使用默认配置"
    }
    
    # 创建必要的目录
    @("data", "logs") | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
            Write-Info "创建目录: $_"
        }
    }
    
    $runArgs = @("run")
    
    if ($Profile -eq "release") {
        $runArgs += "--release"
    }
    
    if ($Watch) {
        # 使用cargo-watch进行热重载
        if (Get-Command "cargo-watch" -ErrorAction SilentlyContinue) {
            $runArgs = @("watch", "-x") + $runArgs
        } else {
            Write-Warning "cargo-watch未安装，无法启用热重载"
        }
    }
    
    try {
        & cargo @runArgs
    }
    catch {
        Write-Error "运行失败: $_"
        exit 1
    }
}

# 构建Docker镜像
function Invoke-Docker {
    Write-Info "构建Docker镜像..."
    
    $imageName = "thermal-control:latest"
    
    try {
        & docker build -t $imageName .
        Write-Success "Docker镜像构建完成: $imageName"
        
        Write-Info "镜像信息:"
        & docker images $imageName
    }
    catch {
        Write-Error "Docker构建失败: $_"
        exit 1
    }
}

# 代码格式化和检查
function Invoke-Format {
    Write-Info "格式化代码..."
    
    try {
        & cargo fmt
        Write-Success "代码格式化完成"
        
        Write-Info "运行Clippy检查..."
        & cargo clippy -- -D warnings
        Write-Success "代码检查通过"
    }
    catch {
        Write-Error "代码检查失败: $_"
        exit 1
    }
}

# 生成文档
function Invoke-Docs {
    Write-Info "生成文档..."
    
    try {
        & cargo doc --no-deps --open
        Write-Success "文档生成完成"
    }
    catch {
        Write-Error "文档生成失败: $_"
        exit 1
    }
}

# 性能基准测试
function Invoke-Bench {
    Write-Info "运行性能基准测试..."
    
    try {
        & cargo bench
        Write-Success "基准测试完成"
    }
    catch {
        Write-Error "基准测试失败: $_"
        exit 1
    }
}

# 主函数
function Main {
    Write-ColorOutput "=== 服务器热控制系统构建脚本 ===" "Magenta"
    Write-Info "操作: $Action, 配置: $Profile"
    
    # 检查依赖
    Test-Dependencies
    
    switch ($Action) {
        "clean" {
            Invoke-Clean
        }
        "build" {
            Invoke-Build
        }
        "test" {
            Invoke-Build
            Invoke-Test
        }
        "run" {
            Invoke-Build
            Invoke-Run
        }
        "docker" {
            Invoke-Docker
        }
        "all" {
            Invoke-Clean
            Invoke-Format
            Invoke-Build
            Invoke-Test
            Invoke-Docs
            Write-Success "所有任务完成"
        }
        default {
            Write-Error "未知操作: $Action"
            exit 1
        }
    }
}

# 显示帮助信息
function Show-Help {
    Write-ColorOutput @"
服务器热控制系统构建脚本

用法: .\build.ps1 [选项]

选项:
  -Action <action>    执行的操作 (build, test, run, docker, clean, all)
  -Profile <profile>  构建配置 (debug, release)
  -Verbose           详细输出
  -Watch             启用热重载 (仅适用于run操作)

示例:
  .\build.ps1 -Action build -Profile release
  .\build.ps1 -Action run -Watch
  .\build.ps1 -Action docker
  .\build.ps1 -Action all -Verbose

"@ "Yellow"
}

# 脚本入口点
if ($args -contains "-h" -or $args -contains "--help") {
    Show-Help
    exit 0
}

try {
    Main
}
catch {
    Write-Error "脚本执行失败: $_"
    exit 1
}