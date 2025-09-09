#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ELK安全证书管理模块
    
.DESCRIPTION
    包含SSL/TLS证书生成、管理和配置功能
#>

<#
.SYNOPSIS
    初始化证书目录结构
#>
function Initialize-CertificateDirectory {
    param(
        [string]$CertPath = "certs"
    )
    
    Write-Log "初始化证书目录结构" "INFO"
    
    $certDirs = @(
        $CertPath,
        "$CertPath/ca",
        "$CertPath/elasticsearch",
        "$CertPath/kibana",
        "$CertPath/logstash",
        "$CertPath/beats"
    )
    
    foreach ($dir in $certDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Log "创建目录: $dir" "DEBUG"
        }
    }
}

<#
.SYNOPSIS
    生成CA根证书
#>
function New-CACertificate {
    param(
        [string]$CertPath = "certs",
        [string]$Domain = "localhost",
        [switch]$Force
    )
    
    Write-Log "生成CA根证书" "INFO"
    
    $caKeyPath = "$CertPath/ca/ca-key.pem"
    $caCertPath = "$CertPath/ca/ca-cert.pem"
    
    # 检查是否已存在CA证书
    if ((Test-Path $caKeyPath) -and (Test-Path $caCertPath) -and -not $Force) {
        Write-Log "CA证书已存在，跳过生成" "INFO"
        return $true
    }
    
    try {
        # 使用OpenSSL生成CA证书（如果可用）
        if (Get-Command openssl -ErrorAction SilentlyContinue) {
            # 生成CA私钥
            & openssl genrsa -out $caKeyPath 4096
            
            # 生成CA证书
            & openssl req -new -x509 -days 365 -key $caKeyPath -out $caCertPath -subj "/C=CN/ST=Beijing/L=Beijing/O=AIOps/OU=IT/CN=AIOps-CA"
            
            Write-Log "CA证书生成成功" "INFO"
            return $true
        } else {
            Write-Log "OpenSSL未安装，使用PowerShell生成自签名证书" "WARN"
            
            # 使用PowerShell生成自签名证书
            $cert = New-SelfSignedCertificate -DnsName "AIOps-CA" -CertStoreLocation "cert:\LocalMachine\My" -KeyUsage CertSign -KeySpec Signature -KeyLength 4096 -KeyAlgorithm RSA -HashAlgorithm SHA256 -Provider "Microsoft Enhanced RSA and AES Cryptographic Provider" -Subject "CN=AIOps-CA, O=AIOps, C=CN"
            
            # 导出证书
            Export-Certificate -Cert $cert -FilePath $caCertPath -Type CERT
            
            # 导出私钥（需要密码保护）
            $password = ConvertTo-SecureString -String "changeme" -Force -AsPlainText
            Export-PfxCertificate -Cert $cert -FilePath "$CertPath/ca/ca.pfx" -Password $password
            
            Write-Log "自签名CA证书生成成功" "INFO"
            return $true
        }
    }
    catch {
        Write-Log "生成CA证书失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    生成服务证书
#>
function New-ServiceCertificate {
    param(
        [string]$ServiceName,
        [string]$Domain = "localhost",
        [string]$CertPath = "certs",
        [switch]$Force
    )
    
    Write-Log "为 $ServiceName 生成服务证书" "INFO"
    
    $serviceKeyPath = "$CertPath/$ServiceName/$ServiceName-key.pem"
    $serviceCertPath = "$CertPath/$ServiceName/$ServiceName-cert.pem"
    $serviceCsrPath = "$CertPath/$ServiceName/$ServiceName.csr"
    
    # 检查是否已存在服务证书
    if ((Test-Path $serviceKeyPath) -and (Test-Path $serviceCertPath) -and -not $Force) {
        Write-Log "$ServiceName 证书已存在，跳过生成" "INFO"
        return $true
    }
    
    try {
        if (Get-Command openssl -ErrorAction SilentlyContinue) {
            # 生成服务私钥
            & openssl genrsa -out $serviceKeyPath 2048
            
            # 生成证书签名请求
            & openssl req -new -key $serviceKeyPath -out $serviceCsrPath -subj "/C=CN/ST=Beijing/L=Beijing/O=AIOps/OU=IT/CN=$Domain"
            
            # 使用CA签名生成服务证书
            $caKeyPath = "$CertPath/ca/ca-key.pem"
            $caCertPath = "$CertPath/ca/ca-cert.pem"
            
            if ((Test-Path $caKeyPath) -and (Test-Path $caCertPath)) {
                & openssl x509 -req -in $serviceCsrPath -CA $caCertPath -CAkey $caKeyPath -CAcreateserial -out $serviceCertPath -days 365
                
                # 清理CSR文件
                Remove-Item $serviceCsrPath -Force -ErrorAction SilentlyContinue
                
                Write-Log "$ServiceName 证书生成成功" "INFO"
                return $true
            } else {
                Write-Log "CA证书不存在，请先生成CA证书" "ERROR"
                return $false
            }
        } else {
            Write-Log "OpenSSL未安装，使用PowerShell生成自签名证书" "WARN"
            
            # 使用PowerShell生成自签名证书
            $cert = New-SelfSignedCertificate -DnsName $Domain -CertStoreLocation "cert:\LocalMachine\My" -KeyLength 2048 -KeyAlgorithm RSA -HashAlgorithm SHA256 -Subject "CN=$Domain, O=AIOps, C=CN"
            
            # 导出证书
            Export-Certificate -Cert $cert -FilePath $serviceCertPath -Type CERT
            
            Write-Log "$ServiceName 自签名证书生成成功" "INFO"
            return $true
        }
    }
    catch {
        Write-Log "生成 $ServiceName 证书失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    生成所有安全证书
#>
function New-SecurityCertificates {
    param(
        [string]$Domain = "localhost",
        [string]$CertPath = "certs",
        [switch]$Force
    )
    
    Write-Log "开始生成ELK安全证书" "INFO"
    
    # 初始化证书目录
    Initialize-CertificateDirectory -CertPath $CertPath
    
    # 生成CA证书
    if (-not (New-CACertificate -CertPath $CertPath -Domain $Domain -Force:$Force)) {
        Write-Log "CA证书生成失败" "ERROR"
        return $false
    }
    
    # 生成各服务证书
    $services = @("elasticsearch", "kibana", "logstash", "beats")
    
    foreach ($service in $services) {
        if (-not (New-ServiceCertificate -ServiceName $service -Domain $Domain -CertPath $CertPath -Force:$Force)) {
            Write-Log "$service 证书生成失败" "ERROR"
            return $false
        }
    }
    
    Write-Log "所有ELK安全证书生成完成" "INFO"
    return $true
}

<#
.SYNOPSIS
    验证证书有效性
#>
function Test-Certificate {
    param(
        [string]$CertificatePath
    )
    
    if (-not (Test-Path $CertificatePath)) {
        Write-Log "证书文件不存在: $CertificatePath" "ERROR"
        return $false
    }
    
    try {
        if (Get-Command openssl -ErrorAction SilentlyContinue) {
            # 使用OpenSSL验证证书
            $result = & openssl x509 -in $CertificatePath -text -noout 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Log "证书验证成功: $CertificatePath" "INFO"
                return $true
            } else {
                Write-Log "证书验证失败: $CertificatePath" "ERROR"
                return $false
            }
        } else {
            # 简单的文件存在性检查
            Write-Log "证书文件存在: $CertificatePath" "INFO"
            return $true
        }
    }
    catch {
        Write-Log "验证证书时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    获取证书信息
#>
function Get-CertificateInfo {
    param(
        [string]$CertificatePath
    )
    
    if (-not (Test-Path $CertificatePath)) {
        Write-Log "证书文件不存在: $CertificatePath" "ERROR"
        return $null
    }
    
    try {
        if (Get-Command openssl -ErrorAction SilentlyContinue) {
            # 使用OpenSSL获取证书信息
            $subject = & openssl x509 -in $CertificatePath -subject -noout
            $issuer = & openssl x509 -in $CertificatePath -issuer -noout
            $dates = & openssl x509 -in $CertificatePath -dates -noout
            
            return @{
                Subject = $subject
                Issuer = $issuer
                Dates = $dates
                Path = $CertificatePath
            }
        } else {
            return @{
                Path = $CertificatePath
                Status = "Available"
            }
        }
    }
    catch {
        Write-Log "获取证书信息时出错: $($_.Exception.Message)" "ERROR"
        return $null
    }
}