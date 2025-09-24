# 下载Google Fonts Inter字体
$fontUrl = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
$fontCss = Invoke-WebRequest -Uri $fontUrl -UseBasicParsing

# 解析CSS中的字体文件URL
$fontUrls = [regex]::Matches($fontCss.Content, "url\(([^)]+)\)") | ForEach-Object { $_.Groups[1].Value }

# 创建本地CSS文件
$localCss = $fontCss.Content

# 下载每个字体文件并更新CSS中的路径
$counter = 1
foreach ($url in $fontUrls) {
    $cleanUrl = $url -replace "['""]", ""
    $fileName = "inter-$counter.woff2"
    $localPath = "assets\fonts\$fileName"
    
    try {
        Invoke-WebRequest -Uri $cleanUrl -OutFile $localPath
        $localCss = $localCss -replace [regex]::Escape($url), "./fonts/$fileName"
        Write-Host "Downloaded: $fileName"
        $counter++
    } catch {
        Write-Host "Failed to download: $cleanUrl"
    }
}

# 保存本地CSS文件
$localCss | Out-File -FilePath "assets\fonts\inter.css" -Encoding UTF8
Write-Host "Google Fonts downloaded and localized"
