<#
.SYNOPSIS
    AIOps API文档同步脚本
    
.DESCRIPTION
    此脚本用于将AIOps测试管理系统的OpenAPI文档同步到各种在线文档平台
    支持Apifox、Postman、SwaggerHub等平台
    
.PARAMETER Platform
    目标平台名称 (apifox, postman, swaggerhub, local)
    
.PARAMETER ApiKey
    平台API密钥（可选，用于自动同步）
    
.PARAMETER ProjectId
    项目ID（可选，用于指定目标项目）
    
.PARAMETER OutputPath
    输出路径（可选，用于本地导出）
    
.EXAMPLE
    .\sync-api-docs.ps1 -Platform apifox
    手动同步到Apifox平台
    
.EXAMPLE
    .\sync-api-docs.ps1 -Platform postman -ApiKey "your-api-key"
    使用API密钥自动同步到Postman
    
.EXAMPLE
    .\sync-api-docs.ps1 -Platform local -OutputPath "./exported-docs"
    导出到本地目录
#>

param(
    [Parameter(Mandatory=$true, HelpMessage="目标平台: apifox, postman, swaggerhub, local")]
    [ValidateSet("apifox", "postman", "swaggerhub", "local")]
    [string]$Platform,
    
    [Parameter(Mandatory=$false, HelpMessage="平台API密钥")]
    [string]$ApiKey,
    
    [Parameter(Mandatory=$false, HelpMessage="项目ID")]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$false, HelpMessage="输出路径")]
    [string]$OutputPath = "./exported-docs"
)

# 脚本配置
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$OpenApiFile = Join-Path $ProjectRoot "test-scenarios\test-web-service\openapi.json"
$DocsDir = Join-Path $ProjectRoot "docs"

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 检查文件是否存在
function Test-OpenApiFile {
    if (-not (Test-Path $OpenApiFile)) {
        Write-ColorOutput "错误: OpenAPI文件不存在: $OpenApiFile" "Red"
        Write-ColorOutput "请确保已生成OpenAPI文档文件" "Yellow"
        exit 1
    }
    Write-ColorOutput "✓ 找到OpenAPI文档文件: $OpenApiFile" "Green"
}

# 验证OpenAPI文档格式
function Test-OpenApiFormat {
    try {
        $content = Get-Content $OpenApiFile -Raw | ConvertFrom-Json
        if (-not $content.openapi) {
            throw "缺少openapi版本信息"
        }
        if (-not $content.info) {
            throw "缺少info信息"
        }
        if (-not $content.paths) {
            throw "缺少paths信息"
        }
        Write-ColorOutput "✓ OpenAPI文档格式验证通过" "Green"
        return $content
    }
    catch {
        Write-ColorOutput "错误: OpenAPI文档格式无效: $($_.Exception.Message)" "Red"
        exit 1
    }
}

# 显示API文档信息
function Show-ApiInfo {
    param($ApiDoc)
    
    Write-ColorOutput "`n=== API文档信息 ===" "Cyan"
    Write-ColorOutput "标题: $($ApiDoc.info.title)" "White"
    Write-ColorOutput "版本: $($ApiDoc.info.version)" "White"
    Write-ColorOutput "描述: $($ApiDoc.info.description)" "White"
    
    $pathCount = ($ApiDoc.paths | Get-Member -MemberType NoteProperty).Count
    Write-ColorOutput "API端点数量: $pathCount" "White"
    
    if ($ApiDoc.servers) {
        Write-ColorOutput "服务器:" "White"
        foreach ($server in $ApiDoc.servers) {
            Write-ColorOutput "  - $($server.url) ($($server.description))" "Gray"
        }
    }
    Write-ColorOutput "==================`n" "Cyan"
}

# 同步到Apifox
function Sync-ToApifox {
    Write-ColorOutput "🚀 准备同步到Apifox..." "Yellow"
    
    Write-ColorOutput "`n📋 手动导入步骤:" "Cyan"
    Write-ColorOutput "1. 打开 https://www.apifox.cn/" "White"
    Write-ColorOutput "2. 登录并选择或创建项目" "White"
    Write-ColorOutput "3. 点击 '导入' → 'OpenAPI/Swagger'" "White"
    Write-ColorOutput "4. 选择 '从文件导入'" "White"
    Write-ColorOutput "5. 上传文件: $OpenApiFile" "Green"
    Write-ColorOutput "6. 确认导入设置并完成导入" "White"
    
    # 尝试打开文件所在目录
    try {
        $fileDir = Split-Path -Parent $OpenApiFile
        Start-Process "explorer.exe" -ArgumentList $fileDir
        Write-ColorOutput "✓ 已打开文件所在目录" "Green"
    }
    catch {
        Write-ColorOutput "⚠ 无法打开文件目录" "Yellow"
    }
    
    # 尝试打开Apifox网站
    try {
        Start-Process "https://www.apifox.cn/"
        Write-ColorOutput "✓ 已打开Apifox网站" "Green"
    }
    catch {
        Write-ColorOutput "⚠ 无法打开浏览器" "Yellow"
    }
}

# 同步到Postman
function Sync-ToPostman {
    Write-ColorOutput "🚀 准备同步到Postman..." "Yellow"
    
    if ($ApiKey) {
        Write-ColorOutput "🔑 检测到API密钥，尝试自动同步..." "Cyan"
        
        # Postman API同步逻辑
        try {
            $headers = @{
                "X-API-Key" = $ApiKey
                "Content-Type" = "application/json"
            }
            
            $apiContent = Get-Content $OpenApiFile -Raw
            $body = @{
                "type" = "openapi"
                "input" = @{
                    "schema" = $apiContent | ConvertFrom-Json
                }
            } | ConvertTo-Json -Depth 10
            
            Write-ColorOutput "正在上传到Postman..." "Yellow"
            # 注意: 这里需要实际的Postman API端点
            # $response = Invoke-RestMethod -Uri "https://api.getpostman.com/import/openapi" -Method Post -Headers $headers -Body $body
            
            Write-ColorOutput "⚠ 自动同步功能需要配置Postman API端点" "Yellow"
            Write-ColorOutput "请使用手动导入方式" "Yellow"
        }
        catch {
            Write-ColorOutput "❌ 自动同步失败: $($_.Exception.Message)" "Red"
            Write-ColorOutput "请使用手动导入方式" "Yellow"
        }
    }
    
    Write-ColorOutput "`n📋 手动导入步骤:" "Cyan"
    Write-ColorOutput "1. 打开Postman应用" "White"
    Write-ColorOutput "2. 点击 'Import' 按钮" "White"
    Write-ColorOutput "3. 选择 'File' 标签" "White"
    Write-ColorOutput "4. 上传文件: $OpenApiFile" "Green"
    Write-ColorOutput "5. 选择导入选项并确认" "White"
    
    # 尝试打开Postman
    try {
        Start-Process "postman://"
        Write-ColorOutput "✓ 尝试打开Postman应用" "Green"
    }
    catch {
        Write-ColorOutput "⚠ 无法打开Postman应用，请手动启动" "Yellow"
    }
}

# 同步到SwaggerHub
function Sync-ToSwaggerHub {
    Write-ColorOutput "🚀 准备同步到SwaggerHub..." "Yellow"
    
    Write-ColorOutput "`n📋 手动导入步骤:" "Cyan"
    Write-ColorOutput "1. 打开 https://swagger.io/tools/swaggerhub/" "White"
    Write-ColorOutput "2. 登录SwaggerHub账户" "White"
    Write-ColorOutput "3. 点击 'Create New' → 'Import and Document API'" "White"
    Write-ColorOutput "4. 选择 'File Upload'" "White"
    Write-ColorOutput "5. 上传文件: $OpenApiFile" "Green"
    Write-ColorOutput "6. 配置API信息并发布" "White"
    
    # 尝试打开SwaggerHub网站
    try {
        Start-Process "https://swagger.io/tools/swaggerhub/"
        Write-ColorOutput "✓ 已打开SwaggerHub网站" "Green"
    }
    catch {
        Write-ColorOutput "⚠ 无法打开浏览器" "Yellow"
    }
}

# 本地导出
function Export-ToLocal {
    Write-ColorOutput "📁 导出到本地目录: $OutputPath" "Yellow"
    
    # 创建输出目录
    if (-not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
        Write-ColorOutput "✓ 创建输出目录: $OutputPath" "Green"
    }
    
    # 复制OpenAPI文件
    $outputFile = Join-Path $OutputPath "openapi.json"
    Copy-Item $OpenApiFile $outputFile -Force
    Write-ColorOutput "✓ 复制OpenAPI文档: $outputFile" "Green"
    
    # 生成HTML文档
    $htmlFile = Join-Path $OutputPath "api-docs.html"
    $htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>AIOps API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui.css" />
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin:0; background: #fafafa; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: './openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            });
        };
    </script>
</body>
</html>
"@
    
    Set-Content -Path $htmlFile -Value $htmlContent -Encoding UTF8
    Write-ColorOutput "✓ 生成HTML文档: $htmlFile" "Green"
    
    # 复制同步指南
    $guideFile = Join-Path $DocsDir "api-sync-guide.md"
    if (Test-Path $guideFile) {
        $outputGuideFile = Join-Path $OutputPath "sync-guide.md"
        Copy-Item $guideFile $outputGuideFile -Force
        Write-ColorOutput "✓ 复制同步指南: $outputGuideFile" "Green"
    }
    
    Write-ColorOutput "`n📋 导出完成!" "Cyan"
    Write-ColorOutput "文件位置:" "White"
    Write-ColorOutput "  - OpenAPI规范: $outputFile" "Gray"
    Write-ColorOutput "  - HTML文档: $htmlFile" "Gray"
    Write-ColorOutput "  - 同步指南: $(Join-Path $OutputPath 'sync-guide.md')" "Gray"
    
    # 尝试打开HTML文档
    try {
        Start-Process $htmlFile
        Write-ColorOutput "✓ 已打开HTML文档" "Green"
    }
    catch {
        Write-ColorOutput "⚠ 无法打开HTML文档" "Yellow"
    }
}

# 主函数
function Main {
    Write-ColorOutput "🔧 AIOps API文档同步工具" "Cyan"
    Write-ColorOutput "目标平台: $Platform" "White"
    
    # 检查OpenAPI文件
    Test-OpenApiFile
    
    # 验证文档格式
    $apiDoc = Test-OpenApiFormat
    
    # 显示API信息
    Show-ApiInfo $apiDoc
    
    # 根据平台执行相应操作
    switch ($Platform.ToLower()) {
        "apifox" {
            Sync-ToApifox
        }
        "postman" {
            Sync-ToPostman
        }
        "swaggerhub" {
            Sync-ToSwaggerHub
        }
        "local" {
            Export-ToLocal
        }
    }
    
    Write-ColorOutput "`n✅ 同步操作完成!" "Green"
    Write-ColorOutput "如有问题，请查看同步指南: docs/api-sync-guide.md" "Yellow"
}

# 执行主函数
try {
    Main
}
catch {
    Write-ColorOutput "❌ 脚本执行失败: $($_.Exception.Message)" "Red"
    Write-ColorOutput "请检查错误信息并重试" "Yellow"
    exit 1
}