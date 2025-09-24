# 批量更新HTML文件中的在线资源引用为本地资源
$htmlFiles = Get-ChildItem -Name "*.html" | Where-Object { $_ -ne "demo.html" }

foreach ($file in $htmlFiles) {
    Write-Host "正在更新 $file..."
    
    # 读取文件内容
    $content = Get-Content $file -Raw -Encoding UTF8
    
    # 替换Font Awesome CDN链接
    $content = $content -replace 'https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/6\.0\.0/css/all\.min\.css', './assets/fonts/font-awesome.min.css'
    
    # 替换Google Fonts链接
    $content = $content -replace 'https://fonts\.googleapis\.com/css2\?family=Inter:wght@300;400;500;600;700&display=swap', './assets/fonts/inter.css'
    
    # 替换Chart.js CDN链接
    $content = $content -replace 'https://cdn\.jsdelivr\.net/npm/chart\.js', './assets/js/chart.min.js'
    
    # 替换占位符图片
    $content = $content -replace 'https://via\.placeholder\.com/32x32/4F46E5/FFFFFF\?text=A', './assets/images/user-avatar.svg'
    
    # 写回文件
    Set-Content $file -Value $content -Encoding UTF8
    Write-Host "已更新 $file"
}

Write-Host "所有HTML文件已更新完成"
