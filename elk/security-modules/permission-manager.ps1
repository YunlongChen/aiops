#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ELK安全权限管理模块
    
.DESCRIPTION
    包含权限配置、访问控制、索引权限管理等功能
#>

<#
.SYNOPSIS
    配置索引权限
#>
function Set-IndexPermissions {
    param(
        [string]$IndexPattern,
        [string[]]$Users = @(),
        [string[]]$Roles = @(),
        [string[]]$Privileges = @("read"),
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "配置索引 $IndexPattern 权限" "INFO"
    
    # 为每个用户配置权限
    foreach ($user in $Users) {
        $userInfo = Get-ElasticsearchUser -Username $user -ElasticsearchUrl $ElasticsearchUrl
        if ($userInfo) {
            # 创建临时角色用于索引权限
            $tempRoleName = "temp_${user}_${IndexPattern}_role".Replace("*", "wildcard").Replace("-", "_")
            
            $indexPrivileges = @(
                @{
                    names = @($IndexPattern)
                    privileges = $Privileges
                }
            )
            
            if (New-ElasticsearchRole -RoleName $tempRoleName -IndexPrivileges $indexPrivileges -ElasticsearchUrl $ElasticsearchUrl) {
                Add-ElasticsearchUserRole -Username $user -Roles @($tempRoleName) -ElasticsearchUrl $ElasticsearchUrl
                Write-Log "为用户 $user 配置索引 $IndexPattern 权限成功" "INFO"
            }
        }
    }
    
    # 为每个角色配置权限
    foreach ($role in $Roles) {
        $indexPrivileges = @(
            @{
                names = @($IndexPattern)
                privileges = $Privileges
            }
        )
        
        # 更新现有角色或创建新角色
        if (New-ElasticsearchRole -RoleName $role -IndexPrivileges $indexPrivileges -ElasticsearchUrl $ElasticsearchUrl) {
            Write-Log "为角色 $role 配置索引 $IndexPattern 权限成功" "INFO"
        }
    }
}

<#
.SYNOPSIS
    配置集群权限
#>
function Set-ClusterPermissions {
    param(
        [string]$RoleName,
        [string[]]$ClusterPrivileges = @("monitor"),
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "配置角色 $RoleName 集群权限" "INFO"
    
    try {
        if (New-ElasticsearchRole -RoleName $RoleName -ClusterPrivileges $ClusterPrivileges -ElasticsearchUrl $ElasticsearchUrl) {
            Write-Log "角色 $RoleName 集群权限配置成功" "INFO"
            return $true
        } else {
            Write-Log "角色 $RoleName 集群权限配置失败" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "配置集群权限时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    创建数据访问策略
#>
function New-DataAccessPolicy {
    param(
        [string]$PolicyName,
        [hashtable[]]$IndexRules = @(),
        [string[]]$AllowedUsers = @(),
        [string[]]$DeniedUsers = @(),
        [string]$TimeRestriction = "",
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "创建数据访问策略: $PolicyName" "INFO"
    
    # 创建策略角色
    $policyRoleName = "policy_$PolicyName"
    
    $indexPrivileges = @()
    foreach ($rule in $IndexRules) {
        $indexPrivileges += @{
            names = $rule.Indices
            privileges = $rule.Privileges
            query = $rule.Query
            field_security = $rule.FieldSecurity
        }
    }
    
    try {
        # 创建角色
        if (New-ElasticsearchRole -RoleName $policyRoleName -IndexPrivileges $indexPrivileges -ElasticsearchUrl $ElasticsearchUrl) {
            # 为允许的用户分配角色
            foreach ($user in $AllowedUsers) {
                Add-ElasticsearchUserRole -Username $user -Roles @($policyRoleName) -ElasticsearchUrl $ElasticsearchUrl
            }
            
            # 保存策略信息
            $policyInfo = @{
                PolicyName = $PolicyName
                RoleName = $policyRoleName
                IndexRules = $IndexRules
                AllowedUsers = $AllowedUsers
                DeniedUsers = $DeniedUsers
                TimeRestriction = $TimeRestriction
                CreatedAt = Get-Date
            }
            
            $policyFile = "policies\$PolicyName.json"
            if (-not (Test-Path "policies")) {
                New-Item -ItemType Directory -Path "policies" -Force | Out-Null
            }
            
            $policyInfo | ConvertTo-Json -Depth 4 | Out-File -FilePath $policyFile -Encoding UTF8
            
            Write-Log "数据访问策略 $PolicyName 创建成功" "INFO"
            return $true
        }
    }
    catch {
        Write-Log "创建数据访问策略时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    配置字段级安全
#>
function Set-FieldLevelSecurity {
    param(
        [string]$RoleName,
        [string]$IndexPattern,
        [string[]]$GrantedFields = @(),
        [string[]]$ExceptFields = @(),
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "配置角色 $RoleName 字段级安全" "INFO"
    
    $fieldSecurity = @{}
    
    if ($GrantedFields.Count -gt 0) {
        $fieldSecurity.grant = $GrantedFields
    }
    
    if ($ExceptFields.Count -gt 0) {
        $fieldSecurity.except = $ExceptFields
    }
    
    $indexPrivileges = @(
        @{
            names = @($IndexPattern)
            privileges = @("read")
            field_security = $fieldSecurity
        }
    )
    
    try {
        if (New-ElasticsearchRole -RoleName $RoleName -IndexPrivileges $indexPrivileges -ElasticsearchUrl $ElasticsearchUrl) {
            Write-Log "角色 $RoleName 字段级安全配置成功" "INFO"
            return $true
        } else {
            Write-Log "角色 $RoleName 字段级安全配置失败" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "配置字段级安全时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    配置文档级安全
#>
function Set-DocumentLevelSecurity {
    param(
        [string]$RoleName,
        [string]$IndexPattern,
        [string]$Query,
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "配置角色 $RoleName 文档级安全" "INFO"
    
    $indexPrivileges = @(
        @{
            names = @($IndexPattern)
            privileges = @("read")
            query = $Query
        }
    )
    
    try {
        if (New-ElasticsearchRole -RoleName $RoleName -IndexPrivileges $indexPrivileges -ElasticsearchUrl $ElasticsearchUrl) {
            Write-Log "角色 $RoleName 文档级安全配置成功" "INFO"
            return $true
        } else {
            Write-Log "角色 $RoleName 文档级安全配置失败" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "配置文档级安全时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    检查用户权限
#>
function Test-UserPermissions {
    param(
        [string]$Username,
        [string]$IndexName,
        [string[]]$RequiredPrivileges = @("read"),
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "检查用户 $Username 对索引 $IndexName 的权限" "INFO"
    
    try {
        # 获取用户信息
        $userInfo = Get-ElasticsearchUser -Username $Username -ElasticsearchUrl $ElasticsearchUrl
        
        if (-not $userInfo) {
            Write-Log "用户 $Username 不存在" "ERROR"
            return $false
        }
        
        # 检查用户角色权限
        $hasPermission = $false
        
        foreach ($role in $userInfo.roles) {
            # 获取角色信息
            $roleResponse = Invoke-ApiRequest -Method "GET" -Uri "$ElasticsearchUrl/_security/role/$role"
            
            if ($roleResponse.$role) {
                $roleInfo = $roleResponse.$role
                
                # 检查集群权限
                if ($roleInfo.cluster -contains "all" -or $roleInfo.cluster -contains "superuser") {
                    $hasPermission = $true
                    break
                }
                
                # 检查索引权限
                foreach ($indexPriv in $roleInfo.indices) {
                    $indexMatches = $false
                    
                    foreach ($indexPattern in $indexPriv.names) {
                        if ($IndexName -like $indexPattern -or $indexPattern -eq "*") {
                            $indexMatches = $true
                            break
                        }
                    }
                    
                    if ($indexMatches) {
                        $hasAllPrivileges = $true
                        foreach ($requiredPriv in $RequiredPrivileges) {
                            if ($indexPriv.privileges -notcontains $requiredPriv -and $indexPriv.privileges -notcontains "all") {
                                $hasAllPrivileges = $false
                                break
                            }
                        }
                        
                        if ($hasAllPrivileges) {
                            $hasPermission = $true
                            break
                        }
                    }
                }
                
                if ($hasPermission) {
                    break
                }
            }
        }
        
        if ($hasPermission) {
            Write-Log "用户 $Username 对索引 $IndexName 具有所需权限" "INFO"
        } else {
            Write-Log "用户 $Username 对索引 $IndexName 缺少所需权限" "WARN"
        }
        
        return $hasPermission
    }
    catch {
        Write-Log "检查用户权限时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    生成权限报告
#>
function Get-PermissionsReport {
    param(
        [string]$ElasticsearchUrl = "https://localhost:9200",
        [string]$OutputPath = "permissions-report.html"
    )
    
    Write-Log "生成权限报告" "INFO"
    
    try {
        # 获取所有用户和角色
        $users = Get-ElasticsearchUsers -ElasticsearchUrl $ElasticsearchUrl
        $roles = Get-ElasticsearchRoles -ElasticsearchUrl $ElasticsearchUrl
        
        # 生成HTML报告
        $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>ELK权限报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .section { margin-bottom: 30px; }
        .role-list { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>ELK权限报告</h1>
    <p>生成时间: $(Get-Date)</p>
    
    <div class="section">
        <h2>用户权限概览</h2>
        <table>
            <tr>
                <th>用户名</th>
                <th>全名</th>
                <th>邮箱</th>
                <th>角色</th>
            </tr>
"@
        
        foreach ($userKey in $users.PSObject.Properties.Name) {
            $user = $users.$userKey
            $rolesStr = ($user.roles -join ", ")
            $html += @"
            <tr>
                <td>$userKey</td>
                <td>$($user.full_name)</td>
                <td>$($user.email)</td>
                <td class="role-list">$rolesStr</td>
            </tr>
"@
        }
        
        $html += @"
        </table>
    </div>
    
    <div class="section">
        <h2>角色权限详情</h2>
        <table>
            <tr>
                <th>角色名</th>
                <th>集群权限</th>
                <th>索引权限</th>
            </tr>
"@
        
        foreach ($roleKey in $roles.PSObject.Properties.Name) {
            $role = $roles.$roleKey
            $clusterPrivs = ($role.cluster -join ", ")
            
            $indexPrivsStr = ""
            if ($role.indices) {
                $indexPrivsList = @()
                foreach ($indexPriv in $role.indices) {
                    $names = ($indexPriv.names -join ", ")
                    $privs = ($indexPriv.privileges -join ", ")
                    $indexPrivsList += "$names ($privs)"
                }
                $indexPrivsStr = ($indexPrivsList -join "; ")
            }
            
            $html += @"
            <tr>
                <td>$roleKey</td>
                <td>$clusterPrivs</td>
                <td>$indexPrivsStr</td>
            </tr>
"@
        }
        
        $html += @"
        </table>
    </div>
</body>
</html>
"@
        
        # 保存报告
        $html | Out-File -FilePath $OutputPath -Encoding UTF8
        
        Write-Log "权限报告已生成: $OutputPath" "INFO"
        return $true
    }
    catch {
        Write-Log "生成权限报告时出错: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    审计权限变更
#>
function Write-PermissionAuditLog {
    param(
        [string]$Action,
        [string]$Target,
        [string]$Details,
        [string]$User = $env:USERNAME
    )
    
    $auditEntry = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        User = $User
        Action = $Action
        Target = $Target
        Details = $Details
    }
    
    $auditLogPath = "security-audit.log"
    $logEntry = "[$($auditEntry.Timestamp)] $($auditEntry.User) - $($auditEntry.Action) - $($auditEntry.Target) - $($auditEntry.Details)"
    
    Add-Content -Path $auditLogPath -Value $logEntry -Encoding UTF8
    Write-Log "权限审计日志已记录" "DEBUG"
}

<#
.SYNOPSIS
    清理过期权限
#>
function Remove-ExpiredPermissions {
    param(
        [int]$DaysOld = 90,
        [string]$ElasticsearchUrl = "https://localhost:9200"
    )
    
    Write-Log "清理 $DaysOld 天前的过期权限" "INFO"
    
    try {
        # 获取所有角色
        $roles = Get-ElasticsearchRoles -ElasticsearchUrl $ElasticsearchUrl
        $cutoffDate = (Get-Date).AddDays(-$DaysOld)
        
        $removedRoles = @()
        
        foreach ($roleKey in $roles.PSObject.Properties.Name) {
            # 检查是否为临时角色（以temp_开头）
            if ($roleKey.StartsWith("temp_")) {
                # 这里可以添加更复杂的过期逻辑
                # 目前简单地移除所有临时角色
                try {
                    $response = Invoke-ApiRequest -Method "DELETE" -Uri "$ElasticsearchUrl/_security/role/$roleKey"
                    if ($response.found -eq $true) {
                        $removedRoles += $roleKey
                        Write-PermissionAuditLog -Action "REMOVE_EXPIRED_ROLE" -Target $roleKey -Details "Removed expired temporary role"
                    }
                }
                catch {
                    Write-Log "删除过期角色 $roleKey 时出错: $($_.Exception.Message)" "ERROR"
                }
            }
        }
        
        Write-Log "已清理 $($removedRoles.Count) 个过期权限" "INFO"
        return $removedRoles
    }
    catch {
        Write-Log "清理过期权限时出错: $($_.Exception.Message)" "ERROR"
        return @()
    }
}