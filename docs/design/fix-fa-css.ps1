# 修复Font Awesome CSS中的字体路径
$cssFile = "assets/fonts/fontawesome-all.min.css"
$content = Get-Content $cssFile -Raw -Encoding UTF8

# 替换字体文件路径
$content = $content -replace '\.\./webfonts/', './'
$content = $content -replace 'url\(([^)]*webfonts/[^)]*)\)', 'url(./$1)'

Set-Content -Path $cssFile -Value $content -Encoding UTF8
Write-Host "Font Awesome CSS paths updated!"
