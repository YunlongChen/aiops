# 修复Font Awesome CSS路径
$htmlFiles = Get-ChildItem -Path . -Filter "*.html" | Where-Object { $_.Name -ne "demo.html" }

foreach ($file in $htmlFiles) {
    Write-Host "Updating $($file.Name)..."
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $content = $content -replace './assets/fonts/font-awesome\.min\.css', './assets/fonts/fontawesome-all.min.css'
    Set-Content -Path $file.FullName -Value $content -Encoding UTF8
}

Write-Host "All HTML files updated with correct Font Awesome CSS path!"
