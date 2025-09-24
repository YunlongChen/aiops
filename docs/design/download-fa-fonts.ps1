# 创建字体文件下载脚本
$fontUrls = @(
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.woff2",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-regular-400.woff2",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-brands-400.woff2"
)

foreach ($url in $fontUrls) {
    $fileName = Split-Path $url -Leaf
    Write-Host "Downloading $fileName..."
    Invoke-WebRequest -Uri $url -OutFile "assets/fonts/$fileName"
}
Write-Host "Font files downloaded successfully!"
