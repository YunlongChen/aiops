#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ELK安全用户管理模块
    
.DESCRIPTION
    包含用户创建、角色分配、权限管理等功能
#>

<#
.SYNOPSIS
    创建Elasticsearch用户
#>
function New-ElasticsearchUser {
    param(
        [string]$Username,
        [string]$Password,
        [string[]]$Roles = @("kibana_user"),
        [string]$FullName = "",
        [string]$Email = "",
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "创建Elasticsearch用户: $Username" "INFO"
    
    $userBody = @{
        password = $Password
        roles = $Roles
    }
    
    if ($FullName) {
        $userBody.full_name = $FullName
    }
    
    if ($Email) {
        $userBody.email = $Email
    }
    
    try {
        $response = Invoke-ApiRequest -Method "POST" -Uri "$ElasticsearchUrl/_security/user/$Username" -Body ($userBody | ConvertTo-Json) -ContentType "application/json"
        
        if ($response.created -eq $true) {
            Write-Log "用户 $Username 创建成功" "INFO"
            return $true
        } else {
            Write-Log "用户 $Username 创建失败" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "创建用户时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    创建Elasticsearch角色
#>
function New-ElasticsearchRole {
    param(
        [string]$RoleName,
        [hashtable]$ClusterPrivileges = @(),
        [hashtable[]]$IndexPrivileges = @(),
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "创建Elasticsearch角色: $RoleName" "INFO"
    
    $roleBody = @{
        cluster = $ClusterPrivileges
        indices = $IndexPrivileges
    }
    
    try {
        $response = Invoke-ApiRequest -Method "POST" -Uri "$ElasticsearchUrl/_security/role/$RoleName" -Body ($roleBody | ConvertTo-Json -Depth 3) -ContentType "application/json"
        
        if ($response.role -and $response.role.created -eq $true) {
            Write-Log "角色 $RoleName 创建成功" "INFO"
            return $true
        } else {
            Write-Log "角色 $RoleName 创建失败" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "创建角色时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    获取用户信息
#>
function Get-ElasticsearchUser {
    param(
        [string]$Username,
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    try {
        $response = Invoke-ApiRequest -Method "GET" -Uri "$ElasticsearchUrl/_security/user/$Username"
        
        if ($response.$Username) {
            Write-Log "获取用户 $Username 信息成功" "INFO"
            return $response.$Username
        } else {
            Write-Log "用户 $Username 不存在" "WARN"
            return $null
        }
    }
    catch {
        Write-Log "获取用户信息时出错: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

<#
.SYNOPSIS
    更新用户密码
#>
function Set-ElasticsearchUserPassword {
    param(
        [string]$Username,
        [string]$NewPassword,
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "更新用户 $Username 密码" "INFO"
    
    $passwordBody = @{
        password = $NewPassword
    }
    
    try {
        $response = Invoke-ApiRequest -Method "POST" -Uri "$ElasticsearchUrl/_security/user/$Username/_password" -Body ($passwordBody | ConvertTo-Json) -ContentType "application/json"
        
        Write-Log "用户 $Username 密码更新成功" "INFO"
        return $true
    }
    catch {
        Write-Log "更新用户密码时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    分配角色给用户
#>
function Add-ElasticsearchUserRole {
    param(
        [string]$Username,
        [string[]]$Roles,
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "为用户 $Username 分配角色: $($Roles -join ', ')" "INFO"
    
    # 获取当前用户信息
    $currentUser = Get-ElasticsearchUser -Username $Username -ElasticsearchUrl $ElasticsearchUrl
    
    if (-not $currentUser) {
        Write-Log "用户 $Username 不存在" "ERROR"
        return $false
    }
    
    # 合并现有角色和新角色
    $allRoles = @($currentUser.roles) + $Roles | Sort-Object -Unique
    
    $userBody = @{
        roles = $allRoles
    }
    
    # 保留其他用户属性
    if ($currentUser.full_name) {
        $userBody.full_name = $currentUser.full_name
    }
    
    if ($currentUser.email) {
        $userBody.email = $currentUser.email
    }
    
    try {
        $response = Invoke-ApiRequest -Method "PUT" -Uri "$ElasticsearchUrl/_security/user/$Username" -Body ($userBody | ConvertTo-Json) -ContentType "application/json"
        
        Write-Log "用户 $Username 角色分配成功" "INFO"
        return $true
    }
    catch {
        Write-Log "分配用户角色时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    移除用户角色
#>
function Remove-ElasticsearchUserRole {
    param(
        [string]$Username,
        [string[]]$Roles,
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "从用户 $Username 移除角色: $($Roles -join ', ')" "INFO"
    
    # 获取当前用户信息
    $currentUser = Get-ElasticsearchUser -Username $Username -ElasticsearchUrl $ElasticsearchUrl
    
    if (-not $currentUser) {
        Write-Log "用户 $Username 不存在" "ERROR"
        return $false
    }
    
    # 移除指定角色
    $remainingRoles = $currentUser.roles | Where-Object { $_ -notin $Roles }
    
    $userBody = @{
        roles = $remainingRoles
    }
    
    # 保留其他用户属性
    if ($currentUser.full_name) {
        $userBody.full_name = $currentUser.full_name
    }
    
    if ($currentUser.email) {
        $userBody.email = $currentUser.email
    }
    
    try {
        $response = Invoke-ApiRequest -Method "PUT" -Uri "$ElasticsearchUrl/_security/user/$Username" -Body ($userBody | ConvertTo-Json) -ContentType "application/json"
        
        Write-Log "用户 $Username 角色移除成功" "INFO"
        return $true
    }
    catch {
        Write-Log "移除用户角色时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    删除用户
#>
function Remove-ElasticsearchUser {
    param(
        [string]$Username,
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "删除用户: $Username" "INFO"
    
    try {
        $response = Invoke-ApiRequest -Method "DELETE" -Uri "$ElasticsearchUrl/_security/user/$Username"
        
        if ($response.found -eq $true) {
            Write-Log "用户 $Username 删除成功" "INFO"
            return $true
        } else {
            Write-Log "用户 $Username 不存在" "WARN"
            return $false
        }
    }
    catch {
        Write-Log "删除用户时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    列出所有用户
#>
function Get-ElasticsearchUsers {
    param(
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    try {
        $response = Invoke-ApiRequest -Method "GET" -Uri "$ElasticsearchUrl/_security/user"
        
        Write-Log "获取用户列表成功" "INFO"
        return $response
    }
    catch {
        Write-Log "获取用户列表时出错: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

<#
.SYNOPSIS
    列出所有角色
#>
function Get-ElasticsearchRoles {
    param(
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    try {
        $response = Invoke-ApiRequest -Method "GET" -Uri "$ElasticsearchUrl/_security/role"
        
        Write-Log "获取角色列表成功" "INFO"
        return $response
    }
    catch {
        Write-Log "获取角色列表时出错: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

<#
.SYNOPSIS
    创建默认用户和角色
#>
function Initialize-DefaultUsersAndRoles {
    param(
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "初始化默认用户和角色" "INFO"
    
    # 创建自定义角色
    $customRoles = @(
        @{
            Name = "aiops_admin"
            ClusterPrivileges = @("all")
            IndexPrivileges = @(
                @{
                    names = @("*")
                    privileges = @("all")
                }
            )
        },
        @{
            Name = "aiops_user"
            ClusterPrivileges = @("monitor")
            IndexPrivileges = @(
                @{
                    names = @("logs-*", "metrics-*", "traces-*")
                    privileges = @("read", "view_index_metadata")
                }
            )
        },
        @{
            Name = "aiops_developer"
            ClusterPrivileges = @("monitor", "manage_index_templates")
            IndexPrivileges = @(
                @{
                    names = @("dev-*", "test-*")
                    privileges = @("all")
                },
                @{
                    names = @("logs-*", "metrics-*")
                    privileges = @("read", "write", "create_index")
                }
            )
        }
    )
    
    # 创建角色
    foreach ($role in $customRoles) {
        New-ElasticsearchRole -RoleName $role.Name -ClusterPrivileges $role.ClusterPrivileges -IndexPrivileges $role.IndexPrivileges -ElasticsearchUrl $ElasticsearchUrl
    }
    
    # 创建默认用户
    $defaultUsers = @(
        @{
            Username = "aiops_admin"
            Password = (New-RandomPassword -Length 16)
            Roles = @("superuser", "aiops_admin")
            FullName = "AIOps Administrator"
            Email = "admin@aiops.local"
        },
        @{
            Username = "aiops_user"
            Password = (New-RandomPassword -Length 12)
            Roles = @("aiops_user", "kibana_user")
            FullName = "AIOps User"
            Email = "user@aiops.local"
        },
        @{
            Username = "aiops_developer"
            Password = (New-RandomPassword -Length 14)
            Roles = @("aiops_developer", "kibana_user")
            FullName = "AIOps Developer"
            Email = "developer@aiops.local"
        }
    )
    
    # 创建用户
    $createdUsers = @()
    foreach ($user in $defaultUsers) {
        if (New-ElasticsearchUser -Username $user.Username -Password $user.Password -Roles $user.Roles -FullName $user.FullName -Email $user.Email -ElasticsearchUrl $ElasticsearchUrl) {
            $createdUsers += @{
                Username = $user.Username
                Password = $user.Password
                Roles = $user.Roles
                FullName = $user.FullName
                Email = $user.Email
            }
        }
    }
    
    # 保存用户凭据到文件
    if ($createdUsers.Count -gt 0) {
        $credentialsFile = "security-credentials.json"
        $createdUsers | ConvertTo-Json -Depth 3 | Out-File -FilePath $credentialsFile -Encoding UTF8
        Write-Log "用户凭据已保存到: $credentialsFile" "INFO"
    }
    
    Write-Log "默认用户和角色初始化完成" "INFO"
    return $createdUsers
}

<#
.SYNOPSIS
    验证用户认证
#>
function Test-ElasticsearchUserAuth {
    param(
        [string]$Username,
        [string]$Password,
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "验证用户 $Username 认证" "INFO"
    
    try {
        # 使用用户凭据进行认证测试
        $credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$Username`:$Password"))
        $headers = @{
            "Authorization" = "Basic $credentials"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri "$ElasticsearchUrl/_security/_authenticate" -Method GET -Headers $headers -SkipCertificateCheck
        
        if ($response.username -eq $Username) {
            Write-Log "用户 $Username 认证成功" "INFO"
            return $true
        } else {
            Write-Log "用户 $Username 认证失败" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "验证用户认证时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    重置用户密码
#>
function Reset-ElasticsearchUserPassword {
    param(
        [string]$Username,
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "重置用户 $Username 密码" "INFO"
    
    # 生成新密码
    $newPassword = New-RandomPassword -Length 12
    
    if (Set-ElasticsearchUserPassword -Username $Username -NewPassword $newPassword -ElasticsearchUrl $ElasticsearchUrl) {
        Write-Log "用户 $Username 密码重置成功，新密码: $newPassword" "INFO"
        
        # 保存新密码到文件
        $passwordResetFile = "password-reset-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
        "用户: $Username`n新密码: $newPassword`n重置时间: $(Get-Date)" | Out-File -FilePath $passwordResetFile -Encoding UTF8
        
        return @{
            Username = $Username
            NewPassword = $newPassword
            ResetTime = Get-Date
        }
    } else {
        Write-Log "用户 $Username 密码重置失败" "ERROR"
        return $null
    }
}