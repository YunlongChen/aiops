# Traefik SSL证书生成脚本
# 用于生成本地开发环境的自签名SSL证书
# 作者: AI Assistant
# 创建时间: 2024

<#
.SYNOPSIS
    生成Traefik使用的SSL证书

.DESCRIPTION
    此脚本用于生成本地开发环境使用的自签名SSL证书，
    包括根CA证书和各个服务的SSL证书。

.PARAMETER Domain
    要生成证书的域名，默认为 "local"

.PARAMETER ValidDays
    证书有效期天数，默认为365天

.PARAMETER Force
    强制重新生成证书，即使已存在

.EXAMPLE
    .\generate-certs.ps1
    使用默认参数生成证书

.EXAMPLE
    .\generate-certs.ps1 -Domain "example.com" -ValidDays 730 -Force
    为example.com域名生成有效期2年的证书，强制覆盖现有证书
#>

param(
    [string]$Domain = "local",
    [int]$ValidDays = 365,
    [switch]$Force
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 脚本配置
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CertsDir = Join-Path $ScriptDir "certs"
$ConfigDir = Join-Path $ScriptDir "ssl-config"

# 证书配置
$CertConfig = @{
    Country = "CN"
    State = "Beijing"
    City = "Beijing"
    Organization = "AIOps"
    OrganizationalUnit = "IT Department"
    CommonName = "*.$Domain"
    Email = "admin@$Domain"
}0

# 服务域名列表
$ServiceDomains = @(
    "traefik.$Domain",
    "ai-engine.$Domain",
    "api.$Domain",
    "grafana.$Domain",
    "prometheus.$Domain",
    "kibana.$Domain",
    "elasticsearch.$Domain",
    "whoami.$Domain"
)

# 函数：写入日志
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Host $LogMessage
}

# 函数：检查OpenSSL是否可用
function Test-OpenSSL {
    try {
        $null = Get-Command openssl -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# 函数：安装OpenSSL（Windows）
function Install-OpenSSL {
    Write-Log "检测到OpenSSL未安装，尝试安装..." "WARN"
    
    # 检查是否有Chocolatey
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Log "使用Chocolatey安装OpenSSL..."
        choco install openssl -y
        return
    }
    
    # 检查是否有Scoop
    if (Get-Command scoop -ErrorAction SilentlyContinue) {
        Write-Log "使用Scoop安装OpenSSL..."
        scoop install openssl
        return
    }
    
    # 检查是否有winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Log "使用winget安装OpenSSL..."
        winget install --id ShiningLight.OpenSSL
        return
    }
    
    Write-Log "无法自动安装OpenSSL，请手动安装后重新运行脚本" "ERROR"
    Write-Log "下载地址: https://slproweb.com/products/Win32OpenSSL.html" "INFO"
    exit 1
}

# 函数：创建目录
function New-Directory {
    param([string]$Path)
    
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Log "创建目录: $Path"
    }
}

# 函数：生成CA根证书
function New-RootCA {
    Write-Log "生成CA根证书..."
    
    $CaKeyPath = Join-Path $CertsDir "ca-key.pem"
    $CaCertPath = Join-Path $CertsDir "ca-cert.pem"
    $CaConfigPath = Join-Path $ConfigDir "ca.conf"
    
    # 检查是否已存在且不强制重新生成
    if ((Test-Path $CaCertPath) -and (-not $Force)) {
        Write-Log "CA根证书已存在，跳过生成" "WARN"
        return
    }
    
    # 创建CA配置文件
    $CaConfig = @"
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
C = $($CertConfig.Country)
ST = $($CertConfig.State)
L = $($CertConfig.City)
O = $($CertConfig.Organization)
OU = $($CertConfig.OrganizationalUnit)
CN = AIOps Root CA
emailAddress = $($CertConfig.Email)

[v3_ca]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer:always
basicConstraints = critical,CA:true
keyUsage = critical,digitalSignature,cRLSign,keyCertSign
"@
    
    $CaConfig | Out-File -FilePath $CaConfigPath -Encoding UTF8
    
    # 生成CA私钥
    $OpenSslCmd = "openssl genrsa -out `"$CaKeyPath`" 4096"
    Write-Log "执行命令: $OpenSslCmd"
    Invoke-Expression $OpenSslCmd
    
    # 生成CA证书
    $OpenSslCmd = "openssl req -new -x509 -days $ValidDays -key `"$CaKeyPath`" -out `"$CaCertPath`" -config `"$CaConfigPath`""
    Write-Log "执行命令: $OpenSslCmd"
    Invoke-Expression $OpenSslCmd
    
    Write-Log "CA根证书生成完成: $CaCertPath"
}

# 函数：生成服务证书
function New-ServiceCert {
    Write-Log "生成服务证书..."
    
    $CaKeyPath = Join-Path $CertsDir "ca-key.pem"
    $CaCertPath = Join-Path $CertsDir "ca-cert.pem"
    $CertKeyPath = Join-Path $CertsDir "key.pem"
    $CertPath = Join-Path $CertsDir "cert.pem"
    $CsrPath = Join-Path $CertsDir "cert.csr"
    $CertConfigPath = Join-Path $ConfigDir "cert.conf"
    
    # 检查是否已存在且不强制重新生成
    if ((Test-Path $CertPath) -and (-not $Force)) {
        Write-Log "服务证书已存在，跳过生成" "WARN"
        return
    }
    
    # 创建SAN列表
    $SanList = @()
    $SanList += "DNS:localhost"
    $SanList += "DNS:127.0.0.1"
    $SanList += "IP:127.0.0.1"
    $SanList += "IP:::1"
    
    foreach ($ServiceDomain in $ServiceDomains) {
        $SanList += "DNS:$ServiceDomain"
    }
    
    $SanString = $SanList -join ","
    
    # 创建证书配置文件
    $CertConfig = @"
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = $($CertConfig.Country)
ST = $($CertConfig.State)
L = $($CertConfig.City)
O = $($CertConfig.Organization)
OU = $($CertConfig.OrganizationalUnit)
CN = $($CertConfig.CommonName)
emailAddress = $($CertConfig.Email)

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation,digitalSignature,keyEncipherment
subjectAltName = $SanString

[v3_ca]
subjectAltName = $SanString
"@
    
    $CertConfig | Out-File -FilePath $CertConfigPath -Encoding UTF8
    
    # 生成服务私钥
    $OpenSslCmd = "openssl genrsa -out `"$CertKeyPath`" 2048"
    Write-Log "执行命令: $OpenSslCmd"
    Invoke-Expression $OpenSslCmd
    
    # 生成证书签名请求
    $OpenSslCmd = "openssl req -new -key `"$CertKeyPath`" -out `"$CsrPath`" -config `"$CertConfigPath`""
    Write-Log "执行命令: $OpenSslCmd"
    Invoke-Expression $OpenSslCmd
    
    # 使用CA签名生成证书
    $OpenSslCmd = "openssl x509 -req -in `"$CsrPath`" -CA `"$CaCertPath`" -CAkey `"$CaKeyPath`" -CAcreateserial -out `"$CertPath`" -days $ValidDays -extensions v3_ca -extfile `"$CertConfigPath`""
    Write-Log "执行命令: $OpenSslCmd"
    Invoke-Expression $OpenSslCmd
    
    # 清理临时文件
    Remove-Item $CsrPath -Force -ErrorAction SilentlyContinue
    
    Write-Log "服务证书生成完成: $CertPath"
}

# 函数：验证证书
function Test-Certificate {
    param([string]$CertPath)
    
    Write-Log "验证证书: $CertPath"
    
    try {
        $OpenSslCmd = "openssl x509 -in `"$CertPath`" -text -noout"
        $CertInfo = Invoke-Expression $OpenSslCmd
        
        Write-Log "证书验证成功"
        return $true
    }
    catch {
        Write-Log "证书验证失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# 函数：设置证书权限
function Set-CertificatePermissions {
    Write-Log "设置证书文件权限..."
    
    $CertFiles = Get-ChildItem -Path $CertsDir -Filter "*.pem"
    
    foreach ($CertFile in $CertFiles) {
        # 设置文件为只读
        $CertFile.IsReadOnly = $true
        
        # 移除继承权限（Windows）
        try {
            $Acl = Get-Acl $CertFile.FullName
            $Acl.SetAccessRuleProtection($true, $false)
            
            # 添加管理员完全控制权限
            $AdminRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                "Administrators", "FullControl", "Allow"
            )
            $Acl.SetAccessRule($AdminRule)
            
            # 添加当前用户读取权限
            $UserRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                $env:USERNAME, "Read", "Allow"
            )
            $Acl.SetAccessRule($UserRule)
            
            Set-Acl -Path $CertFile.FullName -AclObject $Acl
            Write-Log "设置权限: $($CertFile.Name)"
        }
        catch {
            Write-Log "设置权限失败: $($CertFile.Name) - $($_.Exception.Message)" "WARN"
        }
    }
}

# 函数：生成证书信息文件
function New-CertificateInfo {
    Write-Log "生成证书信息文件..."
    
    $InfoPath = Join-Path $CertsDir "cert-info.txt"
    $CertPath = Join-Path $CertsDir "cert.pem"
    
    if (Test-Path $CertPath) {
        $CertInfo = openssl x509 -in "$CertPath" -text -noout
        $CertInfo | Out-File -FilePath $InfoPath -Encoding UTF8
        Write-Log "证书信息已保存: $InfoPath"
    }
}

# 主函数
function Main {
    Write-Log "开始生成Traefik SSL证书..."
    Write-Log "域名: $Domain"
    Write-Log "有效期: $ValidDays 天"
    Write-Log "强制重新生成: $Force"
    
    try {
        # 检查OpenSSL
        if (-not (Test-OpenSSL)) {
            Install-OpenSSL
            
            # 重新检查
            if (-not (Test-OpenSSL)) {
                throw "OpenSSL安装失败或不可用"
            }
        }
        
        Write-Log "OpenSSL版本: $(openssl version)"
        
        # 创建必要目录
        New-Directory $CertsDir
        New-Directory $ConfigDir
        
        # 生成证书
        New-RootCA
        New-ServiceCert
        
        # 验证证书
        $CertPath = Join-Path $CertsDir "cert.pem"
        if (Test-Certificate $CertPath) {
            Write-Log "证书生成并验证成功" "SUCCESS"
        } else {
            throw "证书验证失败"
        }
        
        # 设置权限
        Set-CertificatePermissions
        
        # 生成信息文件
        New-CertificateInfo
        
        Write-Log "SSL证书生成完成！" "SUCCESS"
        Write-Log "证书位置: $CertsDir"
        Write-Log "请将CA证书 (ca-cert.pem) 添加到系统信任存储中"
        
    }
    catch {
        Write-Log "SSL证书生成失败: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

# 执行主函数
Main